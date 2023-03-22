
import os
import sys
import argparse
import glob
import csv

from pathlib import Path
from progress.bar import Bar

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.utils import calculate_stats

def main__():
    parser = argparse.ArgumentParser(
        prog = 'YoYo-66 Analyzer',
        description = 'YoYo-66 Analyzer command-line tool for providing dataset statistics',
        epilog = 'TORNGATS @ 2023'
    )
    parser.print_help()
    
    parser.add_argument('sourcepath', help = 'Search path for loading the multi-layer image files')
    parser.add_argument('-o', '--output', default = os.getcwd(), type = str, help = 'directory path for the result')
    parser.add_argument('-c', '--classnames', type = str, nargs='*', help = 'Specify the list of class labels.')
    parser.add_argument('-s', '--statsfile', type = str, default = None, help = 'The file containing list of files and associated profiles')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.output):
        ValueError("output must be a directory")
    
    files = glob.glob(args.sourcepath)

    fieldnames, gen_stats = [], {}
    with Bar(' Analyzing', max=len(files), suffix='%(percent)d%%') as bar:
        for fnames, stats in calculate_stats(files, args.classnames):
            gen_stats[stats['Name']] = stats
            fieldnames.extend(fnames)
            bar.next()

    result = {}
    if args.statsfile is not None and os.path.isfile(args.statsfile):
        with open(args.statsfile, mode='r') as fin:    
            reader = csv.DictReader(fin)
            records = list(reader)
            for r in records:
                name = Path(r['Name']).stem
                result[name] = {**r, **stats[name]} if name in stats else r
                fieldnames.extend(list(r.keys()))
    else:
        result =  gen_stats
                
    # Write the per image stats
    with open(os.path.join(args.output, 'stats.csv'), mode='w') as fout:
        writer = csv.DictWriter(fout, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=set(fieldnames))
        writer.writeheader()
        for sts in result.values():
            writer.writerow(sts)

if __name__ == "__main__":
    main__()
    