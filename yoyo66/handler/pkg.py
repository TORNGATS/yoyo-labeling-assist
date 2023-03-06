import zipfile
import json
import io
import os

import numpy as np

from functools import lru_cache
from PIL import Image
from PIL.TiffImagePlugin import IFDRational
from typing import Dict, List

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, BaseArchive, Layer, create_image, from_image

class PKGArchive(BaseArchive):

    __ORIG_DIR = 'archive'

    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
        self._handler = None

    def load(self):
        self._handler = zipfile.ZipFile(self.filepath, mode = 'a')

    def updateAndClose(self):
        self._handler.close()
    
    def check_path(self, path : str):
        flist = [x.filename for x in self._handler.infolist()]
        return path in flist

    def get_asset_list(self) -> List[str]:
        flist = []
        for fz in self._handler.infolist():
            fp = fz.filename
            if fp.startswith(self.__ORIG_DIR):
                flist.append(self._make_path(fp))
        return flist

    def get_assets(self) -> Dict[str, np.ndarray]:
        res = {}
        for f in self.get_asset_list():
            arr = self.get_asset(f)
            res[f] = arr
        return res

    def set_assets(self, assets : Dict[str, np.ndarray], overwrite : bool = False):
        for fp, arr in assets.items():
            self.set_asset(fp, arr, overwrite)

    def _make_abspath(self, path : str) -> str:
        gPath = '/'.join(path.split('.'))
        gPath = f'{gPath}.png'
        return os.path.join(self.__ORIG_DIR, gPath)
    
    def _make_path(self, fpath : str) -> str:
        fsec = fpath.split('/')[1:]
        fsec[-1] = fsec[-1].split('.')[0]
        return '.'.join(fsec)

    @lru_cache(maxsize = 3)
    def get_asset(self, path : str) -> np.ndarray:
        gPath = self._make_abspath(path)
        arr = None
        if self.check_path(gPath):
            with self._handler.open(gPath) as gfile:
                arr = np.array(Image.open(gfile))
        return arr

    def set_asset(self,
        path : str, 
        data : np.ndarray,
        overwrite : bool = False
    ):
        gPath = self._make_abspath(path)
        if self.check_path(gPath) and (not overwrite):
            raise KeyError(f'{path} already exist!')
        orig_io = io.BytesIO()
        Image.fromarray(data).save(orig_io, format='png')
        self._handler.writestr(gPath, orig_io.getvalue())
        orig_io.close()

class Exif_JSONEncoder(json.JSONEncoder):
    """A customized JSON encoder for dealing with Exif special types."""

    # overload method default
    def default(self, obj):
        if isinstance(obj, IFDRational):
            return float(obj)
        # Call the default method for other types
        return json.JSONEncoder.default(self, obj)

@mmfile_handler('pkg', ['pkg'])
class PKGFileHandler(BaseFileHandler): # Parham, Keven, Kevin, and Gabriel (PKG)
    """
    PKG file handler for loading and saving pkg files (*.pkg).
    """

    __METAINFO_FILE = 'meta.info'
    __PROP_FILE = 'properties.json'
    __METRICS_FILE = 'metrics.json'

    def __init__(self, filter : List[str] = None) -> None:
        super().__init__(filter)

    def load(self, filepath: str, only_imgs : bool = False) -> phmImage:
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
            # metadata (metadata is mandatory for loading the images)
            with pkg.open(self.__METAINFO_FILE) as f:
                metainfo = json.loads(f.read())
            if not only_imgs:
                # properties
                with pkg.open(self.__PROP_FILE) as f:
                    props = json.loads(f.read())
                # metrics
                with pkg.open(self.__METRICS_FILE) as f:
                    metrics = json.loads(f.read())
            # original image
            orig_file = pkg.open(metainfo['original']['file'])
            orig_img = np.asarray(Image.open(orig_file).convert("RGB"))
            metainfo.pop('original')
            # layers
            for layer_name, info in metainfo.items():

                class_id = self.init_class_id(layer_name)
                if class_id is None:
                    continue

                lfn = metainfo[layer_name]['file']
                lfile = pkg.open(f'layers/{lfn}')
                img = from_image(Image.open(lfile))
                layers.append(Layer(
                    name = layer_name,
                    opacity = metainfo[layer_name]['opacity'],
                    visibility = metainfo[layer_name]['visibility'],
                    image = img,
                    class_id = class_id))

        entity = phmImage(
            filepath = filepath,
            properties = props,
            metrics = metrics,
            orig_image = orig_img,
            layers = layers,
            archive = PKGArchive(filepath)
        )
        return entity

    def save(self, img: phmImage, filepath: str):
        """
        Save a multi-layer image as an pkg file

        Args:
            img (phmImage): Multi-layer image
            filepath (str): Path of openraster file
        """
        
        if os.path.exists(filepath) and img.archive is not None:
            with img.archive as ac:
                old_archives = ac.get_assets()
        else:
            old_archives = False

        with zipfile.ZipFile(filepath, mode = 'w') as pkg:
            img_list = {}
            # Save properties
            prop_dict = img.properties
            prop_dict['title'] = img.title
            for key, val in prop_dict.items():
                if isinstance(val, bytes):
                    prop_dict[key] = val.hex()

            prop = json.dumps(prop_dict, cls = Exif_JSONEncoder)
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
            # Create the layers folder
            zlayers = zipfile.ZipInfo('layers/')
            pkg.writestr(zlayers, '')
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
        
        # Save archive
        if old_archives:
            with img.archive as ac:
                ac.set_assets(old_archives, overwrite=True)
