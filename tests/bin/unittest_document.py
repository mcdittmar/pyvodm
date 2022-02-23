import unittest
from pyvodm.document import *
 
class TestDocument(unittest.TestCase):
  """Test Document class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ Document: valid constructor  """

    try:
      result = Document()

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None


# ================================================================================
class TestElementType(unittest.TestCase):
  """Test ElementType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ ElementType: valid constructor """

    a = "Bob"

    try:
      result = ElementType( name=a )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.name, a )


  def test02(self):
    """ ElementType: valid constructor """

    a = "Bob"
    b = "Person instance"

    try:
      result = ElementType( name=a, desc=b )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.name, a )
    self.assertEqual( result.description, b )


#  def test03(self):
#    """ ElementType: invalid constructor """
#
#    try:
#      result = ElementType()
#
#    except TypeError as te: # catch the error
#      if ( str(te).find("takes at least 2 arguments") == -1 ) and (str(te).find("missing 1 required positional argument") == -1):
#        print(te)
#        raise Exception("Error: expected TypeError not thrown")
#      pass
#    except Exception as ex:
#      print(ex.__class__.__name__ + ": " + str(ex))
#      raise Exception("Error: expected exception not thrown")
#    else:
#      raise Exception("Error: No exception thrown for bad input.")


  def test04(self):
    """ ElementType: invalid constructor """

    try:
      result = ElementType( name=4 )

    except TypeError as te: # catch the error
        if str(te).find("must be string type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test05(self):
    """ ElementType: invalid constructor """

    a = "Bob"
    b = 4

    try:
      result = ElementType( name=a, desc=b )

    except TypeError as te: # catch the error
        if str(te).find("must be string type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


# ================================================================================
class TestObjectType(unittest.TestCase):
  """Test ObjectType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ ObjectType:add_composition() - Valid """

    a = "Bob"
    b = "Person instance"
    item = ObjectType(name="Address", desc="Home Address")

    try:
      result = ObjectType( name=a, desc=b )
      result.add_composition( item )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( len(result._compositions), 1 )


  def test02(self):
    """ ObjectType:add_composition() - invalid """

    a = "Bob"
    b = "Person instance"
    item = 5

    try:
      result = ObjectType( name=a, desc=b )
      result.add_composition( item )

    except TypeError as te: # catch the error
        if str(te).find("argument must be ObjectType object") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test03(self):
    """ ObjectType: test 'referenced' flag control """

    Tname = "Bob"
    Tdesc = "Contact Person"
    x = ObjectType( name=Tname, desc=Tdesc )

    try:
      result = x.isReferenced()
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertFalse( result )

    try:
      x.setReferenced(True)
      result = x.isReferenced()
    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    self.assertTrue( result )

    try:
      x.setReferenced( 1 )
    except TypeError as te: # catch the error
        if str(te).find("must be boolean type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

    try:
      x.setReferenced( "something" )
    except TypeError as te: # catch the error
        if str(te).find("must be boolean type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test99(self):
    """ ObjectType Display """

    a = "Bob"
    b = "Person instance"
    address = ObjectType(name="Address", desc="Home Address")
    employer = ReferenceType( name="Organization", desc="Employer", target="_SAO")

    expected =  "<OBJECT ID='_helpdesk' name='Bob' vodml_role='' vodml_type=''>\n"
    expected += "  <DESCRIPTION>Person instance</DESCRIPTION>\n"
    expected += "  <REFERENCES>\n"
    expected += "    <REFERENCE ID='' name='Organization' vodml_role='' vodml_type='' target='_SAO'>\n"
    expected += "      <DESCRIPTION>Employer</DESCRIPTION>\n"
    expected += "    </REFERENCE>\n"
    expected += "  </REFERENCES>\n"
    expected += "  <COMPOSITIONS>\n"
    expected += "    <OBJECT ID='' name='Address' vodml_role='' vodml_type=''>\n"
    expected += "      <DESCRIPTION>Home Address</DESCRIPTION>\n"
    expected += "    </OBJECT>\n"
    expected += "  </COMPOSITIONS>\n"
    expected += "</OBJECT>\n"

    try:
      x = ObjectType( refid="_helpdesk", name=a, desc=b )
      x.add_composition( address )
      x.add_reference( employer )
      result = str(x)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result, expected )


# ================================================================================
class TestDataType(unittest.TestCase):
  """Test DataType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ DataType: valid constructor """

    a = "height"
    try:
      result = DataType(a)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None


  def test02(self):
    """ DataType: valid constructor """

    a = "height"
    b = "format [m]\' [n]\""

    try:
      result = DataType( name=a, desc=b )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.name, a )
    self.assertEqual( result.description, b )

#  def test03(self):
#    """ DataType: invalid constructor """
#
#    try:
#      result = DataType()
#
#    except TypeError as te: # catch the error
#        if ( str(te).find("takes at least 2 arguments") == -1 ) and (str(te).find("missing 1 required positional argument") == -1):
#          print(te)
#          raise Exception("Error: expected TypeError not thrown")
#        pass
#    except Exception as ex:
#        print(ex.__class__.__name__ + ": " + str(ex))
#        raise Exception("Error: expected exception not thrown")
#    else:
#      raise Exception("Error: No exception thrown for bad input.")

  def test04(self):
    """ DataType: invalid constructor """

    try:
      result = DataType( name=4 )

    except TypeError as te: # catch the error
        if str(te).find("must be string type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test05(self):
    """ DataType: invalid constructor """

    a = "height"
    b = 4

    try:
      result = DataType( name=a, desc=b )

    except TypeError as te: # catch the error
        if str(te).find("must be string type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test06(self):
    """ DataType:add_attribute() - Valid """

    a = "Bob"
    b = "Person instance"
    c = "height"
    d = "format [m]\' [n]\""

    item = DataType( c, desc=d )

    try:
      result = DataType( name=a, desc=b )
      result.add_attribute( item )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( len(result._attributes), 1 )

  def test07(self):
    """ DataType:add_attribute() - invalid """

    a = "Bob"
    b = "Person instance"
    item = 5

    try:
      result = DataType( name=a, desc=b )
      result.add_attribute( item )

    except TypeError as te: # catch the error
        if str(te).find("argument must be ValueType object") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

  def test08(self):
    """ DataType:add_reference() - Valid """

    a = "Bob"
    b = "Person instance"
    item = ReferenceType(name="Organization", desc="Employer", target="_SAO")

    try:
      result = DataType( name=a, desc=b )
      result.add_reference( item )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( len(result._references), 1 )

  def test09(self):
    """ DataType:add_reference() - invalid """

    a = "Bob"
    b = "Person instance"
    item = 5

    try:
      result = DataType( name=a, desc=b )
      result.add_reference( item )

    except TypeError as te: # catch the error
        if str(te).find("argument must be ReferenceType object") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test10(self):
    """ DataType:add_reference() - invalid """

    a = "Bob"
    b = "Person instance"
    item = ReferenceType(name="Organization", desc="Employer", target="")

    try:
      result = DataType( name=a, desc=b )
      result.add_reference( item )

    except ValueError as te: # catch the error
        if str(te).find("invalid or empty reference ID in") == -1:
          print(te)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test99(self):
    """ DataType Display """

    expected = "<DATATYPE ID='' name='height' vodml_role='' vodml_type='' ucd='meta.height;person' value='6ft. 2in.'>\n  <DESCRIPTION>format [m]ft. [n]in.</DESCRIPTION>\n</DATATYPE>\n"
    
    a = "height"
    b = "format [m]ft. [n]in."
    u = "meta.height;person"
    try:
      x = DataType( name=a, desc=b, ucd=u )
      x.type="char"
      x.value="6ft. 2in."

      result = str(x)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result, expected )


# ================================================================================
class TestFieldType(unittest.TestCase):
  """Test FieldType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ FieldType: valid constructor """

    a = "energy"
    try:
      result = FieldType(a)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None


  def test99(self):
    """ FieldType Display """

    expected = "<FIELDTYPE ID='' name='energy' vodml_role='' vodml_type=''>\n  <DESCRIPTION>photon energy</DESCRIPTION>\n</FIELDTYPE>\n"

    a = "energy"
    b = "photon energy"
    try:
      x = FieldType( name=a, desc=b )
      x.type="ivoa:RealQuantity"
      x.unit="keV"

      result = str(x)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result, expected )

# ================================================================================
class TestEnumType(unittest.TestCase):
  """Test EnumType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ EnumType:add_literal() - Valid """

    try:
      result = EnumType(name="classification", desc="Enumeration of Source Classifications", value="STAR")
      result.add_literal( "catalog.SourceClassification.star", "STAR" )
      result.add_literal( "catalog.SourceClassification.galaxy", "GALAXY" )
      result.add_literal( "catalog.SourceClassification.agn", "AGN" )

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( len(result._literals), 3 )


  def test02(self):
    """ EnumType:add_literal() - invalid """

    result = EnumType(name="classification", desc="Enumeration of Source Classifications")
    try:
      result.add_literal( "catalog.SourceClassification.star", 7 )

    except TypeError as te: # catch the error
        if str(te).find("argument must be string type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")

    try:
      result.add_literal( None, "STAR" )

    except TypeError as te: # catch the error
        if str(te).find("argument must be string type") == -1:
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test99(self):
    """ EnumType Display """

    expected =  "<ENUMERATION ID='_srcClass' name='classification' vodml_role='' vodml_type='' value='AGN'>\n"
    expected += "  <DESCRIPTION>Enumeration of Source Classifications</DESCRIPTION>\n"
    expected += "  <LITERAL vodmlid='catalog.SourceClassification.agn' label='AGN' />\n"
    expected += "  <LITERAL vodmlid='catalog.SourceClassification.galaxy' label='GALAXY' />\n"
    expected += "  <LITERAL vodmlid='catalog.SourceClassification.star' label='STAR' />\n"
    expected += "</ENUMERATION>\n"

    try:
        x = EnumType(refid="_srcClass", name="classification", desc="Enumeration of Source Classifications", value="AGN")
        x.add_literal( "catalog.SourceClassification.star", "STAR" )
        x.add_literal( "catalog.SourceClassification.galaxy", "GALAXY" )
        x.add_literal( "catalog.SourceClassification.agn", "AGN" )

        result = str(x)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result, expected )

# ================================================================================
class TestPrimitiveType(unittest.TestCase):
  """Test PrimitiveType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ PrimitiveType() - Valid """

    Tvalstr = "2019-01-23T12:00.0"
    Trole   = "coords:ISOTime.date"
    Ttype   = "ivoa:datetime"
    Tname   = "valid_start"
    Tdesc   = "Start time of validity internval"

    try:
      result = PrimitiveType( name=Tname, desc=Tdesc, value=Tvalstr )
      result.vodml_role = Trole
      result.vodml_type = Ttype

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.name, Tname )
    self.assertEqual( result.vodml_role, Trole )
    self.assertEqual( result.vodml_type, Ttype )
    self.assertEqual( result.value, Tvalstr )


  def test02(self):
    """ PrimitiveType() - invalid """

    try:
        result = PrimitiveType()

    except TypeError as te: # catch the error
        if ( str(te).find("takes at least 2 arguments") == -1 ) and (str(te).find("missing 1 required positional argument") == -1):
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test99(self):
    """ PrimitiveType Display """

    expected =  "<PRIMITIVE ID='' name='valid_start' vodml_role='coords:ISOTime.date' vodml_type='ivoa:datetime' value='20190123T12:00.0'>\n"
    expected += "  <DESCRIPTION>Start time of validity internval</DESCRIPTION>\n"
    expected += "</PRIMITIVE>\n"

    Tvalstr = "20190123T12:00.0"
    Trole   = "coords:ISOTime.date"
    Ttype   = "ivoa:datetime"
    Tname   = "valid_start"
    Tdesc   = "Start time of validity internval"

    try:
        x = PrimitiveType( name=Tname, desc=Tdesc, value=Tvalstr )
        x.vodml_role = Trole
        x.vodml_type = Ttype

        result = str(x)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result, expected )

