

import csv
import glob
import os.path
import numpy as np

from pathlib import Path
from typing import Dict, Any, List, Union, Tuple

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from yoyo66.handler import BaseFileHandler, build_by_file_extension, build_by_name
from yoyo66.handler import (
    GIMPFileHandler, 
    OpenRasterFileHandler, 
    PKGFileHandler,
    list_handler_names,
    get_file_extensions,
    load_file
)
from yoyo66.datastruct import phmImage

class ConvertHandler:
    """
    The base class for handling conversion between multi-layer imagery file formats. 
    """
    
    def __init__(self,
        source_handler : BaseFileHandler,
        dest_handler : BaseFileHandler
    ) -> None:
        self.source_handler = source_handler
        self.dest_handler = dest_handler
    
    def convert_file(self, source_file : str, dest_file : str) -> None:
        """Convert a file `source_file` to a destination format

        Args:
            source_file (str): source file
            dest_file (str): destination file

        Raises:
            ValueError: if source file is invalid
            ValueError: if the multi-layer image is failed to load
        """
        if not self.source_handler.is_valid(source_file):
            raise ValueError('file %s is not valid' % source_file)
        # Loading the multi-layer imagery data from the source file
        img = self.source_handler(source_file)
        if img is None:
            raise ValueError('The coversion process is failed for file %s' % source_file)
        self.dest_handler(dest_file, img)
        
    def convert_dir(self, source_dir : str, dest_dir : str, lazy : bool = True) -> Any:
        """Convert all files inside a directory to a destination formation

        Args:
            source_dir (str): source directory (search string). Read ``glob.glob`` for more information.
            dest_dir (str): destination directory
            lazy (bool, optional): Determine if it loads all multi-layer images or one by one. Defaults to True.

        Raises:
            ValueError: if source or destination directory are invalid

        Returns:
            Any: a list containing the result of conversion

        Yields:
            Iterator[Any]: an iterator if `lazy` is True. Presenting the lazy version of conversion process
        """
        if not os.path.isdir(source_dir) or not os.path.isdir(dest_dir):
            raise ValueError('given paths must be directories')
        
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        search_str = os.path.join(source_dir, '*.%s' % self.source_handler.file_extensions)
        
        def __convert_iter():
            for file in search_str:
                fstat = True
                dest_file = os.path.join(dest_dir, os.path.basename(file))
                try:
                    self.convert_file(file, dest_file)
                except Exception:
                    fstat = False
                yield fstat
        
        citer = __convert_iter()
        return citer if lazy else list(citer)
            
    def __call__(self, source_file : str, dest_file : str, lazy : bool = False) -> Any:
        """Conversion process. It automatically decides if it would be a directory or file conversion.

        Args:
            source_file (str): source path (file or directory (search string))
            dest_file (str): destination directory
            lazy (bool, optional): lazy process setting. Defaults to False.

        Raises:
            ValueError: if source path is invalid.

        Returns:
            Any: the result of conversion
        """
        if os.path.isdir(source_file):
            return self.convert_dir(source_file, dest_file, lazy)
        elif os.path.isfile(source_file):
            self.convert_file(source_file, dest_file)
        else:
            raise ValueError('provided filepaths are invalid!')

def build_converter(
    filter : List[str] = None,
    src_handler : str = None,
    dest_handler : str = None,
    src_fextension : str = None,
    dest_fextension : str = None
) -> ConvertHandler:
    """Creates the proper converter based on given information.
    if src_handler is given, src_fextension will be ignored. Same case for dest_handler and dest_fextension/

    Args:
        categories (Union[Dict[str, int], List[str]]): the categories containing the class name and associated class id
        src_handler (str, optional): the file handler for source files. Defaults to None.
        dest_handler (str, optional): the file handler for destination file conversion. Defaults to None.
        src_fextension (str, optional): the file extension of source files. Defaults to None.
        dest_fextension (str, optional): the file extension of destination files. Defaults to None.
    """
    
    src_obj = None
    dest_obj = None
    if src_obj is not None:
        src_obj = build_by_name(src_handler, filter)
    elif src_fextension is not None:
        src_obj = build_by_file_extension(src_fextension, filter)
    else:
        raise KeyError('The given file handler is not supported!')
    
    if dest_obj is not None:
        dest_obj = build_by_name(dest_handler, filter)
    elif src_fextension is not None:
        dest_obj = build_by_file_extension(dest_fextension, filter)
    else:
        raise KeyError('The given file handler is not supported!')
    
    return ConvertHandler(
        source_handler = src_obj,
        dest_handler = dest_obj
    )

def convert_file__(src_file : str, dest_file : str, filter : List[str] = None):
    """Wrapping function for converting files.

    Args:
        src_file (str): source file path
        dest_file (str): destination file path
        filter (List[str]): List of classes to be considered
    """
    src_ext = Path(src_file).suffix[1:]
    dest_ext = Path(dest_file).suffix[1:]
    
    build_converter(filter, src_fextension=src_ext, dest_fextension=dest_ext)(
        source_file = src_file,
        dest_file = dest_file
    )

def calculate_stats(files : List[str], filter : List[str] = None) -> Tuple[Tuple[str], List[Dict[str, int]]]:
    """Calculate statistics for the multi-layer imagery files.

    Args:
        files (List[str]): List of multi-layer imagery files
        filter (List[str], optional): filter categories. Defaults to None.

    Yields:
        Iterator[Tuple[Tuple[str], List[Dict[str, int]]]]:  a tuple containing the list of fields and a dictionary of statistics name and their values.
    """
    
    for fin in files:
        img = load_file(fin, filter)
        sts = img.get_stats()
        yield list(sts.keys()), sts

def create_from_image(filepath : str) -> phmImage:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f'{filepath} does not exist!')
    
    img = Image.open(filepath)
    exif = img.getexif()
    properties = {}
    
    if exif is not None:
        for key, val in exif.items():
            tag = TAGS.get(key)
            if tag is not None:
                properties[tag] = val
        for key, val in exif.items():
            tag = GPSTAGS.get(key)
            if tag is not None:
                properties[tag] = val

    return phmImage(
        filepath = filepath,
        properties = properties,
        orig_image = np.array(img),
        layers = []
    )