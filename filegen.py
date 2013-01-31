#! /usr/bin/env python
#
# filegen.py
#
# File generation utility.
#

__author__  = 'William Kettler <william_kettler@dell.com>'
__created__ = 'January 31, 2013'

import os
from random import randint
from argparse import ArgumentParser

def trim_slash(d):
    """
    Trim trailing slash.
    """
    return d.rstrip(os.path.sep)

def srand(f, size, bs=None):
    """
    Create a new file and fill it with pseudo random data.
    
    Arguments:
    f -- name of the file
    size -- size in KB
    bs -- block size in KB
    """
   
    if not bs:
        bs = size
   
    buf = os.urandom(1024)
    with open(f, 'w') as fh:
        while True:
            if size > bs:
                fh.write(bs * buf)
                size -= bs
            else:
                fh.write(size * buf)
                break
        fh.flush()

if __name__ == '__main__':
    # Define CLI arguments.
    parser = ArgumentParser(description='File generation utility.')
    parser.add_argument('--dst', dest='dst', type=str, required=True,
        help='destination directory')
    parser.add_argument('--min', dest='min', type=int, required=True,
        help='minimum file size in KB')
    parser.add_argument('--max', dest='max', type=int, required=True,
        help='max file size in KB')
    parser.add_argument('--qty', dest='qty', type=int, required=True,
        help='file count')
    parser.add_argument('--split', dest='split', type=int, required=True,
        help='files per directory')
    args = parser.parse_args()
    
    # Load values
    dst = args.dst
    min_sz = args.min
    max_sz = args.max
    split = args.split
    qty = args.qty
    
    current_dir = 0
    os.mkdir(os.path.join(dst, str(current_dir)))
    
    current_ct = 0
    while True:
        # Exit if file count limit reached.
        if qty == 0:
            break
        
        # Make new directory if file count per dir reached.
        if current_ct == split:
            current_ct = 0
            current_dir += 1
            os.mkdir(os.path.join(dst, str(current_dir)))
        
        # Write file.    
        size = randint(min_sz, max_sz)
        f = os.path.join(dst, str(current_dir), ".".join([str(current_ct), "data"]))
        srand(f, size)
        
        # Update counters.
        current_ct += 1
        qty -= 1