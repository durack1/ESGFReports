#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 22:01:58 2020

PJD  9 Apr 2020 - Updated ESGF scrape script reference
PJD  9 Apr 2020 - Added CMIP6 total project scan
PJD  4 May 2020 - Updated to write files to dated subdir
PJD  2 Jun 2020 - Updated to check for existing directory
PJD  8 Dec 2020 - Updated to include data footprint scans
PJD  1 Sep 2021 - Update macPath
PJD  5 Oct 2021 - Updated to check python version - only 3 works
PJD 16 Mar 2022 - Update macPath
PJD 20 Mar 2022 - Add gitPath
PJD 14 Jun 2022 - Add pkg_resources to test numpy availability
PJD 17 Jan 2023 - Update macPath 22 -> 23
PJD 26 Apr 2023 - Added "403 Forbidden error" check for output to catch SOLR query failures
PJD 22 Jun 2023 - Added matplotlib and numpy imports to catch issues that are not reported by submodules
PJD 27 Feb 2024 - Updated path from admin/23 -> 24
PJD  6 May 2024 - Updated to include institution_id and direct URL reads
PJD 21 Jan 2025 - Updated macPath 24->25
PJD 21 Jan 2025 - Updated pkg_resources -> importlib

@author: durack1
"""
import datetime
import importlib.metadata
import os
import shlex
import subprocess
import sys
import requests

# import pkg_resources

# pkg_resources
# for dist in pkg_resources.working_set:
#    print(dist.project_name, dist.version)
# importlib.metadata
# import importlib.metadata
#
# for dist in importlib.metadata.distributions():
#    print(dist.metadata["Name"], dist.version)


# %% Check Python min version
pyVerInfo = sys.version_info
if pyVerInfo.major < 3:
    print("Python version", pyVerInfo.major, "not supported, quitting..")
    sys.exit()

# %% Check numpy installed
required = {"numpy"}
# installed = {pkg.key for pkg in pkg_resources.working_set}
installed = {dist.metadata["Name"] for dist in importlib.metadata.distributions()}
missing = required - installed
if len(missing) > 0:
    print("missing package:", missing, " exiting..")
    sys.exit()

# %% Get git path
gitPath = os.path.realpath(__file__)
gitPath = gitPath.split("/")[0:-1]
gitPath = os.path.join(os.sep, *gitPath)
print("gitPath:", gitPath)

# %% Define activity_id entries
actIdUrl = (
    "https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/main/CMIP6_activity_id.json"
)
r = requests.get(actIdUrl)
rj = r.json()
activity_id = rj["activity_id"]

# %% Define institution_id entries
instIdUrl = "https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/main/CMIP6_institution_id.json"
r = requests.get(instIdUrl)
rj = r.json()
institution_id = rj["institution_id"]
# Messy_Consortium, NASA-GSFC, PCMDI, PNNL-WACCEM not published 240506
# RUBISCO no latest data 240506

# %% Get time
timeNow = datetime.datetime.now()
timeFormat = timeNow.strftime("%Y-%m-%d")
timeFormatDir = timeNow.strftime("%y%m%d")
print(timeFormat)

# %% Change dir and add script to path
macPath = "".join(
    [
        "/Users/durack1/sync/Docs/admin/LLNL/25/191127_WCRP-WGCM-CMIP/",
        "cmip6_dataset_counts",
    ]
)
os.chdir(macPath)
# Now change to dated subdir
print("CWD:", os.getcwd())
if os.path.isdir(timeFormatDir):
    os.rmdir(timeFormatDir)
os.makedirs(timeFormatDir)
os.chdir(timeFormatDir)
# Add macPath to python path
sys.path.insert(0, macPath)

# %% Loop through activity_id entries for cumulative DATASET totals
keys = activity_id.keys()
for key in keys:
    if key in ["CORDEX", "VIACSAB"]:
        print("Skipping:", key)
        continue
    else:
        print(key)
        cmd = "".join(
            [
                "python ",
                os.path.join(gitPath, "esgfDataPubPlots.py"),
                " --project=CMIP6 --activity_id=",
                key,
                " --start_date=2018-07-01 --end_date=",
                timeFormat,
                " --cumulative",
            ]
        )
        cmd = shlex.split(cmd)
        print(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if "403 Forbidden error" in str(stdout):
            print("\nSOLR index inaccessible.. exiting\n")
            sys.exit()
        stdout, stderr

# And generate CMIP6 complete project totals
cmd = "".join(
    [
        "python ",
        os.path.join(gitPath, "esgfDataPubPlots.py"),
        " --project=CMIP6 --start_date=2018-07-01 --end_date=",
        timeFormat,
        " --cumulative",
    ]
)
cmd = shlex.split(cmd)
print(cmd)
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
stdout, stderr

# python esgfDataPubPlots.py --project=CMIP6 --activity_id=CMIP --start_date=2018-07-01 --end_date=2020-04-07 --cumulative

# %% Loop through activity_id entries for cumulative DATA FOOTPRINT totals
keys = activity_id.keys()
for key in keys:
    if key in ["CORDEX", "VIACSAB"]:
        print("Skipping:", key)
        continue
    else:
        print(key)
        cmd = "".join(
            [
                "python ",
                os.path.join(gitPath, "esgfDataFootprintPlots.py"),
                " --project=CMIP6 --activity_id=",
                key,
                " --start_date=2018-07-01 --end_date=",
                timeFormat,
                " --cumulative --latest --distinct",
            ]
        )
        cmd = shlex.split(cmd)
        print(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout, stderr

# %% Loop through institution_id entries for cumulative DATA FOOTPRINT totals
keys = institution_id.keys()
for key in keys:
    if key in ["MESSy_Consortium", "NASA-GSFC", "PCMDI", "PNNL-WACCEM", "RUBISCO"]:
        print("Skipping:", key)
        continue
    else:
        print(key)
        cmd = "".join(
            [
                "python ",
                os.path.join(gitPath, "esgfDataFootprintPlots.py"),
                " --project=CMIP6 --institution_id=",
                key,
                " --start_date=2018-07-01 --end_date=",
                timeFormat,
                " --cumulative --latest --distinct",
            ]
        )
        cmd = shlex.split(cmd)
        print(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout, stderr

# And generate CMIP6 complete project totals
cmd = "".join(
    [
        "python ",
        os.path.join(gitPath, "esgfDataFootprintPlots.py"),
        " --project=CMIP6 --start_date=2018-07-01 --end_date=",
        timeFormat,
        " --cumulative --latest --distinct",
    ]
)

cmd = shlex.split(cmd)
print(cmd)
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
stdout, stderr
