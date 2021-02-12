#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for getting data into a format readable by the prediction model

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : prediction_model.py
Date    : Tuesday 05 January 2021
History : 05/01/2020 - v1.0 - Create project file
          12/01/2020 - v1.2 - Completed all functions to load DARWIN data from CSV and save to db
          20/01/2020 - v1.3 - Wrote function to handle HSP data from scraper

"""
import os
import glob
import csv
from datetime import datetime, timedelta
from data import services
import re
import sqlite3
import model.prediction_model as model

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Development"  # "Development" "Prototype" "Production"

"""
DARWIN data key columns to transform:
rid:     Train RTTI ID(Real-Time Trains Information Identifier), the date (YYYYMMDD) and a unique ID for that journey
tpl:     TIPLOC (Timing Point Location) code, the name of the points the given train passed - is usually also a station
wta:     Working Time of Arrival, the time that the train is supposed to arrive at the station represented in the TIPLOC
wtp:     Working Time of Passing, the time that the train is supposed to pass through the given TIPLOC
wtd:     Working Time of Departure, the time that the train is supposed to depart the station represented in the TIPLOC 
arr_et:  Estimated Arrival Time, the time DARWIN assumes the train arrived at the given TIPLOC, based on earlier actuals
pass_et: Estimated Passing Time, the time DARWIN assumes the train passed the given TIPLOC based on earlier actual times 
dep_et:  Estimated Departure Time, the time DARWIN assumes the train departed the given TIPLOC, based on earlier data
arr_at:  Actual Time of Arrival, the time the train actually arrived at the station represented in the TIPLOC
pass_at: Actual Time of Passing, the time the train actually passed the given TIPLOC 
dep_at:  Actual Time of Departure, the time the train actually departed the station represented in the TIPLOC 
"""


def raw(table, data_source):
    r"""Pull data from csv files, process for model and save to given table in given db

    Files are taken from \data\scraped and processed, then after writing are moved to \data\scraped\processed.
    :
    :param str data_source: Either "DARWIN" (a51/rdg) or "HSP" depending on data source.
    :param str table:       Table in DB to insert data into (will be created if it doesn't already exist)
    :raises sqlite3.Error:  If script can not connect to db
    """
    network = services.get_network("ga_intercity")
    valid_tpl = network.get_all_stations()  # only get data for stations in the network
    os.chdir(r".\data\scraped")
    for file in glob.glob("*.csv"):
        if data_source == "DARWIN":
            csv_data = __read_darwin_from_csv(file, valid_tpl)
        elif data_source == "HSP":
            csv_data = __read_hsp_from_csv(file, valid_tpl)
        else:
            print(data_source, "is not a valid data source. Currently reading only HSP and DARWIN formatted data.")
            return
        # could add weather data here

        train_data = []
        prev_delay = 0  # track what the delay was at the last station
        for i in range(0, len(csv_data)-1):  # skip the final row since it is None
            entry = csv_data[i]
            source, date, delay = entry_to_query(entry)
            delay_change = delay - prev_delay

            next_entry = csv_data[i + 1]
            if entry[0] != next_entry[0]:  # if we're on the last station (rid code change) process with no destination
                prev_delay = 0  # ready for the next rid
                stn_from   = stn_to = network.get_station(source)
            else:
                # print(entry[0])
                prev_delay = delay
                dest       = next_entry[1]
                path       = network.find_path(source, dest)
                stn_from   = path[0]
                stn_to     = path[1]

            processed_entry = query_to_input(stn_from, stn_to, date)
            processed_entry.append(delay)
            processed_entry.append(delay_change)
            # Might want to look for cancelled trains then add missing stops here, then process rid in one go.
            train_data.append(processed_entry)

        os.chdir(r"..")
        written = __write_to_db(table, train_data)
        os.chdir(r".\scraped")
        print("processed", written, "entries in file", file)

    # move all the files into \processed\ as a batch. This breaks if done on each iteration of previous loop instead.
    for file in glob.glob("*.csv"):
        path = os.path.dirname(os.path.abspath(__file__))
        os.replace(r"{}\scraped\{}".format(path, file), r"{}\scraped\processed\{}".format(path, file))


def __read_darwin_from_csv(file, valid_tpl):
    """Reads the provided DARWIN data CSV file and removes unneeded columns and rows.

    :param str file: Name of file to be processed

    :rtype: list[list[str]]
    :return: list of lists matching the processed rows and columns of the given CSV, with unneeded info removed
    """
    data = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[1] not in valid_tpl:  # skip every entry that isn't for a station listed in valid_tpl
                continue
            # delete columns pta, ptd, arr_wet, arr_atRemoved, pass_wet, pass_atRemoved, dep_wet, dep_atRemoved,
            # cr_code, lr_code
            del_cols = [20, 19, 15, 14, 12, 11, 9, 8, 3, 2]  # reversed, else index will go out of bounds
            for index in del_cols:
                del row[index]
            data.append(row)
        data.append([None, None])  # add an extra row to ensure there is no issues indexing
    return data


def __read_hsp_from_csv(file, valid_tpl):
    """Reads the provided HSP data CSV file and formats it to the same design as DARWIN.

    :param str file: Name of file to be processed

    :rtype: list[list[str]]
    :return: list of lists matching the processed rows and columns of the given CSV, with darwin info added
    """
    data = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # transform crs to tpl
            crs = row[1]
            conn = __connect_to_db()
            cur = conn.cursor()
            cur.execute(""" SELECT tpl FROM stations WHERE crs=? """, (crs,))
            tpl = cur.fetchone()
            if tpl is None:
                continue

            row[1] = tpl[0]
            if row[1] is None or row[1] not in valid_tpl:  # skip every entry that isn't for a station in the tpl list
                continue
            # format time to DARWIN time format (insert colons)
            for i in range(2, 6):
                if row[i] != "":
                    row[i] = row[i][:2] + ":" + row[i][2:]

            # format the file to match DARWIN format
            temp = row[2]; row[2] = row[3]; row[3] = temp  # swap ptd and pta
            row.insert(3, "")  # pad ptd out one place to match DARWIN wtd position
            row.insert(5, ""); row.insert(5, ""); row.insert(5, "")  # pad out dep_at and arr_at
            row.insert(9, "")  # pad out arr_at
            temp = row[8]; row[8] = row[10]; row[10] = temp  # swap dep_at and arr_at
            data.append(row)
        data.append([None, None])  # add an extra row to ensure there is no issues indexing
    return data


def __read_weather_data():  # TBA one day.
    pass


def user_to_query(source, destination, delay):
    """Takes information from the user and returns a valid input for the model

    :param str source: tpl code of the source station
    :param str destination: tpl code of the final destination on this journey
    :param int delay: number of minutes this journey has been delayed by

    :rtype: int
    :return: the amount of minutes the user will be delayed once they get to their final destination

    :raises ValueError: if stations given are not on this network
    """
    now     = datetime.now()
    network = services.get_network("ga_intercity")
    path = network.find_path(source, destination)
    path.append(path[-1])

    train_data = []
    for i in range(0, len(path)-1):
        stn_from = path[i]
        stn_to   = path[i+1]
        processed_entry = query_to_input(stn_from, stn_to, now)
        train_data.append(processed_entry)

    total_delay = int(delay)
    # Put data into the model here
    for train in train_data:
        total_delay += model.use_model(train, total_delay, network)

    return total_delay


def entry_to_query(entry):
    """Takes a line (entry) from the processed CSV file and forms a query (data matching one station input from user)

    :param list[str] entry: list of data: rid, tpl, wta, wtp, wtd, arr_et, pass_et, dep_et, arr_at, pass_at, dep_at
    :rtype: tuple[str, datetime, int]
    :return: The name of the station being queried, the time the train arrived or passed the station, and the delay
    """
    date_str = re.findall(r"\b[0-9]{8}", str(entry[0]))  # remove date from rid
    date = datetime.strptime(date_str[0], "%Y%m%d")

    # find if the time for this tpl is an arrival, passing or departure
    col_index = [2, 5, 8]  # columns for wta, arr_et, arr_at
    if entry[2] == "":  # check if a value for wta exists
        col_index = [x+1 for x in col_index]  # advance to wtp, pass_et, pass_at
        if entry[3] == "":  # check if a value for wtp exists
            col_index = [x+1 for x in col_index]  # use wtd, dep_et, dep_at
    work_time, est_time, act_time = entry[col_index[0]], entry[col_index[1]], entry[col_index[2]]

    # find the difference between timetabled time and actual time in minutes (the delay)
    work_time = work_time.split(":")  # deal with seconds by removing them
    work_time = "".join(work_time[:2])
    work_time = datetime.strptime(work_time, "%H%M")  # convert working time to datetime object
    delay_time = work_time
    dt = date + timedelta(hours=work_time.hour, minutes=work_time.minute)

    delay_mins = 30  # default: train was cancelled, delay is 30 minutes (waiting for the next train)
    if act_time != "":
        delay_mins = __find_delay(act_time, delay_time)
    elif est_time != "":
        delay_mins = __find_delay(est_time, delay_time)

    # deal with cases where delay may still be wildly out for whatever reason, since we can't fix them.
    if delay_mins > 30:
        delay_mins = 30
    elif delay_mins < -30:
        delay_mins = -30

    return entry[1], dt, delay_mins


def query_to_input(source, destination, dt):
    """Processes a trip between two adjacent stops and builds data suitable for model inputs

    :param services.Station source:      object of the station to record
    :param services.Station destination: object of the next station on the network (either stopping or passing)
    :param datetime dt:                  date and time at this point of the journey

    :rtype: list[str, str, int, int, int, int]
    :return: Record entry of form [source, destination, day_of_week, weekday, off_peak, hour_of_day]
    """
    day_of_week = dt.isoweekday()  # 1-7
    weekday = 1
    if day_of_week > 5:
        weekday = 0  # weekend
    hour_of_day = dt.hour

    # find if the train is a peak-service by building the network and checking the peak times. Beyond the demo,
    # this should really take an argument for a given network and call that network's function instead.
    time = dt.strftime("%H%M")
    off_peak = 1  # true
    if weekday and source != destination:
        peaks = source.get_peak(destination)
        for start, end in peaks:  # for each list of peak times in peak, check if the given time is between them
            if start <= time <= end:
                off_peak = 0  # false

    return [source.get_id(), destination.get_id(), day_of_week, weekday, off_peak, hour_of_day]


def __write_to_db(table, data):
    """Takes a list of records and adds them to the given table of database db

    :param str table: Name of the table to insert records into - if this doesn't exist, it will be created
    :param data:      A list of records to be added to the database
    :type data:       list[list[str, str, int, int, int, int, int, int]]

    :rtype:  int
    :return: Number of records added to db
    :raises  sqlite3.Error: If db value is invalid
    """
    conn = __connect_to_db()
    cur = conn.cursor()

    # create table if it doesn't exist
    try:
        cur.execute(""" CREATE TABLE IF NOT EXISTS {} (tpl_from text, tpl_to text, day_of_week integer, 
        weekday integer, off_peak integer, hour_of_day integer, delay integer, delay_change integer );""".format(table))

        # insert into table
        cur.executemany(""" INSERT INTO {} VALUES(?,?,?,?,?,?,?,?) """.format(table), data)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)
        return 0

    return cur.rowcount


def drop_table(table):
    """Warning: This will drop the given table from database db without prompt.

    :param str table: Table to delete from db

    :rtype:   bool
    :returns: True if deleted, else false
    :raises   sqlite3.Error: If table can not be dropped
    """
    conn = __connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute(""" DROP TABLE {} """.format(table))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)
        return False
    return True


def __connect_to_db():
    """Opens and returns a connection to database db or exception if the connection failed

    :return: connection to db
    :raises  sqlite3.Error: if connection to db fails
    """
    conn = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "db.sqlite")
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
    return conn


def __find_delay(actual, expected):
    """Helper function to find the difference between actual and expected arrival/passing times.

    :param str actual: Time the train got to the station
    :param datetime expected: Expected time the train should arrive

    :rtype: int
    :return: train delay in minutes, rounded down
    """
    actual    = datetime.strptime(actual, "%H:%M")
    day_end   = datetime.strptime("2359", "%H%M")
    train_end = train_start = datetime.strptime("0400", "%H%M")
    # check if the train came in after midnight when it was expected before midnight
    if actual <= train_end and train_start <= expected <= day_end:
        actual += timedelta(days=1)
    # check if the train was expected after midnight but came in before midnight
    elif expected <= train_end and train_start <= actual <= day_end:
        expected += timedelta(days=1)

    difference = actual - expected
    return int(difference.total_seconds() / 60)


if __name__ == "__main__":
    os.chdir(r"..")
    raw("a", "HSP")  # source either DARWIN or HSP
