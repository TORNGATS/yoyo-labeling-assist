
import os
import sys
import unittest

from pyora import Project, TYPE_LAYER, TYPE_GROUP
from PIL import Image
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.handler.gimp import GIMPFileHandler
from yoyo66.handler.core import build_by_name

class GIMP_Test(unittest.TestCase):
    
    def test_load_without_category(self):
        file = "tests/resources/gimp_1.ora"
        gimp = build_by_name('gimp')
        img = gimp.load(file)
        print(img)

if __name__ == '__main__':
    unittest.main()

        