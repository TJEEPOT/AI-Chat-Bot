#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script for scraping nationalrail.co.uk

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : scraper.py
Date    : Monday 28 December 2020
Desc.   : Methods to scrape nationalrail.co.uk for data.
History : 28/12/2020 - v1.0 - Create project file
          29/12/2020 - v1.1 - Complete single_fare() implementation
          30/12/2020 - v1.2 - Complete return_fare() implementation, split out validation and added to it
"""
import re
import requests
import datetime
from bs4 import BeautifulSoup

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Prototype"  # "Development" "Prototype" "Production"


def single_fare(dep, arr, date, time):
    """Takes stations and datetime object and creates a single ticket search term
    Validated details are formed into a term to be appended to the search URL.

    :param str dep:     The CRS code of the departing station (e.g. NRW)
    :param str arr:     The CRS code of the arriving station
    :param str date:    A date in the form YYYY/MM/DD (e.g. 2021/01/29) to search for results
    :param str time:    A time in the form HH:MM representing the target time for a train

    :returns: Strings representing the cheapest fare in pounds, the time of the cheapest train as HH:MM and
              the url of the sales page for comparison
    :raises ValueError: If validation of date or time, or of page output fails
    """
    val_date, val_time = __validate_datetime(date, time)  # input validation

    # Form a search url and headers
    terms = dep + "/" + arr + "/" + val_date + "/" + val_time + "/" + "dep"
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/" + terms
    headers = {"User-Agent": "Martin Siddons - UEA",
               "From": "m.siddons@uea.ac.uk"}  # good practice to remain contactable with web admins
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    __validate_result(title=str(soup.find("title")))  # validate if the result is not an error page
    cheap_label = soup.find(class_="cheapest")  # this is the class with the cheapest price

    # Pull out the fare from html and isolate its value with regex
    s = str(cheap_label.parent.find(class_="opsingle").contents[2])
    fare = re.search("£.*", s).group()

    # Pull out journey times from html and isolate the first value with regex
    s = str(cheap_label.parent.find(class_="journey-breakdown").contents[1])
    res_time = re.search("[0-2][0-9]:[0-5][0-9]", s).group()

    return fare, res_time, url


def return_fare(dep, arr, dep_date, dep_time, ret_date, ret_time):
    """Takes stations, dates and times and returns the details for the cheapest tickets from nationalrail.co.uk

    :param str dep:      Initial departure station's CRS code
    :param str arr:      Initial arrival station's CRS code
    :param str dep_date: Departure journey date
    :param str dep_time: Departure journey time
    :param str ret_date: Return journey date
    :param str ret_time: Return journey time

    :returns: Strings for departure and return ticket prices, departure and return times and booking url
    :raises ValueError: if validation of date or time, or of page output fails
    """
    val_out_date, val_out_time = __validate_datetime(dep_date, dep_time)  # validate outbound
    val_ret_date, val_ret_time = __validate_datetime(ret_date, ret_time)  # validate return

    # Form a search url and headers
    terms = dep + "/" + arr + "/" + val_out_date + "/" + val_out_time + "/" + "dep" + \
            "/" + val_ret_date + "/" + val_ret_time + "/" + "dep"
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/" + terms
    headers = {"User-Agent": "Martin Siddons - UEA",
               "From": "m.siddons@uea.ac.uk"}  # good practice to remain contactable with web admins
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    __validate_result(title=str(soup.find("title")))  # validate if the result is not an error page

    # Pull out the fare from html and isolate its value with regex
    s = str(soup.find(id="buyCheapestButton"))
    fare = "£" + re.search(r"\d{2}.\d{2}", s).group()

    # loop over cheap_labels to find journey times and isolate with regex
    res_time = []
    for label in soup.find_all(class_="cheapest"):  # this is the class with the cheapest prices
        s = str(label.parent.find(class_="journey-breakdown").contents[1])
        res_time.append(re.search("[0-2][0-9]:[0-5][0-9]", s).group())

    # if the second journey has no given prices, pull the first time from the return list
    if len(res_time) == 1:
        mtx = soup.find_all(class_="first mtx")
        s = str(mtx[1])
        res_time.append(re.search("[0-2][0-9]:[0-5][0-9]", s).group())

    return fare, res_time[0], res_time[1], url


def delay(train, location, delayed, destination):
    pass


def __validate_datetime(date, time):
    """ Validates that the date and time given are valid for searching

    :param str date: Date in the form YYYY/MM/DD
    :param str time: Time in the form HH:MM

    :returns: Date in the form DDMMYY and time in the form HHMM
    :raises ValueError: If date or time are not valid datetime objects or date is out of bounds
    """
    # Validate date and transform to DDMMYY
    dt_date = datetime.datetime.strptime(date, "%Y/%m/%d")
    today = datetime.date.today()
    if today > dt_date.date():
        raise ValueError("Date can not be earlier than today")
    if today + datetime.timedelta(weeks=11) < dt_date.date():
        raise ValueError("Date can not be more than 11 weeks in the future.")
    val_date = dt_date.strftime("%d%m%y")

    # Validate time and transform to HHMM
    dt_time = datetime.datetime.strptime(time, "%H:%M")
    val_time = dt_time.strftime("%H%M")
    return val_date, val_time


def __validate_result(title=None):
    """Validation for output html. Will validate based on optional parameters

    :param str title: (optional) Page title to be validated

    :raises ValueError: If given parameter does not validate
    :raises NotImplementedError: If no valid parameter is passed
    """
    if title is not None:
        if title == "<title>National Rail Enquiries -</title>":
            raise ValueError("This journey is not available. Ensure the date is not a bank holiday and that there is a "
                             "valid route possible between the given stations.")
        elif title.startswith("<title>Your UK Train Journey Planner - National Rail Enquiries</title>"):
            raise ValueError("Incorrect station name or journey times given.")
        elif title == "<title>National Rail Enquiries - Oh no! We can't find that page</title>":
            raise ValueError("Results page technical issue, try again later")

    else:
        raise NotImplementedError("Argument given for validation is not recognised.")
