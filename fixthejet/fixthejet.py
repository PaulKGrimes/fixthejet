# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 10:47:23 2018
@author: kkrao

Works in Python 3. only. 
Credits: Carreau
Code forked from https://github.com/Carreau/miscs/blob/master/Viridisify.ipynb
"""
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
from scipy.spatial import KDTree
# from ipywidgets import interact
import matplotlib.image as mpimg
from PIL import Image
from argparse import ArgumentParser


def build_parser():
    parser = ArgumentParser()
    parser.add_argument('--input',
            dest='input', help='content image',
            metavar='INPUT', required=True)
    parser.add_argument('--output',
            dest='output', help='output path',
            metavar='OUTPUT', required=True)
    parser.add_argument('--cmap_out', type=str,
            dest='cout', help='Output colormap - choose from matplotlib cmaps (default %(default)s)',
            metavar='COUT', default='viridis')
    cmapin = parser.add_mutually_exclusive_group()
    cmapin.add_argument('--cmap_in', type=str,
            dest='cin', help='Input colormap - choose from matplotlib cmaps (default %(default)s)',
            metavar='CIN', default='jet')
    cmapin.add_argument('--cbar_extent', type=int, nargs=4,
                        dest='cbar_extent', help='Get input colormap from color scale bar between these pixel positions (l, r, t, b)',
                        metavar='CBAR_EXTENT')
    return parser


def read_image(file_name):
    img = Image.open(file_name)
    img = img.convert("RGBA")
    
    imgarr = np.array(img.getdata()).reshape(img.size[1], img.size[0], 4)
    
    # Convert to float
    if np.issubdtype(int, imgarr.dtype):
        imgarr = imgarr/255
    
    return imgarr


def get_cmaps(img, options):
    '''Return the matplotlib colormaps to convert from and to.
    
    arguments:
        img (np.ndarray) : the input image data in an numpy array.
        options (dict) : the command line options'''
    outmap = plt.get_cmap(options.cout)
    if 'cbar_extent' in options:
        inmap = get_cmap_from_img(img, options.cbar_extent)
    else:
        inmap = plt.get_cmap(options.cin)
        
    return inmap, outmap

def get_cmap_from_img(img, cbar_extents):
    '''Get the cmap from a colorbar in the image.
    
    Takes four pixel positions definiing the edges of the color scale bar in the image,
    and creates a matplotlib cmap from the pixels.
    
    The axis of the colorbar is determined by the longer dimension, and the colorbar pixels are
    averaged in the narrow dimension.
    
    arguments:
        img (np.ndarray) : the input image data in an numpy array.
        cbar_extents (list of 4 integers) : the location of the colorbar in the input image.
        
    returns:
        matplotlib.cmap
    '''
    left = cbar_extents[0]
    right = cbar_extents[1]
    top = cbar_extents[2]
    bottom = cbar_extents[3]
    
    if abs(right - left) > abs(bottom - top):
        left = cbar_extents[2]
        right = cbar_extents[3]
        top = cbar_extents[1]
        bottom = cbar_extents[0]
        
        img = img.transpose(axes=[0, 1])
        
    cbar = img[top:bottom+1, left:right+1,  :]
    cscale = np.mean(cbar, axis=1)
    clist = list(map(tuple, cscale))
    clist.reverse()
    incmap = colors.LinearSegmentedColormap.from_list("input_cmap", clist)
    
    return incmap


def convert_image(img, cin, cout, d=0.2, sub=256):
    
    print(f"Converting {cin.name} to {cout.name}")
    oshape = img.shape

    cinsub = cin.resampled(sub)(range(sub))
    K = KDTree(cinsub)
    oshape = img.shape
    img_data = img.reshape((-1,4))
    res = K.query(img_data, distance_upper_bound=d)
    indices = res[1]
    l = len(cinsub)
    indices = indices.reshape(oshape[:2])
    remapped = indices
    indices.max()
    mask = (res[0].reshape(oshape[:2]) > 0.9)
    remapped = remapped / (l-1)
    msk = [mask]*3
    msk.append(np.ones_like(mask))
    mask = np.stack(msk, axis=-1)
    blend = np.where(mask, img, cout(remapped).astype(float)[:,:,:4])
    
    return img, blend

    
def save_image(blend, path):
    mpimg.imsave(path, blend)


def main():
    parser = build_parser()
    options = parser.parse_args()
    print(options)
    try:
        img = read_image(options.input)
    except:
        raise IOError('%s does not exist'%options.input)
    
    cinmap, coutmap = get_cmaps(img, options)

    img, blend = convert_image(img, cinmap, coutmap)
    try:
        save_image(blend, options.output)
    except:
        raise IOError('%s is not writable or does not have a valid file \
                      extension for an image file'%options.output)


if __name__ == '__main__':
    main()
    