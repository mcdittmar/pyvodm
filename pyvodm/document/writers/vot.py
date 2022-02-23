import os

class Indent:
  def __init__(self, level=0 ):
    self.__clear__()

    self._level = level
    self._sp  = "  "
    self._buf = ""

    for ii in range(0, self._level):
        self._buf = self._buf + self._sp

  def __clear__(self):
    self._level = 0
    self._buf   = ""

  def __str__(self):
    return self._buf

  def __repr__(self):
    retstr  = "Not yet implemented.\n"
    return retstr


class VOTWriter:

  def __init__(self, ofile, annotation=None ):
    self.__clear__()

    if type(ofile) not in ( str, ):
      raise TypeError("'ofile' argument must be string type, not {0}".format( ofile.__class__.__name__ ) )

    # Open output file
    try:
        self._fp = open( ofile, "w" )
    except Exception as ex:
        if self._fp is not None:
            self._fp.close()
            self._fp = None
        raise ex

    self._annotation = annotation

    self.VODML = 1


  def __del__(self):
    if self._fp is not None:
      self._fp.close()

  def __clear__(self):
    self._fp = None
    self._annotation = None

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    retstr  = "Not yet implemented.\n"
    return retstr

  global nl
  nl = os.linesep


  def _convert_ivoa_datatype_to_vot( self, ivoatype ):
    """
    Utility method, converts primitive type-s to 
    the corresponding VOTable datatype string.
    """

    #Resolve datatype to VOTable types
    result = ""
    if ivoatype.startswith("ivoa:string"):
      result = "char"
    elif ivoatype.startswith("ivoa:anyURI"):
      result = "char"
    elif ivoatype.startswith("ivoa:datetime"):
      result = "char"
    elif ivoatype.startswith("ivoa:integer") or ivoatype.startswith("ivoa:IntegerQuantity"):
      result = "integer"
    elif ivoatype.startswith("ivoa:nonnegativeInteger"):
      result = "long"
    elif ivoatype.startswith("ivoa:real") or ivoatype.startswith("ivoa:RealQuantity"):
      result = "double"
    elif ivoatype.startswith("ivoa:boolean"):
      result = "boolean"
    elif ivoatype.startswith("coords:Epoch"):
      result = "char"
    else:
      result = "UNMATCHED"

    return result


  def set_annotation( self, tag ):
    if tag == "none":
        self._annotation = None
    elif tag == "vodml":
        self._annotation = self.VODML
    else:
        raise ValueError("Unrecognized annotation type, \"" + tag + "\"" )


  def write( self, doc ):
    """
      Write Document instance to file.
    """
    if doc.__class__.__name__ not in ( "Document", ):
      raise TypeError("'doc' argument must be Document type, not {0}".format( obj.__class__.__name__ ) )

    buf  = str(Indent( 1 ))
    buf2 = str(Indent( 2 ))

    lines = []

    # Preamble
    lines.extend('<?xml version="1.0" encoding="UTF-8"?>'+nl )

    if ( self._annotation is None ):
      lines.extend('<VOTABLE xmlns="http://www.ivoa.net/xml/VOTable/v1.3">'+nl )
    elif ( self._annotation == self.VODML ):
      lines.extend('<VOTABLE xmlns="http://www.ivoa.net/xml/VOTable/v1.4_vodml">'+nl )

    # VODML annotation
    if ( self._annotation == self.VODML ):
        lines.extend( self.write_vodml_annotation( doc, indent=1 ) )

    # VOTable RESOURCE 
    lines.extend( buf + '<RESOURCE>' + nl )
    if ( self._annotation is None ):
      lines.extend( buf2 + '<TABLE>' + nl )
    else:
      lines.extend( buf2 + '<TABLE ID=\"_table1\">' + nl )
      lines.extend( buf2 + '  <DESCRIPTION>With VO-DML annotation enabled, the TABLE content may retain its "native" structure or be reduced to just the PARAM and FIELD elements."</DESCRIPTION>' + nl )

    # Metadata
    lines.extend( self.write_vot_metadata( doc, indent=3 ) )

    # Data
    lines.extend( self.write_vot_data( doc, indent=3 ) )

    lines.extend( buf2 + '</TABLE>' + nl )
    lines.extend( buf + '</RESOURCE>' + nl )
    lines.extend( '</VOTABLE>'+nl )

    self._fp.writelines( lines )

  # ================================================================================
  # VOTable specific methods
  # ================================================================================
  def write_vot_metadata( self, doc, indent=0 ):
    buf = str(Indent( indent ))

    lines = []
    for role in doc._metadata:
      for obj in doc._metadata[ role ]:
        lines.extend( self.write_vot_element( obj, indent ) )

    return lines

  def write_vot_data( self, doc, indent=0 ):
    buf  = str(Indent( indent ))
    buf2 = str(Indent( indent+1 ))
    buf3 = str(Indent( indent+2 ))

    lines = []

    if len( doc._body ) == 0:
      return lines

    # Add field elements
    record  = "<!-- Data FIELDs -->"
    lines.append(buf + record + nl)
    for obj in doc._body:
      lines.extend( self.write_vot_field( obj, indent ) )

    # Begin object record DATA
    record = "<DATA>"
    lines.append(buf + record + nl)

    record = buf2 + "<FITS extnum=\""+str(doc._source_ext)+"\">"
    lines.append( record + nl)

    record = buf3 + "<STREAM href=\""+doc._source+"\"/>"
    lines.append( record + nl)

    record = buf2 + "</FITS>"
    lines.append( record + nl)

    # End with object DATA closing tag
    lines.append( buf + "</DATA>"+nl )

    return lines

  def write_vot_element( self, elem, indent=0 ):
    """
      Writes VOTable element lines.
      If VO-DML annotation is on, confine to JUST PARAM and FIELD elements.
    """
    lines = []

    if elem.__class__.__name__ in ( "ObjectType", ):
      lines = self.write_vot_group( elem, elem.isReferenced(), indent )

    elif elem.__class__.__name__ in ( "DataType", ):
      if elem.value == "":
        lines = self.write_vot_group( elem, False, indent ) # Complex DataType
      else:
        lines = self.write_vot_param( elem, indent )        # Value-d DataType (Quantity)

    elif elem.__class__.__name__ in ( "PrimitiveType", "EnumType"):
      lines = self.write_vot_param( elem, indent )

    elif elem.__class__.__name__ in ( "ReferenceType", ):
      lines = self.write_vot_groupref( elem, indent )

    elif elem.__class__.__name__ in ( "FieldType", ):
      lines = self.write_vot_fieldref( elem, indent )

    else:
      raise ValueError("write_vot_element() - unrecognized element type, '{0}'\n".format( elem.__class__.__name__ ) )

    return lines


  def write_vot_field( self, elem, indent=0 ):
    buf = str(Indent( indent ))
    buf2 = str(Indent( indent + 1 ))

    lines = []

    #Resolve datatype to VOTable types
    datatype = self._convert_ivoa_datatype_to_vot( elem.vodml_type )
    if datatype == "UNMATCHED":
      raise ValueError("write_vot_field() - can not map data type '{0}' on element '{1}'\n".format(elem.vodml_type, elem.refid) )

    # Begin datatype record FIELD
    record = "<FIELD"

    # The field name is stored as the element value.. make ID for the reference to it.
    record += " ID=\"" + "_col-" + elem.value + "\""

    # Add name
    record += " name=\"" + elem.value + "\""

    # Add dtype
    if datatype == "char":
      record += " datatype=\"char\""
      record += " arraysize=\"" + str(len(str(elem.value))) + "\""
    elif datatype == "integer":
      record += " datatype=\"int\""
    elif datatype == "long":
      record += " datatype=\"long\""
    elif datatype == "double":
      record += " datatype=\"double\""
    elif datatype == "boolean":
      record += " datatype=\"boolean\""

    # Add ucd
    if elem.ucd != "":
      record += " ucd=\""+elem.ucd+"\""

    # Add unit
    if elem.unit != "":
      record += " unit=\""+elem.unit+"\""

    # Add content.. [DESCRIPTION, VALUES, LINK]
    if elem.description == "":
      # No content.. 
      record += "/>"
      lines.append(buf + record + nl)
    else:
      # Has content.. close
      record += ">"
      lines.append(buf + record + nl)

      # Add Description
      if elem.description != "":
        line = buf2 + "<DESCRIPTION>" + elem.description + "</DESCRIPTION>" + nl
        lines.append( line )

      # End with closing tag
      lines.append( buf + "</FIELD>"+nl )

    return lines

  def write_vot_fieldref( self, elem, indent=0 ):
    buf = str(Indent( indent ))

    lines = []
    record = "<FIELDref"

    # The field name is stored as the element value.. make ID for the reference to it.
    record += " ref=\"" + "_col-" + elem.value + "\""

    record += "/>"

    lines.append(buf + record + nl)

    return lines

  def write_vot_group( self, elem, referenced, indent=0 ):
    """
    """
    buf = str(Indent( indent ))
    buf2 = str(Indent( indent+1 ))

    lines = []

    record = "<GROUP"
      
    if referenced:
      record += " ID=\"" + elem.refid + "\""

    if elem.name != "":
      record += " name=\"" + elem.name + "\""
      
    # Add content.. 
    if elem.description == "" and len(elem._attributes) == 0 and len(elem._compositions) == 0 and len(elem._references) == 0 :
      record += "/>"
      lines.append(buf + record + nl)
    else:
      record += ">"
      lines.append(buf + record + nl)
    
      # Add Description
      if elem.description != "":
        line = buf2 + "<DESCRIPTION>" + elem.description + "</DESCRIPTION>" + nl
        lines.append( line )

      # Add Sub-Elements
      lines.extend( self.write_vot_group_content( elem, indent+1 ) )
    
      # End with object GROUP closing tag
      lines.append( buf + "</GROUP>"+nl )

    return lines

  def write_vot_group_content( self, elem, indent=0 ):
    buf = str(Indent( indent ))
    lines = []

    # Add attribute elements
    for role in elem._attributes:
      for item in elem._attributes[ role ]:
        lines.extend( self.write_vot_element( item, indent ) )

    # Add composed elements
    if hasattr( elem, '_compositions') and len(elem._compositions) > 0:
      for role in elem._compositions:
        for item in elem._compositions[ role ]:
          lines.extend( self.write_vot_element( item, indent ) )

    # Add reference elements
    for role in elem._references:
      for item in elem._references[ role ]:
        lines.extend( self.write_vot_element( item, indent ) )

    return lines


  def write_vot_groupref( self, elem, indent=0 ):
    """
    """
    buf = str(Indent( indent ))
    buf2 = str(Indent( indent+1 ))

    lines = []

    record = "<GROUP"
      
    if elem.name != "":
      record += " name=\"" + elem.name + "\""

    # Add reference to target
    record += " ref=\"" + elem.target + "\""
      
    # Add content.. 
    if elem.description == "" :
      record += "/>"
      lines.append(buf + record + nl)
    else:
      record += ">"
      lines.append(buf + record + nl)
    
      # Add Description
      line = buf2 + "<DESCRIPTION>" + elem.description + "</DESCRIPTION>" + nl
      lines.append( line )

      # End with object GROUP closing tag
      lines.append( buf + "</GROUP>"+nl )

    return lines

  def write_vot_param( self, elem, indent=0 ):
    buf = str(Indent( indent ))
    buf2 = str(Indent( indent+1 ))

    lines = []

    #Resolve datatype to VOTable types
    if elem.__class__.__name__ in ("EnumType"):
      # Enumeration value is always written as string.
      datatype = self._convert_ivoa_datatype_to_vot( "ivoa:string" )
    else:
      datatype = self._convert_ivoa_datatype_to_vot( elem.vodml_type )
    if datatype == "UNMATCHED":
      raise ValueError("write_vot_param() - can not map data type '{0}' on element '{1}'\n".format(elem.vodml_type, elem.refid) )

    # Begin datatype record PARAM
    record = "<PARAM"

    if self._annotation == self.VODML:
      record += " ID=\"" + elem.refid + "\""

    # Add name
    if elem.name != "":
      record += " name=\"" + elem.name + "\""

    # Add dtype
    if datatype == "char":
      record += " datatype=\"char\""
      record += " arraysize=\"" + str(len(str(elem.value))) + "\""
    elif datatype == "integer":
      record += " datatype=\"int\""
    elif datatype == "long":
      record += " datatype=\"long\""
    elif datatype == "double":
      record += " datatype=\"double\""
    elif datatype == "boolean":
      record += " datatype=\"boolean\""

    # Add ucd
    if elem.ucd != "":
      record += " ucd=\""+elem.ucd+"\""

    # Add value
    #if elem.value != "":
    #  if elem.value.startswith('['):
    #    vstr = elem.value.strip('[] ')
    #    size = len(vstr.split())
    #    record += " arraysize=\""+str(len(vstr.split())) + "\""
    #  else:
    #    vstr = elem.value
    if elem.value != "":
      record += " value=\"" + elem.value + "\""

    # Add unit (PrimitiveType-s do not have units)
    if hasattr( elem, 'unit') and elem.unit != "":
      record += " unit=\""+elem.unit+"\""

    # Add content.. [DESCRIPTION, VALUES, LINK]
    if elem.description == "":
      record += "/>"
      lines.append(buf + record + nl)
    else:
      record += ">"
      lines.append(buf + record + nl)

      # Add Description
      line = buf2 + "<DESCRIPTION>" + elem.description + "</DESCRIPTION>" + nl
      lines.append( line )

      # End with PARAM closing tag
      lines.append( buf + "</PARAM>"+nl )

    return lines

  # ================================================================================
  # VODML Annotation
  # ================================================================================
  def write_vodml_annotation( self, doc, indent=0 ):

    buf = str(Indent( indent ))

    lines = []
    lines.append(buf + "<VODML>" + nl)

    # Model declarations
    lines.extend( self.write_vodml_model_annotation( doc, indent+1 ) )
    
    # Global objects (ie: metadata)
    lines.extend( self.write_vodml_metadata_annotation( doc, indent+1 ) )
    
    # Template objects (ie: body)
    #  - the self._body pointer has JUST the FIELD elements, 
    #    for this, we need the full object spec for the containing object (eg NDPoint)
    lines.extend( self.write_vodml_data_annotation( doc, indent+1 ) )

    lines.append(buf + "</VODML>" + nl)

    return lines

  def write_vodml_model_annotation( self, doc, indent=0 ):
    buf  = str(Indent( indent ))
    buf2 = str(Indent( indent+1 ))

    lines = []
    for prefix in doc._models.keys():
      lines.append( buf + "<MODEL>" + nl )
      lines.append( buf2 + "<NAME>" + prefix + "</NAME>" + nl )
      url = doc._models[ prefix ]
      if url == "":
        lines.append( buf2 + "<URL>" + "model does not have URL specified" + "</URL>" + nl )
      else:
        lines.append( buf2 + "<URL>" + url + "</URL>" + nl )
      lines.append( buf + "</MODEL>" + nl )

    return lines

  def write_vodml_metadata_annotation( self, doc, indent=0 ):
    buf  = str(Indent( indent ))

    lines = []
    for role in doc._metadata:
      if role.lower() == "default":
        lines.append( buf + "<GLOBALS>" + nl )
      else:
        lines.append( buf + "<GLOBALS ID=\"" + role + "\">" + nl )

      for obj in doc._metadata[ role ]:
        lines.extend( self.write_vodml_element_annotation( obj, indent+1 ) )

      lines.append( buf + "</GLOBALS>" + nl )

    return lines

  def write_vodml_data_annotation( self, doc, indent=0 ):
    buf  = str(Indent( indent ))

    lines = []

    # Find Data objects
    data = doc.find_data_node()

    if data is not None:
      lines.append( buf + "<TEMPLATES tableref=\"_table1\">" + nl )

      # Write annotation for data objects
      for obj in data:
        lines.extend( self.write_vodml_element_annotation( obj, indent+2, dataflag=True ) )

      lines.append( buf + "</TEMPLATES>" + nl )

    return lines

  def write_vodml_element_annotation( self, elem, indent=0, dataflag=False ):
    buf  = str(Indent( indent ))
    buf2  = str(Indent( indent+1 ))

    lines = []

    if elem.__class__.__name__ in ( "ObjectType" ):

      if elem._datanode is True and dataflag is False:
        # add '3' to VOTable ID (which is unique) to link to EXTINSTANCES 
        #  record += " ID=\"" + elem.tag + "3\""
        record = "<EXTINSTANCES>"+elem.refid+"3"+"</EXTINSTANCES>"
        lines.append(buf + record + nl)

      else:
        record = "<INSTANCE"

        if elem._datanode is True and dataflag is True:
          # add '3' to VOTable ID (which is unique) to link to EXTINSTANCES 
          record += " ID=\"" + elem.refid + "3\""

        elif elem.isReferenced():
          # adding '2' to VOTable ID (which is unique) to generate
          # separate, but still unique ID for the vo-dml annotated instance
          record += " ID=\"" + elem.refid + "2\"" 
      
        if elem.vodml_type != "":
          record += " dmtype=\"" + elem.vodml_type + "\""
        
        tlen = len(elem._attributes) + len(elem._compositions) + len(elem._references)
        if tlen == 0:
          record += "/>"
          lines.append(buf + record + nl)
        else:
          record += ">"
          lines.append(buf + record + nl)
        
          # Add content.. 
          #  Add attribute elements
          if len(elem._attributes) != 0:
            lines.extend( self.write_vodml_attribute_annotation( elem, indent+1, dataflag ) )
        
          # Add composed elements
          if len(elem._compositions) != 0:
            lines.extend( self.write_vodml_composition_annotation( elem, indent+1, dataflag ) )
          
          # Add reference elements
          if len(elem._references) != 0:
            lines.extend( self.write_vodml_reference_annotation( elem, indent+1, dataflag ) )
         
          # End with object INSTANCE closing tag
          lines.append( buf + "</INSTANCE>"+nl )

    elif elem.__class__.__name__ in ( "DataType" ):

      if elem.value != "":
        # Valued DataType (ie: Quantity)
        record =  "<CONSTANT ref=\"" + elem.refid + "\""
        record += " dmtype=\"" + elem.vodml_type + "\""
        record += "/>"

        lines.append(buf + record + nl)

      else:
        # Complex DataType
        record = "<INSTANCE"
        
        if elem.vodml_type != "":
          record += " dmtype=\"" + elem.vodml_type + "\""
        
        record += ">"
        lines.append(buf + record + nl)
      
        # Add content.. 
        #  Add attribute elements
        lines.extend( self.write_vodml_attribute_annotation( elem, indent+1, dataflag ) )
        
        # Add reference elements
        if len(elem._references) != 0:
          lines.extend( self.write_vodml_reference_annotation( elem, indent+1, dataflag ) )

        # End with object INSTANCE closing tag
        lines.append( buf + "</INSTANCE>"+nl )

    elif elem.__class__.__name__ in ( "PrimitiveType", "EnumType" ):
      record =  "<CONSTANT ref=\"" + elem.refid + "\""
      record += " dmtype=\"" + elem.vodml_type + "\""
      record += "/>"

      lines.append(buf + record + nl)

    elif elem.__class__.__name__ in ( "ReferenceType" ):
      # reference to element
      # adding '2' to VOTable ID (which is unique) to generate
      # separate, but still unique ID for the annotated instance.
      lines.append(buf + "<IDREF>" + elem.target + "2" + "</IDREF>" + nl)

    elif elem.__class__.__name__ in ( "FieldType", ):
      # Add COLUMN reference tag
      record = "<COLUMN ref=\"" + "_col-" + elem.value + "\" dmtype=\"" + elem.vodml_type + "\"/>"

      lines.append(buf + record + nl)

    else:
      raise ValueError("write_vodml_element_annotation() - Unrecognized element type, " + elem.__class__.__name__ )

    return lines


  def write_vodml_attribute_annotation( self, elem, indent=0, dataflag=False ):
    buf   = str(Indent( indent ))
    lines = []

    #  Add attribute elements
    for role in elem._attributes:
      lines.append( buf + "<ATTRIBUTE dmrole=\"" + role + "\">" + nl )

      for item in elem._attributes[ role ]:
        lines.extend( self.write_vodml_element_annotation( item, indent+1, dataflag ) )
        
      lines.append( buf + "</ATTRIBUTE>"+nl )

    return lines

  def write_vodml_composition_annotation( self, elem, indent=0, dataflag=False ):
    buf   = str(Indent( indent ))
    lines = []

    #  Add composition elements
    for role in elem._compositions:
      lines.append( buf + "<COMPOSITION dmrole=\"" + role + "\"> " + nl )

      for item in elem._compositions[ role ]:
        lines.extend( self.write_vodml_element_annotation( item, indent+1, dataflag ) )

      lines.append( buf + "</COMPOSITION> " + nl )

    return lines

  def write_vodml_reference_annotation( self, elem, indent=0, dataflag=False ):
    buf   = str(Indent( indent ))
    lines = []

    # Add reference elements
    for role in elem._references:
      lines.append(buf + "<REFERENCE dmrole=\"" + role + "\">" + nl)

      for item in elem._references[ role ]:
        lines.extend( self.write_vodml_element_annotation( item, indent+1, dataflag ) )

      lines.append(buf + "</REFERENCE>" + nl)

    return lines
