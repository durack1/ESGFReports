#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 14:22:28 2023

@author: durack1
"""

# %% imports
import os


# %% set paths
basePath = "/p/user_pub/work/input4MIPs/"
mipEra = ["CMIP6", "CMIP6Plus"]

for phase in mipEra:
    path = os.path.join(basePath, phase)
    mips = os.listdir(path)
    print("".join([phase, ":", str(len(mips)), " MIPs served"]))
    size = os.path.getsize(path)
    print("".join([phase, ":", str(size/1e12), " size (TB)"]))
