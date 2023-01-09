

import functools
import numbers
import os
from abc import ABC
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Union

from PIL import Image

__original_key__ = 'original'

"""
Dimension is a entity class used to keep the dimension al values (width and height)
Dimension class has two main fields: width and height.
"""
Dimension = namedtuple('Dimension', ['width', 'height'])

@dataclass
class Layer:
    """
    Layer is a base class for mask layers inside a multi-layer image file.
    """
    
    # The index of the layer
    id : int
    # name (str) the name of layer 
    name : str
    # opacity (float) the opacity of the layer. Default 1.0
    opacity : float = field(default=1.0)
    # visibility (bool) determine whether the layer is hidden (False) or not (True). Default True
    visibility : bool = field(default=True)
    # Class identifier
    class_id : int = field(default=1)
    # image (PIL.Image) the imagery data of the layer. Default None
    image : Image = field(default=None)
    # x (int) the x position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    x : int = field(default=0)
    # y (int) the y position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    y : int = field(default=0)

    def is_valid(self) -> bool:
        """Check if the layer is valid. The image is valid if the image field is initialized!

        Returns:
            bool: True if valid
        """
        return self.image is not None

class phmImage(ABC):
    
    def __init__(self,
        filepath : str,
        properties : Dict,
        original_image : Image,
        layers : List[Layer],
        title : str = None
    ):
        super().__init__()
        # File path
        self.filepath = filepath
        # File name
        self.filename = os.path.basename(self.filepath)
        # Image title
        self.title = Path(self.filepath).stem if title is None else title
        # Properties
        self.properties = {
            'filepath' : self.filepath,
            'filename' : self.filename,
            'title' : self.title,
            **properties
        }
        # Layers
        self.layers = layers

    def __getitem__(self, key) -> Union[Dict, Layer] :
        res = None
        if key == 'properties':
            res = self.properties
        elif isinstance(key, str):
            res = self.get_layer(key)
        elif isinstance(key, numbers.Number):
            res = self.get_layer_by_index(key)
        else:
            raise ValueError('Key %s is invalid' % key)
        return res
   
    def get_property(self, prop):
        if not prop in self.properties:
            raise KeyError('Property %s not found' % prop)
        return self.properties[prop]
    
    def set_property(self, prop, value) -> None:
        self.properties[prop] = value
    
    def get_layer(self, layer_name : str) -> Layer:
        layer = None
        for l in self.layers:
            if layer_name == l.name:
                layer = l
                break
        
        if layer is None:
            raise KeyError('%s layer does not exist!' % layer_name)
        return layer
    
    def get_layer_by_index(self, index : int) -> Layer:
        if index >= len(self.layers) or index < 0:
            raise IndexError('Index %d does not exist' % index)
        return self.layers[index]
    
    def get_original_image(self) -> Image:
        return self.original_image
    
    @property
    def dimension(self):
        return self.original_image.size if self.original_image is not None else None
    
    @property
    def mask_layers(self) -> Tuple[Layer]:
        return tuple(self.layers)
    
    @property
    def layers_name(self) -> Tuple[str]:
        return tuple(map(lambda x : x.name, self.layers))
    
    @property
    def layer_names(self) -> Tuple[str]:
        return self.get_layer_names()

    def __iter__(self):
        orig = Layer(id = 0, name = 'original', image = self.original_image)
        return iter(tuple([orig]) + self.mask_layers)