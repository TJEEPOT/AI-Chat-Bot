import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import chatbot.scraper as scraper
import chatbot.prediction_model as model