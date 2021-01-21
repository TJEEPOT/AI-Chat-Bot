#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for generating and using a given model

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : prediction_model.py
Date    : Sunday 03 January 2021
Desc.   : Script holds multiple models to choose from
History : 03/01/2020 - v1.0 - Create project file
          17/01/2020 - v1.1 - Added final KNN model as tested
          20/01/2020 - v1.1 - Added use_model function.

"""
import sqlite3
import os.path
import pandas as pd
import numpy as np
import data.services as services
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Prototype"  # "Development" "Prototype" "Production"


def knn_model_trainer(station_from, station_to, network):
    """ Build a KNN model for delay prediction between the given stations and save to the provided Network object,
    which is copied onto the db.

    :param str station_from:
    :param str station_to:
    :param services.Network network: Network to save the model to
    """
    # get the relevant data from the db
    conn = __connect_to_db()
    df = pd.read_sql_query(""" SELECT * FROM dataset WHERE tpl_from="{}" AND tpl_to="{}" """.format
                           (station_from, station_to), conn)  # data_model

    # preprocessing - splitting attributes (x) and labels (y)
    x = df.iloc[:, 2:-1].values
    y = df.iloc[:, 7].values

    # feature scaling
    scaler = StandardScaler()
    scaler.fit(x)
    x = scaler.transform(x)

    # building the model
    model = KNeighborsClassifier(n_neighbors=30)
    model.fit(x, y)
    print("built model from", station_from, "to", station_to)

    # save model to network object and update network on db
    # stn_to = network.get_station(station_to)
    # model_scaler = [model, scaler]
    # network.get_station(station_from).add_model(stn_to, model_scaler)
    # services.store_network(network, conn)
    conn.close()


def bayes_model_trainer(station_from, station_to, network):
    pass


def ann_model_trainer(station_from, station_to, network):
    pass


def use_model(entry, delay, network):
    model = KNeighborsClassifier()  # "KNeighboursClassifier", "Bayes", "ANN"

    model_name = type(model).__name__
    s_from     = entry[0]
    s_to       = entry[1]

    stn_from = network.get_station(s_from)
    stn_to   = network.get_station(s_to)
    m_s      = stn_from.get_model(stn_to, model_name)
    model    = m_s[0]
    scaler   = m_s[1]

    entry.append(delay)
    data = np.array([entry])
    rows = [0]
    cols = ["tpl_from", "tpl_to", "day_of_week", "weekday", "off_peak", "hour_of_day", "delay"]
    df = pd.DataFrame(data=data, index=rows, columns=cols)

    x = df.iloc[:, 2:].values

    # scale and transform
    x = scaler.transform(x)

    result = model.predict(x)
    print("delay between", s_from, "and", s_to, "predicted to change by", result, "minutes")
    return result[0]


def __connect_to_db():
    """Opens and returns a connection to database db or exception if the connection failed

    :return: connection to db
    :raises  sqlite3.Error: if connection to db fails
    """
    conn = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, r"..\data\db.sqlite")
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
    return conn

