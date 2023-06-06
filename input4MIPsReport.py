#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 14:22:28 2023

@author: durack1
"""

# %% imports
import os

# %% defs


def dirSize(path='.'):
    # https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += dirSize(entry.path)
    return total


# %% set paths
basePath = "/p/user_pub/work/input4MIPs/"
mipEra = ["CMIP6    ", "CMIP6Plus"]

for phase in mipEra:
    path = os.path.join(basePath, phase.rstrip())
    mips = os.listdir(path)
    print("".join([phase, ": ", str(len(mips)), " MIPs served"]))
    size = os.path.getsize(path)
    print("".join([phase, ": ", str(size/1e12), " size (TB)"]))
    sizeNew = dirSize(path)
    print("".join([phase, ": ", sizeNew/1e12, " sizeNew (TB)"]))
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
