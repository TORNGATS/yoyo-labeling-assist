
import os
import sys
import unittest

from pyora import Project, TYPE_LAYER, TYPE_GROUP
from PIL import Image
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.datastruct import phmImage, Layer
from yoyo66.handler.openraster import OpenRasterFileHandler
from yoyo66.handler.core import build_by_name

class ORA_Test(unittest.TestCase):
    
    def test_load_without_category(self):
        file = "tests/resources/ora_1.ora"
        ora = build_by_name('openraster', ['Crack', 'SurfDeg'])
        img = ora.load(file)
        print(img)

    def test_load_with_category(self):
        file = "tests/resources/ora_1.ora"
        ora = build_by_name('openraster', {'Crack' : 100, 'SurfDeg' : 200})
        img = ora.load(file)
        print(img)
    
    def test_save_with_category(self):
        file = "tests/resources/ora_1_test_edited.ora"
        ora = build_by_name('openraster', {'Crack' : 100, 'SurfDeg' : 200})
        # Original
        orig = np.asarray(Image.open('tests/resources/orig.png'))
        # Crack
        crack = Layer('Crack', image = np.asarray(Image.open('tests/resources/crack.png').convert('LA')))
        # Surface Degradation
        surf = Layer('SurfDeg', image = np.asarray(Image.open('tests/resources/surfdeg.png').convert('LA')))
        # Properties & metrics
        props = {'altitudes' : '12312.123', 'test' : 'yoohooo'}
        metrics = {'iou' : 0.78, 'f1' : 0.542}

        img = phmImage(
            filepath = file,
            properties = props,
            metrics = metrics,
            orig_image = orig,
            layers = [crack, surf]
        )
        ora.save(img, file)


if __name__ == '__main__':
    unittest.main()
