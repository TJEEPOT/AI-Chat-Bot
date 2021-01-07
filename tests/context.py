"""
Ensures all tests can import the model modules easily.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import model.scraper as scraper
import model.prediction_model as model
import model.reasoning_engine as re