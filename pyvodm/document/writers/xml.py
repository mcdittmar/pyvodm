
class XMLWriter:

  def __init__(self, ofile ):
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


  def __del__(self):
    if self._fp is not None:
      self._fp.close()

  def __clear__(self):
    self._xmldoc = None
    self._fp = None

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    retstr  = "Not yet implemented.\n"
    return retstr


  def _interpret_Document( self, doc ):
    """
    Translate Document instance in to model object DOM
    """
    import xml.dom.minidom as md

    # Create output DOM
    result = md.Document()

    # Handle namespace..
    #   - not using actual URL so that the namespace string 
    #     is always the same (the actual string does not matter)
    #
    # Determine top level namespace ( kind-of a hack )
    nsbase = "http://ivoa.net/xml"
    nsivoa = "http://ivoa.net/dm/models/vo-dml/xsd"
    topns  = ""
    if "ds" in doc._models.keys():
        topns = "ds"
    elif "meas" in doc._models.keys():
        topns = "meas"
    elif "trans" in doc._models.keys():
        topns = "trans"
    elif "coords" in doc._models.keys():
        topns = "coords"
    elif "ivoa" in doc._models.keys():
        topns = "ivoa"
    nsurl = "{0}/{1}".format( nsivoa, topns )

    # Create root element
    root = result.createElementNS( nsurl, topns+":EXAMPLE")

    # Set contained namespaces
    root.setAttributeNS("xmls", "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance" )
    #nsbase = "http://ivoa.net/xml"
    for key in sorted ( doc._models.keys() ):
        nstag = "xmlns:{0}".format( key )
        if key == "ivoa":
          nsurl = "{0}/{1}".format( nsivoa, key )
        else:
          nsurl = "{0}/{1}".format( nsbase, key )
        root.setAttributeNS("xmls", nstag, nsurl )

        if ( key == topns ):
            root.setAttribute( nstag, nsurl )

    # Add root element to DOM
    result.appendChild(root)

    # Store XML document, for easy access
    self._xmldoc = result

    # Process metadata elements
    for role in doc._metadata:
      for obj in doc._metadata[ role ]:
          item = self._interpret_element( obj )
          root.appendChild( item )

    return result

  def _interpret_element( self, elem ):
    """
    Translate Document ElementType instance in to model object DOM element
    """
    node = None

    if elem.__class__.__name__ in ( "ObjectType" ):
      node = self._interpret_complex_type( elem, elem.isReferenced()  )

    elif elem.__class__.__name__ in ( "DataType", ):
      if elem.value == "":
        node = self._interpret_complex_type( elem, False ) # Complex DataType
      else:
        node = self._interpret_simple_type( elem )        # Value-d DataType (Quantity)
   
    elif elem.__class__.__name__ in ( "PrimitiveType", "EnumType"):
      node = self._interpret_simple_type( elem )
   
    elif elem.__class__.__name__ in ( "ReferenceType", ):
      node = self._interpret_ref_type( elem )

    return node


  def _interpret_complex_type( self, elem, referenced ):
    """
    Translate Document ObjectType or DataType, which has sub-content 
    """
    top = self._xmldoc

    #if ( '.' not in elem.vodml_role ):
    if ( elem.vodml_type == elem.vodml_role ):
        # Primary object
        node = top.createElement( elem.vodml_type )
    else:
        # Secondary object
        [vtype, vrole] = elem.vodml_role.rsplit('.', 1)

        node = top.createElement( vrole )
        node.setAttribute( 'xsi:type', elem.vodml_type  )

    if referenced:
      node.setAttribute( 'ID', elem.refid )

    # Element name - nope
    # node.setAttribute( 'name', elem.name )
    
    # Schema expects specific order of content.
    
    # Add reference elements
    for role in elem._references:
      for item in elem._references[ role ]:
        child = self._interpret_element( item )
        node.appendChild( child )
    
    # Add composed elements
    if hasattr( elem, '_compositions') and len(elem._compositions) > 0:
      for role in elem._compositions:
        for item in elem._compositions[ role ]:
          child = self._interpret_element( item )
          node.appendChild( child )
    
    # Add attribute elements
    for role in elem._attributes:
      for item in elem._attributes[ role ]:
        child = self._interpret_element( item )
        node.appendChild( child )
   
    return node


  def _interpret_simple_type( self, elem ):
    """
    Translate Document Primitive, Enum types
    """
    top = self._xmldoc

    [vtype, vrole] = elem.vodml_role.rsplit('.', 1)
    node = top.createElement( vrole )

    val = elem.value
    if elem.value == "+Inf":
      val = "INF"
    elif elem.value == "-Inf":
      val = "-INF"

    if "Quantity" in elem.vodml_type:
        node.setAttribute( 'xsi:type', elem.vodml_type  )
        if elem.unit is not None and elem.unit != "":
            subnode = top.createElement( "unit" )
            tnode = top.createTextNode( elem.unit )
            subnode.appendChild( tnode )
            node.appendChild( subnode )
        subnode = top.createElement( "value" )
        tnode = top.createTextNode( val )
        subnode.appendChild( tnode )
        node.appendChild( subnode )
    else:
        if "boolean" in elem.vodml_type:
          val = elem.value.lower()

        if elem.__class__.__name__ in ("EnumType"):
          if "." in elem.value:
            [enumtype, enumval] = elem.value.rsplit('.', 1)

            val = enumval

        tnode = top.createTextNode( val )
        node.appendChild( tnode )
 
    return node


  def _interpret_ref_type( self, elem ):
    """
    Translate Document Reference types
    """
    top = self._xmldoc

    [vtype, vrole] = elem.vodml_role.rsplit('.', 1)

    node = top.createElement( vrole )
    node.setAttribute( 'IDREF', elem.target  )

    return node

  def write( self, doc ):
    """
    Write Document instance.
    
    Parameters
    ----------
    
      doc     : Document
                Document class containing an IVOA Model instance to be 
                interpreted and written in XML format.
    
    Returns
    --------
      none


    Raises
    --------
      TypeError : for invalid argument types
        "'<arg>' argument must be <type> type"


    """
    if doc.__class__.__name__ not in ( "Document", ):
      raise TypeError("'doc' argument must be Document type, not {0}".format( obj.__class__.__name__ ) )

    xml = self._interpret_Document( doc )

    xml_str = xml.toprettyxml(indent="  ", encoding="UTF-8" )
    self._fp.write( xml_str.decode() )

