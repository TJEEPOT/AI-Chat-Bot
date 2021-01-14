#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for building a graph object and assembling a specific rail service network

Network + Station code is largely from https://www.bogotobogo.com/python/python_graph_data_structures.php

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : Network.py
Date    : Friday 08 January 2021
History : 05/01/2020 - v1.0 - Create project file
          11/01/2020 - v1.1 - Finalised Network and Station objects, and intercity function, fully tested.
"""
from datetime import datetime


class Station:
    """Defines a station and relationships between stations (graph vertex)"""
    def __init__(self, station):
        self.id = station
        self.connected = {}

    def __str__(self):
        return str(self.id) + ' links to: ' + str([x.id for x in self.connected])

    def add_destination(self, destination, peak=None):
        """Connects a given destination on the network to this station

        :param destination: station that self links to
        :param peak: Trains from the source station to destination between these times counts as a peak train
        """
        if peak is None:
            peak = [[]]
        self.connected[destination] = peak

    def edit_destination(self, destination, peak):
        if destination in self.connected:
            self.connected[destination] = peak
        else:
            print("Station", destination, "not found.")

    def get_connections(self):
        return self.connected.keys()

    def get_id(self):
        return self.id

    def get_peak(self, destination):
        """Takes a Station object connected to self and gives the times between which the train is considered peak-time

        :param Station destination: A station that self links to

        :rtype: list[list[str, str]] or None
        :return: list of times the trains leaving the self station for destination station are classed as peak
        """
        if destination is None:
            return None
        return self.connected[destination]


class Network:
    """Rail network modelled as a Graph data structure"""
    def __init__(self):
        self._rail_line = {}

    def __iter__(self):
        return iter(self._rail_line.values())

    def add_station(self, station):
        new_rail = Station(station)
        self._rail_line[station] = new_rail
        return new_rail

    def get_station(self, station):
        """Returns a Station object for the station being searched for.

        :param str station: tpl (TIPLOC) code for the desired station
        :rtype: Station
        :return: station object of the station being searched for, or None if not found.
        """
        if station in self._rail_line:
            return self._rail_line[station]
        else:
            return None

    def add_rail(self, frm, to, peak):
        """Add a new rail connection between two stations, specifying the times peak trains leave the source station

        :param str frm: Source station the rail runs from
        :param str to:  Destination station the rail connects to
        :param list[list[str, str]] peak: list of [start, end] str objects representing peak travel times
        """
        if frm not in self._rail_line:
            self.add_station(frm)
        if to not in self._rail_line:
            self.add_station(to)

        self._rail_line[frm].add_destination(self._rail_line[to], peak)

    def get_all_stations(self):
        """
        :rtype list[str]
        :return: Names of all stations in this Network
        """
        return list(self._rail_line.keys())

    def find_path(self, source, destination):
        """Find any path between source and destination stations

        :param str source: Source station tpl (TIPLOC) code
        :param str destination: Destination station tpl code

        :rtype: list[Station]
        :return: A list of station objects from source to destination, if it exists, else None.
        """
        source_station = self.get_station(source)
        destination_station = self.get_station(destination)
        if source_station is None or destination_station is None:
            raise ValueError("Station {} or {} does not exist.".format(source, destination))
        return self._find_path_rec(source_station, destination_station, [])

    def _find_path_rec(self, source, destination, path):
        # recursive call to find target. Separated from find_path to allow for validation. Returns list[Station]
        path.append(source)

        if source == destination:
            path.append(destination)
            return path
        for station in source.connected.keys():
            if station not in path:
                new_path = self._find_path_rec(station, destination, path)
                if new_path:
                    return new_path


def build_ga_intercity():
    """Uses the Graph class to build a representation of the train
    stations on the Intercity segment of the Greater Anglia train network

    This should probably be made OOP and be an implementation of an interface, but will do for a demo. Also,
    this service has so many exceptions to its peak times that it's next to impossible to model perfectly,
    but I'm not going to worry so much about that.

    :rtype:  Network
    :return: A Graph object representing the Greater Anglia network
    """
    n = Network()
    stations = ["NRCH", "DISS", "STWMRKT", "NEEDHAM", "IPSWICH", "MANNGTR", "CLCHSTR", "MRKSTEY", "KELVEDN", "WITHAME",
                "HFLPEVL", "CHLMSFD", "INGTSTN", "SHENFLD", "BRTWOOD", "HRLDWOD", "GIDEAPK", "ROMFORD", "CHDWLHT",
                "GODMAYS", "SVNKNGS", "ILFORD", "MANRPK", "FRSTGT", "MRYLAND", "STFD", "BTHNLGR", "LIVST"]

    peak_am_from = "0400"
    peak_to_london = ["0805", "0821", "0833", "0839", "0846", "0857", "0906", "0913", "0916", "0919", "0921", "0925",
                      "0932", "0936", "0937", "0941", "0942", "0943", "0945", "0945", "0946", "0947", "0948", "0949",
                      "0950", "0951", "0957", "1001"]
    # peak_times = _str_to_dt(peak_to_london)

    for i in range(len(stations)-1):  # add connections between stations from Norwich to London
        n.add_rail(stations[i], stations[i+1], [[peak_am_from, peak_to_london[i]]])

    # Connections from London to Norwich
    peak_from_london_am = ["0930", "", "", "", "", "", "", "", "", "", "",
                           "", "", "", "", "", "", "", "", "", "", "",
                           "", "", "", "", "", ""]
    peak_pm_from        = ["1624", "", "", "", "", "", "", "", "", "", "",
                           "", "", "", "", "", "", "", "", "", "", "",
                           "", "", "", "", "", ""]
    peak_from_london_pm = ["1834", "", "", "", "", "", "", "", "", "", "",
                           "", "", "", "", "", "", "", "", "", "", "",
                           "", "", "", "", "", ""]
    for i in reversed(range(1, len(stations))):  # go from London to Norwich
        n.add_rail(stations[i], stations[i-1], [[peak_am_from, peak_from_london_am[i]],
                                                [peak_pm_from[i], peak_from_london_pm[i]]])


    return n


def _str_to_dt(str_list):
    """Turn a list of strings into a list of datetime objects. Strings must be in the range "0000" to "2359"

    :param list[str] str_list: list of strings to convert to datetime objects

    :rtype: list[datetime]
    :return: list of datetime objects
    """
    dt_list = []
    for i in range(len(str_list)):
        dt_list.append(datetime.strptime(str_list[i], "%H%M"))
    return dt_list
