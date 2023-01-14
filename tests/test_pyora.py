
import os
import sys
import unittest

from pyora import Project, TYPE_LAYER, TYPE_GROUP
from PIL import Image
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class PyoraTest(unittest.TestCase):
    
    def test_load(self):
        project = Project.load("tests/resources/ora_1.ora")
        for layer in project.children:
            print(layer.name)
            if layer.type == TYPE_LAYER:
                print(layer.name)
                layer.raw_attributes['test'] = 'Parham'
                
                project.add_layer(layer.image, 'layers/' + layer.name + '_added')

        project.save("tests/resources/ora_1_saved.ora")
    
    def test_load_save(self):
        project = Project.load("tests/resources/ora_1.ora")
        layer = project['/layers/Crack']
        img = np.asarray(layer.image)

        for i in layer.raw_attributes.items():
            print(i)

        for layer in project.children:
            if layer.type == TYPE_GROUP:
                print(layer.name)

if __name__ == '__main__':
    unittest.main()

        