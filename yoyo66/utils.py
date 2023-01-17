

import os.path
from pathlib import Path
from typing import Dict, Any

from yoyo66.handler import BaseFileHandler

class ConvertHandler:
    """
    The base class for handling conversion between multi-layer imagery file formats. 
    """
    
    def __init__(self,
        source_handler : BaseFileHandler,
        dest_handler : BaseFileHandler,
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
        if os.path.isdir(source_file) and os.path.isdir(dest_file):
            return self.convert_dir(source_file, dest_file, lazy)
        elif os.path.isfile(source_file) and os.path.isfile(dest_file):
            self.convert_file(source_file, dest_file)
        else:
            raise ValueError('provided filepaths are invalid!')