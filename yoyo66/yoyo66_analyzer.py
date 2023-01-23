
import os
import sys
import argparse
import json
import glob
import csv

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
    get_file_extensions,
    load_file
)
from yoyo66.utils import convert_file__, calculate_stats

def main__():
    parser = argparse.ArgumentParser(
        prog = 'YoYo-66 Analyzer',
        description = 'YoYo-66 Analyzer command-line tool for providing dataset statistics',
        epilog = 'TORNGATS @ 2023'
    )
    parser.print_help()
    
    parser.add_argument('sourcepath', help = 'Search path for loading the multi-layer image files')
    parser.add_argument('-o', '--output', default = os.getcwd(), type = str, help = 'directory path for the result')
    parser.add_argument('-c', '--categories', default = 'category.json', type = str, help = 'Specify the file (*.json) containing the categories and its associated class ids.')
    parser.add_argument('-s', '--statsfile', type = str, default = None, help = 'The file containing list of files and associated profiles')
    
    args = parser.parse_args()
    
    # Load categories file (json)
    if args.categories is None or not os.path.isfile(args.categories):
        print("categories must be specified! and the filepath needs to be valid")
        return -1
    
    categories = None
    with open(args.categories) as catfile:
        categories = json.load(catfile)
    
    if not os.path.isdir(args.output):
        ValueError("output must be a directory")
    
    files = glob.glob(args.sourcepath)
    fieldnames, stats = calculate_stats(files, categories)
        
    result = {}
    if args.statsfile is not None and os.path.isfile(args.statsfile):
        with open(args.statsfile, mode='r') as fin:    
            reader = csv.DictReader(fin)
            records = list(reader)
            for r in records:
                result[r['Name']] = r
                
    
    # Write the per image stats
    with open(os.path.join(args.output, 'stats.csv'), mode='w') as fout:
        writer = csv.writer(fout, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        writer.writeheader()
        for sts in stats:
            writer.writerow(sts)
        
        