# ================================================================================
class TestReferenceType(unittest.TestCase):
  """Test ReferenceType class """

  def setUp(self):
    """ Setup prior to each test"""

  def test01(self):
    """ ReferenceType() - Valid """

    Tid     = "_3509fffo4bfbqbk"
    Trole   = "coords:Coordinate.frame"
    Ttype   = "coords:SpaceFrame"
    Tname   = "frame"
    Tdesc   = "Reference to ICRS SpaceFrame"
    Ttarget = "_ICRSFrame"

    try:
      result = ReferenceType( refid=Tid, name=Tname, desc=Tdesc, target=Ttarget )
      result.vodml_role = Trole
      result.vodml_type = Ttype

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result.refid, Tid )
    self.assertEqual( result.name, Tname )
    self.assertEqual( result.vodml_role, Trole )
    self.assertEqual( result.vodml_type, Ttype )
    self.assertEqual( result.target, Ttarget )


  def test02(self):
    """ ReferenceType() - invalid """

    try:
        result = ReferenceType()

    except TypeError as te: # catch the error
        if ( str(te).find("takes at least 2 arguments") == -1 ) and (str(te).find("missing 1 required positional argument") == -1):
          print(te)
          raise Exception("Error: expected TypeError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test03(self):
    """ ReferenceType() - invalid """

    try:
        result = ReferenceType(target=[])

    except TypeError as te: # catch the error
        if ( str(te).find("argument must be string type") == -1 ):
          print(te)
          raise Exception("Error: expected ValueError not thrown")
        pass
    except Exception as ex:
        print(ex.__class__.__name__ + ": " + str(ex))
        raise Exception("Error: expected exception not thrown")
    else:
      raise Exception("Error: No exception thrown for bad input.")


  def test99(self):
    """ ReferenceType Display """

    expected =  "<REFERENCE ID='_3509fffo4bfbqbk' name='frame' vodml_role='coords:Coordinate.frame' vodml_type='coords:SpaceFrame' target='_ICRSFrame'>\n"
    expected += "  <DESCRIPTION>Reference to ICRS SpaceFrame</DESCRIPTION>\n"
    expected += "</REFERENCE>\n"

    Tid     = "_3509fffo4bfbqbk"
    Trole   = "coords:Coordinate.frame"
    Ttype   = "coords:SpaceFrame"
    Tname   = "frame"
    Tdesc   = "Reference to ICRS SpaceFrame"
    Ttarget = "_ICRSFrame"

    try:
        x = ReferenceType( refid=Tid, name=Tname, desc=Tdesc, target=Ttarget )
        x.vodml_role = Trole
        x.vodml_type = Ttype

        result = str(x)

    except Exception as ex:
      print(ex.__class__.__name__ + ": " + str(ex))
      raise Exception("Error: unexpected exception thrown")

    assert result is not None
    self.assertEqual( result, expected )


if __name__ == '__main__':

    unittest.main()

    # to customize tests to run
    #suite = unittest.TestSuite()
    #suite.addTest( TestModel('test01') )
    #suite.addTest( TestModelElement('test01') )
    #unittest.TextTestRunner().run(suite)
