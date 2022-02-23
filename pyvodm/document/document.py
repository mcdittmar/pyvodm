import os
from collections import OrderedDict

class Document:
  """
  Container class for a DOM-like hierarchy of VO-DML element
  types which form an instance of a VO-DML datamodel.
  """
  def __init__(self):
    self.__clear__()

  def __clear__(self):
    self._metadata   = OrderedDict()  # Header metadata objects
    self._body       = []             # Body/Data objects
    self._models     = OrderedDict()  # Pointers to relevant models
    self._source     = ""             # Pointer to source file
    self._source_ext = ""             #  - extension number within source file

  def __str__(self):
    retstr = self.__repr__() + "\n"
    return retstr

  def __repr__(self):

    retstr  = "<DOCUMENT>\n"
    retstr += "  <INFO  value='IVAO Datamodel Instance document'/>\n"

    if ( len(self._models) > 0 ):
      # Add Model tags
      for key in self._models.keys():
        retstr += "  <MODEL prefix='{0}' url='{1}'/>\n".format( key, self._models[ key ] )

    if ( len(self._metadata) > 0 ):
      # Add Metadata blocks
      for key in self._metadata.keys():
        metastr = "  "

        tmpstr = "<METADATA name='{0}'>\n".format(key)
        entries = self._metadata[ key ]
        for rec in entries:
          blkstr  = "  " + repr(rec).replace('\n','\n  ')  # indent sub-content
          tmpstr += blkstr + "\n"
        tmpstr += "</METADATA>"

        metastr += tmpstr.replace('\n','\n  ')

        retstr += metastr + "\n"

    retstr  += "</DOCUMENT>\n"

    return retstr


  def add_metadata( self, obj, key="default" ):
    """
    Add Object to metadata section of Document.

    Parameters
    ----------
  
      obj   : ObjectType
                Object to add

      key   : string
                vo-dml id of the Object.

    Returns
    --------
  
      none
  
  
    Raises
    --------
  
      TypeError:  invalid argument error 
  
    """
    if obj.__class__.__name__ not in ( "ObjectType", "DataType" ):
      raise TypeError("'obj' argument must be ObjectType type, not {0}".format( obj.__class__.__name__ ) )

    # make sure hash entry exists for this role
    if self._metadata.get( key ) == None:
      self._metadata[ key ] = []

    # add object to hash
    self._metadata[ key ].append(obj)


  def add_model_pointer( self, prefix, url ):
    """
    Add pointer to Model spec in Document

    Parameters
    ----------
  
      prefix : string
                Model 'name'

      url    : string
                URL pointer to Model spec.

    Returns
    --------
  
      none
  
  
    Raises
    --------
  
      TypeError:  invalid argument error 
  
    """
    if not isinstance( prefix, str ):
      raise TypeError("'prefix' argument must be string type, not {0}".format( prefix.__class__.__name__ ) )

    if not isinstance( url, str ):
      raise TypeError("'url' argument must be string type, not {0}".format( url.__class__.__name__ ) )

    # add object to hash
    self._models[ prefix ] = url


  def add_body( self, obj ):
    """
    Add FieldType to body section of Document.

    Parameters
    ----------
  
      obj   : FieldType
                Object to add

    Returns
    --------
  
      none
  
  
    Raises
    --------
  
      TypeError:  invalid argument error 
  
    """
    if obj.__class__.__name__ not in ( "FieldType", ):
      raise TypeError("'obj' argument must be FieldType type, not {0}".format( obj.__class__.__name__ ) )

    self._body.append(obj)


  def set_datanode( self, role ):
    """
    Find element with the given role and flag it as a datanode (instance template)

    Parameters
    ----------
  
      role   : string
                VO-DML role of the element to flag.

    Returns
    --------
  
      none
  
  
    Raises
    --------
  
      TypeError:  invalid argument error 
  
    """
    if not isinstance( role, str ):
      raise TypeError("'role' argument must be string type, not {0}".format( role.__class__.__name__ ) )

    if role == "":
      return
    
    found = False

    if ( len(self._metadata) > 0 ):
      # Search Metadata blocks
      for key in self._metadata.keys():
        entries = self._metadata[ key ]
        for rec in entries:
          if rec.__class__.__name__ in ( "ObjectType" ):
            if rec.vodml_role == role:
              found = True
              rec._datanode = True
            else:
              if rec.vodml_role in role:
                # the given role is a child of this node
                for child in rec.get_compositions(role):
                  if child.vodml_role == role:
                    found = True
                    child._datanode = True
    if not found:
      raise ValueError("role '"+role+"' not found in document.")


  def find_data_node( self ):
    """
    Find element flagged as a datanode (instance template) and return
    the list of those instances.

    Parameters
    ----------
  
      none

    Returns
    --------
  
      []      - list of ObjectType instances tagged with datanode=True
      None    - if none found
  
  
    Raises
    --------
  
  
    """
    result = None

    # This is not a deep search, and I think the idea was to have these
    # instances on the 'body' element of the Document, but the code has
    # not migrated that far yet, and that element only has the leaves
    # which are FieldType-s.

    if ( len(self._metadata) > 0 ):
      # Search Metadata blocks
      for key in self._metadata.keys():
        entries = self._metadata[ key ]
        for instance in entries:
          if instance.__class__.__name__ in ( "ObjectType" ):
            if instance._datanode == True:
              if result is None:
                result = []
              result.append(instance)
            else:
              # Scan the child compositions of the primary instances.
              # we're not going recursive here... yet
              for compkey in instance._compositions:
                if instance._compositions[compkey][0]._datanode == True:
                  if result is None:
                    result = []
                  result.extend( instance._compositions[compkey] )

    return result

