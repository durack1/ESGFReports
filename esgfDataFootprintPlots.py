#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 21:51:58 2020

PJD  8 Dec 2020 - Downloaded from
https://raw.githubusercontent.com/mauzey1/esgf-utils/cmip6_pub_history/update-reports/esgf_data_footprint_plots.py
PJD 10 Dec 2020 - Updated to include date prefix in filenames
PJD  6 Dec 2021 - If error occurs at js = json.loads(req.text),
                  check open access https://esgf-node.llnl.gov/solr/datasets/select
PJD 16 Mar 2022 - Updated to catch "403 Forbidden" error with SOLR index query
PJD 13 Sep 2022 - Updated sys.exit to raise TimeoutError
PJD 20 Apr 2024 - Updated to print query_url for debugging; flake8 autoformatting
PJD  6 May 2024 - Adding institution_id
PJD  9 May 2024 - Update _instId- to -instId- to allow PB separation from MIPs to institution_id
PJD 23 Jun 2025 - Update to include hard-coded shards list, due to esg-search being offline

@author: @mauzey1, @durack1
"""

import os
import csv
import json
import datetime
import argparse
import numpy
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# import collections
# import sys

timeNow = datetime.datetime.now()
timeFormat = timeNow.strftime("%y%m%d")


def get_solr_query_url():
    search_url = (
        "https://esgf-node.llnl.gov/esg-search/search/"
        "?limit=0&format=application%2Fsolr%2Bjson"
    )

    req = requests.get(search_url)
    js = json.loads(req.text)
    # shards = js["responseHeader"]["params"]["shards"]. # esg-search now offline
    shards = ",".join(
        [
            "localhost:8983/solr/files",
            "localhost:8985/solr/files",
            "localhost:8987/solr/files",
            "localhost:8988/solr/files",
            "localhost:8990/solr/files",
            "localhost:8993/solr/files",
            "localhost:8995/solr/files",
        ]
    )

    solr_url = (
        "https://esgf-node.llnl.gov/solr/files/query"
        "?q=*:*&wt=json"
        "&shards={shards}&{{query}}"
    )
    # other nodes
    # esgf.ceda.ac.uk
    # esgf-data.dkrz.de

    return solr_url.format(shards=shards)


def get_data_footprint_time_data(
    project,
    start_date,
    end_date,
    activity_id=None,
    experiment_id=None,
    institution_id=None,
    cumulative=False,
    latest=None,
    replica=None,
):

    date_format = "%Y-%m-%dT%H:%M:%SZ"
    start_str = start_date.strftime(date_format)
    end_str = end_date.strftime(date_format)

    solr_url = get_solr_query_url()

    query = (
        "rows=0&fq=project:{project}"
        "&json.facet.daily_footprint.type=range"
        "&json.facet.daily_footprint.field=_timestamp"
        '&json.facet.daily_footprint.start="{start_date}"'
        '&json.facet.daily_footprint.end="{end_date}"'
        '&json.facet.daily_footprint.gap="%2B1DAY"'
        '&json.facet.daily_footprint.facet={{data_footprint:"sum(size)"}}'
    )
    if activity_id:
        query += "&fq=activity_id:{activity_id}"
    if experiment_id:
        query += "&fq=experiment_id:{experiment_id}"
    if institution_id:
        query += "&fq=institution_id:{institution_id}"
    if latest is not None:
        query += "&fq=latest:{latest}"
    if replica is not None:
        query += "&fq=replica:{replica}"
    query_url = solr_url.format(
        query=query.format(
            project=project,
            start_date=start_str,
            end_date=end_str,
            activity_id=activity_id,
            experiment_id=experiment_id,
            institution_id=institution_id,
            latest=latest,
            replica=replica,
        )
    )

    print("query_url:", query_url)

    req = requests.get(query_url)
    # check solr index accessible
    if "403 Forbidden" in req.text:
        print("***")
        print("SOLR index inaccessible, 403 Forbidden error, exiting...")
        print("***")
        # sys.exit()
        raise TimeoutError
    js = json.loads(req.text)

    print(js.keys())
    print(js["facets"].keys())
    daily_footprint = js["facets"]["daily_footprint"]["buckets"]
    timestamp = []
    data_footprint = []
    for df in daily_footprint:
        timestamp.append(df["val"])
        if "data_footprint" in df:
            data_footprint.append(df["data_footprint"])
        else:
            data_footprint.append(0)

    datetimes = [datetime.datetime.strptime(t, date_format) for t in timestamp]

    if cumulative:
        data_footprint = numpy.cumsum(data_footprint)

    return (datetimes, data_footprint)


def gen_plot(
    project,
    start_date,
    end_date,
    ymin=None,
    ymax=None,
    activity_id=None,
    experiment_id=None,
    institution_id=None,
    cumulative=False,
    latest=None,
    replica=None,
    output_dir=None,
):

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    # store data in CSV files
    print("Getting ESGF data from {} to {}".format(start_str, end_str))
    datetimes, data_footprint = get_data_footprint_time_data(
        project=project,
        start_date=start_date,
        end_date=end_date,
        activity_id=activity_id,
        experiment_id=experiment_id,
        institution_id=institution_id,
        cumulative=cumulative,
        latest=latest,
        replica=replica,
    )

    if cumulative:
        filename = "esgf_datasets_publication_cumulative_data_footprint_{}".format(
            project
        )
    else:
        filename = "esgf_datasets_publication_data_footprint_{}".format(project)
    if activity_id:
        filename += "_{}".format(activity_id)
    if experiment_id:
        filename += "_{}".format(experiment_id)
    if institution_id:
        filename += "-instId-{}".format(institution_id)
    filename += "_{}-{}".format(start_str, end_str)

    filename = "_".join([timeFormat, filename])  # Append date prefix
    filename = os.path.join(output_dir, filename)

    csv_filename = filename + ".csv"

    print("Writing data to {}".format(csv_filename))
    with open(csv_filename, "w") as csv_file:
        fieldnames = ["date", "data_footprint"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for dt, df in zip(datetimes, data_footprint):
            writer.writerow({"date": dt, "data_footprint": df})

    # plot data
    plot_filename = filename + ".png"
    print("Saving plot to {}".format(plot_filename))

    fig, ax = plt.subplots(figsize=(10, 5))

    # convert footprint to terabytes
    data_footprint = [df / (10**12) for df in data_footprint]

    @ticker.FuncFormatter
    def major_formatter(x, pos):
        return "%.2f TB" % x

    ax.plot(datetimes, data_footprint)

    ylim_min = ymin if ymin else numpy.min(data_footprint)
    ylim_max = ymax if ymax else numpy.max(data_footprint)
    ax.set(xlim=(start_date, end_date), ylim=(ylim_min, ylim_max))

    title = "{} ".format(project)
    if activity_id:
        title += "{} ".format(activity_id)
    if experiment_id:
        title += "{} ".format(experiment_id)
    if institution_id:
        title += "instId-{} ".format(institution_id)
    if cumulative:
        title += "cumulative data footprint on ESGF"
    else:
        title += "data footprint on ESGF"

    ax.set(xlabel="date", ylabel="data footprint", title=title)
    ax.yaxis.set_major_formatter(major_formatter)
    ax.grid()

    fig.savefig(plot_filename)


def main():

    parser = argparse.ArgumentParser(
        description="Gather data footprint per day from ESGF"
    )
    parser.add_argument(
        "--project",
        "-p",
        dest="project",
        type=str,
        default="CMIP6",
        help="MIP project name (default is CMIP6)",
    )
    parser.add_argument(
        "--activity_id",
        "-ai",
        dest="activity_id",
        type=str,
        default=None,
        help="MIP activity id (default is None)",
    )
    parser.add_argument(
        "--experiment_id",
        "-ei",
        dest="experiment_id",
        type=str,
        default=None,
        help="MIP experiment id (default is None)",
    )
    parser.add_argument(
        "--institution_id",
        "-ii",
        dest="institution_id",
        type=str,
        default=None,
        help="MIP institution id (default is None)",
    )
    parser.add_argument(
        "--start_date",
        "-sd",
        dest="start_date",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format (default is None)",
    )
    parser.add_argument(
        "--end_date",
        "-ed",
        dest="end_date",
        type=str,
        default=None,
        help="End date in YYYY-MM-DD format (default is None)",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        type=str,
        default=os.path.curdir,
        help="Output directory (default is current directory)",
    )
    parser.add_argument(
        "--ymax",
        dest="ymax",
        type=int,
        default=None,
        help="Maximum of y-axis for data footprint plot (default is None)",
    )
    parser.add_argument(
        "--ymin",
        dest="ymin",
        type=int,
        default=None,
        help="Minimum of y-axis for data footprint plot (default is None)",
    )
    parser.add_argument(
        "--cumulative",
        dest="cumulative",
        action="store_true",
        help="Get cumulative data footprint of datasets over time (default is False)",
    )
    parser.add_argument(
        "--latest", dest="latest", action="store_true", help="Find the latest datasets"
    )
    parser.add_argument(
        "--deprecated",
        dest="latest",
        action="store_false",
        help="Find the deprecated datasets",
    )
    parser.add_argument(
        "--replica",
        dest="replica",
        action="store_true",
        help="Find datasets that are replicas",
    )
    parser.add_argument(
        "--distinct",
        dest="replica",
        action="store_false",
        help="Find datasets that are distinct",
    )
    parser.set_defaults(cumulative=False, latest=None, replica=None)
    args = parser.parse_args()

    if args.start_date is None:
        print("You must enter a start date.")
        return
    else:
        try:
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect start date format, should be YYYY-MM-DD")
            return

    if args.end_date is None:
        print("You must enter an end date.")
        return
    else:
        try:
            end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect end date format, should be YYYY-MM-DD")
            return

    if not os.path.isdir(args.output):
        print("{} is not a directory. Exiting.".format(args.output))
        return

    gen_plot(
        args.project,
        start_date,
        end_date,
        args.ymin,
        args.ymax,
        args.activity_id,
        args.experiment_id,
        args.institution_id,
        args.cumulative,
        args.latest,
        args.replica,
        args.output,
    )


if __name__ == "__main__":
    main()
