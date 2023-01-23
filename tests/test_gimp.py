
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
from yoyo66.datastruct import create_image

class GIMP_Test(unittest.TestCase):
    
    file = "tests/resources/gimp_1.xcf"
    
    def test_load_without_category(self):
        gimp = build_by_name('gimp', ['Crack', 'SurfDeg'])
        img = gimp.load(self.file)
        print(img)
    
    def test_load_with_category(self):
        file = "tests/resources/gimp_1.xcf"
        gimp = build_by_name('gimp', {'Crack' : 100, 'SurfDeg' : 200})
        img = gimp.load(self.file)
        print(img)
        img.get_stats({'Crack' : 100, 'SurfDeg' : 200})
        
    def test_blend_and_thumbnail(self):
        file = "tests/resources/gimp_1.xcf"
        gimp = build_by_name('gimp', {'Crack' : 100, 'SurfDeg' : 200})
        img = gimp.load(self.file)
        img.thumbnail().save('tests/resources/gimp_1_thumbnail.png')
        img.blended_image().save('tests/resources/gimp_1_blended.png')

if __name__ == '__main__':
    unittest.main()