#================================================================================
class ElementType(object):
  """
  Parent class for vo-dml element types.

  Has the basic information for all vo-dml elements:
    refid        - Element ID (for referencing the element)
    name         - Element name
    description  - Element description

    vodml_role   - VO-DML ID of the element role
    vodml_type   - VO-DML ID of the element type

  """
  def __init__(self, refid="", name="", desc=""):

    if not isinstance( refid, str ):
      raise TypeError("'refid' argument must be string type, not {0}".format( refid.__class__.__name__ ) )

    if not isinstance( name, str ):
      raise TypeError("'name' argument must be string type, not {0}".format( name.__class__.__name__ ) )
  
    if not isinstance( desc, str ):
      raise TypeError("'desc' argument must be string type, not {0}".format( desc.__class__.__name__ ) )


    self.refid        = refid
    self.name         = name
    self.description  = desc

    self.vodml_role   = ""    # VO-DML ID of the instance Role
    self.vodml_type   = ""    # VO-DML ID of the instance Type


  def __str__(self):
    retstr = self.__repr__() + "\n"
    return retstr

  def __repr__(self):
    retstr = "<ELEMENT "+self__repr_basic_args__()
    if self.description == "":
      retstr += "/>"
    else:
      retstr += ">\n"
      retstr += self.__repr_description__()
      retstr += "</ELEMENT>"
    return retstr

  def __repr_basic_args__(self):
    retstr = "ID='{0}' name='{1}' vodml_role='{2}' vodml_type='{3}'".format(self.refid, self.name, self.vodml_role, self.vodml_type)
    return retstr

  def __repr_description__(self):
    retstr = "  <DESCRIPTION>{0}</DESCRIPTION>\n".format(self.description)
    return retstr


