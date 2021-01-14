#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for getting data into a format readable by the prediction model

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : prediction_model.py
Date    : Tuesday 05 January 2021
History : 05/01/2020 - v1.0 - Create project file

"""
import os
import glob
import csv
from datetime import datetime, timedelta
from data import services
import re
import sqlite3

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


def raw(table):
    r"""Pull data from csv files, process for model and save to given table in given db

    Files are taken from \data\scraped and processed, then after writing are moved to \data\scraped\processed.

    :param string table:   Table in DB to insert data into (will be created if it doesn't already exist)
    :raises sqlite3.Error: If script can not connect to db
    """
    os.chdir(r".\data\scraped")
    for file in glob.glob("*.csv"):
        # data = read_from_csv(r"\scraped\{}".format(file))
        csv_data = __read_from_csv(file)
        # could add weather data here

        valid_tpl = ["NRCH", "DISS", "STWMRKT", "NEEDHAM", "IPSWICH", "MANNGTR", "CLCHSTR", "MRKSTEY", "KELVEDN",
                     "WITHAME", "HFLPEVL", "CHLMSFD", "INGTSTN", "SHENFLD", "BRTWOOD", "HRLDWOD", "GIDEAPK",
                     "ROMFORD", "CHDWLHT", "GODMAYS", "SVNKNGS", "ILFORD", "MANRPK", "FRSTGT", "MRYLAND", "STFD",
                     "LIVST"]
        train_data = []
        for i in range(1, len(csv_data)-1):  # skip the header and final row (since final row is None)
            entry = csv_data[i]
            next_entry = csv_data[i+1]
            if entry[0] != next_entry[0]:  # check if we're on the last station (rid code change) if so, move on.
                continue  # we don't record the final station since there's no delay between it and the station after.
            if entry[1] not in valid_tpl:  # skip every entry that isn't for a station listed above (remove later)
                continue
            source, date, delay = __entry_to_query(entry)

            dest     = next_entry[1]
            network  = services.build_ga_intercity()
            path     = network.find_path(source, dest)
            stn_from = path[0]
            stn_to   = path[1]
            processed_entry = __query_to_input(stn_from, stn_to, date, delay)
            # Need to look for cancelled trains then add missing stops here perhaps, then process all stops in one go.
            train_data.append(processed_entry)

        os.chdir(r"..")
        written = __write_to_db(table, train_data)
        print("processed", written, "entries in file", file)
        path = os.path.dirname(os.path.abspath(__file__))
        os.replace(r"{}\scraped\{}".format(path, file), r"{}\scraped\processed\{}".format(path, file))


def __read_from_csv(file):
    """Reads the provided train data CSV file and removes unneeded columns.

    :param str file: Name of file to be processed
    :rtype: list[list[str]]
    :return: list of lists matching the processed rows and columns of the given CSV, with unneeded info removed
    """
    data = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # delete columns pta, ptd, arr_wet, arr_atRemoved, pass_wet, pass_atRemoved, dep_wet, dep_atRemoved,
            # cr_code, lr_code
            del_cols = [20, 19, 15, 14, 12, 11, 9, 8, 3, 2]  # reversed, else index will go out of bounds
            for index in del_cols:
                del row[index]
            data.append(row)
        data.append([None, None])  # add an extra row to ensure there is no issues indexing
    return data


def __read_weather_data():
    pass


def user_to_query(source, destination, delay):
    """Takes information from the user and returns a valid input for the model

    :param str source: tpl code of the source station
    :param str destination: tpl code of the final destination on this journey
    :param int delay: number of minutes this journey has been delayed by

    :rtype: int
    :return: the amount of minutes the user will be delayed once they get to their final destination
    """
    now        = datetime.now()
    network    = services.build_ga_intercity()
    path       = network.find_path(source, destination)
    train_data = []
    for i in range(0, len(path)):
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry = __query_to_input(stn_from, stn_to, now, delay)
        train_data.append(processed_entry)

    # Put data into the model here
    total_delay = 0
    return total_delay


def __entry_to_query(entry):
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
        delta = datetime.strptime(act_time, "%H:%M") - delay_time
        delay_mins = int(delta.total_seconds() / 60)
    elif est_time != "":
        delta = datetime.strptime(est_time, "%H:%M") - delay_time
        delay_mins = int(delta.total_seconds() / 60)

    return entry[1], dt, delay_mins


def __query_to_input(source, destination, dt, delay):
    """Processes a trip between two adjacent stops and builds model inputs

    :param Station source:      object of the station to record
    :param Station destination: object of the next station on the network (either stopping or passing)
    :param datetime dt:     date and time at this point of the journey
    :param int delay:       current delay of the journey in minutes (rounded down)

    :rtype: list[str, str, int, int, int, int, int]
    :return: Record entry of form [source, destination, day_of_week, weekday, off_peak, hour_of_day, delay]
    """
    day_of_week = dt.isoweekday()  # 1-7
    weekday = 1
    if day_of_week > 5:
        weekday = 0  # weekend
    hour_of_day = dt.hour

    # find if the train is a peak-service by building the network and checking the peak times. Beyond the demo,
    # this should really take an argument for a given network and call that network's function.
    time = dt.strftime("%H%M")

    off_peak = 1  # true
    if weekday:
        peaks = source.get_peak(destination)
        for start, end in peaks:  # for each list of peak times in peak, check if the given time is between them
            if start <= time <= end:
                off_peak = 0  # false

    return [source, destination, day_of_week, weekday, off_peak, hour_of_day, delay]


def __write_to_db(table, data):
    """Takes a list of records and adds them to the given table of database db

    :param str table: Name of the table to insert records into - if this doesn't exist, it will be created
    :param data:      A list of records to be added to the database
    :type data:       list[list[str, str, int, int, int, int, int]]

    :rtype:  int
    :return: Number of records added to db
    :raises  sqlite3.Error: If db value is invalid
    """
    conn = connect_to_db()
    cur = conn.cursor()

    # create table if it doesn't exist
    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS {} (tpl_from text, tpl_to text, day_of_week integer, weekday integer, 
                       off_peak integer, hour_of_day integer, delay integer);""".format(table))

        # insert into table
        cur.executemany("""INSERT INTO {} VALUES(?,?,?,?,?,?,?)""".format(table), data)
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
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("""DROP TABLE {}""".format(table))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)
        return False
    return True


def connect_to_db():
    """Opens and returns a connection to database db or exception if the connection failed

    :return: connection to db
    :raises  sqlite3.Error: if connection to db fails
    """
    conn = None
    try:
        conn = sqlite3.connect(r"..\data\db.sqlite")
    except sqlite3.Error as e:
        print(e)
    return conn


if __name__ == "__main__":
    os.chdir(r"..")
    raw("testone")
