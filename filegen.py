#!/usr/bin/python

"""
filegen.py

File generation utility.

Copyright (C) 2013  William Kettler <william.p.kettler@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
        fh.flush()


def filegen(min_sz, max_sz, qty, dst=None, split=None):
    """
        Generate files.
        
        Inputs:
            min_sz (int): Minimum file size
            max_sz (int): Maximum file size
            qty    (int): Total file count
            dst    (str): Destination directory
            split  (int): File per directory
        Outputs:
            NULL
    """
    
    if not dst:
        dst = os.getcwd()
        
    if split:
        current_dir = 0
        os.mkdir(os.path.join(dst, str(current_dir)))
    else:
        current_dir = dst
        split = qty
    
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
        w_srand(f, size)
        
        # Update counters.
        current_ct += 1
        qty -= 1

if __name__ == '__main__':
    # Define CLI arguments.
    parser = ArgumentParser(description='File generation utility.')
    parser.add_argument('--min', dest='min', type=int, required=True,
        help='minimum file size in KB')
    parser.add_argument('--max', dest='max', type=int, required=True,
        help='max file size in KB')
    parser.add_argument('--qty', dest='qty', type=int, required=True,
        help='file count')
    parser.add_argument('--dst', dest='dst', type=str, required=False,
        default=None, help='destination directory')
    parser.add_argument('--split', dest='split', type=int, required=False,
        default=None, help='files per directory')
    args = parser.parse_args()
    
    filegen(args.min, args.max, args.qty, args.dst, args.split)
