

import os.path
from pathlib import Path
from typing import Dict, Any, List, Union

from yoyo66.handler import BaseFileHandler, build_by_file_extension, build_by_name

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
        if not self.source_handler.is_valid(source_file):
            raise ValueError('file %s is not valid' % source_file)
        # Loading the multi-layer imagery data from the source file
        img = self.source_handler(source_file)
        if img is None:
            raise ValueError('The coversion process is failed for file %s' % source_file)
        self.dest_handler(dest_file, img)
        
    def convert_dir(self, source_dir : str, dest_dir : str, lazy : bool = True) -> bool:
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
        if os.path.isdir(source_file):
            return self.convert_dir(source_file, dest_file, lazy)
        elif os.path.isfile(source_file):
            self.convert_file(source_file, dest_file)
        else:
            raise ValueError('provided filepaths are invalid!')

def build_converter(
    categories : Union[Dict[str, int], List[str]],
    src_handler : str = None,
    dest_handler : str = None,
    src_fextension : str = None,
    dest_fextension : str = None
) -> ConvertHandler:
    """Creates the proper converter based on given information.
    if src_handler is given, src_fextension will be ignored. Same case for dest_handler and dest_fextension/

    Args:
        categories (Union[Dict[str, int], List[str]]): _description_
        src_handler (str, optional): _description_. Defaults to None.
        dest_handler (str, optional): _description_. Defaults to None.
        src_fextension (str, optional): _description_. Defaults to None.
        dest_fextension (str, optional): _description_. Defaults to None.
    """
    
    src_obj = None
    dest_obj = None
    if src_obj is not None:
        src_obj = build_by_name(src_handler, categories)
    elif src_fextension is not None:
        src_obj = build_by_file_extension(src_fextension, categories)
    else:
        raise KeyError('The given file handler is not supported!')
    
    if dest_obj is not None:
        dest_obj = build_by_name(dest_handler, categories)
    elif src_fextension is not None:
        dest_obj = build_by_file_extension(dest_fextension, categories)
    else:
        raise KeyError('The given file handler is not supported!')
    
    return ConvertHandler(
        source_handler = src_obj,
        dest_handler = dest_obj
    )

def convert_file__(src_file : str, dest_file : str, categories : Union[Dict[str, int], List[str]]):
    src_ext = Path(src_file).suffix.replace('.', '')
    dest_ext = Path(dest_file).suffix.replace('.', '')
    
    build_converter(categories, src_fextension=src_ext, dest_fextension=dest_ext)(
        source_file = src_file,
        dest_file = dest_file
    )