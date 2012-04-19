#!/usr/bin/env pvpython
# -*- coding: utf-8 -*-
#
# jonas juselius <jonas.juselius@uit.no>
#

# adding some doc bla oof


import sys
#sys.path.append('/usr/lib/paraview')

from argparse import ArgumentParser
from paraview.simple import *
import time

parser = ArgumentParser(description = "Convert legacy VTK files to .png")
parser.add_argument('infile', nargs=1,
        action='store',
        default=None,
        help='name of input file in .vtk format',
        metavar='input.vtk')
parser.add_argument('outfile', nargs='?',
        action='store',
        default=None,
        help='name of output file in .png format',
        metavar='output.png')
parser.add_argument('--colors',
        action='store',
        choices=('default', 'bw', 'wb'),
        default='default',
        help='color scheme')

args = parser.parse_args()

def main():
    reader = LegacyVTKReader(FileNames=args.infile)
    Show(reader)

    view = GetRenderView()
    view.CameraViewUp = [0, 0, 1]
    view.CameraFocalPoint = [0, 0, 0]
    view.CameraViewAngle = 45
    view.CameraPosition = [-1, 0, 0]
    view.ViewSize = [args.size, args.size] 

    dp = GetDisplayProperties()
    print args.colors
    if args.colors == 'bw':
        dp.AmbientColor = [0, 0, 0] 
        dp.DiffuseColor = [0, 0, 0] 
        view.Background = [1, 1, 1]
    elif args.colors == 'wb':
        dp.AmbientColor = [1, 1, 1] 
        dp.DiffuseColor = [1, 1, 1] 
        view.Background = [0, 0, 0]
    else:
        dp.AmbientColor = [1, 1, 1] 
        dp.DiffuseColor = [1, 1, 1] 
        view.Background = [82.0/255.0, 87.0/255.0, 109.0/255.0] 
         
    dp.PointSize = 1
    dp.Representation = "Surface"
    #dp.Representation = "Points"

    Render()
    # save screenshot or view 
    if args.outfile is not None:
        WriteImage(args.outfile)
    else:
        raw_input("Press any key... ")

if __name__ == '__main__':
    main()


# vim:et:sw=4
