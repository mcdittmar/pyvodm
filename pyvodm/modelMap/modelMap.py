from collections import OrderedDict

class ModelMapElement:
  """
  Class representing a single Instance Template (ModelMap) record.

  All attributes are optional, with default="": (really?)
    uid           - Unique ID for the element
    name          - Instance or Instance element name.
                    Elements of the same Object must share the same Base name.
                    (e.g.  ICRSFrame, ICRSFrame.refFrame, ICRSFrame.refPosition)
                    NOTE: in VOTable serializations, this will form the Groups
                    and names of the VOTable elements.
    role          - vo-dml ID of the element
    etype         - Extended type, the actual type of the element (e.g. subclass);
                     default = as specified in model
                     required for abstract model elements
    ucd           - user specified ucd associated with the element (VOTable)
    unit          - user specified units associated with the element (when applicable)
    description   - description
    value         - identifies source of element value. see value property for details

  """

  def __init__(self, uid="", name="", role="", etype="", ucd="", unit="", desc="", value="" ):
    self.__clear__()

    if uid != "":
        self.uid = uid
    if name != "":
        self.name = name
    if role != "":
        self.role = role
    if etype != "":
        self.etype = etype
    if ucd != "":
        self.ucd = ucd
    if unit != "":
        self.unit = unit
    if desc != "":
        self.description = desc
    if value != "":
        self.value = value

  @property
  def value(self):
    """
    value property: string
      Uses a "<code>:<item>" format to identify the content
        o <empty>       - Instance or complex object itself has no direct 'value' source it is comprised of the child elements.
        o lit:<value>   - use provided value
        o key:<keyname> - pull value from specified keyword of file
        o field:<column>- associate value with specified table column
        o inline:<id>   - Object/Instance is defined in template at <id>, serialize inline
        o ref:<id>      - Object/Instance is defined in template at <id>, serialize as reference to
    """
    return self._value

  @value.setter
  def value(self, value):
    # valid codes for value source
    codes = ('lit:', 'key:','field:','inline:','ref:')

    # Deprecate?
    alt_codes = ('add:',  # same as inline?
                )

    tmpstr = str(value).strip()
    if ( ( tmpstr == "" ) or tmpstr.startswith( codes ) or tmpstr.startswith( alt_codes ) ):
      self._value = tmpstr
    else:
      raise TypeError( "'value' argument value invalid. '{0}'".format(tmpstr) )


  def __clear__(self):
    self.uid = ""
    self.name = ""
    self.role = ""
    self.etype = ""
    self.ucd = ""
    self.unit = ""
    self.description = ""
    self.value = ""

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    retstr  = "ModelMapElement: "+ self.uid + "\n"
    retstr += "   ModelPath:    "+ self.name + "\n"
    retstr += "   Role:         "+ self.role + "\n"
    if self.etype == "":
      retstr += "   Type:         "+ "<default>\n"
    else:
      retstr += "   Type:         "+ self.etype + "\n"
    retstr += "   UCD:          "+ self.ucd + "\n"
    retstr += "   Unit:         "+ self.unit + "\n"
    retstr += "   Description:  "+ self.description + "\n"
    retstr += "   Value:        "+ self.value + "\n"
    retstr += "\n"
    return retstr


class ModelMapIter(object):
  """
    Iterator through ModelMap records
  """
  def __init__(self, source ):
    self.__clear__()

    if source.__class__.__name__ not in ( "ModelMap", ):
      raise TypeError("'source' argument must be ModelMap instance, not "+source.__class__.__name__ )

    self.map  = source
    self.keys = source._get_uids()


  def __clear__( self ):
    self.map  = None
    self.keys = None
    self.current  = -1

  def __iter__(self):
    return self

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
      retstr  = "MapIterator"
      return retstr

  def __next__(self):
    self.current += 1
    ii = 0
    if self.current < len(self.keys):
      for item in self.keys:
        if ii == self.current:
          retval = self.map.find( uid=item )
          return retval
        ii += 1
    else:
      raise StopIteration

  def next(self):
    return self.__next__()

  def rewind(self):
    self.current = -1



