class ModelElement:
  """
  Class representing a single VO-DML model element.

  The attributes provide the vo-dml description of that element.
  All attributes are optional: (really?)
    tag           - vo-dml id of the element (without model prefix)
    etype         - element type
                      o package, objectType, dataType, primitiveType, enumeration
                      o attribute, composition, reference, collection, literal 
    dtype         - data type of the element
    extends       - parent class of the element
    multiplicity  - number of allowed instances
    description   - description
    constraint    - any constraint associated with the element (free form)
    semantic      - semantic concept source document

  """

  def __init__(self, tag="", etype="", dtype="", extends="", mult="", desc="", constraint="", semcon="" ):
    self.__clear__()

    if tag != "":
        self.tag = tag
    if etype != "":
        self.etype = etype
    if dtype != "":
        self.dtype = dtype
    if extends != "":
        self.extends = ""
    if mult != "":
        self.multiplicity = mult
    if desc != "":
        self.description = desc
    if constraint != "":
        self.constraint = constraint
    if semcon != "":
        self.semantic = semcon


  def __clear__(self):
    self.tag = ""
    self.etype = ""
    self.dtype = ""
    self.extends = ""
    self.multiplicity = ""
    self.description = ""
    self.constraint = ""
    self.semantic = ""

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    retstr  = "ModelElement:\n"
    retstr += "   Tag:   " + self.tag + "\n"
    retstr += "   EType: " + self.etype + "\n"
    retstr += "   Type:  " + self.dtype + "\n"
    retstr += "   Extend:" + self.extends + "\n"
    retstr += "   Mult:  " + self.multiplicity + "\n"
    retstr += "   Desc:  " + self.description + "\n"
    retstr += "   Constr:" + self.constraint + "\n"
    retstr += "   SemCon:" + self.semantic + "\n"
    retstr += "\n"
    return retstr



