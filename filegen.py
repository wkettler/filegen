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

def w_srand(f, sz, bs, fsync=False):
    """
    Create a new file and fill it with pseudo random data.
    
    Inputs:
        f      (str): File
        sz     (int): File size in KB
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    buf = os.urandom(1024)
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            if sz < bs:
                os.write(fh, buf * sz)
                break
            os.write(fh, buf * bs)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)
            
def w_rand(f, sz, bs, fsync=False):
    """
    Create a new file and fill it with random data.
    
    Inputs:
        f      (str): File
        sz     (int): File size in KB
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    bs *= 1024
    sz *= 1024
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            if sz < bs:
                buf = os.urandom(sz)
                os.write(fh, buf)
                break
            buf = os.urandom(bs)
            os.write(fh, buf)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)
                                
def w_zero(f, sz, bs, fsync=False):
    """
    Create a new file and fill it with zeros.

    Inputs:
        f      (str): File
        sz     (int): File size in KB
        bs     (int): Block size in KB
        fsync (bool): Fsync after IO is complete
    Outputs:
        NULL
    """
    buf = '\0' * 1024
    
    try:
        fh = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
        while True:
            if sz < bs:
                os.write(fh, buf * sz)
                break
            os.write(fh, buf * bs)
            sz -= bs
        # Force write of fdst to disk.
        if fsync:
            os.fsync(fh)
    except:
        raise
    finally:
        os.close(fh)

def filegen(min_sz, max_sz, qty, ftype, bs=1024, dst=None, split=None):
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
        gen = lambda f, size, bs: w_zero(f, size, bs)
    elif ftype == 1:
        print 'Using random file generator.'
        gen = lambda f, size, bs: w_rand(f, size, bs)
    elif ftype == 2:
        print 'Using pseudo-random file generator.'
        gen = lambda f, size, bs: w_srand(f, size, bs)
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
        current_dir = dst
        pwd = dst
        split = qty
    
    current_ct = 0
    while True:
        while current_ct < split:
            # Write file.    
            size = randint(min_sz, max_sz)
            f = os.path.join(pwd, ".".join([str(current_ct), "data"]))
            gen(f, size, bs)
            
            # Update counters.
            current_ct += 1
            qty -= 1
            
        # Exit if file count limit reached.
        if qty == 0:
            break
            
        # Create new working directory
        current_dir += 1
        pwd = os.path.join(dst, str(current_dir))
        os.mkdir(pwd)
        
        # Reset current file count
        current_ct = 0

if __name__ == '__main__':
    from argparse import ArgumentParser

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
    parser.add_argument('--bs', dest='bs', type=int, required=False,
                        default=1024, help='IO record size')
    args = parser.parse_args()
    
    filegen(args.min, args.max, args.qty, args.ftype, args.bs, args.dst, args.split)
