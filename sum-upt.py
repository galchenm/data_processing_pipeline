#!/usr/bin/env python3
# coding: utf8
# Written by Galchenkova M.


"""
"""

import os
import sys
import h5py as h5
import numpy as np
import argparse
import glob

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i','--i', type=str, help="Path with files")
    parser.add_argument('-o','--o', type=str, help="The name of file for making mask")
    parser.add_argument('-f','--f', type=str, help="The format of hdf5 files (cxi/h5)")
    parser.add_argument('-pt','--pt', type=str, help="The pattern in names of hdf5 files (data, EuXFEL)")
    parser.add_argument('-s','--s', type=str, help="Single file")
    parser.add_argument('-n','--n', type=int, help="Num of patterns for the sum")
    parser.add_argument('-h5p', type=str, help="hdf5 path for the cxi file data")

    return parser.parse_args()

def sum_int(files, path_cxi, n=None):
    file_to_check_format = h5.File(files[0],'r')
    data_shape = file_to_check_format[path_cxi].shape
    
    file_to_check_format.close()
    
    print('Data shape is ', data_shape)
    print('Len Data shape is ', len(data_shape))
    if n is not None:
        Sum_Int = 0
        N = n
        num = 0
        print('I am here')
        for ffile in files:
            
            file = h5.File(ffile, 'r')
            data = file[path_cxi]
            if num >= N:
                break
            if len(data_shape) > 2:
                
                Sum_Int += np.sum(data[:,],axis=0)
                
                num += data.shape[0]
                
                print(f'Now we processed {num} patterns')
            else:
                
                Sum_Int += data[:,]
                num += 1
                print(f'Now we processed {num} patterns')
            file.close()
    else:        
        Sum_Int = 0
        for file in files:
            file = h5.File(ffile, 'r')
            data = file[path_cxi]
            if len(data_shape) > 2:
                Sum_Int += np.sum(data[:,],axis=0)
            else:
                Sum_Int += data[:,]
            file.close()
    return Sum_Int


if __name__ == "__main__":
    
    args = parse_cmdline_args()
    
    path_cxi = args.h5p
    correct = True
    
    if args.s is not None:
        file = h5.File(args.s, 'r')
        data = file[path_cxi]
        if args.n is not None:
            Sum_Int = np.sum(data[0:args.n,],axis=0)
        else:
            Sum_Int = np.sum(data[:,],axis=0)        
    elif args.i is not None:
        if args.f is None and args.pt is None:
            files = glob.glob(os.path.join(args.i,'*cxi'))
            if len(files) == 0:
                files = glob.glob(os.path.join(args.i,'*.h5'))
                if len(files) == 0:
                    print(f'Check {args.i} - something went wrong. Carefully check format and filenames')
                    correct = False
                else:
                    Sum_Int = sum_int(files, path_cxi, args.n)
        if args.f is None and args.pt is not None:
            files = glob.glob(os.path.join(args.i,f'*{args.pt}*cxi'))
            if len(files) == 0:
                files = glob.glob(os.path.join(args.i,f'*{args.pt}*h5'))
                if len(files) == 0:
                    print(f'Check {args.i} - something went wrong. Carefully check format and filenames')
                    correct = False
                else:
                    Sum_Int = sum_int(files, path_cxi, args.n)
                    
        if args.f is not None and  args.pt is None:
            files = glob.glob(os.path.join(args.i,f'*{args.f }'))
            if len(files) == 0:
                print(f'Check {args.i} - something went wrong. Carefully check format and filenames')
                correct = False
            else:
                Sum_Int = sum_int(files, path_cxi, args.n)
        if args.f is not None and  args.pt is not None:
            files = glob.glob(os.path.join(args.i,f'*{args.pt}*{args.f }'))
            if len(files) == 0:
                print(f'Check {args.i} - something went wrong. Carefully check format and filenames')
                correct = False
            else:
                Sum_Int = sum_int(files, path_cxi, args.n)
    else:
        print('You have to provide with anything for making mask!')
        correct = False
    
    if correct:
        if args.o is not None:
            output_filename = args.o
        else:
            output_filename = 'forMask-v1.h5'
        f = h5.File(output_filename, 'w')
        f.create_dataset('/data', data=np.array(Sum_Int))
        f.close()
