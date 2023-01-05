

import functools
import numbers
import os
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Union

from PIL import Image

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
    
    #: 
    name : str
    opacity : float = field(default=1.0)
    visibility : bool = field(default=True)
    image : Image = field(default=None)
    x : int = field(default=0)
    y : int = field(default=0)

class phmImage(ABC):
    
    def __init__(self,
        filepath : str,
        title : str = None):
        # File path
        self.filepath = filepath
        # File name
        self.filename = os.path.basename(self.filepath)
        # Image title
        self.title = Path(self.filepath).stem if title is None else title
        # Image dimensions
        self.dimension = None
        # Properties
        self.properties = {
            'filepath' : self.filepath,
            'filename' : self.filename,
            'title' : self.title,
        }

    def __getitem__(self, key) -> Union[Dict, phmLayer] :
        res = None
        if key == 'properties':
            res = self.properties
        elif isinstance(key, str):
            res = self.load_layer(key)
        elif isinstance(key, numbers.Number):
            res = self.load_layer_by_index(key)
        return res
   
    def get_property(self, prop):
        if prop in self.properties:
            raise KeyError('Property %s not found' % prop)
        return self.properties[prop]
    
    def set_property(self, prop, value):
        self.properties[prop] = value
    
    @abstractmethod
    def load_layer(self, layer_name : str) -> phmLayer:
        pass
    
    @abstractmethod
    def load_layer_by_index(self, index : int) -> phmLayer:
        pass
    
    @abstractmethod
    def get_all_layers(self) -> Tuple[phmLayer]:
        pass

    @abstractmethod
    def get_layer_names(self) -> Tuple[str]:
        pass
    
    @abstractmethod
    def get_original_image(self):
        pass
    
    @property
    def layer_names(self) -> Tuple[str]:
        return self.get_layer_names()
    
    @property
    def original_image(self) -> Image:
        return self.get_original_image()

class InMemoryImage(phmImage):
    """!
    @brief The definition of in-memory data structure is determined here. The fields presenting the layers, original data, and metadata associated to the image.
    """
    def __init__(self,
        filepath : str,
        title : str = None,
        layers : List[phmLayer] = []
    ):
        super(phmImage, self).__init__(filepath, title)
        self.layers = layers
    
    def __getitem__(self, key):
        res = None
        if key == 'properties':
            res = self.properties[key]
        elif isinstance(key, str):
            res = self.__getlayer(key)
        elif isinstance(key, numbers.Number):
            res = self.__getlayer_index(key)
        return res
   
    def __getlayer_index(self, index : int):
        if len(self.layers) <= index or index < 0:
            raise IndexError('Layer index is out of range')
        return list(self.layers.items())[index]
    
    def __getlayer(self, name : str):
        if not name in self.layers:
            raise KeyError('the given layer name does not exist!')
        return self.layers[name]
    
    @property
    def original_layer(self):
        return self.layers['original']
    
    