

from pathlib import Path
from typing import Dict, List, Union

from yoyo66.handler import BaseFileHandler, file_handlers
from yoyo66.datastruct import phmImage

@file_handlers('gimp')
class GIMPFileHandler(BaseFileHandler):
    def __init__(self, 
        categories: Union[Dict[str, int], List[str]]
    ) -> None:
        super().__init__(categories)
    
    def read(filepath: str) -> phmImage:
        pass

    def write(img: phmImage, file_path: str):
        pass