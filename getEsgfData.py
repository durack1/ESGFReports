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

@author: durack1
"""
import datetime
import os
import pkg_resources
import shlex
import subprocess
import sys

# add additional library imports used by called functions
import numpy
import matplotlib

# %% Check Python min version
pyVerInfo = sys.version_info
if pyVerInfo.major < 3:
    print("Python version", pyVerInfo.major, "not supported, quitting..")
    sys.exit()

# %% Check numpy installed
required = {"numpy"}
installed = {pkg.key for pkg in pkg_resources.working_set}
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
activity_id = {
    "AerChemMIP": "Aerosols and Chemistry Model Intercomparison Project",
    "C4MIP": "Coupled Climate Carbon Cycle Model Intercomparison Project",
    "CDRMIP": "Carbon Dioxide Removal Model Intercomparison Project",
    "CFMIP": "Cloud Feedback Model Intercomparison Project",
    "CMIP": "CMIP DECK: 1pctCO2, abrupt4xCO2, amip, esm-piControl, esm-historical, historical, and piControl experiments",
    "CORDEX": "Coordinated Regional Climate Downscaling Experiment",
    "DAMIP": "Detection and Attribution Model Intercomparison Project",
    "DCPP": "Decadal Climate Prediction Project",
    "DynVarMIP": "Dynamics and Variability Model Intercomparison Project",
    "FAFMIP": "Flux-Anomaly-Forced Model Intercomparison Project",
    "GMMIP": "Global Monsoons Model Intercomparison Project",
    "GeoMIP": "Geoengineering Model Intercomparison Project",
    "HighResMIP": "High-Resolution Model Intercomparison Project",
    "ISMIP6": "Ice Sheet Model Intercomparison Project for CMIP6",
    "LS3MIP": "Land Surface, Snow and Soil Moisture",
    "LUMIP": "Land-Use Model Intercomparison Project",
    "OMIP": "Ocean Model Intercomparison Project",
    "PAMIP": "Polar Amplification Model Intercomparison Project",
    "PMIP": "Palaeoclimate Modelling Intercomparison Project",
    "RFMIP": "Radiative Forcing Model Intercomparison Project",
    "SIMIP": "Sea Ice Model Intercomparison Project",
    "ScenarioMIP": "Scenario Model Intercomparison Project",
    "VIACSAB": "Vulnerability, Impacts, Adaptation and Climate Services Advisory Board",
    "VolMIP": "Volcanic Forcings Model Intercomparison Project",
}

# %% Get time
timeNow = datetime.datetime.now()
timeFormat = timeNow.strftime("%Y-%m-%d")
timeFormatDir = timeNow.strftime("%y%m%d")
print(timeFormat)

# %% Change dir and add script to path
macPath = "".join(
    [
        "/Users/durack1/sync/Docs/admin/LLNL/24/191127_WCRP-WGCM-CMIP/",
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
