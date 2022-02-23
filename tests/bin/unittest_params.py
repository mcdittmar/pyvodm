import unittest
from pyvodm.utils.params import *
import os, sys, stat, time
#from shutil import copyfile

class TestToolParams(unittest.TestCase):
  """Test params utility functions """

  TEST_BASE_DIR = os.path.join( os.path.dirname(__file__), '../' )

  TESTIN  = ''.join( (TEST_BASE_DIR, "data/") )
  TESTOUT = ''.join( (TEST_BASE_DIR, "out/") )
  TESTSAV = ''.join( (TEST_BASE_DIR, "base/") )
  TESTRES = ''.join( (TEST_BASE_DIR, "res/") )

  instack = "test_stack.lis"

  def setUp(self):
    """ Set parameters prior to each test"""

    if not os.path.exists( self.TESTOUT ):
      os.mkdir( self.TESTOUT )


  def test01(self):
    """ get_params() - parameter file name is None type """

    try:
      # input NoneType name
      params = get_params(None)

    except TypeError as te:  # catch the error
        if str(te).find("input tool-name is not string type.") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test02(self):
    """ get_params() - tool name is empty """

    try:
        # input empty name
        params = get_params("")

    except TypeError as te: # catch the error
        if str(te).find("Invalid (empty) tool name.") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test03(self):
    """ get_params() - no parameter support for tool """

    try:
        # input Non-existent tool
        params = get_params("anytool")

    except ValueError as ve: # catch the error
        if str(ve).find("No parameter support for tool") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  
  def test04(self):
    """ validate_file_param() - Invalid key sent to validate routine """

    try:
      params = get_params( "test" )

      validate_file_param( params, "bobo" )

    except TypeError as ve:   # catch the error
      if str(ve).find("Parameter 'bobo' not found in list.") == -1:
        print(ve)
        raise Exception("Error: expected TypeError not thrown")
      pass
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test05(self):
    """ validate_file_param() - file is non-existent """

    badpath  = "/path/does/not/exist/data.fits"
    try:
      params = get_params( "test" )
      params['infile'] = badpath

      validate_file_param( params, "infile" )

    except ValueError as ve: # catch the error
        if str(ve).find("'infile' file does not exist") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test06(self):
    """ validate_file_param() - file is whitespace """

    try:
      params = get_params( "test" )
      params['infile'] = "  "
      
      validate_file_param( params, "infile" )

    except ValueError as ve:  # catch the error
      if str(ve).find("'infile' parameter is empty.") == -1:
        print(ve)
        raise Exception("Error: expected ValueError not thrown")
      pass
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test07(self):
    """ validate_file_param() - file is valid file """

    goodfile = self.TESTIN + "test_sample.fits"
    expected = goodfile

    try:
      params = get_params( "test" )
      params['infile'] = goodfile

      validate_file_param( params, "infile" )
      result = params["infile"]

    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result, expected )


  def test08(self):
    """ validate_file_param() - file is valid comma delimited list """

    goodfile = self.TESTIN + "test_sample.fits" + "," + self.TESTIN + "test_sample.dtf"
    expected = goodfile

    try:
      params = get_params( "test" )
      params['infile'] =  goodfile

      validate_file_param( params, "infile" )
      result = params["infile"]

    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result, expected )


  def test09(self):
    """ validate_file_param() - file is valid stack """

    goodstack = ''.join(( "@", self.TESTIN, self.instack ))
    expected = goodstack
    try:
      params = get_params( "test" )
      params['infile'] = goodstack

      validate_file_param( params, "infile" )
      result = params["infile"]

    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result, expected )


  def test12(self):
    """ validate_dir_param() - location does not exist """

    try:
      params = get_params( 'test' )
      params['outdir'] = "/anydir"

      validate_dir_param( params, "outdir" )

    except ValueError as ve: #  catch the error
      if str(ve).find("'outdir' location does not exist") == -1:
        print(ve)
        raise Exception("Error: expected ValueError not thrown")
      pass
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test13(self):
    """ validate_dir_param() - location is a file not a directory """

    afile =  ''.join(( self.TESTIN, self.instack))
    try:
      params = get_params( 'test' )
      params['outdir'] = afile

      validate_dir_param( params, "outdir" )

    except ValueError as ve: #  catch the error
      if str(ve).find("'outdir' exists, but is not a directory") == -1:
        print(ve)
        raise Exception("Error: expected ValueError not thrown")
      pass
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test14(self):
    """ validate_dir_param() - location is non-writeable """

    try:
      # create an un-writeable dir
      tmpdir  = ''.join(( self.TESTOUT, "/mydir", str(time.time())))
      # assign the dir read-only
      os.mkdir(tmpdir, stat.S_IREAD)

      params = get_params( 'test' )
      params['outdir'] = tmpdir

      validate_dir_param( params, "outdir" )

    except ValueError as ve:   # catch the error
      if str(ve).find("'outdir' location is not writeable") == -1:
        print(ve)
        raise Exception("Error: expected ValueError not thrown")
      pass
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")
    finally:
      #clean the temp-dir
      os.rmdir(tmpdir)


  def test15(self):
    """ validate_dir_param() - location is valid writeable directory  """

    outdir = self.TESTOUT
    expected = outdir
    try:
      params = get_params( 'test' )
      params['outdir'] = outdir

      validate_dir_param( params, "outdir" )
      result = params["outdir"]

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result, expected )


  def test200(self):
    """ basic functionality: print parameters
        The print method writes to stdout, capture this and compare.
    """
    valstr = "\nTool Parameters\n  infile:              <TESTIN>/test_stack.lis\n  outdir:              <TESTOUT>\n  keyname:             SAMPLE\n  format:              vot\n  thresh:              0.25\n  clobber:             True\n  verbose:             1\n  mode:                h\n\n"

    from io import StringIO

    backup = sys.stdout
    sys.stdout = StringIO() # capture output
    try:
      params = get_params( 'test' )
      print_params(params)
      out = sys.stdout.getvalue() # store output
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")
    finally:
      sys.stdout.close()  # close the stream
      sys.stdout = backup # restore the original stdout

    # apply substitutions
    a = out.replace( self.TESTIN, "<TESTIN>/")
    b = a.replace( self.TESTOUT, "<TESTOUT>")
    out = b.replace( self.TESTRES, "<TESTRES>/")

    if not out == valstr:
      print("Captured output")
      for item in out.split("\n"):
        print("Line: XX" + item + "XX")
      raise Exception("results do not match.")


  def test201(self):
    """ print_params() - bad input (None)
    """
    try:
      print_params( None )
    except TypeError as te:  # catch the error
        if str(te).find("argument must be dictionary type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")



if __name__ == '__main__':

    unittest.main()

    # to customize tests to run
    #suite = unittest.TestSuite()
    #suite.addTest( TestModel('test01') )
    #suite.addTest( TestModelElement('test01') )
    #unittest.TextTestRunner().run(suite)
