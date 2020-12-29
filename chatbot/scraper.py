#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script for scraping nationalrail.co.uk

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : scraper.py
Date    : Monday 28 December 2020
Desc.   : Methods to scrape nationalrail.co.uk for data.
History : 28/12/2020 - v1.0 - Create project file
"""
import re
import requests
import datetime
from bs4 import BeautifulSoup

__author__ = "Martin Siddons"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__ = "m.siddons@uea.ac.uk"
__status__ = "Development"  # "Development" "Prototype" "Production"


def single_fare(dep, arr, date, time):
    """Takes stations and datetime object and validates them.

    Validated details are formed into a term to be appended to the search URL.

    :param dep:     The CRS code of the departing station (e.g. NRW)
    :param arr:     The CRS code of the arriving station
    :param date:    A date in the form YYYY/MM/DD (e.g. 2021/01/29) to search for results
    :param time:    A time in the form HH:MM representing the target time for a train

    :returns        Strings representing the cheapest fare in pounds, the time of the cheapest train as HH:MM and
                    the url of the sales page for comparison.
    """
    # Validate date and transform to DDMMYY
    dt_date = datetime.datetime.strptime(date, "%Y/%m/%d")
    if dt_date.date() - datetime.timedelta(weeks=11) > datetime.date.today():
        raise ValueError("Date can not be more than 11 weeks in the future.")
    val_date = dt_date.strftime("%d%m%y")

    # Validate time and transform to HHMM
    dt_time = datetime.datetime.strptime(time, "%H:%M")
    val_time = dt_time.strftime("%H%M")

    # Form a search url and headers
    terms = dep + "/" + arr + "/" + val_date + "/" + val_time + "/" + "dep"
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/" + terms
    headers = {"User-Agent": "Martin Siddons - UEA Student",
               "From": "m.siddons@uea.ac.uk"}  # good practice to remain contactable with web admins
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Validation: check if the result is an error page
    title = str(soup.find("title"))
    if title == "<title>National Rail Enquiries -</title>":
        raise ValueError("This journey is not available. Ensure the date is not a bank holiday and that there is a "
                         "valid route possible between the given stations.")
    elif title == "<title>Your UK Train Journey Planner - National Rail Enquiries</title>":
        raise ValueError("Incorrect station name given.")
    cheap_label = soup.find(class_="cheapest")  # this is the class with the cheapest price

    # Pull out the fare from html and isolate its value with regex
    s = str(cheap_label.parent.find(class_="opsingle").contents[2])
    fare = re.search("£.*", s).group()

    # Pull out journey times from html and isolate the first value with regex
    s = str(cheap_label.parent.find(class_="journey-breakdown").contents[1])
    time = re.search("[0-2][0-9]:[0-5][0-9]", s).group()

    return fare, time, url


def return_fare(dep, arr, date, time, retdep, retarr, retdate, rettime):
    pass


def delay(train, location, timedelayed, destination):
    pass
