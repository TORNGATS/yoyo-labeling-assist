

from pyora import Project, TYPE_LAYER, TYPE_GROUP
from PIL import Image
import numpy as np

##### 1
# project = Project.load("/home/phm/Pictures/test.ora")

# for layer in project.children:
#     print(layer.name)
#     if layer.type == TYPE_LAYER:
#         print(layer.name)
#         layer.raw_attributes['test'] = 'Parham'
        
#         project.add_layer(layer.image, 'phm/' + layer.name)

# project.save("/home/phm/Pictures/test2.ora")

#### 2
project = Project.load("/home/phm/Pictures/gimp.ora")
layer = project['/layers/Crack']
img = np.asarray(layer.image)
layer.image.save('/home/phm/Pictures/phm.png')
layer['hello'] = 'Parham'

for i in layer.raw_attributes.items():
    print(i)

imga = Image.fromarray(np.where(np.asarray(img[:,:,-1]) != 0, 100, 0).astype(np.uint8), 'L').save('/home/phm/Pictures/phm2.png')

for layer in project.children:
    if layer.type == TYPE_GROUP:
        print(layer.name)

        