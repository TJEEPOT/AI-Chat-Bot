"""
Ensures all tests can import the model modules easily.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import model.scraper as scraper
import model.prediction_model as model
import chatbot.presenter as presenter
import data.process_data as process
import data.services as services
from data.services import Network