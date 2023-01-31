
import os
import sys
import unittest

from pyora import Project, TYPE_LAYER, TYPE_GROUP
from PIL import Image
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.datastruct import phmImage, Layer, from_image
from yoyo66.handler import PKGFileHandler, build_by_name, load_file

from yoyo66.utils import create_from_image

class phmImage_Test(unittest.TestCase):

    def test_create(self):
        file = "tests/resources/orig.png"
        img = create_from_image(file)
        pkg = build_by_name('pkg')
        pkg.save(img, 'tests/resources/create_from_img.pkg')
        
    def test_load_created_img(self):
        file = 'tests/resources/create_from_img.pkg'
        img = load_file(file)
        print(img.title)
        print(img.orig_layer.image.shape)
        
        
if __name__ == '__main__':
    unittest.main()
