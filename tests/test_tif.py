
import os
import sys
import time
import unittest

from PIL import Image
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.utils import create_image
from yoyo66.datastruct import phmImage, Layer, from_image
from yoyo66.handler.core import build_by_name

class Tif_Test(unittest.TestCase):

    def test_load_without_category(self):
        st = time.time() * 1000
        file = "tests/resources/tif_2.tif"
        pkg = build_by_name('tiff', ['Crack', 'SurfDeg'])
        img = pkg.load(file)
        print(img)
        et = time.time() * 1000
        print('Execution time:', et - st, 'miliseconds')

    def test_save_with_category(self):
        file = "tests/resources/tif_1.tif"
        classes = {'Crack' : 100, 'SurfDeg' : 200}
        pkg = build_by_name('tiff', ['Crack', 'SurfDeg'])
        # Original
        orig = np.asarray(Image.open('tests/resources/orig.png'))
        # Crack
        crack = Layer('Crack', class_id=classes['Crack'], image = from_image(Image.open('tests/resources/crack.png')))
        # Surface Degradation
        surf = Layer('SurfDeg', class_id=classes['SurfDeg'], image = from_image(Image.open('tests/resources/surfdeg.png')))
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
        pkg.save(img, file)


if __name__ == '__main__':
    unittest.main()