class Model:
  """
  Class representing a VO-DML compliant data model.

  The model consists of 3 main components
    o Model description attributes
    o Imported model dictionary
       key = model name
    o Dictionary of ModelElement records
       key = full vo-dml id of element (with model prefix)

  """
  def __init__(self, fname):
    """
    Instantiate a Model instance from source file.
    Supported formats:
      o VO-DML/XML serialization
         - identified by file name suffix (.xml)
      o ASCII table
         - identified by file name suffix (.db)
    """
    self.__clear__()

    if ( fname.strip() == "" ):
      raise IOError( "'fname' argument empty; must provide Model description file. " )

    if ( fname.endswith("xml") ):
      self.__readXML( fname )
    elif ( fname.endswith("db") ):
      self.__readDB( fname )
    else:
      raise( ValueError("Unable to identify Model description file type.") )

  def __clear__(self):
      self.name   = ""
      self.prefix   = ""
      self.description = ""
      self.title    = ""
      self.author   = ""
      self.version  = ""
      self.prever   = ""
      self.lastmod  = ""
      self.url      = ""
      self.imports  = {}
      self._records = {}


  def __str__(self):
    return self.__repr__()

  def __repr__(self):
      retstr  = "# -----------------------------------\n"
      retstr += "# VO Data Model Summary              \n"
      retstr += "# -----------------------------------\n"
      retstr += "Prefix="+self.prefix+"\n"
      retstr += "Description="+self.description+"\n"
      retstr += "URI="+self.url+"\n"
      retstr += "Title="+self.title+"\n"
      retstr += "Author="+self.author+"\n"
      retstr += "Version="+self.version+"\n"
      retstr += "PreviousVersion="+self.prever+"\n"
      retstr += "LastModified="+self.lastmod+"\n"
      for key in sorted( self.imports ):
        retstr += "Import='"+key+":"+self.imports[key]+"'\n"
      retstr += "#\n"
      retstr += "#\n"
      retstr += "# {0:43}& {1:15}& {2:50}& {3:5}& {4:50}\n".format('Tag','Element Type','Type','Mult','Description')
      retstr += "#"+'-'*159+"\n"

      for key in sorted( self._records):
        item = self._records[key]
        retstr += "{0:45}& {1:15}& {2:50}& {3:5}& {4:50}\n".format( item.tag, item.etype, item.dtype, item.multiplicity, item.description )

      return retstr

  def __readDB(self, fname ):
    """
    Load ASCII vo-dml model specification table.

    Content format:
      o Header Segment
        + lines starting with '#' are ignored as comments
        + List of key=value pairs for model description elements
          - Prefix
          - Description
          - URI
          - Title
          - Author
          - Version
          - PreviousVersion
          - LastModified
          - Import
      o Model element table
        + '&' delimited table, of ModelElement records
          Tag, EType, DType, Multiplicity, Description

    Parameters
    ----------
  
      fname: string
                Filename of vo-dml model specification table.

    Returns
    --------
  
      None
  
  
    Raises
    --------
  
    IOError:
               Invalid fname input.
               Error opening file.

    """
    if ( fname.strip() == "" ):
      raise IOError( "'fname' argument value invalid. '{0}'".format(fname) )

    #Open file (read-only); will close() when we leave this block
    with open( fname, 'r') as fp: 
      content = fp.readlines()

    #Loop records
    #  - skip empty records and records starting with '#'
    #  - handle metadata records
    #  - handle data records
    #    o parse on '&'
    #    o strip leading/trailing whitespace 
    #    o instantiate ModelElement
    #    o add to records hash (key=<tag with prefix>)
    for line in content:
      line = line.strip()
      if line == '' or line[0] == '#':
        continue
      elif line.startswith("Name="):
        self.name = line[line.find("=")+1:]
      elif line.startswith("Prefix="):
        self.prefix = line[line.find("=")+1:]
      elif line.startswith("Description="):
        self.description = line[line.find("=")+1:]
      elif line.startswith("Title="):
        self.title = line[line.find("=")+1:]
      elif line.startswith("Author="):
        self.author = line[line.find("=")+1:]
      elif line.startswith("Version="):
        self.version = line[line.find("=")+1:]
      elif line.startswith("PreviousVersion="):
        self.prever = line[line.find("=")+1:]
      elif line.startswith("LastModified="):
        self.lastmod = line[line.find("=")+1:]
      elif line.startswith("URL=") or line.startswith("URI="):
        self.url = line[line.find("=")+1:]
      else:
        parts = line.split('&')
        elem = ModelElement( tag=parts[0].strip(),
                             etype=parts[1].strip(),
                             dtype=parts[2].strip(),
                             mult=parts[3].strip(),
                             desc=parts[4].strip(),
                             )
        key = self.prefix+":"+elem.tag
        self._records[ key ] = elem


  def __readXML(self, fname ):
    """
    Load vo-dml/XML model specification.

    Parameters
    ----------
  
      fname: string
                Filename of vo-dml/XML model specification.
                (May be URL)

    Returns
    --------
  
      None
  
  
    Raises
    --------
  
    IOError:
               Invalid fname input.
               Error opening file.

    """
    if ( fname.strip() == "" ):
      raise IOError( "'fname' argument value invalid. '{0}'".format(fname) )

    import xml.dom.minidom as xml
    import os
    import sys
    if sys.version_info[0] < 3:
      from urllib2 import urlopen
    else:
      from urllib.request import urlopen

    try:
      if fname.startswith("http:") or  fname.startswith("https:") or fname.startswith("file:"):
        fh = urlopen( fname )
        dom = xml.parse( fh )
      else:
        dom = xml.parse( fname )
    except Exception:
      raise( IOError("Problem opening Model description file '"+fname+"'.") )

    try:
      top = dom.firstChild
      for child in top.childNodes:
        if child.nodeName == "name":
          self.name = self.__getXMLText( child.childNodes )
          self.prefix = self.__getXMLText( child.childNodes )
        elif child.nodeName == "description":
          self.description = "'"+self.__getXMLText( child.childNodes ).replace( os.linesep, ' ')+"'"
        elif child.nodeName == "title":
          self.title = "'"+self.__getXMLText( child.childNodes )+"'"
        elif child.nodeName == "author":
          self.author = "'"+self.__getXMLText( child.childNodes )+"'"
        elif child.nodeName == "version":
          self.version = self.__getXMLText( child.childNodes )
        elif child.nodeName == "previousVersion":
          self.prever = self.__getXMLText( child.childNodes )
        elif child.nodeName == "lastModified":
          self.lastmod = self.__getXMLText( child.childNodes )
        elif child.nodeName == "uri":
          self.url = self.__getXMLText( child.childNodes )
        elif child.nodeName == "import":
          key = child.getElementsByTagName("name")[0].childNodes[0].data
          url = child.getElementsByTagName("url")[0].childNodes[0].data
          self.imports[ key ] = url
        elif child.nodeName == "package":
          self.__processXMLElement( child )
        elif child.nodeName == "primitiveType":
          self.__processXMLElement( child )
        elif child.nodeName == "dataType":
          self.__processXMLElement( child )
        elif child.nodeName == "objectType":
          self.__processXMLElement( child )
        elif child.nodeName == "enumeration":
          self.__processXMLElement( child )
        else:
          if child.nodeType != child.TEXT_NODE:
            print("skipping node: "+child.nodeName )
    except Exception:
      raise( IOError("Problem interpreting Model description file '"+fname+"'.") )


  def __getXMLText(self, nodelist ):
    """
    """
    rc = []
    for node in nodelist:
      if node.nodeType == node.TEXT_NODE:
        rc.append(node.data)
    return ''.join(rc).strip()

  def __processXMLElement(self, node ):
    """
    """
    import os
    children = []

    elementtype = node.nodeName

    multiplicity = ""
    ext = ""
    constr = ""
    semanticconcept = ""
    for child in node.childNodes:
      try:
        # Collect node element definition set
        if child.nodeName == "vodml-id":
          vodmlid = self.__getXMLText( child.childNodes )
        elif child.nodeName == "name":
          datatype = self.__getXMLText( child.childNodes )
        elif child.nodeName == "description":
          description = self.__getXMLText( child.childNodes ).replace( os.linesep, ' ')
        elif child.nodeName == "extends":
          ext = self.__getXMLText( child.childNodes )
        elif child.nodeName == "datatype":
          datatype = child.getElementsByTagName("vodml-ref")[0].childNodes[0].data
        elif child.nodeName == "constraint":
          constr = self.__getXMLText( child.childNodes )
        elif child.nodeName == "semanticconcept":
          semanticconcept = self.__getXMLText( child.childNodes )
        elif child.nodeName == "multiplicity":
          tmin = child.getElementsByTagName("minOccurs")[0].childNodes[0].data
          tmax = child.getElementsByTagName("maxOccurs")[0].childNodes[0].data
          if tmin == tmax:
            multiplicity = tmin
          elif tmax == "-1":
            multiplicity = tmin+"..*"
          else:
            multiplicity = tmin+".."+tmax
        elif child.nodeName == "isOrdered":
          pass
        else:
          # child is a complex object.. add to list for further processing
          children.append( child )
      except Exception:
        raise( ValueError("Problem interpreting Model element '"+node.nodeName+"' item '"+child.nodeName+"'.") )

    if elementtype == "literal" or elementtype == "package":
      datatype = ""

    # Create ModelElement for this node.
    elem = ModelElement( tag=vodmlid,
                         etype=elementtype,
                         dtype=datatype,
                         extends=ext,
                         mult=multiplicity,
                         desc=description,
                         constraint=constr,
                         semcon=semanticconcept,
                         )

    # Add to Model records list
    key = self.prefix+":"+elem.tag
    self._records[ key ] = elem

    # process child elements
    for child in children:
      if child.nodeType != child.TEXT_NODE:
        self.__processXMLElement( child )


  def get( self, tag ):
    """
    Return the ModelElement record associated with the provided vodml-id
  
    Parameters
    ----------
  
      tag: string
                VODML-ID of desired model element.

  
    Returns
    --------
  
      element: ModelElement
                Model element record.
  
  
    Raises
    --------
  
      None
    """

    try:
      result = self._records[tag]
    except KeyError as ke: # no matching tag
      raise ValueError("Input tag not found in Model '{0}'".format(tag) )

    return result


  def write( self, ofile ):
    """
    """
    # Open output file
    try:
      fp = open( ofile, "w" )
    except Exception as ex:
      if fp is not None:
        fp.close()
        fp = None
        raise ex

    fp.writelines( str(self) )