#================================================================================
class ObjectType(ElementType):
  """
  Extension of ElementType representing a VO-DML ObjectType

  Adds
    attributes   - Set of element attributes
                     keyed by 'role' may have multiple instances for any role.
    references   - Set or references to other ObjectType-s
                     keyed by 'role' may have multiple instances for any role.
    compositions - Set of compositions with other ObjectType-s
   
  """

  def __init__(self, refid="", name="", desc="" ):
    super(ObjectType, self).__init__(refid, name, desc)

    self._attributes   = OrderedDict()
    self._references   = OrderedDict()
    self._compositions = OrderedDict()

    self._referenced  = False # internal flag that the Object is referenced from another Element(s)
    self._datanode    = False # internal flag that the Object starts a template describing multiple instances (ie:Table content)
   
  def __repr__(self):
    retstr = "<OBJECT "+self.__repr_basic_args__()
    if ( (self.description == "") and (len(self._attributes)+len(self._references)+len(self._compositions)) == 0 ):
      retstr += "/>"
    else:
      retstr += ">\n"

      if ( self.description != "" ):
        retstr += self.__repr_description__()

      if len(self._attributes) > 0:
        # Add attributes block
        tmpstr = "  " + self.__repr_attributes__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"

      if len(self._references) > 0:
        # Add references block
        tmpstr = "  " + self.__repr_references__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"

      if len(self._compositions) > 0:
        # Add compositions block
        tmpstr = "  " + self.__repr_compositions__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"

      retstr += "</OBJECT>"
    return retstr

  def __repr_attributes__(self):
    retstr = "<ATTRIBUTES>\n"
    for item in self._attributes.keys():
      for inst in self._attributes[item]:
        tmpstr = "  "+repr(inst).replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"
    retstr += "</ATTRIBUTES>"
    return retstr

  def __repr_references__(self):
    retstr = "<REFERENCES>\n"
    for item in self._references.keys():
      for inst in self._references[item]:
        tmpstr  = "  "+repr(inst).replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"
    retstr += "</REFERENCES>"
    return retstr

  def __repr_compositions__(self):
    retstr = "<COMPOSITIONS>\n"
    for item in self._compositions.keys():
      for inst in self._compositions[item]:
        tmpstr  = "  "+repr(inst).replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"
    retstr += "</COMPOSITIONS>"
    return retstr


  def add_attribute(self, item):
    """
    Add provided object to attribute list

    Parameters
    ----------
  
      item   : ValueType
                Attribute element of Object.
  
    Returns
    --------
  
        none
  
  
    Raises
    --------
  
       TypeError:  invalid argument error 
  
    """

    #if isinstance( item, ValueType ):
    if item.__class__.__name__ not in ( "DataType", "EnumType", "PrimitiveType", "FieldType" ):
      raise TypeError("'item' argument must be ValueType object, not "+item.__class__.__name__ )

    # make sure hash entry exists for this role
    if self._attributes.get( item.vodml_role ) == None:
      self._attributes[ item.vodml_role ] = []

    # add object to hash
    self._attributes[ item.vodml_role ].append(item)


  def add_composition( self, item  ):
    """
    Add provided object to composition list

    Parameters
    ----------
  
      item   : ObjectType
                Element in composition with this Object.
  
    Returns
    --------
  
      none
  
  
    Raises
    --------
  
      TypeError:  invalid argument error 
  
    """
    if item.__class__.__name__ not in ( "ObjectType", ):
      raise TypeError("'item' argument must be ObjectType object, not "+item.__class__.__name__ )

    # make sure hash entry exists for this role
    if self._compositions.get( item.vodml_role ) == None:
      self._compositions[ item.vodml_role ] = []

    # add object to hash
    self._compositions[ item.vodml_role ].append( item )


  def add_reference(self, item):
    """
    Add provided object to reference list

    Parameters
    ----------

    item   : ReferenceType
             Reference to Element.

    Returns
    --------

        none


    Raises
    --------

         TypeError:  invalid argument error

    """

    if item.__class__.__name__ not in ( "ReferenceType", ):
      raise TypeError("'item' argument must be ReferenceType object, not "+item.__class__.__name__ )

    if item.target == "":
      raise ValueError("invalid or empty reference ID in \'"+item.name+"\'")

    # make sure hash entry exists for this role
    if self._references.get( item.vodml_role ) == None:
      self._references[ item.vodml_role ] = []

    # add object to hash
    self._references[ item.vodml_role ].append(item)


  def get_compositions( self, role ):
    """
      Returns a list of composed Objects with the assigned role.

    Parameters
    ----------
  
      role   : string
                VO-DML role to match
  
    Returns
    --------
  
      none
  
  
    Raises
    --------

      none
    """
    retval = None

    for key in self._compositions : # dictionary
      if key == role:
        retval = self._compositions[ role ]

    return retval
 

  def isReferenced(self):
    """
    Reports state of flag indicating that the element is referenced or not.

    Parameters
    ----------

      none
  
  
    Returns
    --------
  
      flag   : boolean
                True  = element is referenced by other elements.
                False = it is not.
  
  
    Raises
    --------

      none

    """
    return self._referenced


  def setReferenced( self, flag ):
    """
    Identify the element as being referenced or not.
    Useful shortcut for serializations to control the inclusion of the element ID.

    Parameters
    ----------
  
      flag   : boolean
                True  = element is referenced by other elements.
                False = it is not.
  
    Returns
    --------
  
      none
  
  
    Raises
    --------
       TypeError:  invalid argument error 

    """
    if not isinstance( flag, bool ):
      raise TypeError("'flag' argument must be boolean type, not "+flag.__class__.__name__ )

    self._referenced = flag



