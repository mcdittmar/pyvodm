import unittest
from pyvodm.model.builders import *
import os
 
class TestDocBuilder(unittest.TestCase):
  """Test DocBuilder Class """

  TEST_BASE_DIR = os.path.join( os.path.dirname(__file__), '../' )

  TESTIN  = ''.join( (TEST_BASE_DIR, "data/") )
  TESTOUT = ''.join( (TEST_BASE_DIR, "out/") )
  TESTSAV = ''.join( (TEST_BASE_DIR, "base/") )
  TESTRES = ''.join( (TEST_BASE_DIR, "res/") )

  def setUp(self):
    """ Setup prior to each test"""

    if not os.path.exists( self.TESTOUT ):
      os.mkdir( self.TESTOUT )


  def test01(self):
    """ Basic Test  """

    try:
        b = DocBuilder()

        # Add models
        b.add_model( self.TESTRES+"Sample.vo-dml.xml")
        b.add_model( self.TESTRES+"Filter.db")
        b.add_model( self.TESTRES+"IVOA-v1.0.vo-dml.xml")

        # Add instance map
        b.add_instance_map( self.TESTRES+"test_modelmap.db")

        d = b.process( self.TESTIN+"test_sample.fits" )

        # Write doc to file
        tfile = self.TESTOUT+"docBuilder_test01.txt"
        fh = open( tfile, 'w' )
        fh.write( str(d) )
        fh.close()

    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: unexpected exception thrown")

    # Validate
    assert b is not None
    tags = b.models.keys()
    assert ('sample' in tags ) is True
    assert ('filter' in tags ) is True
    assert b.template is not None
    assert d is not None
    self.assertEqual( len(b._referenced), 2 )
    assert ('_0105IApdgix1jeja' in b._referenced) is True
    assert ('_100bQ8LarUAorcmn' in b._referenced) is True
    # Verify resulting Document content


  def test02(self):
    """ Test missing models  """

    b = DocBuilder()
    
    # Add models
    b.add_model( self.TESTRES+"Sample.vo-dml.xml")
    b.add_model( self.TESTRES+"Filter.db")

    try:
        # Add instance map
        b.add_instance_map( self.TESTRES+"test_modelmap.db")

    except ValueError as ve: # catch the error
        if str(ve).find("Template requires Models not loaded") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test_get_header(self):
    """ Test method _get_header() """

    fname = "".join( (self.TESTIN, 'test_sample.fits') )
    
    b = DocBuilder()
    meta = b._get_header( fname, 1 )

    # Validate
    self.assertIsNotNone( meta )
    self.assertEqual( len(meta), 17 )

    # Show them.
    #for key, value in meta.items():
    #  print( f'{key} = {value}' )
    


if __name__ == '__main__':

    unittest.main()

    # to customize tests to run
    #suite = unittest.TestSuite()
    #suite.addTest( TestModel('test01') )
    #suite.addTest( TestModelElement('test01') )
    #unittest.TextTestRunner().run(suite)
