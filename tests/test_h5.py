
import os
import sys
import time
import unittest

from PIL import Image
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.datastruct import phmImage, Layer, from_image
from yoyo66.handler.hfive import H5FileHandler
from yoyo66.handler.core import build_by_name

class H5_Test(unittest.TestCase):

    def test_load_without_category(self):
        st = time.time() * 1000
        file = "tests/resources/h5_1.h5"
        h5 = build_by_name('h5', ['Crack', 'SurfDeg'])
        img = h5.load(file)
        print(img)
        et = time.time() * 1000
        print('Execution time:', et - st, 'miliseconds')

    def test_save_with_category(self):
        file = "tests/resources/h5_1.h5"
        classes = {'Crack' : 100, 'SurfDeg' : 200}
        h5 = build_by_name('h5', ['Crack', 'SurfDeg'])
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
        h5.save(img, file)


if __name__ == '__main__':
    unittest.main()
