
import numpy as np
import json

from typing import Union, Dict, List
from tifffile import TiffFile, TiffWriter, DATATYPE, PHOTOMETRIC

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer, ORIGINAL_LAYER_KEY, create_image, from_image

@mmfile_handler('tiff', ['tif'])
class TiffFileHandler(BaseFileHandler):

    __ORIGINAL_LAYER = 'Original'
    __METRIC_STARTKEY = 'metric_'

    def __init__(self, categories: Union[Dict[str, int], List[str]]) -> None:
        super().__init__(categories)

    def load(self, filepath: str) -> phmImage:
        orig_img = None
        properties = {}
        metrics = {}
        layers = []
        with TiffFile(filepath) as tif:
            for page in tif.pages:
                # Check if the layer is named!
                if not 'PageName' in page.tags:
                    continue
                name = page.tags['PageName'].value
                # Load image data
                img = page.asarray()
                # Loading the original image
                if name == self.__ORIGINAL_LAYER:
                    orig_img = img
                    # Loading metadata
                    metadata = json.loads(page.description)
                    for key, value in metadata.items():
                        if key.startsWith(self.__METRIC_STARTKEY):
                            metrics[key.replace(self.__METRIC_STARTKEY, '')] = value
                        else:
                            properties[key] = value
                elif name in self.categories:
                    classid = self.categories[name]
                    img = np.where(np.asarray(img) != 0, 1, 0).astype(np.int8)
                    layers.append(Layer(
                        name = name,
                        class_id = classid,
                        image = img
                    ))

        return phmImage(
            filepath = filepath,
            properties = properties,
            orig_image = orig_img,
            layers = layers,
            metrics = metrics
        )


    def save(self, img: phmImage, filepath: str) -> None:
         with TiffWriter(filepath) as tif:
            #  Save Original image
            metrics = {}
            for k, v in img.metrics:
                metrics[f'{self.__METRIC_STARTKEY}{k}'] = v

            tif.write(img.orig_layer.image,
                dtype = img.orig_layer.image.dtype,
                photometric=PHOTOMETRIC.RGB,
                software = 'PHM',
                compression = 'zlib',
                metadata = {**img.properties, **metrics},
                extratags=[(285, DATATYPE.ASCII, len(self.__ORIGINAL_LAYER), self.__ORIGINAL_LAYER, False)]
            )
            # Save layers
            for layer in img.layers:
                dd = layer.classmap()
                tif.write(dd,
                    dtype = dd.dtype,
                    photometric = PHOTOMETRIC.MINISBLACK,
                    software = 'PHM',
                    compression = 'zlib',
                    extratags=[(285, DATATYPE.ASCII, len(layer.name), layer.name, False)]
                )
