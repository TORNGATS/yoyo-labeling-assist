
import numpy as np

from PIL import Image
from pathlib import Path
from typing import Dict, List, Union
from typing import Any, Callable, Dict, List
from gimpformats.gimpXcfDocument import GimpDocument

from yoyo66.handler import BaseFileHandler, file_handlers
from yoyo66.datastruct import phmImage, Layer, ORIGINAL_LAYER_KEY

@file_handlers('gimp')
class GIMPFileHandler(BaseFileHandler):

    __file_formats__ = ['jpg', 'jpeg', 'png', 'tiff', 'bmp']

    def __init__(self, categories: Union[Dict[str, int], List[str]]) -> None:
        super().__init__(categories)
    
    def load(self, filepath: str) -> phmImage:
        # Argument initialization and checking
        if not Path(filepath).is_file():
            raise ValueError(message=f'The file ({filepath}) does not exist!')
        if not filepath.endswith(".xcf"):
            raise ValueError(message=f'The file format ({filepath}) is not supported!')
        #####################
        # Load the GIMP file
        gimp = GimpDocument(filepath)
        layers = gimp.textLayerFlags
        # Go through the layers
        orig_img = None
        layers = []
        for layer in layers:
            # Check if the layer is a group layers
            if not layer.isGroup:
                layer_name = layer.name
                fex = layer_name.split('.')[-1].lower()
                if fex in self.__file_formats__:
                    # Add the original layer
                    orig_img = layer.image
                else:
                    img = layer.image
                    if img.mode in ("RGBA", "LA") or \
                        (img.mode == "P" and "transparency" in img.info):
                        channels = img.split()
                        img_ch = channels[-1].convert('1')
                        if not layer_name in self.categories:
                            continue
                        class_id = self.categories[layer_name]
                        limg = np.where(np.asarray(img_ch) != 0, 1, 0).astype(np.int8)
                        layers.append(Layer(
                            name = layer_name,
                            class_id = class_id,
                            image = limg
                        ))
        return phmImage(
            filepath = filepath,
            properties = {},
            orig_image = orig_img,
            layers = layers
        )

    def update(self, img: phmImage, file_path: str):
        raise NotImplementedError('Update feature is not implemented yet!')