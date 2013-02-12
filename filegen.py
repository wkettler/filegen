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

def w_srand(f, size, bs=16, fsync=False):
    """
    Create a new file and fill it with pseudo random data.
    
    Arguments:
    f -- name of the file
    size -- size in KB
    bs -- block size in KB
    fsync -- fsync after IO is complete
    """
    buf = os.urandom(1024)
    with open(f, 'wb') as fh:
        while True:
            if size < bs:
                fh.write(buf * size)
                break
            fh.write(buf * bs)
            size -= bs
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())
            
def w_rand(f, size, bs=16, fsync=False):
    """
    Create a new file and fill it with random data.
    
    Arguments:
    f -- name of the file
    size -- size in KB
    bs -- block size in KB
    fsync -- fsync after IO is complete
    """
    bs *= 1024
    size *= 1024

    with open(f, 'wb') as fh:
        while True:
            if size < bs:
                buf = os.urandom(size)
                fh.write(buf)
                break
            buf = os.urandom(bs)
            fh.write(buf)
            size -= bs
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())
            
def w_zero(f, size, bs=16, fsync=False):
    """
    Create a new file and fill it with zeros.

    Arguments:
    f -- name of the file
    size -- size in KB
    bs -- block size in KB
    fsync -- fsync after IO is complete
    """
    buf = '\0' * 1024
    with open(f, 'wb') as fh:
        while True:
            if size < bs:
                fh.write(buf * size)
                break
            fh.write(buf * bs)
            size -= bs
        # Force write of fdst to disk.
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())

if __name__ == '__main__':
    # Define CLI arguments.
    parser = ArgumentParser(description='File generation utility.')
    parser.add_argument('--ftype', '-f', dest='ftype', type=int, required=False,
        default=0, help='file type (0=zero, 1=rand, 2=srand)')
    parser.add_argument('--dst', '-d', dest='dst', type=str, required=True,
        help='destination directory')
    parser.add_argument('--min', dest='min', type=int, required=True,
        help='minimum file size in KB')
    parser.add_argument('--max', dest='max', type=int, required=True,
        help='max file size in KB')
    parser.add_argument('--qty', '-q', dest='qty', type=int, required=True,
        help='file count')
    parser.add_argument('--split', '-s', dest='split', type=int, required=True,
        help='files per directory')
    args = parser.parse_args()
    
    # Load values
    dst = args.dst
    min_sz = args.min
    max_sz = args.max
    split = args.split
    qty = args.qty
    ftype = args.ftype
    
    
    # Define file type
    if ftype == 0:
        print 'Using zero file generator.'
        gen = lambda f, size: w_zero(f, size)
    elif ftype == 1:
        print 'Using random file generator.'
        gen = lambda f, size: w_rand(f, size)
    elif ftype == 2:
        print 'Using pseudo file generator.'
        gen = lambda f, size: w_srand(f, size)
    else:
        print 'ERROR: Invalid file type specified.'
        parser.print_help()
    
    current_dir = 0
    current_ct = 0
    os.mkdir(os.path.join(dst, str(current_dir)))
    while qty != 0:        
        # Make new directory if file count per dir reached.
        if current_ct == split:
            current_ct = 0
            current_dir += 1
            os.mkdir(os.path.join(dst, str(current_dir)))
        
        # Write file.    
        size = randint(min_sz, max_sz)
        f = os.path.join(dst, str(current_dir), ".".join([str(current_ct), "data"]))
        gen(f, size)
        
        # Update counters.
        current_ct += 1
        qty -= 1
        
    print 'Complete!'