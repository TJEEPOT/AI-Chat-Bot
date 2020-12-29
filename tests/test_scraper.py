#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test scripts for scraper.py

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : test_scraper.py
Date    : Monday 28 December 2020
Desc.   : Testing methods in scraper.py
History : 28/12/2020 - v1.0 - Create project file
"""
import unittest
from context import scraper


class TestStringMethods(unittest.TestCase):

    def test_single_basic(self):
        # greater anglia, ensure date and time is correctly formatted, cheapest fare is the first result on page
        cost, time, url = scraper.single_fare("NRW", "LST", "2021/01/29", "16:30")
        self.assertEqual(cost, "£10.00")
        self.assertEqual(time, "16:30")
        self.assertEqual(url, "https://ojp.nationalrail.co.uk/service/timesandfares/NRW/LST/290121/1630/dep")
        # print("the cheapest fare is", trip[0], "departing at", trip[1], ". Book this ticket at", trip[2])

    def test_single_date(self):
        # greater anglia, testing non-norwich stations and non-quarterly time, cheapest fare is the ### result
        cost, time, url = scraper.single_fare("CHM", "IPS", "2021/02/03", "11:05")
        self.assertEqual(cost, "£16.00")
        self.assertEqual(time, "11:03")
        self.assertEqual(url, "https://ojp.nationalrail.co.uk/service/timesandfares/CHM/IPS/030221/1105/dep")

    def test_single_multi_route(self):
        # testing that a route that requires multiple networks will deliver results
        cost, time, url = scraper.single_fare("PNZ", "GOF", "2021/01/29", "16:30")
        self.assertEqual(cost, "£259.30")
        self.assertEqual(time, "22:09")
        self.assertEqual(url, "https://ojp.nationalrail.co.uk/service/timesandfares/PNZ/GOF/290121/1630/dep")

    def test_single_future_date(self):
        # testing date more than 12 weeks in the future, should return error
        self.assertRaises(ValueError, scraper.single_fare, "NRW", "LST", "2021/05/15", "16:30")

    def test_single_incorrect_departure(self):
        # testing that a non-matching departure station is caught
        self.assertRaises(ValueError, scraper.single_fare, "AAA", "NRW", "2021/01/29", "16:30")

    def test_single_incorrect_arrival(self):
        # same as above but for arrival station
        self.assertRaises(ValueError, scraper.single_fare, "NRW", "AAA", "2021/01/29", "16:30")

    def test_single_incorrect_day(self):
        # testing that an incorrect day value is caught
        self.assertRaises(ValueError, scraper.single_fare, "NRW", "LST", "2021/01/33", "16:30")

    def test_single_incorrect_time(self):
        # testing that an incorrect time is caught
        self.assertRaises(ValueError, scraper.single_fare, "NRW", "LST", "2021/01/29", "26:00")


if __name__ == "__main__":
    unittest.main()
