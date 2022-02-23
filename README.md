#
# Python tool to generate example serializations of VO Datamodel elements.
#

doit.sh [build, clean, install, test]
  * 'Makefile' for the package

doc/
  * Documentation relate to the tool

resources/
  * Templates for each example file.

src/
  * Source code (Python-3.5)
  * 
  * Dependencies:
    # System modules
      + collections.OrderedDict
      + os
      + shutil
      + sys
      + tempfile
      + urllib.request.urlopen
      + urllib2 
         NOTE: The urllib2 module has been split across several modules in Python 3 named 
               urllib.request and urllib.error. The 2to3 tool will automatically adapt 
               imports when converting your sources to Python 3.
      + xml.dom.minidom

    # CIAO modules
      + paramio
      + pycrates as cr
      + stk

test/
  * Utility test code




maketags.pl
  * utility script to generate uuid strings for use in the templates (16 char random strings)

