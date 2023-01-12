
import random

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple

from yoyo66.datastruct import phmImage

# List of file handlers
file_handlers = {}

def mmfile_handler(name, file_extensions : List[str]):
    """ 
    The decorator presenting the file handler

    Args:
        name (str): name of the file handler
    """
    def __embed_func(clss):
        global file_handlers

        if isinstance(clss, BaseFileHandler):
            file_handlers[name] = (clss, file_extensions)

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

    @abstractmethod
    def save(self, img : phmImage, file_path : str) -> None:
        pass

def build_by_name(name : str, categories : Dict[str, int]) -> BaseFileHandler:
    if name in file_handlers:
        raise KeyError(f'{name} does not exist in file handlers!')

    return file_handlers[name](categories)


def build_by_file_extension(ext : str) -> BaseFileHandler:
    name = None
    for nm, fxs in file_handlers.items():
        for x in fxs:
            if ext == x:
                name = nm
                break

    if name is None: 
        raise KeyError(f'{ext} does not associated with any file handler')

    return build_by_name(name)
