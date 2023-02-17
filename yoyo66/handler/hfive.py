
import h5py as hp
import numpy as np

from typing import List, Tuple, Dict, Any
from pathlib import Path

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer, create_image

@mmfile_handler('h5', ['h5'])
class H5FileHandler(BaseFileHandler):

    __H5_FILEEXTENSION = '.h5'
    __PROP_PREFIX = 'prop_'
    __METRICS_PREFIX = 'metric_'
    __LAYERS_KEY = 'layers'
    __ORIG_KEY = 'original'

    def __init__(self, filter: List[str] = None) -> None:
        super().__init__(filter)

    def __read_metadata(self, handler) -> Tuple[Dict, Dict]:
        metrics = {}
        props = {}
        for k, v in handler.attrs.items():
            if k.startswith(self.__PROP_PREFIX):
                key = k.replace(self.__PROP_PREFIX, '')
                props[key] = v
            elif k.startswith(self.__METRICS_PREFIX):
                key = k.replace(self.__METRICS_PREFIX, '')
                metrics[key] = v
        
        return props, metrics
    
    def __write_metadata(self, handler, 
        metrics : Dict[str, Any],
        props : Dict[str, Any]
    ):
        # Write the metrics
        for k, v in props.items():
            handler.attrs[f'{self.__PROP_PREFIX}{k}'] = v
        for k, v in metrics.items():
            handler.attrs[f'{self.__METRICS_PREFIX}{k}'] = v        

    def __layer_path(self, clss : str):
        return f'{self.__LAYERS_KEY}/{clss}'

    def load(self, filepath: str, only_imgs : bool = False) -> phmImage:
        # Argument initialization and checking
        if not Path(filepath).is_file():
            raise ValueError(message=f'The file ({filepath}) does not exist!')
        if not filepath.endswith(self.__H5_FILEEXTENSION):
            raise ValueError(message=f'The file format ({filepath}) is not supported!')
        #####################
        img = None
        with hp.File(filepath, mode = 'r') as fin:
            # Load metrics and properties
            props = metrics = {}
            if not only_imgs:
                props, metrics = self.__read_metadata(fin)
            # Load original layer
            if not self.__ORIG_KEY in fin.keys():
                raise KeyError('original layer is missing!')
            orig = np.array(fin[self.__ORIG_KEY])
            # Load mask layers
            layers = []
            layers_group = fin[self.__LAYERS_KEY]
            for layer_name in layers_group.keys():
                class_id = self.init_class_id(layer_name)
                if class_id is None:
                    continue
                layer = np.array(layers_group[layer_name])
                layers.append(Layer(
                    name = layer_name,
                    class_id = class_id,
                    image = layer
                ))
            img = phmImage(
                filepath = filepath,
                properties = props,
                metrics = metrics,
                orig_image = orig,
                layers = layers
            )
        
        return img

    def save(self, img: phmImage, filepath: str):
        with hp.File(filepath, mode = 'w') as fout:
            # Write the metrics and properties
            self.__write_metadata(fout, img.metrics, img.properties)
            # Write the original image
            orig = img.orig_layer.image
            fout.create_dataset(
                name = self.__ORIG_KEY,
                shape = orig.shape,
                dtype = orig.dtype,
                compression = 'gzip',
                compression_opts = 9,
                data = orig
            )
            # Write the layers
            for layer in img.layers:
                lname = layer.name
                limg = create_image(layer)
                limg = np.array(limg)
                fout.create_dataset(
                    name = self.__layer_path(lname),
                    shape = limg.shape,
                    dtype = limg.dtype,
                    data = limg,
                    compression = 'gzip',
                    compression_opts = 9,
                )

