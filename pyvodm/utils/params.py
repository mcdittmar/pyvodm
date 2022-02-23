import os

from collections import OrderedDict

"""
  Parameter interface handling.
"""

# ================================================================================
def fix_bool_param( pars, pname ):
  """
  Evaluates the specified parameter as a boolean, reassign value to result.
     True if parameter value == 1; otherwise False.

  Parameters
  ----------

    pars : dictionary
           python dictionary of the parameter key-value pairs 

    pname : string
           parameter name (key) to check.

  Returns
  --------
   none


  Raises
  --------
   none

  """
  try:
    fnam = pars[ pname ]
  except KeyError:
    raise TypeError("Parameter '"+pname+"' not found in list.")

  bval = ( pars[pname] == 1 )
  pars[pname] = bval


# ================================================================================
def validate_dir_param( pars, pname ):
  """
  Checks that the specified parameter is a valid directory path.
    o not empty
    o path exists and is a directory
    o location is writeable

  Also enforces that the value ends with '/'

  Parameters
  ----------

    pars : dictionary
           python dictionary of the parameter key-value pairs 

    pname : string
           parameter name (key) to check.

  Returns
  --------
 
   none


  Raises
  --------

  TypeError  : 
               invalid function argument error 

  IOError    :
               missing parameter

  ValueError :
               parameter values error; empty, nonexistent, not directory

  """
  try:
    fnam = pars[ pname ]
  except KeyError:
    raise TypeError("Parameter '"+pname+"' not found in list.")

  # check empty string
  if fnam == "" :
    raise ValueError("'"+pname+"' parameter is empty.")

  # do checks:
  if not os.path.exists( fnam ):
    raise ValueError("'"+pname+"' location does not exist, \"{0}\".".format(fnam))
  else:
    if not os.path.isdir( fnam ):
      raise ValueError("'"+pname+"' exists, but is not a directory, \"{0}\".".format(fnam) )
    elif not os.access(fnam, os.W_OK ):
      raise ValueError("'"+pname+"' location is not writeable, \"{0}\".".format(fnam) )

  # ensure outdir path ends with '/' so tool does not have to check
  if not fnam.endswith('/'):
    fnam = fnam + '/'
    pars[ pname ] = fnam


# ================================================================================
def validate_file_param( pars, pname ):
  """
  Checks that the specified parameter value has a valid 'file' format, and 
  that the specified file(s) exist.

  Valid formats are:
   o filename:
      * path to file on disk 
        eg: '/data/sample/myfile.fits'
      * URL ("http:", "https:", "file:")

   o stack:
      * '@' + path to list file on disk
        eg: '@/data/sample/inputs.lis'
     
   o comma delimited list of files

  Parameters
  ----------

    pars : dictionary
           python dictionary of the parameter key-value pairs 

    pname : string
           parameter name (key) to check.

  Returns
  --------
   none


  Raises
  --------

  TypeError  : 
               invalid function argument error 

  IOError    :
               missing parameter

  ValueError :
               parameter values error,  nonexistent, or empty, or wrong datatype 

  """

  try:
    fnam = pars[ pname ]
  except KeyError:
    raise TypeError("Parameter '"+pname+"' not found in list.")
  
  # check empty string
  if fnam.strip() == "":
    raise ValueError("'"+pname+"' parameter is empty.")
    
  # check for stack (starts with '@')
  if fnam[0] == '@':
    item = fnam[1:]           # remove '@' 
    if os.path.isfile(item) == False:
      raise ValueError("'"+pname+"' stack file does not exist, \"{0}\".".format(item))

  # check input file existance
  #   this may be overdoing it.
  if fnam.startswith("http:") or fnam.startswith("https:") or fnam.startswith("file:"):
    import sys
    if sys.version_info[0] < 3:
      from urllib2 import urlopen
    else:
      from urllib.request import urlopen

    try:
      fh = urlopen( item )
    except Exception as ex:
      raise ValueError("'"+pname+"' file does not exist, \"{0}\".".format(item))
  else:
    ifiles = stk_build( fnam )
    for item in ifiles:
      if os.path.isfile(item) == False:
        raise ValueError("'"+pname+"' file does not exist, \"{0}\".".format(item))



