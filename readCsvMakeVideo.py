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
PJD 19 May 2022 - Update for multi-file output PB only (adapted from readCsv.py)
PJD 17 Jan 2023 - Update homePath 22 -> 23
PJD  6 May 2024 - Updated to sync with latest readCsv.py
                TODO: get dynamic legend info from plot

@author: durack1
"""

import csv
import datetime
import glob
import os
import pdb
import shutil
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num
import matplotlib.pyplot as plt
import numpy as np

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
# create zeros array to fill incrementally
y2 = np.zeros([y.shape[0], y.shape[1]])

for val1 in x:
    # create array to plot
    step = int(val1 - x[0])
    if val1 == len(x) - 1:
        print("if val1 == len(x) -1")
        pdb.set_trace()  # never reached?
        continue

    # Legend labels
    actLabels = []
    offset = 1
    for count, val2 in enumerate(list(files.keys())):
        if val2 == "CMIP6":
            continue  # Skip totals
        if count == 8:
            actLabels.append("DynVarMIP")
            offset = offset + 1
            pass
        if count == 19:
            actLabels.append("SIMIP")
            offset = offset + 1
            pass
        # print(count,val2)
        print(
            "actLabels:",
            val2,
            int(arr2[-1, count + 1]),
            "step:",
            step,
            "count:",
            count,
            "offset:",
            offset,
        )
        if step == 2134:
            pdb.set_trace()
        actLabel = " ".join([val2, str(int(arr2[step, count + offset] / 1e12))]).ljust(
            16
        )
        actLabels.append(actLabel)
    # print(actLabels)

    # Basic stacked area chart
    y2[:, 0:step] = y[:, 0:step]
    # create plot
    fig = plt.figure(figsize=(9, 6), dpi=300)  # Defaults to 6.4,4.8
    ax = plt.subplot(1, 1, 1)
    # https://jonathansoma.com/lede/data-studio/matplotlib/list-all-fonts-available-in-matplotlib-plus-samples/
    # https://matplotlib.org/stable/api/font_manager_api.html#matplotlib.font_manager.FontManager.findfont
    # https://datascienceparichay.com/article/change-font-type-in-matplotlib-plots/
    # plt.rcParams.update({'font.monospace': 'Courier New'}
    #                    )  # doesn't seem to work
    # plt.rcParams.keys()
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
    plt.stackplot(x, y2, labels=actLabels, colors=colList)
    # https://stackoverflow.com/questions/21933187/how-to-change-legend-fontname-in-matplotlib
    leg2 = plt.legend(
        loc="upper left", ncol=2, prop={"family": "Microsoft Sans Serif", "size": 8}
    )

    # Controlling legend sizing
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html

    print(leg2.keys())
    pdb.set_trace()

    # loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5)

    plt.title(
        "".join(
            [
                "Federated CMIP6 cumulative dataset footprint (Updated: ",
                timeNow.strftime("%Y-%m-%d"),
                ")",
            ]
        ),
        fontname="Microsoft Sans Serif",
    )
    plt.xlabel("Date", fontname="Microsoft Sans Serif")
    plt.ylabel("Dataset size (PetaByte, 1e15)", fontname="Microsoft Sans Serif")
    yticks = np.arange(0, 16, 1)
    ylabels = []
    """
    for count,val3 in enumerate(yticks):
        if count in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
            val = ''.join([str(int(val3)), '.5'])
            print(count, val, val3)
            ylabels.append(val)
        else:
            ylabels.append(int(val))
    """
    for count, val3 in enumerate(yticks):
        ylabels.append(val3)
    print("yticks:", yticks)
    print("ylabels:", ylabels)
    plt.yticks(yticks, ylabels, fontname="Microsoft Sans Serif")
    plt.yticks(fontname="Microsoft Sans Serif")
    plt.subplots_adjust(
        left=0.06, right=0.96, bottom=0.08, top=0.95, wspace=0, hspace=0
    )
    anoStr = "".join(
        [
            "CMIP6 total 'latest' datasets (TeraByte, 1e12): ",
            str(int(arr2[step, 1] / 1e12)),
        ]
    )
    print(anoStr)
    # plt.annotate(anoStr,xy=(dateList[0],1.95e6),xytext=(dateList[0],1.95e6))
    dateTweak = date2num(datetime.date(2018, 5, 1))
    datasetNumTweak = 9.25
    plt.annotate(
        anoStr,
        xy=(dateTweak, datasetNumTweak),
        xytext=(dateTweak, datasetNumTweak),
        fontname="Microsoft Sans Serif",
    )
    print("dateList:", dateList[step])
    print("timeCount:", str(step), step)
    outDir = "-".join(["demo", timeNow.strftime("%y%m%d")])

    # Cleanup dest dir
    print("val1:", val1, x[0])
    if val1 == x[0]:
        if os.path.exists(outDir):
            shutil.rmtree(outDir)
        os.makedirs(outDir)
    plt.savefig(
        os.path.join(
            "-".join(["demo", timeNow.strftime("%y%m%d")]),
            "_".join(["{:04d}".format(step), "ESGF-PubStatsPB-MSSans.png"]),
        )
    )
    plt.close()

# %% call to ffmpeg - 2 steps to prepare a powerpoint-ready graphic object

# (ffmpeg700) ml-9953350:demo-240506 durack1$ s
# (ffmpeg700) ml-9953350:demo-240506 durack1$ cd Docs/admin/LLNL/24/191127_WCRP-WGCM-CMIP/cmip6_dataset_counts/demo-240506/
# (ffmpeg700) ml-9953350:demo-240506 durack1$ ffmpeg -framerate 48 -i %04d_ESGF-PubStatsPB-MSSans.png 240506_output_48.mp4
# (ffmpeg700) ml-9953350:demo-240506 durack1$ ffmpeg -i 240506_output_48.mp4 -c:v libx264 -preset slow -profile:v high -level:v 4.0 -pix_fmt yuv420p -crf 22 -codec:a aac 240506_output_48_new.mp4

# old
# (ffmpeg512) ml-9953350:~ durack1$ s
# /Users/durack1/sync
# (ffmpeg512) ml-9953350:sync durack1$ cd Docs/admin/LLNL/23/191127_WCRP-WGCM-CMIP/cmip6_dataset_counts/demo/
# (ffmpeg512) ml-9953350:demo durack1$ ffmpeg -framerate 48 -i %04d_ESGF-PubStatsPB-MSSans.png 230117_output_48.mp4

# (ffmpeg512) ml-9953350:demo durack1$ ffmpeg -i 230117_output_48.mp4 -c:v libx264 -preset slow -profile:v high -level:v 4.0 -pix_fmt yuv420p -crf 22 -codec:a aac 230117_output_48_new.mp4

# https://trac.ffmpeg.org/wiki/Slideshow
# (ffmpeg501) ml-9585568:demo durack1$ ffmpeg -framerate 48 -i %04d_ESGF-PubStatsPB.png output_48.mp4
# https://stackoverflow.com/questions/44130350/convert-videos-with-ffmpeg-to-powerpoint-2016-compatible-video-format
# (ffmpeg501) ml-9585568:demo durack1$ ffmpeg -i output_48.mp4 -c:v libx264 -preset slow -profile:v high -level:v 4.0 -pix_fmt yuv420p -crf 22 -codec:a aac output_48_new.mp4  # for powerpoint
