import os
import sys
import subprocess

if sys.version_info[0] < 3:
  from urllib2 import urlopen
else:
  from urllib.request import urlopen

from pyvodm.model import Model
from pyvodm.modelMap import ModelMap
from pyvodm.document import Document, ObjectType, DataType, EnumType, PrimitiveType, ReferenceType, FieldType


class DocBuilder:
  """
  Class to orchestrate the construction of a Document.

  Attributes:
    models    - Hash of VO-DML models   (Model)
    map       - Instance Template       (ModelMap)
    fheader   - Source data file header (OrderedDict)

  """

  def __init__(self):
    """
    """
    self.__clear__()

  def __clear__(self):
    self.models   = {}
    self.template = None
    self.fheader = None

    self._document = None   # Document being built
    self._referenced = []   # IDs of objects referenced by others


  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    retstr  = "Method not yet implemented."
    return retstr

  # --------------------------------------------------------------------------------
  # Private methods
  # --------------------------------------------------------------------------------
  def _identify_referenced_elements( self ):
    """
    Scan the map, identifying elements which are referenced by other objects.
    This just provides a shortcut means of setting the 'referable' field.
    """

    for element in self.template.iter():
      if element.value.startswith("ref:"):
        refid = element.value.split(":").pop()
        if refid not in self._referenced:
          self._referenced.append( refid )


  def _identify_required_models( self ):
    """
    Scan the map, identifying which models are represented.
    """
    required = []

    for element in self.template.iter():
      if not element.role.startswith("vodml:"):

        # check model of element 'role'
        prefix = element.role.split(":")[0]
        if prefix not in required:
          required.append( prefix )

        # check model of element 'type'
        try:
          self._resolve_vodml_type( element )
        except Exception:
          pass
        else:
          prefix = element.etype.split(":")[0]
          if prefix not in required:
            required.append( prefix )
    
    #if len(required) > 0:
    #  print("Template requires the following Models, {0}\n".format( sorted(required) ) )

    return required


  def _check_for_required_models( self ):
    """
    Scan the map, identifying which models are represented.
    And check that they are loaded.
    """
    missing  = {}

    required = self._identify_required_models()
    for prefix in required:
      try:
        m = self.models[prefix]
      except Exception:
        # missing model spec
        missing[ prefix ] = 1
        pass

    if len(missing) > 0:
      raise ValueError("Template requires Models not loaded, {0}\n".format( sorted(missing.keys()) ) )
                       

  def _load_document( self ):
    """
    Load Document content using Structure elements from map file.
    Structural elements are those with Role = "vodml:*" and 
    organizes the Instances into blocks.
        Role
        vodml:metadata   - Starts block of metadata instances
        vodml:templates  - Starts block of data instances
                            (may contain metadata, but at least some of the
                             elements are expected to be FieldType)
        vodml:instance   - Insert specified instance here.
                             (value identifies instance by ID)
        vodml:terminate  - End of Structural records
                             convenience tag to stop ModelMap iteration
    """
    key = ""
    level = ""

    for element in self.template.iter():
      if element.role.startswith("vodml:"):
        if element.role == "vodml:metadata":
          key = element.name
          level = element.role
          continue
        elif element.role == "vodml:templates":
          key = element.etype
          level = element.role
          self.document.set_datanode( element.etype )
          continue
        elif element.role == "vodml:instance":
          # create specified instance
          tag = element.value.split(":").pop()
          obj = self._new_element( tag )
        
          # add instance to appropriate section of the Document
          if level == "vodml:metadata":
            self.document.add_metadata( obj, key )
        
