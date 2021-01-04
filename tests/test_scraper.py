#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test scripts for scraper.py

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : test_scraper.py
Date    : Monday 28 December 2020
Desc.   : Testing methods in scraper.py
History : 28/12/2020 - v1.0 - Create project file
          29/12/2020 - v1.1 - Completed tests for single fare
          30/20/2020 - v1.2 - Completed tests for return fare
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
        # print("The cheapest fare is {} departing at {}. Book this ticket at {}".format(fare, time, url))

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

    def test_single_past_date(self):
        # testing that a date in the past returns an error
        self.assertRaises(ValueError, scraper.single_fare, "NRW", "LST", "2020/12/01", "16:30")

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

    def test_return_same_day(self):
        # testing the same-day return works correctly
        cost, time_out, time_ret, url = scraper.return_fare(
            "NRW", "LST", "2021/01/21", "16:30", "2021/01/21", "18:00")
        self.assertEqual(cost, "£20.00")
        self.assertEqual(time_out, "16:30")
        self.assertEqual(time_ret, "20:30")
        self.assertEqual(url, "https://ojp.nationalrail.co.uk/service/timesandfares/NRW/LST/210121/1630/dep/210121"
                              "/1800/dep")

    def test_return_separate_days(self):
        # out and return are different days
        cost, time_out, time_ret, url = scraper.return_fare(
            "NRW", "LST", "2021/01/21", "16:30", "2021/01/29", "18:00")
        self.assertEqual(cost, "£20.00")
        self.assertEqual(time_out, "16:30")
        self.assertEqual(time_ret, "20:30")
        self.assertEqual(url, "https://ojp.nationalrail.co.uk/service/timesandfares/NRW/LST/210121/1630/dep/290121"
                              "/1800/dep")

    def test_return_one_price(self):
        # only one price is given for out and return journeys
        cost, time_out, time_ret, url = scraper.return_fare(
            "NRW", "LST", "2021/01/21", "16:30", "2021/01/24", "05:00")
        self.assertEqual(cost, "£58.30")
        self.assertEqual(time_out, "16:30")
        self.assertEqual(time_ret, "06:28")
        self.assertEqual(url, "https://ojp.nationalrail.co.uk/service/timesandfares/NRW/LST/210121/1630/dep/240121"
                              "/0500/dep")

    def test_return_past_date(self):
        # testing that if the return journey date is in past, and error is raised
        self.assertRaises(ValueError, scraper.return_fare, "NRW", "LST", "2020/12/01", "16:30", "2020/12/01", "18:00")

    def test_return_before_outbound(self):
        # testing if return journey date is earlier than outbound an error is returned
        self.assertRaises(ValueError, scraper.return_fare, "NRW", "LST", "2021/01/29", "16:30", "2021/01/28", "18:00")

    def test_return_future_date(self):
        # test that the if return date is too far forward and error is generated
        self.assertRaises(ValueError, scraper.return_fare, "NRW", "LST", "2021/01/29", "16:30", "2021/05/28", "18:00")


if __name__ == "__main__":
    unittest.main()
