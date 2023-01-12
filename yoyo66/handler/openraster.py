
import numpy as np

from PIL import Image
from pathlib import Path
from typing import Dict, List, Union
from pyora import Project, TYPE_LAYER

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer, ORIGINAL_LAYER_KEY

@mmfile_handler('openraster')
class OpenRasterFileHandler(BaseFileHandler):

    __ora_extension = '.ora'
    __ORIG_LAYER_KEY = '/original'
    __LAYERS_KEY = '/layers'
    __PROPERTIES_KEY = 'prop_'
    __METRICS_KEY = 'metrics_'

    def __init__(self, categories: Union[Dict[str, int], List[str]]) -> None:
        super().__init__(categories)
    
    def load(self, filepath: str) -> phmImage:
        # Argument initialization and checking
        if not Path(filepath).is_file():
            raise ValueError(message=f'The file ({filepath}) does not exist!')
        if not filepath.endswith(self.__ora_extension):
            raise ValueError(message=f'The file format ({filepath}) is not supported!')
        #####################
        # Load the OpenRaster file
        project = Project.load(filepath)
        # Layer containing original layer
        if not self.__ORIG_LAYER_KEY in project or \
            not self.__LAYERS_KEY in project:
            raise ValueError('Invalid file format %s' % filepath)
        
        orig_img = project[self.__ORIG_LAYER_KEY]
        # Extract Properties
        props = {}
        metrics = {}
        for it in orig_img.raw_attributes.items():
            if it[0].startswith(self.__PROPERTIES_KEY):
                pkey = it[0].replace(self.__PROPERTIES_KEY, '')
                props[pkey] = it[1]
            elif it[0].startswith(self.__METRICS_KEY):
                pkey = it[0].replace(self.__METRICS_KEY, '')
                metrics[pkey] = it[1]

        # Mask Layers
        mask_layers = []
        layers = project['/layers']
        for layer in layers.children:
            if layer.type == TYPE_LAYER:
                layer_name = layer.name
                img = layer.image
                if img.mode in ("RGBA", "LA") or \
                    (img.mode == "P" and "transparency" in img.info):
                    channels = img.split()
                    img_ch = channels[-1].convert('1')
                    if not layer_name in self.categories:
                        continue
                    class_id = self.categories[layer_name]
                    limg = np.where(np.asarray(img_ch) != 0, 1, 0).astype(np.int8)
                    mask_layers.append(Layer(
                        name = layer['name'],
                        opacity = layer['opacity'],
                        visibility = layer['visibility'],
                        image = np.asarray(limg),
                        class_id = class_id,
                        x = layer.offsets[0], y = layer.offsets[1]
                    ))
        
        return phmImage(
            filepath = filepath,
            properties = props,
            metrics = metrics,
            orig_image = np.asarray(orig_img.image),
            layers = mask_layers
        )

    def save(self, img: phmImage, file_path: str):
        dim = img.dimension
        project = Project.new(width = img.width, height = img.height)
        # Create original layer
        orig_layer = project.add_layer(Image.fromarray(img.orig_layer.image), self.__ORIG_LAYER_KEY)
        # Add properties
        for k, v in img.properties.items():
            orig_layer.raw_attributes[self.__PROPERTIES_KEY + k] = v
        # Add Metrics
        for k, v in img.metrics.items():
            orig_layer.raw_attributes[self.__METRICS_KEY + k] = v
        # Add Layers
        masks = project.add_group(path=self.__LAYERS_KEY)
        for layer in img.layers:
            img = Image.fromarray(layer.image.astype(np.uint8), 'L')
            masks.add_layer(
                image = img,
                name = layer.name,
                offsets = (layer.x, layer.y),
                opacity = layer.opacity,
                visible = layer.visibility
            )
        
        project.save(file_path)