#          elif level == "vodml:templates":
#            self.document.add_body( obj )
#            data = None
#            for item in self.document._metadata.get("Default"):
#              try:
#                data = item.get_compositions( key )
#              except Exception as ex:
#                pass
#            if data is not None:
#              data.append(obj)
        
        elif element.role == "vodml:terminate":
          break
        else:
          raise ValueError("Unrecognized structural role in template map, '{0}'".format(element.role) )


  def _new_element(self, tag ):
    """
    Create instance of element associated with the given tag.

    Parameters:
    ----------
      tag       - string
                    UID of element to create from template map.

    """
    if type(tag) not in ( str, ):
      raise TypeError("'tag' argument must be string type, not {0}".format( tag.__class__.__name__ ) )

    result = None

    # Get ModelMap element record
    #  raises ValueError if not matched
    element = self.template.find( uid=tag )

    # Get corresponding Model specification
    #  raises ValueError if not matched
    prefix = element.role.split(":")[0]
    modelspec = self.models[prefix].get( element.role )

    if modelspec.etype in ["objectType"]:
      result = self._new_objectType( tag )
    elif modelspec.etype in ["dataType"]:
      result = self._new_dataType( tag )
    elif modelspec.etype in ["attribute"]:
      result = self._new_valueType( tag )
    elif modelspec.etype in ["collection", "composition"]:
      result = self._new_composition( tag )
    elif modelspec.etype in ["reference"]:
       result = self._new_reference( tag )
    else:
      raise ValueError("Unrecognized element type ("+modelspec.etype+") for tag=\'"+tag+"\'")

    #Set flag if this element is referenced.
    if tag in self._referenced:
      result.setReferenced( True )

    return result

  def _new_valueType(self, tag ):
    """
    Create instance of appropriate subclass of ValueType.
    """
    #Get ModelMap element record
    element = self.template.find( uid=tag )

    # resolve vodml_type
    self._resolve_vodml_type( element )

    # check Model spec of this class to see what kind of ValueType this is.
    try:
      datype = element.etype
      kind = self.models[datype.split(":")[0]].get( datype ).etype
    except KeyError:
      raise KeyError("new_valueType() - Problem resolving Type of '{0}', Model not loaded?.\n".format( datype ) )
    except:
      raise ValueError("new_valueType() - Unexpected problem resolving type of '{0}.\n",format(datype) )

    #Instantiate the specific ValueType 
    if kind in ["dataType"]:
      result = self._new_dataType( tag )
    elif kind in ["enumeration"]:
      result = self._new_enumType( tag )
    elif kind in ["primitiveType"]:
      result = self._new_primType( tag )
    else:
      raise ValueError("new_valueType() - Unrecognized ValueType flavor '{0}.\n",format(kind) )

    return result


  def _new_enumType(self, tag ):
    """
    Create new instance of EnumType.
    """
    #Get ModelMap element record
    element = self.template.find( uid=tag )

    # resolve instance name
    ename = element.name.split(':').pop().split('.').pop()

    # resolve vodml_type
    self._resolve_vodml_type( element )

    # resolve value
    valstr = self._resolve_value( element )

    #Create it.
    result = EnumType( refid=tag, name=ename, desc=element.description, value=valstr )

    #Assign vodml role and type
    result.vodml_role  = element.role
    result.vodml_type = element.etype

    #Add Literals list from Model.
    prefix = element.role.split(":")[0]
    model = self.models[prefix]
    #TODO: iterator through model records
    for item in model._records.keys():
      if item.startswith( element.etype+"." ):  # Child of Enumeration type.
        result.add_literal( item, item.split(".").pop() )

    return result


  def _new_primType(self, tag ):
    """
    Create new instance of Primitive Type.
    """
    #Get ModelMap element record
    element = self.template.find( uid=tag )

    # resolve instance name
    ename = element.name.split(':').pop().split('.').pop()

    # resolve vodml_type
    self._resolve_vodml_type( element )

    # resolve value
    valstr = self._resolve_value( element )

    #Create it.
    result = PrimitiveType( refid=tag, name=ename, desc=element.description, value=valstr )

    #Assign vodml role and type
    result.vodml_role  = element.role
    result.vodml_type = element.etype

    return result


  def _new_dataType(self, tag ):
    """
    Create new instance of DataType.
    """
    #Get ModelMap element record
    element = self.template.find( uid=tag )

    # resolve instance name
    ename = element.name.split(':').pop().split('.').pop()

    # resolve vodml_type
    self._resolve_vodml_type( element )

    # initialize value
    valstr = element.value

    #Create it.
    # o Handle complex DataType-s
    if valstr.startswith("inline:"):
      # o Complex DataType populated by another instance record.
      # create THAT instance...
      tag = valstr[ valstr.find(":")+1: ]
      result = self._new_element( tag )

      # re-assign element role to this spec.
      result.vodml_role = element.role

    else:
      if valstr == "":
        # o Non-valued DataType-s 
        obj = DataType( refid=tag,
                        name=ename,
                        desc=element.description,
                        ucd=element.ucd
                      )
        result = self._add_children( obj )

      elif element.value.startswith("field:"):
        result = None
        valstr = self._resolve_value( element )
        result = FieldType( refid=tag,
                            name=ename,
                            desc=element.description,
                            unit=element.unit,
                            ucd=element.ucd,
                            value=valstr,
                            )
      else:
        # o Handle value-d DataType-s (ie: Quantities)
        valstr = self._resolve_value( element )
        result = DataType( refid=tag,
                           name=ename,
                           desc=element.description,
                           value=valstr,
                           unit=element.unit,
                           ucd=element.ucd
                         )

      #Assign vodml role and type
      result.vodml_role = element.role
      result.vodml_type = element.etype

    return result


  def _new_objectType(self, tag ):
    """
    Create new instance of ObjectType.

    Parameters:
      tag          - string   
                       UID of template map record
    """
    #Get ModelMap element record
    element = self.template.find( uid=tag )

    # resolve name
    ename = element.name

    # resolve vodml_type
    self._resolve_vodml_type( element )

    # Create object
    result = ObjectType(refid=tag,
                        name=ename,
                        desc=element.description
                       )

    #Assign vodml role and type 
    result.vodml_role = element.role
    result.vodml_type = element.etype

    #Add child elements
    result = self._add_children( result )

    return result


  def _new_composition(self, tag ):
    """
    Create new instance of composition to ObjectType.
    """

    #Get ModelMap element record
    element = self.template.find( uid=tag )

    if not element.value.startswith("inline:"):
      raise ValueError("Unrecognized value spec for composition element ("+tag+").")

    #Get ID of composed instance.
    itag = element.value.split(":").pop()

    #Create object
    result = self._new_objectType( itag )

    # re-assign element role to this spec.
    result.vodml_role = element.role

    #Set flag if this element is referenced.
    if itag in self._referenced:
      result.setReferenced( True )

    return result

  def _new_reference(self, tag ):
    """
    Create new instance of Reference to ObjectType.
    """
    #Get ModelMap element record
    element = self.template.find( uid=tag )

    # resolve instance name
    ename = element.name.split(':').pop().split('.').pop()

    # resolve vodml_type
    self._resolve_vodml_type( element )

    # resolve value for target
    if not element.value.startswith("ref:"):
      raise ValueError("Unrecognized value spec for reference element ("+tag+"), does not contain reference.")
    valstr = element.value.split(':').pop().strip()

    # Create it.
    result = ReferenceType( refid=tag, name=ename, desc=element.description, target=valstr )

    #Add vodml role and type info
    result.vodml_role = element.role
    result.vodml_type = element.etype

    return result


  def _add_children(self, obj ):
    """
    Add children elements to the provided object 
    """
    result = obj

    tag = obj.refid

    # Find children of provided Object in ModelMap
    children = self.template.find_children( tag )
    for key in children.keys():
      child = children[key]

      item = self._new_element( key )
      ctype = item.__class__.__name__
      if ctype in [ "ObjectType" ]:
        result.add_composition( item )
      elif ctype in [ "ReferenceType" ]:
        result.add_reference( item )
      elif ctype in [ "DataType", "EnumType", "PrimitiveType" ]:
        result.add_attribute( item )
      elif ctype in [ "FieldType" ]:
        result.add_attribute( item )
        self.document.add_body( item )
      else:
        raise ValueError("Unrecognized child object type. {0}".format( item.__class__.__name__ ) )

    return result

  def _resolve_value(self, element ):
    """
    Evaluate ModelMap element value field and resolve it

    Parameters
      element   - ModelMap record

    Returns
      result    - resolved value as a string
    
    """
    result = ""

    if element.value.startswith("lit:"):
      # Element value is provided directly
      result = element.value[element.value.find(":")+1:]

    elif element.value.startswith("key:"):
      # pull keyword value from file header info
      if self.fheader is None:
        raise ValueError("No source file info loaded, can not resolve value for element '{0}'\n".format( element.uid ) )
      else:
        kname = element.value[element.value.find(":")+1:].strip()
        try:
          kval = self.fheader[ kname ]
        except KeyError as ex:
          raise ValueError("Key '{0}' not found in source file, can not resolve value for element '{1}'\n".format(kname, element.uid) )

      # return key value as string
      result = str( kval )

    elif element.value.startswith("field:"):
      result = element.value[element.value.find(":")+1:].strip()

