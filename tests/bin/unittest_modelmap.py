import unittest
from pyvodm.modelMap import *
import os
 
class TestModelMapElement(unittest.TestCase):
  """Test ModelMapElement class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ ModelMapElement: valid constructor  """

    a =  "7bl4ryZpLwCUd3of"
    b =  "DataID.datasetID"
    c =  "ds:dataset.DataID.datasetID"
    h =  ""
    d =  "meta.id;meta.dataset"
    e =  ""
    f =  "key:DSIDENT"
    g =  "IVOA Dataset Identifier"
    try:
      result = ModelMapElement(uid=a, name=b, role=c, etype=h, ucd=d, unit=e, value=f, desc=g )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.uid, a )
    self.assertEqual( result.name, b )
    self.assertEqual( result.role, c )
    self.assertEqual( result.etype, h )
    self.assertEqual( result.ucd, d )
    self.assertEqual( result.unit, e )
    self.assertEqual( result.value, f )
    self.assertEqual( result.description, g )


  def test02(self):
    """ ModelMapElement: display"""

    expected = 'ModelMapElement: 7bl4ryZpLwCUd3of\n   ModelPath:    DataID.datasetID\n   Role:         ds:dataset.DataID.datasetID\n   Type:         <default>\n   UCD:          meta.id;meta.dataset\n   Unit:         \n   Description:  IVOA Dataset Identifier\n   Value:        \n\n'

    try:
      rec = ModelMapElement( uid="7bl4ryZpLwCUd3of",
                             name="DataID.datasetID",
                             role="ds:dataset.DataID.datasetID",
                             etype="",
                             ucd="meta.id;meta.dataset",
                             unit="",
                             value="",
                             desc="IVOA Dataset Identifier"
                           )
      result = str(rec)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result, expected )


  def test03(self):
    """ ModelMapElement: value property"""

    # Instantiate ModelMapElement
    rec = ModelMapElement( uid="7bl4ryZpLwCUd3of",
                           name="DataID.datasetID",
                           role="ds:dataset.DataID.datasetID",
                           etype="",
                           ucd="meta.id;meta.dataset",
                           unit="",
                           value="",
                           desc="IVOA Dataset Identifier"
                          )

    try:
        # Test set value to None
        rec.value = None
    except TypeError as te: # catch the error
        if str(te).find("'value' argument value invalid") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
        # Test set value to bad format
        rec.value = "bad:content"
    except TypeError as te: # catch the error
        if str(te).find("'value' argument value invalid") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
        # Test set value to good format
        rec.value = "key:DSIDENT"
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: unexpected exception thrown")

    self.assertEqual( rec.value, "key:DSIDENT" )

    try:
        # Test set value to empty string
        rec.value = "   "
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: unexpected exception thrown")

    self.assertEqual( rec.value, "" )



# ================================================================================
class TestModelMap(unittest.TestCase):
  """Test ModelMap class """

  TEST_RESOURCE_DIR = os.path.join( os.path.dirname(__file__), '../res/' )
  
  # Model Description files
  fname = ''.join( (TEST_RESOURCE_DIR, 'test_modelmap.db' ) )

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ ModelMap: valid constructor """

    try:
      result = ModelMap( self.fname )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None

  def test02(self):
    """ ModelMap: constructor with empty argument string """

    try:
      result = ModelMap( " " )

    except IOError as ie: # catch the error
        if str(ie).find("argument value invalid.") == -1:
          print(ie)
          raise Exception("Error: expected IOError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test03(self):
    """ ModelMap: constructor with file dne """

    try:
      result = ModelMap( "/data/dne.tab" )

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
    """ ModelMap: find() method """

    tuid = "_50XbEKAqJbw3QCCV"
    tname = "SrcLumin.value"
    trole = "sample:catalog.LuminosityMeasurement.value"

    m = ModelMap( self.fname )

    try:
      # test invalid input
      result = m.find( uid=None )

    except TypeError as te: # catch the error
        if str(te).find("must specify uid or name") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
      # test invalid input
      result = m.find( name=None )

    except TypeError as te: # catch the error
        if str(te).find("must specify uid or name") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
      # test invalid input (both set)
      result = m.find( uid=tuid, name=tname )

    except TypeError as te: # catch the error
        if str(te).find("must specify uid or name") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
      # test uid not matched
      result = m.find( uid="unmatched_string" )

    except ValueError as ve: # catch the error
        if str(ve).find("Matching record not found in ModelMap, uid=") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
      # test name not matched
      result = m.find( name="unmatched_string" )

    except ValueError as ve: # catch the error
        if str(ve).find("Matching record not found in ModelMap, name=") == -1:
          print(ve)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
        raise Exception("Error: No exception thrown for bad input.")

    try:
      # test valid uid
      result = m.find( uid=tuid )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result.uid, tuid )
    self.assertEqual( result.role, trole )

    try:
      # test valid name
      result = m.find( name=tname )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( result.uid, tuid )
    self.assertEqual( result.role, trole )


  def test06(self):
    """ ModelMap: find_children() with valid input """


    children = { "_31PB0wN4yle0K5mQ": "SrcPos.longitude",
                 "_30XJg9FgKp5qr9vc": "SrcPos.latitude",
                 "_30yF4Lns5HehrK8h": "SrcPos.frame",
               }
    uid = "_309W3rygu5gAFiob"  #Source Position
    try:
      m = ModelMap( self.fname )
      result = m.find_children( uid )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertEqual( len(result), 3 )
    for k in children:
        self.assertEqual( result[k].name, children[k] )



if __name__ == '__main__':

    unittest.main()

    # to customize tests to run
    #suite = unittest.TestSuite()
    #suite.addTest( TestModel('test01') )
    #suite.addTest( TestModelElement('test01') )
    #unittest.TextTestRunner().run(suite)
