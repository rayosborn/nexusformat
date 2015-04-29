#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Copyright (c) 2013, NeXpy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING, distributed with this software.
#-----------------------------------------------------------------------------
import argparse, os, sys, traceback

from nexusformat.nexus import NeXusError
from nexusformat.tools.stack import nxstack
from nexusformat import __version__

def main():

    debug = False
    dump_stack = False

    parser = argparse.ArgumentParser(
        description="Stack images into a single NeXus file")
    parser.add_argument('-d', '--directory', default=os.getcwd(),
                        help="directory containing the raw images")
    parser.add_argument('-p', '--prefix', nargs='+',
                        help="common prefix to all images")
    parser.add_argument('-e', '--extension', default='.tif',
                        help="file extension of raw images")
    parser.add_argument('-o', '--output', help="name of NeXus output file")
    parser.add_argument('-b', '--background',
                        help="Name of background (dark) image to be subtracted")
    parser.add_argument('-s', '--spec',
                        help="Name of SPEC file used in collecting images")
    parser.add_argument('-f', '--first', default=0, type=int,
                        help="first frame to be included in the stacked data")
    parser.add_argument('-l', '--last', type=int,
                        help="last frame to be included in the stacked data")
    parser.add_argument('-r', '--reverse', action='store_true',
                        help="store images in reverse order")
    parser.add_argument('-c', '--compression', help="HDF5 compression method")
    parser.add_argument('-v', '--version', action='version', 
                        version='nxstack v%s' % __version__)
    parser.add_argument('-g', '--debug', action='store_true',
                        help="enable debugging")

    args = parser.parse_args()

    debug = args.debug
    if debug:
        dump_stack = True

    directory = args.directory
    extension = args.extension
    if not extension.startswith('.'):
        extension = '.' + extension
    output = args.output

    compression = args.compression

    background = args.background

    spec = args.spec
    if spec:
        try:
            spec_file = glob.glob(os.path.join(directory, spec))[-1]
        except IndexError:
            spec_file = None
    else:
        spec_file = None

    first = args.first
    last = args.last
    reverse = args.reverse
    prefixes = args.prefix

    try:
        nxstack(directory, prefixes, extension, output, background, spec, 
                first, last, reverse, compression, __version__)
    except NeXusError as e:
        if dump_stack:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        else:
            print str(e)

if __name__ == "__main__":
    main()
