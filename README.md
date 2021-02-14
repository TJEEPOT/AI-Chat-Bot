# What It Does
This is an AI Chat Bot which gives details for train tickets, can give estimated arrival times if your train is delayed as well as giving helpful information regarding train services to the user.

Note: Jupyter notebooks have been left in the model folder in order to show some of the testing code used when evaluating the models. 

# Setup Notes
Clone this repo and set up your venv. Install pips from requirements.txt then run `python -m spacy download 
en_core_web_sm` to ensure spacy has the correct files.

# Usage Notes
To start the chatbot, run `python -m chatbot` from terminal inside the main project folder and navigate to 
http://127.0.0.1:5000/ in your browser.

To import data from HSP or DARWIN to the system, run `python -m data [HSP/DARWIN] [table]` where `[HSP/DARWIN` is the format of the dataset and `[table]` is the name of a table in database db. CSV files of the correct format in `\data\scraped` will then be transformed into the state needed for the model to interpret and added to the named table. Finally, processed files are moved to the `processed` folder inside `scraped`. 

# Credits
Designed by Natural Unintelligence - University of East Anglia (CMP) 2020/21:
* Steven Diep
* Sam Humphreys
* Martin Siddons
