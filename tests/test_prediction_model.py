#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test scripts for prediction_model.py

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : test_prediction_model.py
Date    : Monday 28 December 2020
Desc.   : Testing methods in prediction_model.py
History : 28/12/2020 - v1.0 - Create project file

"""
import unittest
from context import model


class MyTestCase(unittest.TestCase):
    def test_knn_model_retrieval(self):
        diss = network.get_station("DISS")
        knn_model, scalar = network.get_station("NRCH").get_model(diss, "KNeighborsClassifier")
        self.assertEqual("KNeighborsClassifier", type(knn_model).__name__)

    def test_use_model_diss_stwmrkt(self):
        entry = ['DISS', 'STWMRKT', 5, 1, 1, 9]
        result = model.use_model(entry, 0, network)
        self.assertGreaterEqual(2, result)
        self.assertLessEqual(-1, result)

    def test_use_model_nrch_livst(self):
        now = datetime.now()
        path = network.find_path("NRCH", "LIVST")
        path.append(path[-1])
        train_data = []
        for i in range(0, len(path)-1):
            stn_from = path[i]
            stn_to = path[i + 1]
            processed_entry = process.query_to_input(stn_from, stn_to, now)
            train_data.append(processed_entry)

        total_delay = 0  # initial delay
        for train in train_data:
            total_delay += model.use_model(train, total_delay, network)

        print("Total delay is", total_delay, "minutes.")
        self.assertGreaterEqual(2, total_delay)
        self.assertLessEqual(-10, total_delay)

    def test_use_model_livst_nrch(self):
        now = datetime.now()
        path = network.find_path("LIVST", "NRCH")
        path.append(path[-1])
        train_data = []

        for i in range(0, len(path)-1):
            stn_from = path[i]
            stn_to = path[i + 1]
            processed_entry = process.query_to_input(stn_from, stn_to, now)
            train_data.append(processed_entry)

        total_delay = 0  # initial delay
        for train in train_data:
            total_delay += model.use_model(train, total_delay, network)

        print("Total delay is", total_delay, "minutes.")
        self.assertGreaterEqual(2, total_delay)
        self.assertLessEqual(-6, total_delay)

    def test_use_model_clchstr_nrch_5(self):
        now = datetime.now()
        path = network.find_path("CLCHSTR", "NRCH")
        path.append(path[-1])
        train_data = []

        for i in range(0, len(path)-1):
            stn_from = path[i]
            stn_to = path[i + 1]
            processed_entry = process.query_to_input(stn_from, stn_to, now)
            train_data.append(processed_entry)

        total_delay = 5
        for train in train_data:
            total_delay += model.use_model(train, total_delay, network)

        print("Total delay is", total_delay, "minutes.")
        self.assertGreaterEqual(10, total_delay)
        self.assertLessEqual(-5, total_delay)

    def test_use_model_clchstr_livst_5(self):
        now = datetime.now()
        path = network.find_path("CLCHSTR", "LIVST")
        train_data = []

        for i in range(0, len(path)-1):
            stn_from = path[i]
            stn_to = path[i + 1]
            processed_entry = process.query_to_input(stn_from, stn_to, now)
            train_data.append(processed_entry)

        total_delay = 5  # initial delay
        for train in train_data:
            total_delay += model.use_model(train, total_delay, network)

        print("Total delay is", total_delay, "minutes.")
        self.assertGreaterEqual(10, total_delay)
        self.assertLessEqual(-5, total_delay)


if __name__ == '__main__':
    unittest.main()
