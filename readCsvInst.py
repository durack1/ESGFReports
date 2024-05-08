#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 20:09:50 2020

Script to read CSV files and assign entries to times
Format: 2018-07-02 00:00:00,292

PJD  4 May 2020 - Updated to write files to dated subdir
PJD  4 May 2020 - Use cdatN200202 durack1ml conda env for new python/matplotlib
                 (colour palette different in early python instances)
PJD 24 Aug 2020 - Updated total dataset count placement (y-axis) due to data growth
PJD 24 Aug 2020 - Updated x-axis/subplot boundaries to deal with expanding time axis
PJD  8 Dec 2020 - Updated to add plot of data footprint (rather than just datasets)
PJD  9 Dec 2020 - Update to include missing MIPs in data footprint (8 DynVarMIP, 20 SIMIP)
PJD 10 Dec 2020 - Further tweaks to correct MIP ordering in PB legend
PJD 31 Mar 2021 - PublicationStats - datasetNumTweak = 2.4e6 -> 2.95e6
PJD 31 Mar 2021 - PublicationStatsPB - datasetNumTweak = 5.5 -> 6.05
PJD 16 May 2021 - PublicationStats/PB - datasetNumTweak = 2.9e6 -> 3.2; 6.05 -> 6.2
PJD 16 May 2021 - PublicationStats - yticks - 4.5e6 -> 5.5e6, ylabs too
PJD  1 Sep 2021 - Update os.chdir -> homePath
PJD  1 Sep 2021 - PublicationStats - datasetNumTweak = 3.125e6 -> 3.4e6
PJD  5 Oct 2021 - Updated to attempt to dynamically locate text info
PJD  6 Dec 2021 - Added explicit str -> int conversion L249
PJD 16 Mar 2022 - Updated homePath
PJD 20 Mar 2022 - Update datasetNumTweak, y-axis lims
PJD 17 Jan 2023 - Update homePath 22 -> 23
PJD 23 Sep 2023 - Update to deal with >12 PB data, and total datasets 7.3 -> 8
PJD 27 Feb 2024 - Updated path from admin/23 -> 24
PJD 27 Feb 2024 - Updated yticks 0-13 -> 0-14
PJD 27 Feb 2024 - Updated 'latest' text 2018-06-03 -> 2018-05-01
PJD  8 Apr 2024 - Updated 'latest' text in count figure -> 2018-05-01; other minor tweaks
                TODO: get dynamic legend info from plot

