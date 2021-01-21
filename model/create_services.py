#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for creating networks and models. Thanks to how pickle works, this has to be separate from services.py

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : create_services.py
Date    : Monday 18 January 2021
History : 18/01/2021 - v1.0 - Create project file, build_ga_intercity()
          20/01/2021 - v1.1 - Create build_model(), build_all_station_models()

"""
import data.services as services
import prediction_model as model

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Prototype"  # "Development" "Prototype" "Production"


def build_ga_intercity():
    """ Just calls build_train_network() with rail and peak times info. I hate pickle so so so much.

    :rtype: bool
    :return: True if all the data was added to the db, else False
    """
    # connections from Norwich to London
    stations   = ["NRCH", "DISS", "STWMRKT", "NEEDHAM", "IPSWICH", "MANNGTR", "CLCHSTR",
                  "WITHAME", "CHLMSFD", "INGTSTN", "SHENFLD", "STFD", "LIVST"]  # "INGTSTN" only for historical trains
    peaks_from = [["0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400",
                   "0400"]]
    peaks_to   = [["0758", "0815", "0827", "0832", "0839", "0851", "0900", "0917", "0919", "0924", "0930", "0947",
                   "0958"]]

    result1 = services.build_train_network("ga_intercity", stations, peaks_from, peaks_to)

    # Connections from London to Norwich
    stations   = ['LIVST', 'STFD', 'SHENFLD', 'INGTSTN', 'CHLMSFD', 'WITHAME', 'CLCHSTR',
                  'MANNGTR', 'IPSWICH', 'NEEDHAM', 'STWMRKT', 'DISS', 'NRCH']  # "INGTSTN" only for historical trains

    peaks_from = [["0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400", "0400",
                   "0400"],
                  ["1624", "1632", "1648", "1653", "1658", "1708", "1710", "1719", "1728", "1736", "1741", "1754",
                   "1816"]]
    peaks_to   = [["0928", "0938", "0950", "0955", "1001", "1012", "1020", "1029", "1041", "1050", "1053", "1106",
                   "1125"],
                  ["1832", "1840", "1856", "1855", "1906", "1916", "1918", "1927", "1936", "1945", "1951", "2004",
                   "2026"]]
    result2 = services.build_train_network("ga_intercity", stations, peaks_from, peaks_to)

    if result1 and result2:
        return True
    return False


def build_model():
    n = services.get_network("ga_intercity")
    model.knn_model_trainer("DISS", "STWMRKT", n)


def build_all_station_models():
    n = services.get_network("ga_intercity")
    # path = n.find_path("NRCH", "LIVST")
    path = n.find_path("LIVST", "NRCH")
    path.append(path[-1])

    for i in range(len(path)-1):
        stn_from = path[i].get_id()
        stn_to   = path[i+1].get_id()
        model.knn_model_trainer(stn_from, stn_to, n)


if __name__ == "__main__":
    # build_ga_intercity()
    # build_model()
    # build_all_station_models()
    pass
