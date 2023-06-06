#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 14:22:28 2023

@author: durack1
"""

# %% imports
import os

# %% function defs


def getDirSize(start_path='.'):
    # https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    totalSize, totalFiles = [0 for _ in range(2)]
    seen = {}
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                stat = os.stat(fp)
            except OSError:
                continue

            try:
                seen[stat.st_ino]
            except KeyError:
                seen[stat.st_ino] = True
            else:
                continue

            totalSize += stat.st_size
            totalFiles += 1

    return totalSize, totalFiles


# %% set paths
basePath = "/p/user_pub/work/input4MIPs/"
mipEra = ["CMIP6    ", "CMIP6Plus"]

bToTb = 1024*1024*1024*1024  # byte -> TB
bToGb = 1024*1024*1024  # byte -> GB

for phase in mipEra:
    path = os.path.join(basePath, phase.rstrip())
    mips = os.listdir(path)
    print("".join([phase, ": ", str(len(mips)), " MIPs served"]))
    print(mips)
    size = os.path.getsize(path)
    print("".join([phase, ": ", "{:5.3f}".format(size/bToGb), " size (GB)"]))
    sizeNew, totalFiles = getDirSize(path)
    print("".join([phase, ": ", "{:5.3f}".format(
        sizeNew/bToGb), " sizeNew (GB); totalFiles: ", str(totalFiles)]))
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
