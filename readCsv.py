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

import csv
import datetime
import glob
import os
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num
import matplotlib.pyplot as plt
import numpy as np

# import pdb

# %% time labels
timeNow = datetime.datetime.now()
timeFormat = timeNow.strftime("%y%m%dT%H%M%S")
timeFormatDir = timeNow.strftime("%y%m%d")

# %% Set home dir
homePath = "".join(
    [
        "/Users/durack1/sync/Docs/admin/LLNL/24/191127_WCRP-WGCM-CMIP/",
        "cmip6_dataset_counts",
    ]
)

# %% DATASETS

# %% Read available files
os.chdir(homePath)
csvFiles = glob.glob(os.path.join(timeFormatDir, "*_dataset_*_counts_*.csv"))
csvFiles.sort()
# Create dictionary
files = {}
for count, actId in enumerate(csvFiles):
    # print('{:02d}'.format(count),actId,len(actId.split('_')))
    actIdSplit = actId.split("_")
    # print(actIdSplit[-2])
    dates = actIdSplit[-1].split("-")[-1].split(".")[0]
    year = int(dates[0:4])
    month = int(dates[4:6])
    day = int(dates[-2:])
    # print(year,month,day)
    files[actIdSplit[-2]] = actId

# print(files)
actCount = len(files)

# %% Create time axis
startTime = datetime.date(2018, 7, 2)
endTime = datetime.date(year, month, day)
times = endTime - startTime  # days=642

dateList = [startTime + datetime.timedelta(days=x) for x in range(times.days)]
# print(dateList)
# dateList = np.array(dateList)
# print(len(dateList))
dateCount = len(dateList)

# %% Create numpy array
arr1 = np.zeros([dateCount, actCount + 1])
for count, x in enumerate(dateList):
    arr1[count, 0] = x.toordinal()

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
    #    arr1[x,count+1] = tmpCount[tmpTimeInd[dateMatch]]
    # Write data to array - using full time axis
    for dateMatch, x in enumerate(dateList):
        for dateMatch2, y in enumerate(tmpTime):
            # Catch case where times match
            if x == y:
                # print('dateList:',dateList[dateMatch],tmpTime[dateMatch2],':tmpTime')
                arr1[dateMatch, count + 1] = tmpCount[dateMatch2]
                break
            # Catch case where no match, use previous timestemp value
            elif dateMatch2 == len(tmpTime) - 1:
                arr1[dateMatch, count + 1] = arr1[dateMatch - 1, count + 1]

# %% Print arr1
# print(arr1)
# print('arr1 shape:',arr1.shape)
# print(files.keys())

# %% Now plot - https://python-graph-gallery.com/250-basic-stacked-area-chart/

xtick_locator = AutoDateLocator()
xtick_formatter = AutoDateFormatter(xtick_locator)

# Setup variables
# time axis and arrays
x = date2num(dateList)
y = arr1[:, 2:]  # Omit CMIP6 cumulative
# print('dateList: ',len(dateList))
# print('y shape:',y.shape)
y = y.swapaxes(0, 1)
# print('y shape:',y.shape)
# Legend labels
actLabels = []
for count, val in enumerate(list(files.keys())):
    if val == "CMIP6":
        continue  # Skip totals
    # print(count,val)
    # print(val,int(arr1[-1,count+1]))
    actLabels.append(" ".join([val, str(int(arr1[-1, count + 1]))]))
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
# plt.stackplot(x,y,labels=list(files.keys()),colors=colList)
plt.stackplot(x, y, labels=actLabels, colors=colList)
legHandle = plt.legend(
    loc="upper left", ncol=2, fontsize=8, bbox_to_anchor=(0.0, 0.999)
)
plt.title(
    "".join(
        [
            "Federated CMIP6 cumulative dataset count (Updated: ",
            timeNow.strftime("%Y-%m-%d"),
            ")",
        ]
    )
)
plt.xlabel("Date")
plt.ylabel("Dataset counts (Millions, 1e6)")
yticks = np.arange(0, 7.5e6, 5e5)
ylabels = []
for count, val in enumerate(yticks):
    if count in [1, 3, 5, 7, 9, 11, 13]:
        val2 = "".join([str(int(val / 1e6)), ".5"])
        print(count, val, val2)
        ylabels.append(val2)
    else:
        ylabels.append(int(val / 1e6))
print("yticks:", yticks)
print("ylabels:", ylabels)
# sys.exit()
plt.yticks(yticks, ylabels)
plt.subplots_adjust(left=0.06, right=0.96, bottom=0.08, top=0.95, wspace=0, hspace=0)
anoStr = "".join(["CMIP6 total datasets: ", str(int(arr1[-1, 1]))])
print(anoStr)
# plt.annotate(anoStr,xy=(dateList[0],1.95e6),xytext=(dateList[0],1.95e6))
dateTweak = date2num(datetime.date(2018, 5, 1))
datasetNumTweak = 4.2e6
plt.annotate(
    anoStr, xy=(dateTweak, datasetNumTweak), xytext=(dateTweak, datasetNumTweak)
)
print("dateList[0]:", dateList[0])
# sys.exit()
plt.savefig("_".join([timeFormat, "ESGF-PublicationStats.png"]))

