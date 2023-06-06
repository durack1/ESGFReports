#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 14:22:28 2023

@author: durack1
"""

# %% imports
import os
from pathlib import Path

# %% defs


def getDirSize(fullPath):
    # https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    return ByteSize(sum(file.stat().st_size for file in Path(fullPath).rglob('*')))


class ByteSize(int):

    _KB = 1024
    _suffixes = 'B', 'KB', 'MB', 'GB', 'PB'

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.bytes = self.B = int(self)
        self.kilobytes = self.KB = self / self._KB**1
        self.megabytes = self.MB = self / self._KB**2
        self.gigabytes = self.GB = self / self._KB**3
        self.petabytes = self.PB = self / self._KB**4
        suffixes, last = self._suffixes
        suffix = next((
            suffix
            for suffix in suffixes
            if 1 < getattr(self, suffix) < self._KB
        ), last)
        self.readable = suffix, getattr(self, suffix)

        super().__init__()

    def __str__(self):
        return self.__format__('.2f')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())

    def __format__(self, format_spec):
        suffix, val = self.readable
        return '{val:{fmt}} {suf}'.format(val=val, fmt=format_spec, suf=suffix)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        return self.__class__(super().__add__(other))

    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        return self.__class__(super().__sub__(other))

    def __radd__(self, other):
        return self.__class__(super().__add__(other))

    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other))


# %% set paths
basePath = "/p/user_pub/work/input4MIPs/"
mipEra = ["CMIP6    ", "CMIP6Plus"]

for phase in mipEra:
    path = os.path.join(basePath, phase.rstrip())
    mips = os.listdir(path)
    print("".join([phase, ": ", str(len(mips)), " MIPs served"]))
    size = os.path.getsize(path)
    print("".join([phase, ": ", str(size/1e12), " size (TB)"]))
    sizeNew = getDirSize(path)
    print("".join([phase, ": ", sizeNew.PB, " size (PB)"]))
    print(path)
    # loop through mips and capture insitution_id's
    instIds = []
    for mip in mips:
        path = os.path.join(basePath, phase.rstrip(), mip)
        mipList = os.listdir(path)
        for xmip in mipList:
            if xmip not in instIds:
                instIds.append(xmip)
    print("".join([phase, ": ", str(len(instIds)), " total instIds"]))
    instIds.sort()
    print(instIds)
    print('----------')
