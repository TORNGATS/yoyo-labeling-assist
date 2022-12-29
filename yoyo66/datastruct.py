
"""!
@file datastruct.py
@brief The in-memory data structure definition and all related utils.
@author Parham Nooralishahi
"""

# Imports
import os
import numbers

from pathlib import Path
from collections import namedtuple

Dimension = namedtuple('Dimension', ['width', 'height'])

class phmImage:
    """!
    @class phmImage
    @brief The definition of in-memory data structure is determined here. The fields presenting the layers, original data, and metadata associated to the image.
    """
    def __init__(self,
        filepath : str,
        title : str = None
    ):
        # File path
        self.filepath = filepath
        # File name
        self.filename = os.path.basename(self.filepath)
        # Image title
        self.title = Path(self.filepath).stem if title is None else title
        # Image dimensions
        self.dimension = None
        # Image layers
        self.layers = {}
        # Image metadata
        self.metadata = {
            'filepath' : self.filepath,
            'filename' : self.filename,
            'title' : self.title,
        }
    
    def __getitem__(self, key):
        res = None
        if key == 'metadata':
            res = self.metadata[key]
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
    
    