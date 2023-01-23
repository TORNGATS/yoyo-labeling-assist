
import zipfile
import json
import io
import numpy as np

from PIL import Image
from typing import Dict, List, Union
from pyora import Project, TYPE_LAYER

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer, ORIGINAL_LAYER_KEY, create_image, from_image

@mmfile_handler('pkg', ['pkg'])
class PKGFileHandler(BaseFileHandler): # Parham, Keven, and Gabriel (PKG)
    """
    PKG file handler for loading and saving pkg files (*.pkg).
    """


    __METAINFO_FILE = 'meta.info'
    __PROP_FILE = 'properties.json'
    __METRICS_FILE = 'metrics.json'

    def __init__(self, categories: Union[Dict[str, int], List[str]]) -> None:
        super().__init__(categories)
        
    def load(self, filepath: str) -> phmImage:
        """Load the multi-layer image using the presented file path (pkg file).

        Args:
            filepath (str): the path to an openraster file

        Returns:
            phmImage: Loaded multi-layer image
        """
        
        metainfo = {}
        props = {}
        metrics = {}
        orig_img = None
        layers = []
        with zipfile.ZipFile(filepath, mode = 'r') as pkg:
            # metadata
            with pkg.open(self.__METAINFO_FILE) as f:
                metainfo = json.loads(f.read())
            # properties
            with pkg.open(self.__PROP_FILE) as f:
                props = json.loads(f.read())
            # metrics
            with pkg.open(self.__METRICS_FILE) as f:
                metrics = json.loads(f.read())
            # original image
            orig_file = pkg.open(metainfo['original']['file'])
            orig_img = np.asarray(Image.open(orig_file))
            metainfo.pop('original')
            # layers
            for lname, info in metainfo.items():
                if not lname in self.categories:
                    continue
                class_id = self.categories[lname]
                lfn = metainfo[lname]['file']
                lfile = pkg.open(f'layers/{lfn}')
                img = from_image(Image.open(lfile))
                layers.append(Layer(
                    name = lname,
                    opacity = metainfo[lname]['opacity'],
                    visibility = metainfo[lname]['visibility'],
                    image = img,
                    class_id = class_id))

        return phmImage(
            filepath = filepath,
            properties = props,
            metrics = metrics,
            orig_image = orig_img,
            layers = layers
        )

    def save(self, img: phmImage, filepath: str):
        """Save a multi-layer image as an pkg file

        Args:
            img (phmImage): Multi-layer image
            filepath (str): Path of openraster file
        """

        with zipfile.ZipFile(filepath, mode = 'w') as pkg:
            img_list = {}
            # Save properties
            prop_dict = img.properties
            prop_dict['title'] = img.title
            prop = json.dumps(prop_dict)
            pkg.writestr(self.__PROP_FILE, prop)
            # Save metrics
            mtr = json.dumps(img.metrics)
            pkg.writestr(self.__METRICS_FILE, mtr)
            # Save original image
            img_list['original'] = {
                'file' : f'{img.title}.png',
                'opacity' : img.orig_layer.opacity,
                'visibility' : img.orig_layer.visibility
            }
            orig_io = io.BytesIO()
            Image.fromarray(img.orig_layer.image).save(orig_io, format='png')
            pkg.writestr(f'{img.title}.png', orig_io.getvalue())
            orig_io.close()
            # Save thumbnail
            thumbnail = img.thumbnail()
            orig_io = io.BytesIO()
            thumbnail.save(orig_io, format='png')
            pkg.writestr('thumbnail.png', orig_io.getvalue())
            orig_io.close()
            # Save Layers
            for layer in img.layers:
                img_list[layer.name] = {
                    'file' : f'{layer.name}.png',
                    'opacity' : layer.opacity,
                    'visibility' : layer.visibility
                }
                layer_io = io.BytesIO()
                create_image(layer).save(layer_io, format='png')
                pkg.writestr(f'layers/{layer.name}.png', layer_io.getvalue(), zipfile.ZIP_DEFLATED)
                layer_io.close()
            # Save metadata
            pkg.writestr(self.__METAINFO_FILE, json.dumps(img_list))