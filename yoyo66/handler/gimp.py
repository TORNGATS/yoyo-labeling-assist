
import numpy as np

from PIL import Image
from pathlib import Path
from typing import Dict, List, Union
from typing import Any, Callable, Dict, List
from gimpformats.gimpXcfDocument import GimpDocument

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer, ORIGINAL_LAYER_KEY, from_image

@mmfile_handler('gimp', ['xcf'])
class GIMPFileHandler(BaseFileHandler):
    """
    GIMP file handler for loading and saving gimp files (*.xcf).
    """

    __file_formats__ = ['jpg', 'jpeg', 'png', 'tiff', 'bmp']
    __gimp_extension = '.xcf'

    def __init__(self, categories: Union[Dict[str, int], List[str]]) -> None:
        super().__init__(categories)
    
    def load(self, filepath: str) -> phmImage:
        """Load the multi-layer image using the presented file path (gimp file).

        Args:
            filepath (str): the path to a gimp file

        Raises:
            ValueError: if file does not exist
            ValueError: if file extension does not supported by GIMP handler.

        Returns:
            phmImage: Loaded multi-layer image
        """
        # Argument initialization and checking
        if not Path(filepath).is_file():
            raise ValueError(message=f'The file ({filepath}) does not exist!')
        if not filepath.endswith(self.__gimp_extension):
            raise ValueError(message=f'The file format ({filepath}) is not supported!')
        #####################
        # Load the GIMP file
        gimp = GimpDocument(filepath)
        layers = gimp.textLayerFlags
        # Go through the layers
        orig_img = None
        layers = []
        for layer in gimp.layers:
            # Check if the layer is a group layers
            if not layer.isGroup:
                layer_name = layer.name
                fex = layer_name.split('.')[-1].lower()
                if fex in self.__file_formats__:
                    # Add the original layer
                    orig_img = np.asarray(layer.image)
                else:
                    img = layer.image
                    if img.mode in ("RGBA", "LA") or \
                        (img.mode == "P" and "transparency" in img.info):
                        if not layer_name in self.categories:
                            continue
                        
                        class_id = self.categories[layer_name]
                        limg = from_image(img)
                        if not layer_name in self.categories:
                            continue
                        layers.append(Layer(
                            name = layer_name,
                            class_id = class_id,
                            image = limg))
        return phmImage(
            filepath = filepath,
            properties = {},
            orig_image = orig_img,
            layers = layers
        )

    def save(self, img: phmImage, filepath: str):
        """Save a multi-layer image as a gimp file

        Args:
            img (phmImage): Multi-layer image
            filepath (str): Path of gimp file

        Raises:
            NotImplementedError: GIMP file handler does not support saving images.
        """
        raise NotImplementedError('Update feature is not implemented yet!')