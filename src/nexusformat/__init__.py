# -----------------------------------------------------------------------------
# Copyright (c) 2013-2021, NeXpy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING, distributed with this software.
# -----------------------------------------------------------------------------

__package_name__ = 'nexusformat'
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__documentation_author__ = 'Ray Osborn'
__documentation_copyright__ = '2013-2021, Ray Osborn'

__license__ = 'BSD'
__author_name__ = 'NeXpy Development Team'
__author_email__ = 'nexpydev@gmail.com'
__author__ = __author_name__ + ' <' + __author_email__ + '>'

__url__ = 'http://nexpy.github.io/nexpy/'
__download_url__ = 'https://github.com/nexpy/nexusformat/'

__description__ = 'nexusformat: Python API to access NeXus data'
__long_description__ = \
    """
This package provides a Python API to open, create, and manipulate `NeXus data
<http://www.nexusformat.org/>`_ written in the HDF5 format. The 'nexusformat'
package provides the underlying API for `NeXpy
<http://nexpy.github.io/nexpy>`_, which provides a GUI interface. It also
contains a command-line script, `nxstack` for merging TIFF or CBF files into a
single HDF5 array.

The latest development version is always available from `NeXpy's GitHub
site <https://github.com/nexpy/nexusformat>`_.
"""
