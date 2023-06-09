
import numpy as np
import json

from typing import List
from tifffile import TiffFile, TiffWriter, DATATYPE, PHOTOMETRIC

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer

@mmfile_handler('tiff', ['tif'])
class TiffFileHandler(BaseFileHandler):
    """
    Tiff file handler for loading and saving pkg files (*.tif).
    """

    __ORIGINAL_LAYER = 'Original'
    __METRIC_STARTKEY = 'metric_'

    def __init__(self, filter : List[str] = None) -> None:
        super().__init__(filter)

    def load(self, filepath: str, only_imgs : bool = False) -> phmImage:
        """Load the multi-layer image using the presented file path (tiff file).

        Args:
            filepath (str): the path to an tiff file

        Returns:
            phmImage: Loaded multi-layer image
        """

        orig_img = None
        properties = {}
        metrics = {}
        layers = []
        with TiffFile(filepath) as tif:
            for page in tif.pages:
                # Check if the layer is named!
                if not 'PageName' in page.tags:
                    continue
                layer_name = page.tags['PageName'].value
                # Load image data
                img = page.asarray()
                # Loading the original image
                if layer_name == self.__ORIGINAL_LAYER:
                    orig_img = img
                    # Loading metadata
                    metadata = json.loads(page.description)
                    for key, value in metadata.items():
                        if key.startswith(self.__METRIC_STARTKEY):
                            metrics[key.replace(self.__METRIC_STARTKEY, '')] = value
                        else:
                            properties[key] = value
                else:
                    class_id = self.init_class_id(layer_name)
                    if class_id is None:
                        continue
                    
                    img = np.max(np.asarray(img), axis=2) if len(img.shape) > 2 else img
                    img = np.where(img != 0, 1, 0).astype(np.int8)
                    layers.append(Layer(
                        name = layer_name,
                        class_id = class_id,
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
        """Save a multi-layer image as a tiff file

        Args:
            img (phmImage): Multi-layer image
            filepath (str): Path of tiff file
        """

        with TiffWriter(filepath) as tif:
            #  Save Original image
            metrics = {}
            for k, v in img.metrics.items():
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
                # dd = layer.classmap()
                dd = layer.classmap_rgba()
                tif.write(dd,
                    dtype = dd.dtype,
                    photometric = PHOTOMETRIC.RGB,
                    software = 'PHM',
                    compression = 'zlib',
                    extratags=[(285, DATATYPE.ASCII, len(layer.name), layer.name, False)]
                )