#    elif element.value.startswith("field:"):
#      try:
#        kname = element.value[element.value.find(":")+1:]
#        if type(self.tab) in ( [cr.TABLECrate] ):
#          #value comes from TableCrate column
#          col    = self.tab.get_column( kname )
#          tag    = "_col-"+kname
#          refid  = "_col-"+kname
#          valstr = ""
#          kunit  = col.unit
#        elif type(self.tab) in ( [cr.IMAGECrate] ):
#          col    = self.tab.get_image()
#          tag    = "_image-"+col.name
#          refid  = "_image-"+col.name
#          valstr = ""
#          kunit  = col.unit
#      except:
#        valstr = "FIELD NOT FOUND"
#
#    elif element.value.startswith("image.shape"):
#      try:
#        kname = element.value[element.value.find(":")+1:]
#        col = self.tab.get_image()
#        if element.value.startswith("image.shape[0]:"):
#          valstr = str( col.get_shape()[0] )
#        elif element.value.startswith("image.shape[1]:"):
#          valstr = str( col.get_shape()[1] )
#        elif element.value.startswith("image.shape[2]:"):
#          valstr = str( col.get_shape()[2] )
#        elif element.value.startswith("image.shape[3]:"):
#          valstr = str( col.get_shape()[3] )
#      except:
#        valstr = "IMAGE NOT FOUND"
#
#    elif element.value.startswith("ss."):
#      kname = element.value[element.value.find(":")+1:]
#      try:
#        if type(self.tab) in ( [cr.TABLECrate] ):
#          #Get TableCrate column
#          col = self.tab.get_column( kname )
#        elif type(self.tab) in ( [cr.IMAGECrate] ):
#          #Get ImageCrate axes
#          col = self.tab.get_axis( kname )
#      except:
#        valstr = "COL NOT FOUND"
#
#      try:
#        if element.value.startswith("ss.min:"):
#          #pull domain minimum
#          valstr = str( col.get_tlmin() )
#          kunit  = col.unit
#        elif element.value.startswith("ss.max:"):
#          #pull domain maximum
#          valstr = str( col.get_tlmax() )
#          kunit  = col.unit
#      except:
#        valstr = "SUBSPACE PARAM NOT FOUND"
#
#    elif element.value.startswith("trans."):
#      kname = element.value[element.value.find(":")+1:]
#      try:
#        if type(self.tab) in ( [cr.TABLECrate] ):
#          #Get Transform from TableCrate column
#          col   = self.tab.get_column( kname )
#          trans = col.get_transform()
#        elif type(self.tab) in ( [cr.IMAGECrate] ):
#          #Get Transform from ImageCrate axes
#          trans = self.tab.get_transform( kname )
#      except:
#        valstr = "XFORM NOT FOUND"
#
#      try:
#        if element.value.startswith("trans.ctype:"):
#          #pull Projection type from TableCrate column transform
#          tmpstr = str( trans.get_parameter_value("CTYPE")[0] )
#          valstr = tmpstr.split('-').pop()
#        elif element.value.startswith("trans.crpix"):
#          #pull Native Reference value from TableCrate column transform
#          vals = trans.get_parameter_value("CRPIX")
#          if element.value.startswith("trans.crpix[0]:"):
#            valstr = str( vals[0] )
#          elif element.value.startswith("trans.crpix[1]:"):
#            valstr = str( vals[1] )
#        elif element.value.startswith("trans.crval"):
#          #pull Target Reference value from TableCrate column transform
#          vals = trans.get_parameter_value("CRVAL")
#          if element.value.startswith("trans.crval[0]:"):
#            valstr = str( vals[0] )
#          elif element.value.startswith("trans.crval[1]:"):
#            valstr = str( vals[1] )
#        elif element.value.startswith("trans.cdelt"):
#          #pull Target Reference value from TableCrate column transform
#          vals = trans.get_parameter_value("CDELT")
#          if element.value.startswith("trans.cdelt[0]:"):
#            valstr = str( vals[0] )
#          elif element.value.startswith("trans.cdelt[1]:"):
#            valstr = str( vals[1] )
#        elif element.value.startswith("trans.matrix"):
#          #pull Transform Matrix element from TableCrate column transform
#          matrix = trans.get_transform_matrix()      
#          if element.value.startswith("trans.matrix[0][0]:"):
#            valstr = str( matrix[0][0] )
#          elif element.value.startswith("trans.matrix[0][1]:"):
#            valstr = str( matrix[0][1] )
#          elif element.value.startswith("trans.matrix[0][2]:"):
#            valstr = str( matrix[0][2] )
#          elif element.value.startswith("trans.matrix[1][0]:"):
#            valstr = str( matrix[1][0] )
#          elif element.value.startswith("trans.matrix[1][1]:"):
#            valstr = str( matrix[1][1] )
#          elif element.value.startswith("trans.matrix[1][2]:"):
#            valstr = str( matrix[1][2] )
#          elif element.value.startswith("trans.matrix[2][0]:"):
#            valstr = str( matrix[2][0] )
#          elif element.value.startswith("trans.matrix[2][1]:"):
#            valstr = str( matrix[2][1] )
#          elif element.value.startswith("trans.matrix[2][2]:"):
#            valstr = str( matrix[2][2] )
#      except:
#        valstr = "XFORM PARAM NOT FOUND"
#
    else:
      raise ValueError("Unrecognized value form on element '{0}'".format(element.uid) )
