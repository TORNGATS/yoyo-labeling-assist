
import random

from abc import ABC
from typing import Dict, List, Union

from yoyo66.datastruct import phmImage

file_handlers = []

def handler(name):
    def __embed_func(clss):
        global file_handlers

        if isinstance(clss, )
        file_handlers[name] = clss

    return __embed_func

def list_file_handlers():
    return file_handlers

class BaseFileHandler(ABC):
    def __init__(self,
        categories : Union[Dict[str, int], List[str]]
    ) -> None:
        super().__init__()
        
        self.categories = {}
        # Check if it is a list, convert it to a dictionary
        if isinstance(categories, List):
            indexes = random.sample(range(0, 255), len(categories))
            for index in range(len(categories)):
                self.categories[categories[index]] = indexes[index]
        else:
            self.categories = categories

    
    def read(filepath : str) -> phmImage:
        pass

    def write(img : phmImage, file_path : str) -> None:
        pass