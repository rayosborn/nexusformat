#!/usr/bin/env python 
# -*- coding: utf-8 -*-

"""
This package provides a Python API that subclasses the 
nexusformat package to work with HDF5 files served by h5serv. 

"""
from __future__ import (absolute_import, division, print_function)
import six

import os

import numpy as np
import h5pyd as h5

from nexusformat.nexus import *

NX_SERVER = 'http://34.233.121.234:5101'
NX_DOMAIN = '/home/jreadey/'

__all__ = ['NXRemoteFile', 'nxloadremote', 
           'nxgetserver', 'nxsetserver', 'NX_SERVER', 
           'nxgetdomain', 'nxsetdomain', 'NX_DOMAIN']

class NXRemoteFile(NXFile):

    """
    Structure-based interface to the NeXus file API.

    Usage::

      file = NXFile(filename, ['r','rw','w'])
        - open the NeXus file
      root = file.readfile()
        - read the structure of the NeXus file.  This returns a NeXus tree.
      file.writefile(root)
        - write a NeXus tree to the file.

    Example::

      nx = NXFile('REF_L_1346.nxs','r')
      tree = nx.readfile()
      for entry in tree.NXentry:
          process(entry)
      copy = NXFile('modified.nxs','w')
      copy.writefile(tree)

    Note that the large datasets are not loaded immediately.  Instead, the
    when the data set is requested, the file is reopened, the data read, and
    the file closed again.  open/close are available for when we want to
    read/write slabs without the overhead of moving the file cursor each time.
    The :class:`NXdata` objects in the returned tree hold the object values.
    """

    def __init__(self, name, mode='r', server=None,  domain=None, 
                 **kwds):
        """
        Creates an h5py File object for reading and writing.
        """
        self.h5 = h5
        self._name = name
        self._mode = 'r'
        if server is None:
            server = NX_SERVER
        self._server = server
        if domain is None:
            domain = NX_DOMAIN
        self._domain = domain
        self._filename = os.path.join(self._domain, self._name)                             
        self._file = self.h5.File(self._filename, mode, endpoint=server)
        self._path = '/'

    def __repr__(self):
        return '<NXRemoteFile "%s" (mode %s)>' % (self._filename,
                                                  self._mode)

    def open(self, **kwds):
        if not self.isopen():
            self._file = self.h5.File(self._filename, self._mode, 
                                      endpoint=self._server)
            self.nxpath = '/'
        return self

    def close(self):
        if self.isopen():
            self._file.close()

    def isopen(self):
        if self._file.id.uuid != 0:
            return True
        else:
            return False

#    @property
#    def domain(self):
#        domain = self.name.split('.')[0].split('/')
#        domain.reverse()
#        domain.append(self._domain)
#        return '.'.join(domain)

    @property
    def file(self):
        if not self.isopen():
            self.open()
        return self._file

    def readfile(self):
        """
        Reads the NeXus file structure from the file and returns a tree of 
        NXobjects.

        Large datasets are not read until they are needed.
        """
        _mode = self._mode
        self._mode = 'r'
        self.nxpath = '/'
        root = self._readgroup('root', self._file['/'])
        root._group = None
        root._file = self
        root._filename = self._filename
        root._mode = self._mode = _mode
        return root

    def _readchildren(self, group):
        children = {}
        for name, value in group.items():
            self.nxpath = self.nxpath + '/' + name
            if isinstance(value, self.h5.Group):
                children[name] = self._readgroup(name, value)
            else:
                children[name] = self._readdata(name, value)
            self.nxpath = self.nxparent
        return children

    def _readgroup(self, name, group):
        """
        Reads the group with the current path and returns it as an NXgroup.
        """
        if group is None:
            return NXgroup(name=name)
        attrs = self._readattrs()
        nxclass = self._readclass(attrs.pop('NX_class', 'NXgroup'))
        if self.nxpath == '/':
            nxclass = 'NXroot'
        children = self._readchildren(group)
        _target, _filename, _abspath = self._readlink()
        if self.nxpath != '/' and _target is not None:
            group = NXlinkgroup(nxclass=nxclass, name=name, attrs=attrs,
                                new_entries=children, target=_target, 
                                file=_filename, abspath=_abspath)
        else:
            group = NXgroup(nxclass=nxclass, name=name, attrs=attrs, 
                            new_entries=children)
        for obj in children.values():
            obj._group = group
        group._changed = True
        return group

    def _readdata(self, name, field):
        """
        Reads a data object and returns it as an NXfield or NXlink.
        """
        if field is None:
            return NXfield(name=name)
        _target, _filename, _abspath = self._readlink()
        if _target is not None:
            if _filename is not None:
                try:
                    value, shape, dtype, attrs = self.readvalues()
                    return NXlinkfield(
                        target=_target, file=_filename, abspath=_abspath,
                        name=name, value=value, dtype=dtype, shape=shape, 
                        attrs=attrs)
                except Exception:
                    pass
            return NXlinkfield(name=name, target=_target, file=_filename, 
                               abspath=_abspath)
        else:
            value, shape, dtype, attrs = self.readvalues(field)
            return NXfield(value=value, name=name, dtype=dtype, shape=shape, 
                           attrs=attrs)
 
    def _readattrs(self):
        return dict(self[self.nxpath].attrs.items())

    def readvalues(self, field):
        shape, dtype = field.shape, field.dtype
        if shape == (1,):
            shape = ()
        #Read in the data if it's not too large
        if np.prod(shape) < 1000:# i.e., less than 1k dims
            try:
                value = field[()]
                if isinstance(value, np.ndarray) and value.shape == (1,):
                    value = np.asscalar(value)
            except ValueError:
                value = None
        else:
            value = None
        attrs = self.attrs
        return value, shape, dtype, attrs

def getserver():
    global NX_SERVER
    return NX_SERVER

nxgetserver = getserver

def setserver(value):
    """
    Sets the default server and port for remote access.
    """
    global NX_SERVER
    NX_SERVER = value

nxsetserver = setserver

def getdomain():
    global NX_DOMAIN
    return NX_DOMAIN

nxgetdomain = getdomain

def setdomain(value):
    """
    Sets the default domain for remote access.
    """
    global NX_DOMAIN
    NX_DOMAIN = value

nxsetdomain = setdomain

def loadremote(filename, server=None, domain=None, mode='r'):
    """
    Reads a remote NeXus file returning a tree of objects.
    """
    if server is None:
        server = NX_SERVER
    if domain is None:
        domain = NX_DOMAIN
    with NXRemoteFile(filename, mode, server=server, domain=domain) as f:
        tree = f.readfile()
    return tree

nxloadremote = loadremote