# %%
# print(dateList[0],dateList[-1])
# print(['dateList len:',len(dateList)])
# print(tmpTime[0])
# print(['tmpTime len: ',len(tmpTime)])
# print(['tmpCount len:',len(tmpCount)])
# for count,x in enumerate(dateListInd):
#    print('dateListInd:',dateList[dateListInd[count]],tmpTime[tmpTimeInd[count]],':tmpTimeInd')


# %% DATASET FOOTPRINTS

# %% Read available files
os.chdir(homePath)
csvFiles = glob.glob(os.path.join(timeFormatDir, "*_datasets_*_footprint_*.csv"))
csvFiles.sort()
# Create dictionary
files = {}
for count, actId in enumerate(csvFiles):
    # print('{:02d}'.format(count),actId,len(actId.split('_')))
    actIdSplit = actId.split("_")
    # print(actIdSplit[-2])
    dates = actIdSplit[-1].split("-")[-1].split(".")[0]
    year = int(dates[0:4])
    month = int(dates[4:6])
    day = int(dates[-2:])
    # print(year,month,day)
    files[actIdSplit[-2]] = actId

# print(files)
actCount = len(files) + 2  # Add missing MIPs (8 DynVarMIP, 20 SIMIP)

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
arr2 = np.zeros([dateCount, actCount + 1])
for count, x in enumerate(dateList):
    arr2[count, 0] = x.toordinal()

# %% Read CSV
offset = 0  # initialize variable
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

    if count in [0, 8, 19]:  # Deal with missing 8 DynVarMIP, 20 SIMIP
        offset = offset + 1
        print("offset:", offset)
    for dateMatch, x in enumerate(dateList):
        for dateMatch2, y in enumerate(tmpTime):
            # Catch case where times match
            if x == y:
                # print('dateList:',dateList[dateMatch],tmpTime[dateMatch2],':tmpTime')
                # arr2[dateMatch, count+1] = tmpCount[dateMatch2]
                arr2[dateMatch, count + offset] = tmpCount[dateMatch2]
                break
            # Catch case where no match, use previous timestamp value
            elif dateMatch2 == len(tmpTime) - 1:
                arr2[dateMatch, count + offset] = arr2[dateMatch - 1, count + offset]

# %% Print arr2
# print(arr2)
# print('arr2 shape:',arr2.shape)
# print(files.keys())

# %% Now plot - https://python-graph-gallery.com/250-basic-stacked-area-chart/

xtick_locator = AutoDateLocator()
xtick_formatter = AutoDateFormatter(xtick_locator)

# Setup variables
# time axis and arrays
x = date2num(dateList)
y = arr2[:, 2:]  # Omit CMIP6 cumulative
y = y / 1e15  # Scale from bytes to PB 10^15
# print('values:',y[:,0])
# print('dateList: ',len(dateList))
# print('y shape:',y.shape)
y = y.swapaxes(0, 1)
# print('y shape:',y.shape)
# Legend labels
actLabels = []
offset = 1
for count, val in enumerate(list(files.keys())):
    if val == "CMIP6":
        continue  # Skip totals
    if count == 8:
        actLabels.append("DynVarMIP")
        offset = offset + 1
        pass
    if count == 19:
        actLabels.append("SIMIP")
        offset = offset + 1
        pass
    # print(count,val)
    # print(val,int(arr2[-1,count+1]))
    # actLabels.append(' '.join([val, str(int(arr2[-1, count+1]))]))
    # actLabels.append(' '.join([val, str(int(arr2[-1, count+1]/1e12))]))
    actLabels.append(" ".join([val, str(int(arr2[-1, count + offset] / 1e12))]))
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
# plt.stackplot(x,y,labels=list(files.keys()),colors=colList)
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
"""
for count,val in enumerate(yticks):
    if count in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
        val2 = ''.join([str(int(val)), '.5'])
        print(count, val, val2)
        ylabels.append(val2)
    else:
        ylabels.append(int(val))
"""
for count, val in enumerate(yticks):
    ylabels.append(val)
print("yticks:", yticks)
print("ylabels:", ylabels)
# sys.exit()
plt.yticks(yticks, ylabels)
plt.subplots_adjust(left=0.06, right=0.96, bottom=0.08, top=0.95, wspace=0, hspace=0)
anoStr = "".join(
    ["CMIP6 total 'latest' datasets (TeraByte, 1e12): ", str(int(arr2[-1, 1] / 1e12))]
)
print(anoStr)
# plt.annotate(anoStr,xy=(dateList[0],1.95e6),xytext=(dateList[0],1.95e6))
dateTweak = date2num(datetime.date(2018, 5, 1))
datasetNumTweak = 8.75
plt.annotate(
    anoStr, xy=(dateTweak, datasetNumTweak), xytext=(dateTweak, datasetNumTweak)
)
print("dateList[0]:", dateList[0])
# print(leg2.get_frame().get_bbox().bounds)
# pdb.set_trace()
# sys.exit()
plt.savefig("_".join([timeFormat, "ESGF-PublicationStatsPB.png"]))

# %%
# print(dateList[0],dateList[-1])
# print(['dateList len:',len(dateList)])
# print(tmpTime[0])
# print(['tmpTime len: ',len(tmpTime)])
# print(['tmpCount len:',len(tmpCount)])
# for count,x in enumerate(dateListInd):
#    print('dateListInd:',dateList[dateListInd[count]],tmpTime[tmpTimeInd[count]],':tmpTimeInd')
