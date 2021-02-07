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
          01/02/2020 - v1.2 - Added bayes model generator.
          04/02/2020 - v1.3 - Added ANN model generator.

"""
import sqlite3
import os.path
import pandas as pd
import numpy as np
from data import services
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import BayesianRidge
from sklearn.neural_network import MLPClassifier

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Prototype"  # "Development" "Prototype" "Production"


def knn_model_trainer(station_from, station_to, network):
    """ Build a KNN model for delay prediction between the given stations and save to the provided Network object,
    which is copied onto the db.

    :param str station_from: TPL code of the station the train is leaving from
    :param str station_to:   TPL code of the station the train is next calling at
    :param services.Network network: Network to save the model to
    """
    # get the relevant data from the db
    conn = __connect_to_dataset()
    df = pd.read_sql_query(""" SELECT * FROM dataset WHERE tpl_from="{}" AND tpl_to="{}" AND delay_change<=5 
                               AND delay_change>=-5 """.format(station_from, station_to), conn)  # data_model
    conn.close()

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
    conn = __connect_to_db()
    stn_to = network.get_station(station_to)
    model_scaler = [model, scaler]
    network.get_station(station_from).add_model(stn_to, model_scaler)
    services.store_network(network, conn)
    conn.close()


def bayes_model_trainer(station_from, station_to, network):
    """ Build a Bayesian Ridge Regression Model from the requested journey and save to the provided Network object,
    which is copied onto the db.

    :param station_from: TPL code of the station the train is leaving from
    :param station_to:   TPL code of the station the train is next calling at
    :param services.Network network: Network to save the model to

    :rtype: BayesianRidge
    :return: BayesianRidge model to compute the delay between the given stations
    """
    # get the data
    conn = __connect_to_dataset()
    df = pd.read_sql_query(""" SELECT * FROM dataset WHERE tpl_from="{}" AND tpl_to="{}" """.format
                           (station_from, station_to), conn)  # data_model
    conn.close()

    # split data into attributes and labels
    x = df.iloc[:, 2:-1].values
    y = df.iloc[:, 7].values

    # build model
    model = BayesianRidge()
    model.fit(x, y)
    # an algorithm is needed to accurately interpret the floating-point value given by the model as a categorical value.

    # save model to network object and update network on db
    conn = __connect_to_db()
    stn_to = network.get_station(station_to)
    model_scaler = [model, None]
    network.get_station(station_from).add_model(stn_to, model_scaler)
    services.store_network(network, conn)
    conn.close()


def ann_model_trainer(station_from, station_to, network):
    """ Build a Multi-layer Perceptron Artificial Neural Network to predict train delays between the given stations
    and save to the provided Network object, which is copied onto the db.

    :param station_from: TPL code of the station the train is leaving from
    :param station_to: TPL code of the station the train is next calling at
    :param services.Network network: Network to save the model to
    """
    # get the relevant data from the db
    conn = __connect_to_dataset()
    df = pd.read_sql_query(""" SELECT * FROM dataset WHERE tpl_from="{}" AND tpl_to="{}" AND delay_change<=5 
                               AND delay_change>=-5 """.format(station_from, station_to), conn)  # data_model
    conn.close()

    # preprocessing - splitting attributes (x) and labels (y)
    x = df.iloc[:, 2:-1].values
    y = df.iloc[:, 7].values

    # feature scaling
    scaler = StandardScaler()
    scaler.fit(x)
    x = scaler.transform(x)

    # run the model
    model = MLPClassifier(hidden_layer_sizes=5, activation='tanh', max_iter=1000, learning_rate_init=0.003)
    model.fit(x, y)
    print("built model from", station_from, "to", station_to)

    # save model to network object and update network on db
    conn = __connect_to_db()
    stn_to = network.get_station(station_to)
    model_scaler = [model, scaler]
    network.get_station(station_from).add_model(stn_to, model_scaler)
    services.store_network(network, conn)
    conn.close()


def use_model(entry, delay, network):
    model = KNeighborsClassifier()  # "KNeighborsClassifier", "MLPClassifier"
    model_name = type(model).__name__
    s_from     = entry[0]
    s_to       = entry[1]

    # pull the model and station objects from the Network object
    stn_from = network.get_station(s_from)
    stn_to   = network.get_station(s_to)
    m_s      = stn_from.get_model(stn_to, model_name)  # list containing the model and the scaler
    model    = m_s[0]
    scaler   = m_s[1]

    entry.append(delay)
    data = np.array([entry])
    df = pd.DataFrame(data=data)

    # assign attributes, scale and transform
    x = df.iloc[:, 2:].values
    if scaler is not None:
        x = scaler.transform(x)

    result = model.predict(x)
    result = result[0]  # change the array returned from the prediction into an integer value
    while delay + result < -1:
        result += 1  # quick fix for runaway negative time estimations which are not handled well by the models

    change = "increase"
    if result < 0:
        change = "decrease"
    print("delay between", s_from, "and", s_to, "predicted to", change, "by", result, "minutes, to", (delay + result))
    return result


def __connect_to_dataset():
    """Opens and returns a connection to dataset database or exception if the connection failed

    :return: connection to db
    :raises  sqlite3.Error: if connection to db fails
    """
    conn = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, r"..\data\dataset.sqlite")
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
    return conn


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