#    else:
#      valstr = element.value

    return result


  def _resolve_vodml_type(self, element ):
    """
    Evaluate ModelMap element, if vodml_type is not specified
    extract and assign the default from Model specs.

    Parameters
      element   - ModelMap record
    
    """
    if element.etype == "":
      # ModelMap does not specify, use default from Model
      # o Get corresponding Model record for this element
      prefix = element.role.split(":")[0]
      modelspec = self.models[prefix].get( element.role )
      
      # o Pull default type from Model spec.
      if ':' not in modelspec.dtype:
        vodml_type = prefix + ":" + modelspec.tag
      else:
        vodml_type = modelspec.dtype
          
      element.etype = vodml_type


  # --------------------------------------------------------------------------------
  # Public methods
  # --------------------------------------------------------------------------------
  def add_model( self, fname ):
    """
    Loads specified model specification and adds to stored set.
  
    Parameters
    ----------
  
      fname: string
                Filename/URL of vo-dml model specification table.

    Returns
    --------
  
      None
  
  
    Raises
    --------
  
    IOError:
               Invalid fname input.
               Error opening file.
    """

    m = Model( fname )
    m.url = fname
    
    self.models[ m.prefix ] = m


  def add_instance_map( self, fname ):
    """
    Load and store specified instance template.
    Any existing map will be replaced.
  
    Parameters
    ----------
  
      fname: string
                Filename of model instance specification table (ModelMap).

    Returns
    --------
  
      None
  
  
    Raises
    --------
  
    IOError:
               Invalid fname input.
               Error opening file.
    """

    # load the instance map 
    self.template = ModelMap( fname )

    # check that all required models are loaded
    self._check_for_required_models()

    # identify elements which are referenced
    self._identify_referenced_elements()



  def process( self, infile, exten=1 ):
    """
    Process provided file and create Document.
  
    Arguments
    ---------
    
      infile   : string
                 input file to process
      exten    : integer
                 HDU of file to process (0 based)

    Returns
    --------

      Document :   Model instance with content populated from file
  
  
    Raises
    --------
  
      TypeError:  invalid argument error 
  
      IOError  :  problem interacting with file.

    """

    # Copy file to local temporary space
    if infile.startswith("http:") or  infile.startswith("https:") or infile.startswith("file:"):
      fname = infile
    elif infile.startswith('.'):