#================================================================================
class ValueType(ElementType):
  """
  Extension of ElementType representing a VO-DML ValueType

  Adds
    ucd          - UCD associated with the element

  """
  def __init__(self, refid="", name="", desc="", ucd="" ):
    super(ValueType, self).__init__(refid, name, desc)

    if not isinstance( ucd, str ):
      raise TypeError("'ucd' argument must be string type, not {0}".format( ucd.__class__.__name__ ) )

    self.ucd = ucd

  def __repr__(self):
    retstr = "<VALUETYPE " + self.__repr_valuetype_args__()
    if self.description == "":
      retstr += "/>"
    else:
      retstr += ">\n"
      retstr += self.__repr_description__()
      retstr += "</VALUETYPE>"
    return retstr

  def __repr_valuetype_args__(self):
    retstr  = self.__repr_basic_args__()
    if self.ucd != "":
      retstr += " ucd='{0}'".format(self.ucd)
    return retstr

#================================================================================
class PrimitiveType(ValueType):
  """
  Extension of ValueType representing a VO-DML Primitive-s

  Adds
    value        - instance value (as string)

  """
  def __init__(self, value, refid="", name="", desc="", ucd="" ):
    super(PrimitiveType, self).__init__(refid, name, desc, ucd)

    if not isinstance( value, str ):
      raise TypeError("'value' argument must be string type, not {0}".format( value.__class__.__name__ ) )

    self.value = value

  def __repr__(self):
    retstr = "<PRIMITIVE " + self.__repr_valuetype_args__()

    retstr += " value='{0}'".format(self.value)

    if self.description == "":
      retstr += "/>"
    else:
      retstr += ">\n"
      retstr += self.__repr_description__()
      retstr += "</PRIMITIVE>"


    return retstr


#================================================================================
class EnumType(ValueType):
  """
  Extension of ElementType represening a VO-DML Enumerations

  Adds
    value        - instance value (as string)
    literals     - Set of enumeration literals
                     key   = vo-dml id of literal
                     value = associated label
   
  """

  def __init__(self, refid="", name="", desc="", value="", ucd=""):
    super(EnumType, self).__init__(refid, name, desc, ucd)
    
    if not isinstance( value, str ):
      raise TypeError("'value' argument must be string type, not {0}".format( value.__class__.__name__ ) )

    self.value = value
    self._literals = OrderedDict()


  def __repr__(self):
    retstr = "<ENUMERATION "+self.__repr_valuetype_args__()

    retstr += " value='{0}'".format(self.value)

    if ( (self.description == "") and (len(self._literals) == 0) ):
      retstr += "/>"
    else:
      retstr += ">\n"

      if ( self.description != "" ):
        retstr += self.__repr_description__()

      if len(self._literals) > 0:
        for item in sorted( self._literals.keys() ):
          retstr += "  <LITERAL vodmlid='{0}' label='{1}' />\n".format( item, self._literals[ item ] )
      
      retstr += "</ENUMERATION>"
    return retstr

  def add_literal(self, vodmlid, label):
    """
    Add provided object to literals list

    Parameters
    ----------
  
      vodmlid   : string
                  VO-DML ID of the literal

      label     : string
                  Associated label
  
    Returns
    --------
  
        none
  
  
    Raises
    --------
  
       TypeError:  invalid argument error 
  
    """
    if not isinstance( vodmlid, str ):
      raise TypeError("'vodmlid' argument must be string type, not {0}".format( vodmlid.__class__.__name__ ) )

    if not isinstance( label, str ):
      raise TypeError("'label' argument must be string type, not {0}".format( label.__class__.__name__ ) )

    # add to hash
    self._literals[ vodmlid ] = label

