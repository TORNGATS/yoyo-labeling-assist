

import functools
import numbers
import os
from abc import ABC, abstractmethod
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
class phmLayer:
    """
    phmLayer is a base class for layers inside a multi-layer image file.
    """
    
    # name (str) the name of layer 
    name : str
    # opacity (float) the opacity of the layer. Default 1.0
    opacity : float = field(default=1.0)
    # visibility (bool) determine whether the layer is hidden (False) or not (True). Default True
    visibility : bool = field(default=True)
    # image (PIL.Image) the imagery data of the layer. Default None
    image : Image = field(default=None)
    # x (int) the x position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    x : int = field(default=0)
    # y (int) the y position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    y : int = field(default=0)

    def is_valid(self):
        return self.image is not None

class phmImage(ABC):
    
    def __init__(self,
        filepath : str,
        dimension : Dimension,
        properties : Dict,
        layers : List[phmLayer],
        title : str = None
    ):
        # File path
        self.filepath = filepath
        # File name
        self.filename = os.path.basename(self.filepath)
        # Image title
        self.title = Path(self.filepath).stem if title is None else title
        # Image dimensions
        self.dimension = dimension
        # Properties
        self.properties = {
            'filepath' : self.filepath,
            'filename' : self.filename,
            'title' : self.title,
            **properties
        }
        # Layers
        self.layers = layers

    def __getitem__(self, key) -> Union[Dict, phmLayer] :
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
    
    def get_layer(self, layer_name : str) -> phmLayer:
        layer = None
        for l in self.layers:
            if layer_name == l.name:
                layer = l
        
        if layer is None:
            raise KeyError('%s layer does not exist!' % layer_name)
        return layer
    
    def get_layer_by_index(self, index : int) -> phmLayer:
        if index >= len(self.layers):
            raise IndexError('Index %d does not exist' % index)
        return self.layers[index]
    
    def get_all_layers(self) -> Tuple[phmLayer]:
        return tuple(self.layers)

    def get_layer_names(self) -> Tuple[str]:
        return tuple(map(lambda x : x.name, self.layers))
    
    def get_original_image(self):
        return self.layers[__original_key__]
    
    @property
    def layer_names(self) -> Tuple[str]:
        return self.get_layer_names()
    
    @property
    def original_image(self) -> Image:
        return self.get_original_image()
