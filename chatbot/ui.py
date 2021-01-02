#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Client presenter for transferring data to/from the UI

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : ui.py
Date    : Saturday 02 January 2021
Desc.   : Presenter for UI using Flask
History : 02/01/2020 - v1.0 - Complete basic implementation

"""
from flask import Flask, render_template, request, jsonify, make_response

__author__ = "Sam Humphreys"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Sam Humphreys"
__email__ = "s.humphreys@uea.ac.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('interface.html')


@app.route("/get_reply", methods=['POST'])
def get_reply():

    if request.method == 'POST':
        user_input = request.get_json()
        print(user_input)
        response = make_response(jsonify({"message": generate_response(user_input)}), 200)
        return response


# main logic function calling other modules
def generate_response(user_input):
    return user_input.upper()


if __name__ == "__main__":
    app.run()