# ================================================================================
def get_params( tool, argv=None ):
  """
  Generic method to load tool parameters to a dictionary.

  Parameters
  ----------

    tool : string
           a tool name, associated with a parameter file 
    argv : array_like
           command line arguments, if any

  Returns
  --------
 
   pars : dictionary
          dictionary of the parameter key-value pairs 


  Raises
  --------

  TypeError  : 
               invalid function argument error 

  """

  # check tool argument.
  if type(tool) not in ( str, ):
    raise TypeError("The input tool-name is not string type.")
  elif tool.strip() == "":
    err = "Invalid (empty) tool name."
    raise TypeError(err)

  try:
    # Get parameter set with defaults
    pars = _init_params( tool )
    
    # override command line arguements
    set_params( pars, argv )

  except Exception as e:  # catch any exception
    raise(e)

  return pars


# ================================================================================
def set_params( pars, argv=None ):
  """
  Update parameters from argument list.

  Parameters
  ----------

    pars : Ordered dictionary
           parameter list
    argv : array_like
           command line arguments, if any

  Returns
  --------
 
    none

  Raises
  --------

  TypeError  : 
               invalid function argument error 

  """

  try:

    # override command line arguements
    if argv is not None and len(argv) > 1:
      for item in argv[1:]:
        name = None
        
        if '=' in item:
          (name, value) = item.split( '=', 2 )
        else:
          if item.endswith('+'):
            # boolean argument set to true
            name = item[:-1]
            value = True
          elif item.endswith('-'):
            # boolean argument set to false
            name = item[:-1]
            value = False

        if name in pars:
          if name == "verbose":
            pars[name] = int( value )
          else:
            pars[name] = value;
        else:
          raise ValueError("Parameter '{}' not found in list.".format( name ) )


  except Exception as e:  # catch any exception
    raise(e)

  return pars


# ================================================================================
def print_params( pars ):
   """
   Print tool parameters to STDOUT.
   
   Parameters
   ----------
   
   pars : dictionary
       python dictionary of the parameter key-value pairs 
   
   
   Returns
   --------
     none
   
   """
   try:
     keys = pars.keys()
   except AttributeError:
    raise TypeError("'pars' argument must be dictionary type, not "+pars.__class__.__name__ )
     

   print("\nTool Parameters")
   for item in keys:
     print("  %-20s %-s" % ( item+':', pars[item]))
   print("")


# ================================================================================
def _init_params( toolname ):
  """
  Initialize dictionary with tool parameter set.

   Parameters
   ----------
   toolname : string
       tool name whose parameters to initialize
   
   
   Returns
   --------

   params : dictionary
       python dictionary of the parameter key-value pairs 
   

  Raises
  --------
  ValueError  : 
               unrecognized tool

  """
  
  # parameter dictionary 
  params = OrderedDict()

  if ( toolname == "test" ):
    params['infile'] = "<TESTIN>/test_stack.lis"     # File or Stack parameter
    params['outdir'] = "<TESTOUT>"                   # Directory parameter
    params['keyname'] = "SAMPLE"                     # String parameter
    params['format'] = "vot"                         # String parameter with options list
    params['thresh'] = 0.25                          # float parameter
    params['clobber'] = True                         # boolean parameter
    params['verbose'] = 1                            # integer parameter
    params['mode'] = 'h'                             # 
  else:
    raise ValueError("No parameter support for tool '{}'".format(toolname) )

  return params


# ================================================================================
def stk_build( stkname ):
  """
  Interpret stack, returns file list

   Parameters
   ----------
   stkname : string
       stack/file name to process
   
   
   Returns
   --------

   stack : list
       List of files in stack
   

  Raises
  --------

  """
  stack = []

  if stkname[0] == '@':
    #stack file
    try:
      with open( stkname[1:], 'r') as fp: 
        content = fp.readlines()
    except Exception as ex:
      emsg = str(ex)
      emsg = emsg.replace('[Errno 2] ','')
      raise IOError( emsg )

    # prepend path to entries and add to stack
    dirname = os.path.abspath( os.path.dirname( stkname[1:] ) )
    for entry in content:
      entry = entry.strip()
      if not entry.startswith('/'):
        filename = "{}/{}".format( dirname, entry )
      else:
        filename = entry
        
      stack.append( filename )

  elif "," in stkname:
    # comma delimited set of files
    stack.extend( stkname.split(",") )
    
  else:
    # stack is a single file.
    stack.append( stkname )

  return stack