#================================================================================
class DataType(ValueType):
  """
  Extension of ElementType represening a VO-DML DataType

  Adds
    attributes   - Set of element attributes
                     keyed by 'role' may have multiple instances for any role.
    references   - Set or references to other ObjectType-s
                     keyed by 'role' may have multiple instances for any role.
   
  """

  def __init__(self, refid="", name="", desc="", vodml_type="", value="", unit="", ucd=""):
    super(DataType, self).__init__(refid, name, desc, ucd)
    
    if not isinstance( vodml_type, str ):
      raise TypeError("'vodml_type' argument must be string type, not {0}".format( dtype.__class__.__name__ ) )

    if not isinstance( value, str ):
      raise TypeError("'value' argument must be string type, not {0}".format( value.__class__.__name__ ) )

    self.vodml_type = vodml_type
    self.value = value
    self.unit  = unit

    self._attributes  = OrderedDict()
    self._references  = OrderedDict()


  def __repr__(self):
    retstr = "<DATATYPE "+self.__repr_valuetype_args__()
    if self.value != "":
      retstr += " value='{0}'".format(self.value)
      if self.unit != "":
        retstr += " unit='{0}'".format(self.unit)

    if ( (self.description == "") and (len(self._attributes) == 0) and (len(self._references) == 0 ) ):
      retstr += "/>"
    else:
      retstr += ">\n"

      if ( self.description != "" ):
        retstr += self.__repr_description__()

      if len(self._attributes) > 0:
        tmpstr = "  " + self.__repr_attributes__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"
      
      if len(self._references) > 0:
        tmpstr = "  " + self.__repr_references__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"

      retstr += "</DATATYPE>"
    return retstr

  def __repr_attributes__(self):
    retstr = "<ATTRIBUTES>\n"
    for item in self._attributes.keys():
      for inst in self._attributes[item]:
        tmpstr  = "  "+repr(inst).replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"
    retstr += "</ATTRIBUTES>"
    return retstr

  def __repr_references__(self):
    retstr = "<REFERENCES>\n"
    for item in self._references.keys():
      for inst in self._references[item]:
        tmpstr  = "  "+repr(inst).replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"
    retstr += "</REFERENCES>"
    return retstr


  def add_attribute(self, item):
    """
    Add provided object to attribute list

    Parameters
    ----------
  
      item   : ValueType
                Attribute element of Object.
  
    Returns
    --------
  
        none
  
  
    Raises
    --------
  
       TypeError:  invalid argument error 
  
    """

    #if isinstance( item, ValueType ):
    if item.__class__.__name__ not in ( "DataType", "EnumType", "PrimitiveType", "FieldType" ):
      raise TypeError("'item' argument must be ValueType object, not "+item.__class__.__name__ )

    # make sure hash entry exists for this role
    if self._attributes.get( item.vodml_role ) == None:
      self._attributes[ item.vodml_role ] = []

    # add object to hash
    self._attributes[ item.vodml_role ].append(item)


  def add_reference(self, item): ## item == ObjectType
    """
    Add provided object to reference list

    Parameters
    ----------

    item   : ReferenceType
             Reference to Element.

    Returns
    --------

        none


    Raises
    --------

         TypeError:  invalid argument error

    """

    if item.__class__.__name__ not in ( "ReferenceType", ):
      raise TypeError("'item' argument must be ReferenceType object, not "+item.__class__.__name__ )

    if item.target == "":
      raise ValueError("invalid or empty reference ID in \'"+item.name+"\'")

    # make sure hash entry exists for this role
    if self._references.get( item.vodml_role ) == None:
      self._references[ item.vodml_role ] = []

    # add object to hash
    self._references[ item.vodml_role ].append(item)


#================================================================================
class FieldType(DataType):
  """
  Extension of DataType to distinguish fields from metadata

  """

  def __init__(self, refid="", name="", desc="", vodml_type="", value="", unit="", ucd=""):
    super(FieldType, self).__init__(refid, name, desc, vodml_type, value, unit, ucd )

  def __repr__(self):
    retstr = "<FIELDTYPE "+self.__repr_valuetype_args__()
    if self.value != "":
      retstr += " value='{0}'".format(self.value)
      if self.unit != "":
        retstr += " unit='{0}'".format(self.unit)
    if ( (self.description == "") and (len(self._attributes) == 0) and (len(self._references) == 0 ) ):
      retstr += "/>"
    else:
      retstr += ">\n"
      if ( self.description != "" ):
        retstr += self.__repr_description__()

      if len(self._attributes) > 0:
        tmpstr = "  " + self.__repr_attributes__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"

      if len(self._references) > 0:
        tmpstr = "  " + self.__repr_references__().replace('\n','\n  ')  # indent sub-content
        retstr += tmpstr + "\n"

      retstr += "</FIELDTYPE>"
    return retstr
    
#================================================================================
class ReferenceType(ElementType):
  """
  Extension of ElementType representing a reference to a VO-DML Element

  Adds
    target      - ID of referenced element

  """
  def __init__(self, target, refid="", name="", desc="" ):
    super(ReferenceType, self).__init__(refid, name, desc)

    if not isinstance( target, str ):
      raise TypeError("'target' argument must be string type, not {0}".format( target.__class__.__name__ ) )

    self.target = target

  def __repr__(self):
    retstr = "<REFERENCE " + self.__repr_basic_args__()
    retstr += " target='{0}'".format(self.target)
    if self.description == "":
      retstr += "/>"
    else:
      retstr += ">\n"
      retstr += self.__repr_description__()
      retstr += "</REFERENCE>"
    return retstr

