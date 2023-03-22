

import functools
import numbers
import os
from abc import ABC, abstractmethod
from PIL import Image
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Union, Callable, Any

import numpy as np

ORIGINAL_LAYER_KEY = 'original'

"""
Dimension is a entity class used to keep the dimension al values (width and height)
Dimension class has two main fields: width and height.
"""
Dimension = namedtuple('Dimension', ['width', 'height'])

@dataclass(init=False)
class Layer:
    """
    Layer is the class for mask layers inside a multi-layer image file.
    """

    # name (str) the name of layer 
    _name : str = field(repr=False, compare=True)
    # opacity (float) the opacity of the layer. Default 1.0
    opacity : float = field(default=1.0, compare=False)
    # visibility (bool) determine whether the layer is hidden (False) or not (True). Default True
    visibility : bool = field(default=True, compare=False)
    # Class identifier
    class_id : int = field(default=1, compare=False)
    # image (PIL.Image) the imagery data of the layer. Default None
    image : np.ndarray = field(default=None, compare=False)
    # x (int) the x position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    x : int = field(default=0, compare=False)
    # y (int) the y position of the layer. Normally it should be always zero but it can be non-zero in case the layer is smaller than the image size.
    y : int = field(default=0, compare=False)

    def __init__(self,
        name: str,
        opacity: float = 1,
        visibility: bool = True,
        class_id: int = 1,
        image: np.ndarray = None,
        x: int = 0,
        y: int = 0
    ) -> None:
        self.name = name
        self.opacity = opacity
        self.visibility = visibility
        self.class_id = class_id
        self.image = image
        self.x = x
        self.y = y

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name.strip().lower()

    def is_valid(self) -> bool:
        """ Check if the layer is valid. The image is valid if the image field is initialized!

        Returns:
            bool: True if valid
        """
        return self.image is not None

    def is_empty(self) -> bool:
        return np.sum(self.image)
    
    def get_stats(self) -> Dict[str, float]:
        """Provide statistics about the layer

        Returns:
            Dict[str, float]: Calculated statistics
        """
        total = self.dimension[0] * self.dimension[1]
        if total == 0: 
            total = 1
        dcount = np.sum(self.image)
        return {
            'pixcount' : dcount,
            'total' : total,
            'cover' : (dcount / total) * 100
        }

    def classmap(self) -> np.ndarray:
        """Calculate class map of the layer. The class map uses the mask and the classid to create class map.

        Returns:
            numpy.ndarray: classmap
        """
        return self.image * self.class_id
    
    def classmap_rgb(self) -> np.ndarray:
        return np.array(Image.fromarray(self.classmap().astype('uint8')).convert('RGB'))
    
    def classmap_rgba(self) -> np.ndarray:
        img = self.classmap().astype('uint8')
        alpha = np.zeros(img.shape)
        alpha = np.where(img > 0, 255, 0)
        
        pilimg = Image.fromarray(img).convert('RGBA')
        pilimg.putalpha(Image.fromarray(alpha.astype('uint8')).convert('L'))
        
        # return np.array(Image.fromarray(self.classmap().astype('uint8')).convert('RGBA'))
        return np.array(pilimg)
    
    @property
    def dimension(self) -> Tuple[int, int]:
        """ Dimension of the layer

        Returns:
            Tuple[int, int]: The size of the layer (width, height)
        """
        return (self.image.shape[0], self.image.shape[1])

def from_image(img : Image) -> np.ndarray:
    """Convert a ``PIL.Image`` to ``numpy.ndarray`` presenting the layer.

    Args:
        img (Image): the image

    Returns:
        np.ndarray: the matrix presenting the image.
    """

    channels = img.split()
    # Extract transparency channel
    img_ch = channels[-1].convert('1')
    return np.where(np.asarray(img_ch) != 0, 1, 0).astype(np.int8)

def create_image(layer : Layer) -> Image:
    img = Image.fromarray(layer.classmap(), mode = 'L')

    # Add alpha channel to the image.
    alpha = np.where(layer.image != 0, 255, 0).astype(np.int8)
    alpha = Image.fromarray(alpha, mode = 'L')
    img.putalpha(alpha)
    return img

def default_create_blendimage_func(orig : np.ndarray, layers : List[np.ndarray]) -> Image:
    """the default function for blending layers

    Args:
        orig (np.ndarray): the original image
        layers (List[np.ndarray]): the layers

    Returns:
        Image: the blended image
    """

    lorig = Image.fromarray(orig).convert('RGBA')
    lorig.putalpha(255)
    result = lorig
    if layers is not None and layers:
        # Create the blended layers
        merged = np.dstack(layers)
        # The layers are blended together and their priority is based on their class ids, 
        # So bigger class ids will be preferred pixel by pixel.
        # It is assumed that the layers have one color channel
        blayer = np.max(merged, axis = 2)
        alpha = np.where(blayer != 0, 255, 0).astype(np.int8)
        
        blayer = Image.fromarray(blayer, mode = 'L')
        alpha = Image.fromarray(alpha, mode = 'L')
        blayer.putalpha(alpha)

        result = Image.alpha_composite(lorig, blayer.convert('RGBA'))
    return result

