
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
from yoyo66.handler.pkg import PKGFileHandler
from yoyo66.handler.core import build_by_name
from yoyo66.utils import create_from_image

class phmImage_Test(unittest.TestCase):

    def test_create(self):
        file = "/home/phm/Datasets/S1014684.JPG"
        img = create_from_image(file)
        pkg = build_by_name('pkg')
        pkg.save(img, '/home/phm/Datasets/S1014684.pkg')
        
if __name__ == '__main__':
    unittest.main()
