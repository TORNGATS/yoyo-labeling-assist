
import os
import argparse
import json
import glob

from pathlib import Path

from yoyo66.handler import (
    GIMPFileHandler, 
    OpenRasterFileHandler, 
    PKGFileHandler,
    list_handler_names,
    get_file_extensions
)
from yoyo66.utils import convert_file__

def main__():
    parser = argparse.ArgumentParser(
        prog = 'YoYo-66 Converter',
        description = 'YoYo-66 Converter command line tool for working with multi-layer imagery datasets',
        epilog = 'TORNGATS @ 2023'
    )
    parser.print_help()
    
    parser.add_argument('-i', '--input', type = str, nargs = 1, help = 'Filepath to the input file/directory. in case of directory mode, the input is a filter string like /home/phm/d*.xcf.')
    parser.add_argument('-o', '--output', default = os.getcwd(), type = str, nargs = 1, help = 'Filepath to the output file/directory.')
    parser.add_argument('-m', '--mode', default = 'file', choices = ['file', 'directory'], help = 'Determine the mode of given file/directory.')
    parser.add_argument('-t', '--type', nargs = '?', choices = list_handler_names(), help = 'Determine the targeted file type. The file type is only used when the mode is set to directory')
    parser.add_argument('-c', '--categories', default = 'category.json', type = str, help = 'Specify the file (*.json) containing the categories and its associated class ids.')
    
    args = parser.parse_args()
    
    if args.mode is None:
        print("'mode' must be specified!")
        return -1
    if args.input is None:
        print("input filepath must be specified!")
        return -1
    if not os.path.isfile(args.input):
        print("input filepath is invalid!")
        return -1
    # Load categories file (json)
    if args.categories is None or not os.path.isfile(args.categories):
        print("categories must be specified! and the filepath needs to be valid")
        return -1
    categories = None
    with open(args.categories) as catfile:
        categories = json.load(catfile)
    
    create_out_filepath = lambda fin, fout, type : os.path.join(fout, f'{Path(os.path.basename(fin)).stem}.{get_file_extensions(type)[0]}')
    
    outfile = args.output
    if args.mode == 'file':
        outfile = outfile if not os.path.isdir(outfile) else create_out_filepath(args.input, outfile, args.type) 
        convert_file__(args.input, outfile, categories)
    elif args.mode == 'directory':
        if not os.path.isdir(args.output):
            print("output field must be a directory path")
        for fin in glob.glob(args.input):
            outfile = 
        

if __name__ == "__main__":
    main__()