
import os
import argparse

from yoyo66.handler import (
    GIMPFileHandler, 
    OpenRasterFileHandler, 
    PKGFileHandler,
    list_handler_names
)

def main__():
    parser = argparse.ArgumentParser(
        prog = 'YoYo-66 Converter',
        description = 'YoYo-66 Converter command line tool for working with multi-layer imagery datasets',
        epilog = 'TORNGATS @ 2023'
    )
    parser.print_help()
    
    parser.add_argument('-i', '--input', type = str, nargs = 1, help = 'Filepath to the input file/directory.')
    parser.add_argument('-o', '--output', default = os.getcwd(), type = str, nargs = 1, help = 'Filepath to the output file/directory.')
    parser.add_argument('-m', '--mode', default = 'file', choices = ['file', 'directory'], help = 'Determine the mode of given file/directory.')
    parser.add_argument('-t', '--filetype', nargs = '?', choices = list_handler_names(), help = 'Determine the targeted file type. The file type is only used when the mode is set to directory')
    
    args = parser.parse_args()
    
    if args.mode is None:
        print("'mode' must be specified!")
        return -1
    
    if args.mode == 'file':
        if args.input is None:
            print("input filepath must be specified!")
            return -1
        if not os.path.isfile(args.input):
            print("input filepath is invalid!")
            return -1
        if os.path.isdir(args.output):
            
            
        
        

if __name__ == "__main__":
    main__()