class ModelMap:
  """
  Class representing VO-DML model instance template (ie: model map).

  Currently, this is a uni-directional interface, loading a model map file and
  providing access to the content.

  """

  def __init__(self, fname):
    """
    Instantiate a ModelMap instance from source file.

    Parameter
    ---------
      fname:  string
              Reads specified file and interprets each non-comment line as a ModelMapElement.

    Supported formats:
    -----------------
      o ASCII table
        + Lines starting with '#' are considered comments, and ignored
        + Each entry is '&' delimited table of ModelMapElement records
           - uid
           - name
           - role
           - etype
           - ucd
           - unit
           - description
           - value 
          See ModelMapElement for description of each field.

    Raises
    --------
    IOError:   Invalid fname input.
               Error opening file.
    """

    self.__clear__()

    self.__readDB( fname )

  def __clear__(self):
      self._records = OrderedDict()


  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    """
    Structured string representation of ModelMap content.
    """
    retstr  = "#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    retstr += "# STRUCTURE\n"
    retstr += "# {0:19}& {1:64}& {2:49}& {3:46}& {4:46}& {5:21}& {6:61}& {7:26}\n".format('ID','Instance/Element Name', 'Role (VODML-ID)', 'Extended Type','UCD', 'Unit', 'Description', 'Value')
    retstr += "#"+'-'*322+"\n"

    for key in (self._records.keys()):
      item = self._records[key]
      if item.role.startswith("vodml:"):
        retstr += " {0:20}& {1:64}& {2:49}& {3:46}& {4:46}& {5:21}& {6:61}& {7:26}\n".format( item.uid, item.name, item.role, item.etype, item.ucd, item.unit, item.description, item.value )

    retstr += "#\n"
    retstr += "#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    retstr += "# INSTANCES\n"
    retstr += "# {0:19}& {1:64}& {2:49}& {3:46}& {4:46}& {5:21}& {6:61}& {7:26}\n".format('ID','Instance/Element Name', 'Role (VODML-ID)', 'Extended Type','UCD', 'Unit', 'Description', 'Value')
    retstr += "#"+'-'*322+"\n"

    for key in (self._records.keys()):
      item = self._records[key]
      if not item.role.startswith("vodml:"):
        retstr += " {0:20}& {1:64}& {2:49}& {3:46}& {4:46}& {5:21}& {6:61}& {7:26}\n".format( item.uid, item.name, item.role, item.etype, item.ucd, item.unit, item.description, item.value )

    return retstr

  # Private: Add ModelMapElement record to the Map
  def __add_record( self, elem ):
    self._records[elem.uid] = elem

  # Private: Return List of Map element uids.
  def _get_uids( self ):
    return self._records.keys()


  # Private: Load model map from file.
  def __readDB(self, fname ):

    if ( fname.strip() == "" ):
      raise IOError( "'fname' argument value invalid. '{0}'".format(fname) )

    #Open file (read-only); will close() when we leave this block
    try:
      with open( fname, 'r') as fp: 
        content = fp.readlines()
    except Exception as ex:
      emsg = str(ex)
      emsg = emsg.replace('[Errno 2] ','')
      raise IOError( emsg )

    #Loop records
    #  - skip empty records and records starting with '#'
    #  - handle data records
    #    o parse on '&'
    #    o strip leading/trailing whitespace 
    #    o instantiate ModelMapElement
    #    o add to records hash (key=uid, with prefix?)
    for line in content:
      if line[0] == '#' or line.strip() == '':
        continue
      else:
          parts = line.split('&')
          elem = ModelMapElement( uid=parts[0].strip(),
                                  name=parts[1].strip(),
                                  role=parts[2].strip(),
                                  etype=parts[3].strip(),
                                  ucd=parts[4].strip(),
                                  unit=parts[5].strip(),
                                  desc=parts[6].strip(),
                                  value=parts[7].strip(),
                                )
          self.__add_record( elem )


  def find( self, uid=None, name=None ):
    """
    Scans the ModelMap for a record matching the input tag and returns it.
    User supplies EITHER uid or name of record to match.  Since both should
    be unique within the context of a template, providing both is not 
    necessary.

    Parameters
    ----------
  
      uid: string
                ID of desired model element.

      name: string
                Instance name of desired model element. (case sensitive)

  
    Returns
    --------
  
      element: ModelMapElement
                ModelMap record.
  
  
    Raises
    --------
  
      TypeError:   Invalid usage
      ValueError:  No matching record found

    """
    result = None
    found = False
    emsg = "Matching record not found in ModelMap"

    if ( uid is not None and name is None ):
      try:
        result = self._records[uid]
      except KeyError as ke: # no matching ID
        emsg += ", uid='{0}'.".format(uid)
        raise ValueError( emsg )

    elif ( name is not None and uid is None ):
      for uid in self._records.keys():
        rec = self._records[uid]
        if rec.name == name:
          result = rec
          found = True
          break
      if not found:
        emsg += ", name='{0}'.".format(name)
        raise ValueError( emsg )

    else:
      raise TypeError("Invalid usage; must specify uid or name")

    return result


  def find_children( self, uid ):
    """
    Finds the direct children of specified element from this ModelMap.
    NOTE: This should handle multiple occurances of Objects in the Map..
          returning only the children of the specified instance.
  
    Parameters
    ----------
  
      uid: string
                ID of parent model element.

    Returns
    --------
  
      results: OrderedDict
                Dictionary of ModelMapElement records for each child element.
  
    Raises
    --------
  
      ValueError:  Input uid not found in ModelMap
    """
    result = OrderedDict()

    parent = None
    pattern = ""

    for k in self._records.keys():
      if k == uid:
        parent = self._records[k]
        pattern = parent.name+"."
        continue

      if parent is not None:
        record = self._records[k]

        # check if we are in same Instance (match against parent name)
        if record.name.startswith( pattern ):
            result[k] = record
        else:
          break

    if parent is None:
      raise ValueError("Input ID not found in ModelMap, uid='{0}'.".format(uid) )

    return result


  def iter( self ):
    """
    Return ModelMapIter iterator.
    """
    return ModelMapIter( self )


