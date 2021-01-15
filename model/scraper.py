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
          15/01/2020 - v1.3 - Complete historical_trains() implementation including helper functions.
"""
import re
import requests
import datetime
import os
from bs4 import BeautifulSoup

__author__     = "Martin Siddons"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Martin Siddons"
__email__      = "m.siddons@uea.ac.uk"
__status__     = "Production"  # "Development" "Prototype" "Production"


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


def historical_trains():
    """Specify which train details to retrieve from the online datafeeds, find the required data, format into the
    required way and save to the data/scraped folder.

    :rtype: bool
    :return: True if scrape was a success else false.
    """
    time_from = "0400"
    time_to   = "0800"
    date_from = "2017-01-01"
    date_to   = "2017-01-05"
    days      = "WEEKDAY"  # "WEEKDAY" "SATURDAY" "SUNDAY"

    rids = __hsp_metrics(time_from, time_to, date_from, date_to, days)
    csv_data = [["rid", "crs", "ptd", "pta", "dep_at", "arr_at"]]  # header row
    for rid in rids:
        csv_data.append(__hsp_details(rid))

    print(csv_data)
    # save the CSV data to disk
    return True


def __hsp_metrics(time_from, time_to, date_from, date_to, days):
    """Pull JSON from National Rail's HSP metrics datafeed, find all RID codes and return them. This service seems to
    take a while to reply - be cautious as to how much data you wish to have returned.

    :param str time_from: Start time for search in the form 'HHMM' e.g. '0400'
    :param str time_to:   End time for search in the form 'HHMM' e.g. '2359'
    :param str date_from: Date to search from, in the form 'YYYY-mm-dd' e.g. '2017-01-01'
    :param str date_to:   Date to search until, in the form 'YYYY-mm-dd' e.g. '2017-02-01'
    :param str days:      Either 'WEEKDAY', 'SATURDAY' or 'SUNDAY' to search those days.

    :rtype:  set
    :return: Unique RID codes for all journeys from NRW to LST between the given dates and times.
    """
    """
    Documentation can be found at https://wiki.openraildata.com/index.php/HSP.
    When registering at https://datafeeds.nationalrail.co.uk/ you only need the HSP subscription.
    In 'Planned usage', mention you are using the HSP data for educational purposes, for a project, and for a limited 
    time. The T & Cs should not be an issue, nor the limit on the number of requests an hour - but do be polite and 
    do not swamp the web service with an excessive number of requests.
    """
    api_url = "https://hsp-prod.rockshore.net/api/v1/serviceMetrics"
    headers = {"Content-Type": "application/json"}
    auths = (os.environ.get("HSP_EMAIL"), os.environ.get("HSP_PASSWORD"))  # SET YOUR OWN ENVIRONMENT VARIABLES
    data = {
        "from_loc": "NRW",
        "to_loc": "LST",
        "from_time": time_from,
        "to_time": time_to,
        "from_date": date_from,
        "to_date": date_to,
        "days": days
    }

    r = requests.post(api_url, headers=headers, auth=auths, json=data)
    json_response = r.json()

    valid_rids = set()
    services = json_response["Services"]
    for service in services:
        metrics = service["serviceAttributesMetrics"]
        rids = metrics["rids"]
        for rid in rids:
            if rid not in valid_rids:
                valid_rids.add(rid)

    return valid_rids


def __hsp_details(rid):
    """Take a rid code and retrieve the journey from National Rail's HSP details datafeed, format the data into what
    is needed for storing in csv and return.

    :param str rid: A rid code for the journey to be returned

    :rtype list
    :return: Details to be added to CSV.
    """
    api_url = "https://hsp-prod.rockshore.net/api/v1/serviceDetails"

    headers = {"Content-Type": "application/json"}
    auths = (os.environ.get("HSP_EMAIL"), os.environ.get("HSP_PASSWORD"))  # SET YOUR OWN ENVIRONMENT VARIABLES

    data = {"rid": rid}
    r = requests.post(api_url, headers=headers, auth=auths, json=data)

    json_response = r.json()
    details = json_response["serviceAttributesDetails"]
    locations = details["locations"]
    results = []
    for loc in locations:
        line = [rid, loc["location"], loc["gbtt_ptd"], loc["gbtt_pta"], loc["actual_td"], loc["actual_ta"]]
        results.append(line)
    return results


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


if __name__ == "__main__":
    historical_trains()
