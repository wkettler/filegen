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

def w_srand(f, size, bs=1024, fsync=False):
    """
        Create a new file and fill it with pseudo random data.
    
        Inputs:
            f      (str): name of the file
            size   (int): size in KB
            bs     (int): block size in KB
            fsync (bool): fsync after IO is complete
        Outputs:
            NULL
    """
    buf = '\0' * 1024
    with open(f, 'wb') as fh:
        while True:
            if size < bs:
                fh.write(buf * size)
                break
            fh.write(buf * bs)
            size -= bs
        # Sync
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())
            
def w_rand(f, size, bs=1024, fsync=False):
    """
        Create a new file and fill it with random data.
    
        Inputs:
            f      (str): name of the file
            size   (int): size in KB
            bs     (int): block size in KB
            fsync (bool): fsync after IO is complete
        Outputs:
            NULL
    """
    buf = os.urandom(1024)
    with open(f, 'wb') as fh:
        while True:
            if size < bs:
                fh.write(buf * size)
                break
            fh.write(buf * bs)
            size -= bs
        # Sync
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())
                                
def w_zero(f, size, bs=1024, fsync=False):
    """
        Create a new file and fill it with zeros.
    
        Inputs:
            f      (str): name of the file
            size   (int): size in KB
            bs     (int): block size in KB
            fsync (bool): fsync after IO is complete
        Outputs:
            NULL
    """
    buf = '\0' * 1024
    with open(f, 'wb') as fh:
        while True:
            if size < bs:
                fh.write(buf * size)
                break
            fh.write(buf * bs)
            size -= bs
        # Sync
        if fsync:
            fh.flush()
            os.fsync(fh.fileno())


def filegen(min_sz, max_sz, qty, ftype, dst=None, split=None):
    """
        Generate files.
        
        Inputs:
            min_sz (int): Minimum file size
            max_sz (int): Maximum file size
            qty    (int): Total file count
            ftype  (int): File type
            dst    (str): Destination directory
            split  (int): File per directory
        Outputs:
            NULL
    """
    # Define file type
    if ftype == 0:
        print 'Using zero file generator.'
        gen = lambda f, size: w_zero(f, size)
    elif ftype == 1:
        print 'Using random file generator.'
        gen = lambda f, size: w_rand(f, size)
    elif ftype == 2:
        print 'Using pseudo-random file generator.'
        gen = lambda f, size: w_srand(f, size)
    else:
        raise RuntimeError('Invalid file type.')
    
    # Use current directory if not defined
    if not dst:
        dst = os.getcwd()
        
    if split:
        current_dir = 0
        pwd = os.path.join(dst, str(current_dir))
        os.mkdir(pwd)
    else:
        pwd = dst
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
    parser.add_argument('--ftype', '-f', dest='ftype', type=int, required=True,
        choices=[0, 1, 2], help='file type (0=zero, 1=rand, 2=srand)')
    parser.add_argument('--dst', dest='dst', type=str, required=False,
        default=None, help='destination directory')
    parser.add_argument('--split', dest='split', type=int, required=False,
        default=None, help='files per directory')
    args = parser.parse_args()
    
    filegen(args.min, args.max, args.qty, args.ftype, args.dst, args.split)
