#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 14:22:28 2023

@author: durack1
"""

# %% imports
import json
import os
import requests
import numpy as np

# %% function defs


def getDirSize(start_path='.'):
    # https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    totalSize, totalFiles = [0 for _ in range(2)]
    seen = {}
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            if ".json" in f:
                continue  # skip json files
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


def getFacetIds(url, facet):
    req = requests.get(url)
    js = json.loads(req.text)
    facetIdsJson = js["facet_counts"]["facet_fields"][facet]
    facetIdLen = len(facetIdsJson)
    rng = np.arange(0, facetIdLen, 2)
    facetIds = []
    for x in rng:
        facetIds.append(facetIdsJson[x])

    return facetIds


def makeUrl(phase, facet):
    url = "".join(["https://esgf-node.llnl.gov/esg-search/search/",
                   "?limit=0&format=application%2Fsolr%2Bjson&facets=",
                   facet, "&project=input4mips&project=input4MIPs&mip_era=",
                   phase, "&distrib=false"])

    return url


# %% set paths
basePath = "/p/user_pub/work/input4MIPs/"
mipEra = ["CMIP6    ", "CMIP6Plus"]

bToTb = 1024*1024*1024*1024  # byte -> TB
bToGb = 1024*1024*1024  # byte -> GB

for phase in mipEra:
    path = os.path.join(basePath, phase.rstrip())
    mips = os.listdir(path)
    if phase == "CMIP6    ":
        mips.extend(["GeoMIP", "LS3MIP", "LUMIP"])  # Kludge
    print("".join([phase, ": ", str(len(mips)), " MIPs served"]))
    mips.sort()
    print(mips)
    size, totalFiles = getDirSize(path)
    print("".join([phase, ": ", "{:5.3f}".format(
        size/bToGb), " size (GB); totalFiles: ", str(totalFiles)]))
    print(path)
    # loop through mips and capture insitution_id's
    instIds = []
    for mip in mips:
        if mip in ["GeoMIP", "LS3MIP", "LUMIP"]:
            continue  # Kludge
        path = os.path.join(basePath, phase.rstrip(), mip)
        mipList = os.listdir(path)
        for xmip in mipList:
            if xmip not in instIds:
                instIds.append(xmip)
    print("".join([phase, ": ", str(len(instIds)), " total instIds"]))
    instIds.sort()
    print(instIds)
    url = makeUrl(phase.rstrip(), "source_id")
    srcIds = getFacetIds(url, "source_id")
    srcIds.sort()
    print("".join([phase, ": ", str(len(srcIds)), " total srcIds"]))
    print(srcIds)
    url = makeUrl(phase.rstrip(), "variable_id")
    varIds = getFacetIds(url, "variable_id")
    varIds.sort()
    print("".join([phase, ": ", str(len(varIds)), " total varIds"]))
    print(varIds)
    print('----------')
