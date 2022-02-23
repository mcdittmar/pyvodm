import unittest
from pyvodm.model import *
import os
 
class TestModelElement(unittest.TestCase):
  """Test ModelElement class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ ModelElement: valid constructor  """

    a = "catalog.SkyCoordinate.latitude",
    b = "ivoa:RealQuantity",
    c = "1",
    f = "The latitude part of this position in units of degrees."
    try:
      result = ModelElement(tag=a, dtype=b, mult=c, desc=f )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.tag, a )
    self.assertEqual( result.dtype, b )
    self.assertEqual( result.multiplicity, c )
    self.assertEqual( result.description, f )


  def test02(self):
    """ ModelElement: display"""

    expected = 'ModelElement:\n   Tag:   catalog.SkyCoordinate.latitude\n   EType: \n   Type:  ivoa:RealQuantity\n   Extend:\n   Mult:  1\n   Desc:  The latitude part of this position in units of degrees.\n   Constr:\n   SemCon:\n\n'
    try:
      rec    = ModelElement(tag="catalog.SkyCoordinate.latitude",
                            dtype="ivoa:RealQuantity",
                            mult="1",
                            desc="The latitude part of this position in units of degrees."
                            )
      result = str(rec)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result, expected )



class TestModel(unittest.TestCase):
  """Test Model class """

  TEST_RESOURCE_DIR = os.path.join( os.path.dirname(__file__), '../res/' )
  
  # Model Description files
  fname = ''.join( (TEST_RESOURCE_DIR, 'Sample.db' ) )
  xname = ''.join( (TEST_RESOURCE_DIR, 'Sample.vo-dml.xml') )

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ Model: valid constructor - ASCII format """

    try:
      result = Model( self.fname )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None

  def test02(self):
    """ Model: constructor with empty argument string """

    try:
      result = Model( " " )

    except IOError as ie: # catch the error
        if str(ie).find("argument empty; must provide Model description file.") == -1:
          print(ie)
          raise Exception("Error: expected IOError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test03(self):
    """ Model: constructor with file dne """

    try:
      result = Model( "/data/dne.db" )

    except IOError as ie: # catch the error
        if str(ie).find("No such file or directory") == -1:
          print(ie)
          raise Exception("Error: expected IOError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test04(self):
    """ Model: constructor with unrecognized type """

    try:
      result = Model( "/data/dne.tab" )

    except ValueError as ve: # catch the error
        if str(ve).find("Unable to identify Model description file type.") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test05(self):
    """ Model: valid constructor - VO-DML/XML format """

    try:
      result = Model( self.xname )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None

  def test06(self):
    """ Model: valid constructor from URL """

    url = "https://volute.g-vo.org/svn/trunk/projects/dm/Cube/vo-dml/Cube-1.0.vo-dml.xml"
    try:
      result = Model( url )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None


  def test07(self):
    """ Model: invalid constructor from URL """

    url = "https://volute.g-vo.org/svn/trunk/projects/dm/Cube/vo-dml/Square-1.0.vo-dml.xml"
    try:
      result = Model( url )

    except IOError as ie: # catch the error
        if str(ie).find("Problem opening Model description file") == -1:
          print(ie)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test08(self):
    """ Model: get() with valid input """

    tag = "catalog.LuminosityMeasurement.value"
    key = "sample:"+tag
    try:
      m = Model( self.fname )
      result = m.get( key )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result.tag, tag )
    self.assertEqual( result.dtype, "ivoa:RealQuantity" )
    self.assertEqual( result.multiplicity, "1" )
    self.assertEqual( result.description, "TODO : Missing description : please, update your UML model asap." )

  def test09(self):
    """ Model: get() with no match to input tag  """

    tag = "sample:catalog.LuminosityType.dne"
    try:
      m = Model( self.fname )
      result = m.get( tag )

    except ValueError as ve: # catch the error
        if str(ve).find("Input tag not found in Model") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
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

