
import os
import sys
import unittest

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import yoyo66.handler
from yoyo66.datastruct import phmImage, Layer
from yoyo66.handler.pkg import PKGFileHandler
from yoyo66.handler.core import build_by_name
from yoyo66.utils import ConvertHandler, build_converter, convert_file__

class Convert_Test(unittest.TestCase):

    def test_file_converter(self):
        srcfile = 'tests/resources/gimp_1.xcf'
        desfile = 'tests/resources/gimp_2_ora_convert.ora'
        convert_file__(
            src_file = srcfile, 
            dest_file = desfile, 
            categories = {'Crack' : 100, 'SurfDeg' : 200}
        )

if __name__ == '__main__':
    unittest.main()
