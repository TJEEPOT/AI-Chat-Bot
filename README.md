# What It Does
This is an AI Chat Bot which gives details for train tickets, can give estimated arrival times if your train is delayed as well as giving helpful information regarding train services to the user.

# Usage Notes
To start the chatbot, run `python -m chatbot` from terminal inside the main project folder and navigate to 
http://127.0.0.1:5000/ in your browser.

To import data from DARWIN to the system, run `python -m data [table]` where `[table]` is the name of a table in 
database db. CSV files of the correct format in `\data\scraped` will then be transformed into the state needed for the 
model to interpret and added to the named table. Finally, processed files are moved to the `processed` folder inside 
`scraped`. 

# Credits
Designed by Natural Unintelligence - University of East Anglia (CMP) 2020/21:
* Steven Diep
* Sam Humphreys
* Martin Siddons
