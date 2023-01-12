
from typing import Dict, List, Union
from pyora import Project, TYPE_LAYER

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer, ORIGINAL_LAYER_KEY

@mmfile_handler('pkg')
class PKGFileHandler(BaseFileHandler): # Parham, Keven, and Gabriel (PKG)
    def __init__(self, categories: Union[Dict[str, int], List[str]]) -> None:
        pass
        