@author: durack1
"""
# %% imports
import csv
import datetime
import glob
import os
import pdb
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num
import matplotlib.pyplot as plt
import numpy as np

# %% time labels
timeNow = datetime.datetime.now()
timeFormat = timeNow.strftime("%y%m%dT%H%M%S")
timeFormatDir = timeNow.strftime("%y%m%d")


timeFormatDir = "240506"


# %% Set home dir
homePath = "".join(
    [
        "/Users/durack1/sync/Docs/admin/LLNL/24/191127_WCRP-WGCM-CMIP/",
        "cmip6_dataset_counts",
    ]
)

# %% DATASET FOOTPRINTS

# %% Read available files
os.chdir(homePath)
csvFiles = glob.glob(
    os.path.join(timeFormatDir, "*_datasets_*_footprint_CMIP6_instId*.csv")
)
csvFiles.sort()
# Create dictionary
files = {}
for count, instId in enumerate(csvFiles):
    # print('{:02d}'.format(count),actId,len(actId.split('_')))
    instIdSplit = instId.split("_")
    # print(actIdSplit[-2])
    dates = instIdSplit[-1].split("-")[-1].split(".")[0]
    year = int(dates[0:4])
    month = int(dates[4:6])
    day = int(dates[-2:])
    # print(year,month,day)
    files[instIdSplit[-2].replace("instId-", "")] = instId

# print(files)
instCount = (
    len(files) + 5
)  # Add missing instIds "MESSy_Consortium", "NASA-GSFC", "PCMDI", "PNNL-WACCEM", "RUBISCO"

# %% Create time axis
startTime = datetime.date(2018, 7, 2)
endTime = datetime.date(int(year), int(month), int(day))
times = endTime - startTime  # days=642

dateList = [startTime + datetime.timedelta(days=x) for x in range(times.days)]
# print(dateList)
# dateList = np.array(dateList)
# print(len(dateList))
dateCount = len(dateList)

# %% Create numpy array
arr = np.zeros([dateCount, instCount + 1])
for count, x in enumerate(dateList):
    arr[count, 0] = x.toordinal()

# %% Read CSV
os.chdir(homePath)
for count, filePath in enumerate(files):
    print(count, filePath, files[filePath])
    tmpTime = []
    tmpCount = []
    # with open(files[filePath],newline='') as csvfile:
    with open(files[filePath]) as csvfile:
        tmp = csv.reader(csvfile, delimiter=",")
        for row in tmp:
            if row[0] == "date":
                continue
            # print(row)
            year, month, day = row[0].split("-")
            day = day.split(" ")[0]
            # print(year,month,day)
            tmpTime.append(datetime.date(int(year), int(month), int(day)))
            tmpCount.append(row[1])
            # print(tmpTime)
    # Check CMIP-piControl
    # if count == 2:
    # print('tmpCount:',filePath)
    # print(tmpCount)
    # Compare time axes
    inds = np.intersect1d(dateList, tmpTime, assume_unique=True, return_indices=True)
    intersects, dateListInd, tmpTimeInd = inds
    # print('inds len:',len(inds))
    # print('inds type:',type(inds))
    # print(inds)
    # print('dateListInd len:',len(dateListInd))
    # print(dateListInd)
    # print('tmpTimeInd len:',len(tmpTimeInd))
    # print(tmpTimeInd)
    # Write data to array - omits dates with no entry
    # for dateMatch,x in enumerate(dateListInd):
    #    print('dateListInd:',dateList[dateListInd[dateMatch]],tmpTime[tmpTimeInd[dateMatch]],':tmpTimeInd')
    #    arr2[x,count+1] = tmpCount[tmpTimeInd[dateMatch]]
    # Write data to array - using full time axis

    for dateMatch, x in enumerate(dateList):
        for dateMatch2, y in enumerate(tmpTime):
            # Catch case where times match
            if x == y:
                # print('dateList:',dateList[dateMatch],tmpTime[dateMatch2],':tmpTime')
                # arr2[dateMatch, count+1] = tmpCount[dateMatch2]
                arr[dateMatch, count] = tmpCount[dateMatch2]
                break
            # Catch case where no match, use previous timestamp value
            elif dateMatch2 == len(tmpTime) - 1:
                arr[dateMatch, count] = arr[dateMatch - 1, count]

# %% Print arr
# print(arr)
# print('arr shape:',arr.shape)
# print(files.keys())

# %% create US vs international composite
# for count, key in enumerate(files.keys()):
#  print(count, key)
USInds = [0, 15, 23, 28, 29, 34, 37, 40, 41, 42]
print("len(USInds):", len(USInds))
inds = np.arange(0, 44)
IntInds = list(set(USInds).symmetric_difference(set(inds)))
print("len(IntInds):", len(IntInds))
arr.shape
USarr = arr[:, USInds]
USarrComp = USarr.sum(axis=1)
print("USarr.shape:", USarr.shape)
Intarr = arr[:, IntInds]
IntarrComp = Intarr.sum(axis=1)
print("Intarr.shape:", Intarr.shape)
comparr = np.stack((USarrComp, IntarrComp), axis=1)


# %% Now plot all - https://python-graph-gallery.com/250-basic-stacked-area-chart/

xtick_locator = AutoDateLocator()
xtick_formatter = AutoDateFormatter(xtick_locator)

# Setup variables
# time axis and arrays
x = date2num(dateList)
y = arr / 1e15  # Scale from bytes to PB 10^15
y = y.swapaxes(0, 1)
# Legend labels
actLabels = []
offset = 1
for count, val in enumerate(list(files.keys())):
    actLabels.append(" ".join([val, str(int(arr[-1, count] / 1e12))]))
# print(actLabels)

# Basic stacked area chart.
fig = plt.figure(figsize=(9, 6), dpi=300)  # Defaults to 6.4,4.8
ax = plt.subplot(1, 1, 1)
ax.xaxis.set_major_locator(xtick_locator)
ax.xaxis.set_major_formatter(xtick_formatter)
# Create colour lookup
# https://stackoverflow.com/questions/8389636/creating-over-20-unique-legend-colors-using-matplotlib
NUM_COLORS = 23
colList = []
# https://matplotlib.org/tutorials/colors/colormaps.html#classes-of-colormaps
cm = plt.get_cmap("gist_rainbow")
cm = plt.get_cmap("tab20c")  # also tab 20b, tab20
for i in range(NUM_COLORS):
    colList.append(cm(1.0 * i / NUM_COLORS))
# print(colList)
plt.stackplot(x, y, labels=actLabels, colors=colList)
leg2 = plt.legend(loc="upper left", ncol=2, fontsize=8)
plt.title(
    "".join(
        [
            "Federated CMIP6 cumulative dataset footprint (Updated: ",
            timeNow.strftime("%Y-%m-%d"),
            ")",
        ]
    )
)
plt.xlabel("Date")
plt.ylabel("Dataset size (PetaByte, 1e15)")
yticks = np.arange(0, 15, 1)
ylabels = []

for count, val in enumerate(yticks):
    ylabels.append(val)
print("yticks:", yticks)
print("ylabels:", ylabels)
plt.yticks(yticks, ylabels)
plt.subplots_adjust(left=0.06, right=0.96, bottom=0.08, top=0.95, wspace=0, hspace=0)
dateTweak = date2num(datetime.date(2018, 5, 1))
datasetNumTweak = 8.75
print("dateList[0]:", dateList[0])
plt.savefig("_".join([timeFormat, "ESGF-PublicationStats-instId-PB.png"]))

# %% Now plot US/Int - https://python-graph-gallery.com/250-basic-stacked-area-chart/

xtick_locator = AutoDateLocator()
xtick_formatter = AutoDateFormatter(xtick_locator)

# Setup variables
# time axis and arrays
x = date2num(dateList)
y = comparr / 1e15  # Scale from bytes to PB 10^15
y = y.swapaxes(0, 1)
# Legend labels
actLabels = []
offset = 1
actLabels = ["US Modeling Groups", "International Modeling Groups"]

# Basic stacked area chart.
fig = plt.figure(figsize=(9, 6), dpi=300)  # Defaults to 6.4,4.8
ax = plt.subplot(1, 1, 1)
ax.xaxis.set_major_locator(xtick_locator)
ax.xaxis.set_major_formatter(xtick_formatter)
NUM_COLORS = 23
colList = []
# https://matplotlib.org/tutorials/colors/colormaps.html#classes-of-colormaps
cm = plt.get_cmap("gist_rainbow")
cm = plt.get_cmap("tab20c")  # also tab 20b, tab20
# for i in range(NUM_COLORS):
for i in [22, 5]:  # 5 orange, 22/23 grey
    colList.append(cm(1.0 * i / NUM_COLORS))

plt.stackplot(x, y, labels=actLabels, colors=colList)
leg2 = plt.legend(loc="upper left", ncol=1, fontsize=14)
plt.title(
    "".join(
        [
            "Federated CMIP6 cumulative dataset footprint (Updated: ",
            timeNow.strftime("%Y-%m-%d"),
            ")",
        ]
    )
)
plt.xlabel("Date")
plt.ylabel("Dataset size (PetaByte, 1e15)")
yticks = np.arange(0, 15, 1)
ylabels = []

for count, val in enumerate(yticks):
    ylabels.append(val)
print("yticks:", yticks)
print("ylabels:", ylabels)
plt.yticks(yticks, ylabels)
plt.subplots_adjust(left=0.06, right=0.96, bottom=0.08, top=0.95, wspace=0, hspace=0)
dateTweak = date2num(datetime.date(2018, 5, 1))
datasetNumTweak = 8.75

print("dateList[0]:", dateList[0])
plt.savefig("_".join([timeFormat, "ESGF-PublicationStats-instIdUSInt-PB.png"]))

# %%
# print(dateList[0],dateList[-1])
# print(['dateList len:',len(dateList)])
# print(tmpTime[0])
# print(['tmpTime len: ',len(tmpTime)])
# print(['tmpCount len:',len(tmpCount)])
# for count,x in enumerate(dateListInd):
#    print('dateListInd:',dateList[dateListInd[count]],tmpTime[tmpTimeInd[count]],':tmpTimeInd')
