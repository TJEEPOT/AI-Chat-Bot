#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Client presenter for transferring data to/from the UI

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : presenter.py
Date    : Saturday 02 January 2021
Desc.   : Presenter for UI using Flask
History : 02/01/2021 - v1.0 - Complete basic implementation.
          04/01/2021 - v1.1 - Moved to chatbot directory, renamed to presenter.py
"""
from flask import Flask, render_template, request, jsonify, make_response
import model.scraper as scraper

__author__     = "Sam Humphreys"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Sam Humphreys"
__email__      = "s.humphreys@uea.ac.uk"
__status__     = "Development"  # "Development" "Prototype" "Production"

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('interface.html')


@app.route("/get_reply", methods=['POST'])
def get_reply():
    if request.method == 'POST':
        user_input = request.get_json()
        # print(user_input)
        response = make_response(jsonify({"message": generate_response(user_input)}), 200)
        return response


# main logic function calling other modules
def generate_response(user_input):
    #
    # CALL TO NLP WOULD GO HERE
    # train_details = nlp.process(user_input)
    #
    try:
        dep, arr, date, time = user_input.split(", ")
        fare, time, url = scraper.single_fare(dep, arr, date, time)
    except ValueError:
        return "Incorrect input, please try again."
    return "The cheapest fare is {} departing at {}. Book this ticket at {}".format(fare, time, url)


if __name__ == "__main__":
    app.run()
