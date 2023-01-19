
import os.path
import random
import pathlib

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple, Any

from yoyo66.datastruct import phmImage

# List of file handlers
file_handlers = {}
__supported_file_extensions = []

def mmfile_handler(name, file_extensions : List[str]):
    """ 
    The decorator presenting the file handler

    Args:
        name (str): name of the file handler
    """
    def __embed_clss(clss):
        global file_handlers
        global __supported_file_extensions
        if issubclass(clss, BaseFileHandler):
            sts = False
            # Check if the file extension is already covered by another file handler
            for ex in file_extensions:
                if ex in __supported_file_extensions:
                    sts = True
            if sts:
                raise TypeError(f'file extensions associated to {name} are already covered by other file handlers')
            # Add the file extension field to the handler class
            file_handlers[name] = (clss, file_extensions) 

    return __embed_clss

def get_file_extensions(handler : str) -> str:
    global file_handlers
    if not handler in file_handlers:
        raise KeyError(f'{handler} does not supported!')
    return file_handlers[handler][-1]

def list_file_handlers() -> Tuple:
    """ List of file handlers registered using the defined decorator!

    Returns:
        Tuple: List of file handler
    """
    return file_handlers

def list_handler_names() -> Tuple:
    return tuple(file_handlers.keys())

class BaseFileHandler(ABC):
    """
    This is the base class for all file handlers
    """

    def __init__(self,
        categories : Union[Dict[str, int], List[str]]
    ) -> None:
        super().__init__()

        # File extensions filled by the creator method
        self.file_extensions = []
        # The field contains the determined categories and associated class id
        self.categories = {}
        # Check if it is a list, convert it to a dictionary
        if isinstance(categories, List):
            indexes = random.sample(range(0, 255), len(categories))
            for index in range(len(categories)):
                self.categories[categories[index]] = indexes[index]
        else:
            self.categories = categories

    def is_valid(self, filepath : str) -> bool:
        fext = pathlib.Path(filepath).suffix.replace('.', '')
        return fext in self.file_extensions

    def __call__(self, filepath : str, img : phmImage = None) -> Any:
        if not self.is_valid(filepath):
            raise ValueError("File extension is not supported by the selected file handler!")

        if img is None:
            # if the img field is None, it means the method uses the given path to load the multi-level imagery file.
            return self.load(filepath)
        else:
            # if the img field is given, it means the call method uses the given path to save the multi-level imagery file.
            self.save(img, filepath)
        
    @abstractmethod
    def load(self, filepath : str) -> phmImage:
        pass

    @abstractmethod
    def save(self, img : phmImage, filepath : str) -> None:
        pass

def build_by_name(name : str, categories : Union[Dict[str, int], List[str]]) -> BaseFileHandler:
    if not name in file_handlers:
        raise KeyError(f'{name} does not exist in file handlers!')

    # Instantiate the handler based on the given name
    handler = file_handlers[name][0](categories)
    # Initialize the file extensions associated with the handler!
    handler.file_extensions = file_handlers[name][1]
    return handler

def build_by_file_extension(ext : str, categories : Union[Dict[str, int], List[str]]) -> BaseFileHandler:
    name = None
    for nm, fxs in file_handlers.items():
        if ext in fxs[-1]:
            name = nm
            break

    if name is None: 
        raise KeyError(f'{ext} does not associated with any file handler')

    return build_by_name(name, categories)
