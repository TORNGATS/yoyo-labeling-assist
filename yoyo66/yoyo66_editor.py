
import os
import sys
import argparse
import tempfile as tf
import subprocess as sp
import pathlib

sys.path.append(os.getcwd())
sys.path.append(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from yoyo66.handler import (
    GIMPFileHandler, 
    OpenRasterFileHandler, 
    PKGFileHandler,
    TiffFileHandler,
    H5FileHandler
)

from yoyo66.handler import load_file, build_by_name, build_by_file_extension

def main ():
    parser = argparse.ArgumentParser(
        prog = 'YoYo-66 Editor',
        description = 'YoYo-66 Editor is an intermadiator using editor tool (default GIMP software) to edit multi-layer images.',
        epilog = 'TORNGATS @ 2023'
    )
    parser.print_help()
    parser.add_argument('filepath', help = 'Filepath to a multi-layer image.')
    parser.add_argument('-e', '--exe', default = 'gimp', type = str, help = 'Editor tool command')
    
    args = parser.parse_args()
    if args.filepath is None:
        raise ValueError('filepath must be specified')
    
    fpath = args.filepath
    print(f'Loading {fpath} ...')
    if not os.path.isfile(fpath):
        raise ValueError(f'{fpath} does not exist!')
    ext = pathlib.Path(fpath).suffix[1:]
    handler = build_by_file_extension(ext)
    # Load the multi-layer image
    print(f'Loading the handlers ...')
    orig = handler.load(fpath)
    # Make an instance of TIFF handler
    tifobj = build_by_name('tiff')
    dsc = tf.NamedTemporaryFile(prefix='yoyo66_', suffix='.tif')
    tifobj.save(orig, dsc.name)
    print(f'Opening {args.exe} ...')
    process = sp.Popen(f'{args.exe} {dsc.name}', shell=True, close_fds=True)
    process.wait()
    print(f'Loading the changes ...')
    # Load the edited image
    edited_img = tifobj.load(dsc.name)
    # Update the original image using the edited image
    dsc.close()
    print(f'Updating the image ...')
    orig.update_from(edited_img)
    # Save the updated image
    handler.save(orig, fpath)

if __name__ == "__main__":
    main()