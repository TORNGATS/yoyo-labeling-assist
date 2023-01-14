

import functools
import numbers
import os
from abc import ABC
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Union, Callable

import numpy as np

ORIGINAL_LAYER_KEY = 'original'

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

    # name (str) the name of layer 
    name : str
    # opacity (float) the opacity of the layer. Default 1.0
    opacity : float = field(default=1.0)
    # visibility (bool) determine whether the layer is hidden (False) or not (True). Default True
    visibility : bool = field(default=True)
    # Class identifier
    class_id : int = field(default=1)
    # image (PIL.Image) the imagery data of the layer. Default None
    image : np.ndarray = field(default=None)
    # x (int) the x position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    x : int = field(default=0)
    # y (int) the y position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    y : int = field(default=0)

    def is_valid(self) -> bool:
        """ Check if the layer is valid. The image is valid if the image field is initialized!

        Returns:
            bool: True if valid
        """
        return self.image is not None

    @property
    def dimension(self) -> Tuple[int, int]:
        """ Dimension of the layer

        Returns:
            Tuple[int, int]: The size of the layer (width, height)
        """
        return (self.image.shape[0], self.image.shape[1])

    @property
    def classmap(self):
        return self.image * self.class_id


class phmImage:
    """ 
    It is the base class for the multi-layer image.
    """
    
    def __init__(self,
        filepath : str,
        properties : Dict,
        orig_image : np.ndarray,
        layers : List[Layer],
        title : str = None,
        metrics : Dict = {}
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
            'title' : self.title,
            **properties
        }
        # Metrics
        self.metrics = metrics
        # Layers
        self.layers = layers
        # Original Layer
        self.orig_layer = Layer(
            name = ORIGINAL_LAYER_KEY,
            image = orig_image,
            x = 0, y = 0
        )
   
    def get_metric(self, key : str):
        if not key in self.metrics:
            raise KeyError('Metric %s not found' % prop)
        return self.metrics[key]

    def set_metric(self, key, value) -> None:
        self.metrics[key] = value

    def get_property(self, prop : str):
        if not prop in self.properties:
            raise KeyError('Property %s not found' % prop)
        return self.properties[prop]
    
    def set_property(self, prop, value) -> None:
        self.properties[prop] = value
    
    def get_layer(self, layer_name : str) -> Layer:
        resly = tuple(filter(lambda l : l.name == layer_name, self.layers))
        if len(resly) == 0:
             raise KeyError('%s layer does not exist!' % layer_name)

        return resly[0]
    
    def get_layer_by_index(self, index : int) -> Layer:
        if index >= len(self.layers) or index < 0:
            raise IndexError('Index %d does not exist' % index)
        
        return self.layers[index]

    def get_classmap(self, fusion_func : Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        layers = self.mask_layers
        ls = [l.classmap for l in layers]
        ls = np.dstack(ls)
        return fusion_func(ls)

    def get_dp_ready(self, fusion_func : Callable[[np.ndarray], np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        return (
            self.original_layer.image,
            self.get_classmap(fusion_func)
        )

    @property
    def classmap(self) -> np.ndarray:
        return self.get_classmap(lambda x : np.amax(x, axis = 2))

    @property
    def original_layer(self) -> Layer:
        return self.orig_layer
    
    @property
    def mask_layers(self) -> Tuple[Layer]:
        return tuple(self.layers)

    @property
    def layer_names(self) -> Tuple[str]:
        return self.get_layer_names()

    @property
    def dimension(self):
        return self.orig_layer.dimension

    @property
    def width(self):
        return self.dimension[0]

    @property
    def height(self):
        return self.dimension[1]

    @property
    def count_layers(self):
        return len(self.layers) + 1

    def __iter__(self):
        return iter(tuple([self.orig_layer]) + self.mask_layers)
    
    def __str__(self) -> str:
        return f'{self.title} (Layers : {self.count_layers}) [Dimension : {self.dimension}]'

    def __getitem__(self, key) -> Union[Dict, Layer] :
        res = None
        if key == 'properties':
            res = self.properties
        elif key == ORIGINAL_LAYER_KEY:
            res = self.orig_layer
        elif isinstance(key, str):
            res = self.get_layer(key)
        elif isinstance(key, numbers.Number):
            res = self.get_layer_by_index(key)
        else:
            raise ValueError('Key %s is invalid' % key)
        return res