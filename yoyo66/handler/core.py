
import random

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple

from yoyo66.datastruct import phmImage

# List of file handlers
file_handlers = []

def handler(name):
    """ the decorator presenting the file handler

    Args:
        name (str): name of the file handler
    """
    def __embed_func(clss):
        global file_handlers

        if isinstance(clss, BaseFileHandler):
            file_handlers[name] = clss

    return __embed_func

def list_file_handlers() -> Tuple:
    """ List of file handlers registered using the defined decorator!

    Returns:
        Tuple: List of file handler
    """
    return file_handlers

class BaseFileHandler(ABC):
    """
    This is the base class for all file handlers
    """

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

    @abstractmethod
    def load(self, filepath : str) -> phmImage:
        pass

    def save(self, img : phmImage, file_path : str) -> None:
        pass