class BaseArchive(ABC):
    def __init__(self, filepath : str) -> None:
        self.filepath = filepath
    
    def __enter__(self):
        self.load()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.updateAndClose()

    def __setitem__(self, 
        path : str, 
        data : np.ndarray
    ):
        self.set_asset(path, data)

    def __getitem__(self, path : str) -> np.ndarray:
        return self.get_asset()

    @abstractmethod
    def set_assets(self, assets : Dict[str, np.ndarray]):
        pass

    @abstractmethod
    def get_assets(self) -> Dict[str, np.ndarray]:
        pass

    @abstractmethod
    def get_asset_list(self) -> List[str]:
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def updateAndClose(self):
        pass

    @abstractmethod
    def get_asset(self, path : str) -> np.ndarray:
        pass

    @abstractmethod
    def set_asset(self,
        path : str, 
        data : np.ndarray
    ):
        pass

class phmImage:
    """ 
    It is the class for the multi-layer image.
    """
    
    def __init__(self,
        filepath : str,
        properties : Dict,
        orig_image : np.ndarray,
        layers : List[Layer] = [],
        title : str = None,
        metrics : Dict = {},
        archive : BaseArchive = None
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
        # Archive
        self.archive = archive

    def update_from(self, img, only_layers : bool = False):
        # Update layers
        self.layers = list(img.layers)
        if not only_layers:
            # Update properties
            self.properties.update(img.properties)
            # Update metrics
            self.metrics.update(img.metrics)

    def get_stats(self):
        """Provides statistics about the multi-layer image

        Args:
            categories (Dict[str, int]): the categories of interest
        """
        lstats = {}
        defects = []
        # Layers statistics
        for layer in self.layers:
            sts = layer.get_stats()
            if sts['pixcount'] == 0:
                continue
            defects.append(layer.name)
            for k,v in sts.items():
                lstats[f'{layer.name.title()} {k.title()}'] = v
        # Image statistics
        ls = np.dstack([l.image for l in self.layers])
        ls = np.max(ls, axis = 2)
        mask_cover = (np.sum(ls) / (self.dimension[0] * self.dimension[1])) * 100    
        return {
            **lstats,
            'Name' : self.title,
            'Mask Cover' : mask_cover,
            'Defects' : ','.join(map(str, set(defects))) 
        }

    def get_metric(self, key : str) -> Any:
        """Returning the metric stored inside the multi-layer image

        Args:
            key (str): Metric name

        Raises:
            KeyError: if metric does not exist

        Returns:
            Any: Value associated to metric name
        """
        if not key in self.metrics:
            raise KeyError('Metric %s not found' % key)
        return self.metrics[key]

    def set_metric(self, key : str, value : Any) -> None:
        """Setting a metric

        Args:
            key (str): metric name
            value (Any): metric value
        """
        self.metrics[key] = value

    def get_property(self, prop : str) -> Any:
        """Returning the property stored inside the multi-layer image

        Args:
            prop (str): property name

        Raises:
            KeyError: if property does not exist 

        Returns:
            Any: Value associated to property name
        """
        if not prop in self.properties:
            raise KeyError('Property %s not found' % prop)
        return self.properties[prop]
    
    def set_property(self, prop : str, value) -> None:
        """Setting a property

        Args:
            prop (str): property name
            value (Any): property value
        """

        self.properties[prop] = value
    
    def get_layer(self, layer_name : str) -> Layer:
        """Getting a layer based on the given name.

        Args:
            layer_name (str): Layer's name

        Raises:
            KeyError: if layer name does not exist

        Returns:
            Layer: The layer associated to the layer's name
        """

        resly = tuple(filter(lambda l : l.name == layer_name, self.layers))
        if len(resly) == 0:
             raise KeyError('%s layer does not exist!' % layer_name)

        return resly[0]
    
    def get_layer_by_index(self, index : int) -> Layer:
        """Getting a layer based on its index

        Args:
            index (int): Index of the requested layer

        Raises:
            IndexError: if the index is invalid

        Returns:
            Layer: The layer associated to the layer's index
        """

        if index >= len(self.layers) or index < 0:
            raise IndexError('Index %d does not exist' % index)
        
        return self.layers[index]

    def get_classmap(self, fusion_func : Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        """Getting classmap based on the given blending function.

        Args:
            fusion_func (Callable[[np.ndarray], np.ndarray]): blending function

        Returns:
            np.ndarray: classmap resulted by applying blending function on the multi-layer image
        """

        layers = self.mask_layers
        ls = [l.classmap() for l in layers]
        ls = np.dstack(ls)
        return fusion_func(ls)

    def get_dp_ready(self, fusion_func : Callable[[np.ndarray], np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Getting a data item ready to use in deep learning application

        Args:
            fusion_func (Callable[[np.ndarray], np.ndarray]): blending function

        Returns:
            Tuple[np.ndarray, np.ndarray]: a tuple containing the original image and target class map
        """

        return (
            self.original_layer.image,
            self.get_classmap(fusion_func)
        )

    def classmap(self) -> np.ndarray:
        """Calculating class map using default blending function

        Returns:
            np.ndarray: class map representing the class map using the given categories
        """
        return self.get_classmap(lambda x : np.amax(x, axis = 2))
    
    def classmap_rgb(self) -> np.ndarray:
        return np.array(Image.fromarray(self.classmap().astype('uint8')).convert('RGB'))
        
    def blended_image(self, 
        blending_func : Callable[[np.ndarray, List[np.ndarray]], Any] = default_create_blendimage_func
    ) -> Image:
        """Render a blended version of the multi-layer image

        Args:
            blending_func (Callable[[np.ndarray, List[np.ndarray]], Any], optional): blending function. Defaults to default_create_blendimage_func.

        Returns:
            Image: _description_
        """

        orig = self.original_layer.image
        layers = list(map(lambda x : x.classmap(), self.layers))
        return blending_func(orig, layers)
    
    def thumbnail(self, size : Tuple[int,int] = (400,350)) -> Image:
        """Making thumbnail of the multi-layer image

        Args:
            size (Tuple[int,int], optional): Size of thumbnail image. Defaults to (400,350).

        Returns:
            Image: thumbnail version of the image
        """

        img = self.blended_image()
        img.thumbnail(size)
        return img

    def to_img_dict(self) -> Dict[str, np.ndarray]:
        """Provides a dictionary representation of the multi-layer image where original image and layers are packed.

        Returns:
            Dict[str, np.ndarray]: image and the layers packed as a dictionary
        """
        result = {'Original': self.original_layer.image}
        for layer in self.layers:
            result[layer.name] = layer.image
        
        return result

    def get_layer_names(self) -> Tuple[str]:
        """Provides the layer names

        Returns:
            Tuple[str]: layer names.
        """
        return [layer.name for layer in self.layers]

    @property
    def original_layer(self) -> Layer:
        """Original layer of the multi-layer image

        Returns:
            Layer: an instance of the original layer
        """
        return self.orig_layer
    
    @property
    def mask_layers(self) -> Tuple[Layer]:
        """List of mask layer

        Returns:
            Tuple[Layer]: List of masks
        """
        return tuple(self.layers)

    @property
    def layer_names(self) -> Tuple[str]:
        """Getting a list of mask layers in the multi-layer image

        Returns:
            Tuple[str]: List of mask layers
        """
        return tuple(self.get_layer_names())

    @property
    def dimension(self) -> Tuple[int,int]:
        """Getting the dimension of multi-layer image

        Returns:
            Tuple[int,int]: the size of multi-layer image
        """
        return self.orig_layer.dimension

    @property
    def width(self) -> int:
        """Width of the multi-layer image

        Returns:
            int: Width of the multi-layer image
        """
        return self.dimension[1]

    @property
    def height(self) -> int:
        """Height of the multi-layer image

        Returns:
            int: Height of the multi-layer image
        """
        return self.dimension[0]

    @property
    def count_layers(self) -> int:
        """Getting the number of mask and original layers 

        Returns:
            int: number of layers (mask and original)
        """
        return len(self.layers) + 1

    def __iter__(self):
        """Getting an iterator for surveying layers in the multi-layer image

        Returns:
            iter: iterator
        """
        return iter(tuple([self.orig_layer]) + self.mask_layers)
    
    def __str__(self) -> str:
        """Returing the string representation of multi-layer image"""
        return f'{self.title} (Layers : {self.count_layers}) [Dimension : {self.dimension}]'

    def __getitem__(self, key : str) -> Union[Dict, Layer] :
        """Getting an entity from multi-layer image

        Args:
            key (str): the name of the entity

        Raises:
            ValueError: if the entity does not exist

        Returns:
            Union[Dict, Layer]: layer if the `key` is a layer name and properties if key is `properties`.
        """
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
