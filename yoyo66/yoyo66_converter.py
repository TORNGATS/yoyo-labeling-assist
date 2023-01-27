
import os
import sys
import argparse
import json
import glob

from pathlib import Path
from progress.bar import Bar

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
    
    parser.add_argument('-i', '--input', type = str, help = 'Filepath to the input file/directory. in case of directory mode, the input is a filter string like /home/phm/d*.xcf.')
    parser.add_argument('-o', '--output', default = os.getcwd(), type = str, help = 'Filepath to the output file/directory.')
    parser.add_argument('-m', '--mode', default = 'file', choices = ['file', 'directory'], help = 'Determine the mode of given file/directory.')
    parser.add_argument('-t', '--type', nargs = '?', choices = list_handler_names(), help = 'Determine the targeted file type. The file type is only used when the output is a directory')
    parser.add_argument('-c', '--classnames', type = str, nargs='*', help = 'Specify the list of class labels.')
    parser.add_argument('-s', '--silent', action='store_true', help = 'Silent mode supress all raise exception.')
    parser.add_argument('--override', action='store_false', help = 'Override mode prevent conversion when the output file has already exist if not set.')
    
    args = parser.parse_args()
    
    if args.mode is None:
        print("'mode' must be specified!")
        return -1
    if args.input is None:
        print("input filepath must be specified!")
        return -1
    
    create_out_filepath = lambda fin, fout, type : os.path.join(fout, f'{Path(os.path.basename(fin)).stem}.{get_file_extensions(type)[0]}')
    
    files = []
    infile = args.input
    outfile = args.output

    if args.mode == 'file':
        if not os.path.isfile(args.input):
            print("input filepath is invalid!")
            return -1
        outfile = outfile if not os.path.isdir(outfile) else create_out_filepath(infile, outfile, args.type)
        files = [outfile]
        if not args.override and os.path.isfile(outfile):
            print("The output file has already exist")
            return 0
        convert_file__(infile, outfile, args.classnames)
    elif args.mode == 'directory':
        if not os.path.isdir(outfile):
            print("output field must be a directory path")
            return -1

        files = glob.glob(infile)
        
        with Bar(' Converting', max=len(files), suffix='%(percent)d%%') as bar:
            for fin in files:
                outfile = args.output
                bar.message = fin
                outfile = create_out_filepath(fin, outfile, args.type)
                try:
                    if not (not args.override and os.path.isfile(outfile)):
                        convert_file__(fin, outfile, args.classnames)
                        print(' Successful')
                except Exception as ex:
                    if not args.silent:
                        raise ex
                    print(' Failed')
                finally:
                    bar.next()

if __name__ == "__main__":
    main__()