
"""
yoyo66.handler.core contains all the base functionalities for file handlers
"""

import os.path
import random
import pathlib

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple, Any

from yoyo66.datastruct import phmImage

# List of file handlers
file_handlers = {}
# List of file extensions supported by the defined file handlers
__supported_file_extensions = []

def mmfile_handler(name : str, file_extensions : List[str]):
    """This decorator is used to introduce an implemented file handler to the library.
    In order to implement a file handler, the decorator is used on top of the implemented file handler
    that is inherited from ``BaseFileHandler`` class.

    Args:
        name (str): name of the file handler that the system use to call the handler
        file_extensions (List[str]): the supported file extensions

    Raises:
        TypeError : if the file extension is not supported but any of presented file handler.
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

def get_file_extensions(handler : str) -> List[str]:
    """Gets the file extensions supported by the specified file handlers.

    Args:
        handler (str): the name of file handler

    Raises:
        KeyError: if the specified file handler is not registered.

    Returns:
        str: the list of supported file extensions
    """
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

def list_handler_names() -> Tuple[str]:
    """ The list of file handlers' name

    Returns:
        Tuple[str]: list of registered file handlers's name
    """
    return tuple(file_handlers.keys())

class BaseFileHandler(ABC):
    """
    Base class for all file handlers
    """

    def __init__(self,
        filter : List[str] = None
    ) -> None:
        """
        Args:
            filter (List[str], optional): List of class names to load. Defaults to None.
        """
        super().__init__()

        # File extensions filled by the creator method
        self.file_extensions = []

        self.categories = {}
        if filter is None or not filter:
            self._enable_filter = False
        else:
            indexes = random.sample(range(0, 255), len(filter))
            for index in range(len(filter)):
                self.categories[filter[index]] = indexes[index]
            self._enable_filter = True

    def is_valid(self, filepath : str) -> bool:
        """Check if the file path is valid based on the file extension

        Args:
            filepath (str): The given file path of the multi-layer file

        Returns:
            bool: `True` if file extension is supported by this file handler
        """
        fext = pathlib.Path(filepath).suffix[1:]
        return fext in self.file_extensions

    def __call__(self, filepath : str, img : phmImage = None) -> Any:
        """A call function for saving and loading the images.
        if the `img` is None, the function acts as loading function and uses the `filepath` to load the multi-layer image.
        Otherwise, it uses the `filepath` to save the `img`.

        Args:
            filepath (str): The file path
            img (phmImage, optional): the multi-layer image. Defaults to None.

        Raises:
            ValueError: if the file extension does not supported by this file handler.

        Returns:
            Any: returns None if the function acts as the save function. Otherwise, it returns the loaded multi-layer image.
        """
        if not self.is_valid(filepath):
            raise ValueError("File extension is not supported by the selected file handler!")

        if img is None:
            # if the img field is None, it means the method uses the given path to load the multi-level imagery file.
            return self.load(filepath)
        else:
            # if the img field is given, it means the call method uses the given path to save the multi-level imagery file.
            self.save(img, filepath)

    def init_class_id(self, layer_name) -> int:
        if not layer_name in self.categories:
            if self._enable_filter:
                return None
            self.categories[layer_name] = random.randint(0, 255)
        return self.categories[layer_name]

    @abstractmethod
    def load(self, filepath : str, only_imgs : bool = False) -> phmImage:
        """Load a multi-layer image using the presented file path.

        Args:
            filepath (str): File path

        Returns:
            phmImage: Loaded multi-layer image
        """
        pass

    @abstractmethod
    def save(self, img : phmImage, filepath : str) -> None:
        """Save a multi-layer image in the specified file path.

        Args:
            img (phmImage): a multi-layer image
            filepath (str): the specified file path for saving the image
        """
        pass

def build_by_name(name : str, filter : List[str] = None) -> BaseFileHandler:
    """Build an instance of a file handler based on the given name

    Args:
        name (str): name of the file handler
        filter (List[str], optional): List of class names to load. Defaults to None.

    Raises:
        KeyError: if the given name is not a registered file handler

    Returns:
        BaseFileHandler: an instance of requested file handler
    """

    if not name in file_handlers:
        raise KeyError(f'{name} does not exist in file handlers!')

    # Instantiate the handler based on the given name
    handler = file_handlers[name][0](filter)
    # Initialize the file extensions associated with the handler!
    handler.file_extensions = file_handlers[name][1]
    return handler

def build_by_file_extension(ext : str, filter : List[str] = None) -> BaseFileHandler:
    """Build an instance of a file handler based on the given file extension

    Args:
        ext (str): the name of file extension
        filter (List[str], optional): List of class names to load. Defaults to None.

    Raises:
        KeyError: if the given name is not a registered file handler

    Returns:
        BaseFileHandler: an instance of requested file handler
    """
    
    name = None
    for nm, fxs in file_handlers.items():
        if ext in fxs[-1]:
            name = nm
            break

    if name is None: 
        raise KeyError(f'{ext} does not associated with any file handler')

    return build_by_name(name, filter)

def load_file(filepath : str, filter : List[str] = None) -> phmImage:
    """A quick access for loading a file based on its file extension.

    Args:
        filepath (str): file path of the multi-layer image file
        filter (List[str], optional): List of class names to load. Defaults to None.

    Raises:
        ValueError: if file does not exist

    Returns:
        phmImage: Loaded multi-layer image
    """
    
    if not os.path.isfile(filepath):
        raise ValueError(f'File is invalid: {filepath}')

    # Extract file extension of the given file
    ext = pathlib.Path(filepath).suffix[1:]
    # Loading the file handler based on the given file extension
    handler = build_by_file_extension(ext, filter)
    
    return handler.load(filepath)