#      fname = "file://"+os.getcwd()+infile[1:]
      fname = "file://"+os.path.abspath( infile )
    else:
      fname = "file://"+infile
    
    import tempfile
    fh = urlopen( fname )
    tfile = tempfile.NamedTemporaryFile( delete=False )
    tfile.write( fh.read() )
    tfile.close()
    
    # Load file header
    self.fheader = self._get_header( tfile.name, exten )

    # Delete temporary file
    os.unlink(tfile.name)
    
    # Create Document to hold content
    self.document = Document()
    self.document._source = fname
    self.document._source_ext = exten
    
    # load Document from file.
    self._load_document()

    # Attach info on models used in the Document
    # NOTE: we have already checked that all required models are loaded
    #       so can be loose with accessing the models hash here.
    used = self._identify_required_models()
    for prefix in used:
      self.document.add_model_pointer( prefix, self.models[prefix].url )
    
    # return resulting document
    result = self.document
    self.document = None
    return result


  def _get_header( self, filename, exten=1 ):
    """
    Loads file metadata into local variable
    """
    from astropy.table import Table

    # Open file/exten
    t = Table.read( filename, hdu=exten )

    # Extract header metadata
    result = t.meta

    # Remove unnecessary records
    if result is not None:
      for key in ( 'comments', 'HISTORY' ):
        try:
          del result[ key ]
        except KeyError as ex:
          pass
    
    return result;
