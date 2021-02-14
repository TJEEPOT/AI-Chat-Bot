#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Client presenter for transferring data to/from the UI

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : presenter.py
Date    : Saturday 02 January 2021
Desc.   : Presenter for UI using Flask
History : 02/01/2021 - v1.0 - Complete basic implementation.
          04/01/2021 - v1.1 - Moved to chatbot directory, renamed to presenter.py
          08/01/2021 - v1.2 - Added voice recognition facility.
          20/01/2021 - v1.3 - Changed implementation to socketio
"""
import random

from flask import Flask, render_template, request, jsonify, make_response
import speech_recognition as sr
from chatbot.nlp import parse_user_input
from flask_socketio import SocketIO, send, emit

__author__ = "Sam Humphreys"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Sam Humphreys"
__email__ = "s.humphreys@uea.ac.uk"
__status__ = "Development"  # "Development" "Prototype" "Production"

app = Flask(__name__)
app.config['SECRET_KEY'] = "iamasecretkey"  # I'll pretend I didn't see this.
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template('interface.html')


@app.route("/get_audio", methods=['POST'])
def get_audio():
    """Gets audio data from the client to process into text

    :returns: Strings for departure and return ticket prices, departure and return times and booking url
    :raises ValueError: if validation of date or time, or of page output fails
    """
    if request.method == 'POST':
        audio_file = request.files['file']
        words = __process_speech(audio_file)
        response = make_response(jsonify({"message": words}), 200)
        return response


def __process_speech(user_audio):
    speech_recog = sr.Recognizer()
    with sr.AudioFile(user_audio) as source:
        audio = speech_recog.listen(source)
    try:
        words = speech_recog.recognize_google(audio, language="en-GB")
        print("Words: {}".format(words))
        return words
    except Exception as e:
        print(e)


def send_message(bot_response):
    send(bot_response)


def send_list(message_to_send, list_to_send):
    emit('list', ({"passed_message": message_to_send, "passed_list": list_to_send}))


@socketio.on('connect')
def user_connected():
    # do stuff here if we want a greeting message
    bot_feedback = {
        'greeting': [
            "Hello! How may I help you today?",
            "Welcome! Please ask me about tickets, help, or delays.",
            "Hello, how may I help you today?",
            "Hi! Please ask me about tickets, help, or delays.",
            "Hey! I currently offer assistance in booking tickets, "
            "providing help information, or estimate your train delay."
        ]
    }
    greeting_message = random.choice(bot_feedback['greeting'])  # plug in to random responses
    send(greeting_message)


@socketio.on('disconnect')
def user_disconnected():
    from model.reasoning_engine import refresh_user_knowledge
    print("hello")
    refresh_user_knowledge()


@socketio.on('message')
def receive_message(user_input):
    from model.reasoning_engine import process_user_input
    print("User message:" + user_input)
    # send to NLP
    nlp_response = parse_user_input(user_input)
    # send to RE
    process_user_input(nlp_response)


def run():
    socketio.run(app)


if __name__ == "__main__":
    run()
