
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

class PKG_Test(unittest.TestCase):

    def test_load_without_category(self):
        st = time.time() * 1000
        file = "tests/resources/pkg_1.pkg"
        pkg = build_by_name('pkg', ['Crack', 'SurfDeg'])
        img = pkg.load(file)
        print(img)
        et = time.time() * 1000
        print('Execution time:', et - st, 'miliseconds')

    def test_rewite_archive(self):
        file = "tests/resources/pkg_archive.pkg"
        pkg = build_by_name('pkg', ['Crack', 'SurfDeg'])
        img = pkg.load(file)
        pkg.save(img, "tests/resources/pkg_archive_rewrite.pkg")

    def test_save_archive(self):
        st = time.time() * 1000
        file = "tests/resources/pkg_archive.pkg"
        pkg = build_by_name('pkg', ['Crack', 'SurfDeg'])
        img = pkg.load(file)
        print(img)
        with img.archive as ac:
            ac.set_asset(
                path = 'phm.postprocessing.crack',
                data = from_image(Image.open('tests/resources/crack.png')),
                overwrite=True
            )
            ac.set_asset(
                path = 'phm.postprocessing.surfdeg',
                data = from_image(Image.open('tests/resources/surfdeg.png')),
                overwrite=True
            )
        et = time.time() * 1000
        print('Execution time:', et - st, 'miliseconds')

    def test_load_archive(self):
        file = "tests/resources/pkg_archive.pkg"
        pkg = build_by_name('pkg', ['Crack', 'SurfDeg'])
        img = pkg.load(file)
        with img.archive as ac:
            arr = ac.get_asset('phm.postprocessing.crack')
            print(arr.shape)
            print(ac.get_assets())

    def test_save_layer_and_new_archive(self):
        st = time.time() * 1000
        file = "tests/resources/IMG_8239_infer.pkg"
        new_status = np.array(Image.open("tests/resources/dilated.png"))[:,:,-1] / 255
        new_status = Layer(name="dilated", class_id=1, image=new_status)
        
        pkg = build_by_name('pkg', [])
        img = pkg.load(file)
        print(img)
        img.layers = [new_status]
        print(img)
        with img.archive as ac:
            ac.set_asset(
                path = 'predictions.dilated',
                data = np.array(create_image(new_status)),
                overwrite=True
            )
        pkg.save(img, "tests/resources/IMG_8239_infer.pkg")
        et = time.time() * 1000
        print('Execution time:', et - st, 'miliseconds')

    def test_save_with_category(self):
        file = "tests/resources/pkg_1.pkg"
        classes = {'Crack' : 100, 'SurfDeg' : 200}
        pkg = build_by_name('pkg', ['Crack', 'SurfDeg'])
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
