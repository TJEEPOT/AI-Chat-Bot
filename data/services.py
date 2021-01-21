#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for building a graph object and assembling a specific rail service network

Network + Station code is largely from https://www.bogotobogo.com/python/python_graph_data_structures.php

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : Network.py
Date    : Friday 08 January 2021
History : 05/01/2020 - v1.0 - Create project file
          11/01/2020 - v1.1 - Finalised Network and Station objects, and intercity function, fully tested.
          18/01/2020 - v1.2 - Moved network creation code out and replaced intercity function with a fetch from the db.
"""
import pickle
import sqlite3
import os.path
import sklearn.neighbors as skl

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Prototype"  # "Development" "Prototype" "Production"


class Station:
    """Defines a station and relationships between stations (graph vertex)"""
    def __init__(self, station):
        self.id          = station
        self.connected   = {}
        # above is: {Station: {int:peak, KNeighboursClassifier:model, BayesClassifier:model, ANNClassifier:model}}

    # def __str__(self):
    #     return str(self.id) + ' links to: ' + str([x.id for x in self.connected])

    def add_destination(self, destination, peak=None):
        """Connects a given destination on the network to this station

        :param destination: station that self links to
        :param peak: Trains from the source station to destination between these times counts as a peak train
        """
        if peak is None:
            peak = [[]]
        if destination not in self.connected:
            self.connected[destination] = {}
        self.connected[destination]["peak"] = peak

    def add_model(self, destination, model_scaler):
        """ Takes a model of delays between this station and the destination and stores it in the 'connected' dict """
        name = type(model_scaler[0]).__name__  # get the object's class name
        self.connected[destination][name] = model_scaler

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
        return self.connected[destination]["peak"]

    def get_model(self, destination, model_name):
        """ returns the requested model for journeys to 'destination'

        :param Station destination: Station object of the destination
        :param str model_name: Name of the model matching stored key in network

        :return: Model which matches the requested model"""
        return self.connected[destination][model_name]


class Network:
    """Rail network modelled as a Graph data structure"""
    def __init__(self, name):
        self.name = name
        self._rail_line = {}

    def __iter__(self):
        return iter(self._rail_line.values())

    def get_name(self):
        return self.name

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

        path  = []
        queue = [[source_station]]
        while queue:
            path = queue.pop(0)
            last_station = path[-1]
            if last_station == destination_station:
                return path
            for station in last_station.connected.keys():
                new_path = list(path)
                new_path.append(station)
                queue.append(new_path)

    def __find_path_rec(self, source, destination, path):
        # recursive call to find target. Separated from find_path to allow for validation. Returns list[Station]
        path.append(source)
        to_visit = []

        if source == destination:
            # path.append(destination)
            return path
        for station in source.connected.keys():
            to_visit.append(station)
        if to_visit:
            next_station = to_visit.pop(0)
            if next_station not in path:
                new_path = self.__find_path_rec(next_station, destination, path)
                if new_path:
                    return new_path

    def append_rails(self, stations, peaks_from, peaks_to):
        """Helper function to add stations and rails when to a given network when it's being built

        :param list[str] stations: list of stations to add rails between
        :param list[list[str]] peaks_from: start times of peak periods for each station
        :param list[list[str]] peaks_to:   end times of peak periods for each station
        """
        # add connections between stations
        for i in range(len(stations) - 1):
            station_peaks = []
            for j in range(len(peaks_from)):  # iterate for as many peak periods that are given (usually one or two)
                station_peaks.append([peaks_from[j][i], peaks_to[j][i]])
            self.add_rail(stations[i], stations[i + 1], station_peaks)
        # add the final station in separately
        station_peaks = []
        for j in range(len(peaks_from)):
            station_peaks.append([peaks_from[j][-1], peaks_to[j][-1]])
        self.add_rail(stations[-1], stations[-1], station_peaks)


def build_train_network(net_name, stations, peaks_from, peaks_to):
    """ Uses the Network class to build a representation of the train stations of a given network using the supplied
    stations and peak time timetables and saves to the corresponding entry in the network table of database db. If
    given network already exists, this will append the data given to the existing network

    :param str net_name:                name of the network we are building
    :param list[str] stations:          list of station tpl codes on this network in order of how they are linked
    :param list[list[str]] peaks_from:  start times of peak travel periods for trains leaving from station[n]
    :param list[list[str]] peaks_to:    end times of peak travel periods for trains leaving from station[n]

    :rtype: bool
    :return: True if network was built and saved correctly else false
    """
    # check if the network already exists
    conn = __connect_to_db()
    cur  = conn.cursor()

    cur.execute(""" SELECT object FROM networks WHERE name=? """, (net_name,))
    result = cur.fetchone()

    appending = False
    n = Network(net_name)
    if result is not None:
        appending = True
        n = pickle.loads(result[0])

    n.append_rails(stations, peaks_from, peaks_to)
    success = store_network(n, conn, appending)
    conn.close()
    return success


def store_network(network, conn, appending=True):
    """function to pickle and save the given network object.

    :param Network network:
    :param sqlite3.Connection conn: sqlite3 Connection
    :param appending: True if network already exists else False
    :return: True if successful else false
    """
    cursor = conn.cursor()
    serial_n = pickle.dumps(network)  # serialise the network in order to store it
    if appending:
        cursor.execute(""" UPDATE networks SET object=? WHERE name=? """, (serial_n, network.get_name()))
    else:
        cursor.execute(""" INSERT INTO networks VALUES(?,?) """, (network.get_name(), serial_n))
    conn.commit()
    return True


def get_network(name):
    """Retrieves the given network from the network table of the database

    :param str name: Name of network to retrieve, as listed in networks table
    :rtype:  Network
    :return: A Network object representing the Greater Anglia network
    """
    conn = __connect_to_db()
    cur = conn.cursor()
    cur.execute(""" SELECT object FROM networks WHERE name=? """, (name,))
    data = cur.fetchone()
    retrieved_n = pickle.loads(data[0])
    return retrieved_n


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


if __name__ == "__main__":
    n = get_network("ga_intercity")
    print(n.get_name())
