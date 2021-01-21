"""

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : reasoning_engine.py
Date    : Friday 1 January 2021
Desc.   : Methods to handle conversation between user and bot through the use of forward chaining
History : 01/01/2021 - v1.0 - Created project file
          03/01/2021 - v1.1 - Completed handling ticket request from user
          05/01/2021 - v1.2 - Finished validation of information for ticket
          06/01/2021 - v1.3 - Completed option for return ticket
          10/01/2021 - v2.0 - Redesigned engine to understand delay queries
          11/01/2021 - v2.1 - Separated each piece of train information into their own methods
          14/01/2021 - v2.2 - Connected SQLite database to engine for validation of CRS code
          15/01/2021 - v2.3 - Conversation now loops to answer more than one query
          15/01/2021 - v2.4 - Immediately skips to confirmation of ticket if all information is provided at once
          15/01/2021 - v2.5 - Removed duplicate code when querying user for departure/arrival location
          16/01/2021 - v2.6 - End user can adjust their ticket information if input was incorrect
          17/01/2021 - v2.7 - Using a temporary dictionary to process query information to prepare integration with NLP

"""
import sqlite3
import datetime
from experta import *
from fuzzywuzzy import process

__author__ = "Steven Diep"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Steven Diep"
__email__ = "steven_diep@hotmail.co.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"

bot_feedback = {
    'greeting': [
        "Hello!",
        "Welcome!",
        "Hello, how may I help you today?",
        "Hi!",
        "Hey"
    ],
    'query': [
        "I can assist you with booking tickets, provide general information regarding train services "
        "or predict the arrival of your delayed train.",
        "Please ask me about booking tickets, train delay information, or help",
        "Would you like to book a ticket, see potential delays, or do you require general help?"
    ],
    'ask_from_location': [
        "Where are you travelling from?",
        "Where are you departing from?",
        "What is your departure station?",
        "Please tell me the station you are departing from.",
        "What station are you going from?",
        "What station are you travelling from?"
    ],
    'ask_to_location': [
        "Where is your destination?",
        "Where are you travelling to?",
        "Please tell me the station you are arriving at."
        "What station are you going to?",
        "What station are you travelling to",
        "Where is the station you are arriving at?"
    ],
    'ask_date': [
        "What date are you planning to leave on?",
        "Please tell me the date you are leaving.",
        "Please enter the date you are leaving.",
        "May you tell me the date you are departing?"
    ],
    'ask_time': [
        "What time are you departing?",
        "Please let me know the time you are leaving.",
        "May you tell me what time you are leaving?",
        "Please enter the time you are leaving."
    ],
    'ask_return': [
        "Are you returning?",
        "Will you be returning?",
        "Are you looking to purchase a return ticket?",
        "Will you return?",
        "Do you plan on returning?",
        "Would you like to purchase a return ticket?",
        "Would you like to make a return journey?"
    ],
    'ask_return_date': [
        "Please tell me the date you are returning.",
        "What date are you returning on?",
        "Please enter the date you are returning on.",
        "May you please tell me the date you are returning?"
    ],
    'ask_return_time': [
        "What time are you returning?",
        "Please enter the time you are returning.",
        "May you please tell me the time you are returning?"
    ],
    'ask_confirmation': [
        "Is this correct?",
        "May you please confirm the booking you made?",
        "Is your booking correct?",
        "Please confirm your booking."
    ],

    'no_answer': [
        "Sorry, I did not understand that.",
        "Sorry, I have no answer.",
        "I did not understand that, please ask again.",
        "Oops, I did not get that."
    ],
    'invalid_date': [
        "Please enter a valid date",
    ],
    'past_date': [

    ],
    'past_departure_date': [

    ],

}


class Chatbot(KnowledgeEngine):
    @DefFacts()
    def initial_action(self):
        yield Fact(action="begin")
        if self.dictionary.get("intent") != "":
            self.currentInfo['intent'] = self.dictionary.get('intent')
            yield Fact(queryType=self.dictionary.get('intent'))

        if self.dictionary.get("from_crs") != "":
            self.currentInfo['from_station'] = self.dictionary.get('from_station')
            self.currentInfo['from_crs'] = self.dictionary.get('from_crs')
            yield Fact(departure_location=self.dictionary.get('from_station'),
                       departCRS=self.dictionary.get('from_crs'))

        if self.dictionary.get("to_crs") != "":
            self.currentInfo['to_station'] = self.dictionary.get('to_station')
            self.currentInfo['to_crs'] = self.dictionary.get('to_crs')
            yield Fact(arrival_location=self.dictionary.get('to_station'),
                       arriveCRS=self.dictionary.get('to_crs'))

        if self.dictionary.get("outward_date") != "":
            self.currentInfo['outward_date'] = self.dictionary.get('outward_date')
            yield Fact(departure_date=self.dictionary.get('outward_date'))

        if self.dictionary.get("outward_time") != "":
            self.currentInfo['outward_time'] = self.dictionary.get('outward_time')
            yield Fact(leaving_time=self.dictionary.get('outward_time'))

        if self.dictionary.get("confirmation") != "":       # can only be true (yes) or false (no)
            if self.dictionary.get("confirmation"):
                self.currentInfo['confirmation'] = self.dictionary.get('confirmation')
                yield Fact(return_or_not="yes")
            else:
                self.currentInfo['confirmation'] = self.dictionary.get('confirmation')
                yield Fact(return_or_not="no")

        if self.dictionary.get("return_date") != "" and \
                self.dictionary.get("outward_date") <= self.dictionary.get("return_date"):
            self.currentInfo['return_date'] = self.dictionary.get('return_date')
            yield Fact(return_date=self.dictionary.get('return_date'))

        if self.dictionary.get("return_time") != "":
            if self.dictionary.get("outward_date") == self.dictionary.get("return_date") and \
                    self.dictionary.get("outward_time") < self.dictionary.get("return_time"):
                self.currentInfo['return_time'] = self.dictionary.get('return_time')
                yield Fact(return_time=self.dictionary.get('return_time'))

        if self.dictionary.get("no_category"):      # if list has is populated
            self.currentInfo['no_category'] = self.dictionary.get('no_category')
        print(self.currentInfo)

        '''if self.currentInfo.get("intent") != "":                # when the bot receives a new input the re will check the current info it already has 
            self.currentInfo['intent'] = self.dictionary.get('intent')
            yield Fact(queryType=self.dictionary.get('intent'))

        if self.currentInfo.get("from_crs") != "":
            self.currentInfo['from_station'] = self.dictionary.get('from_station')
            self.currentInfo['from_crs'] = self.dictionary.get('from_crs')
            yield Fact(departure_location=self.dictionary.get('from_station'),
                       departCRS=self.dictionary.get('from_crs'))

        if self.currentInfo.get("to_crs") != "":
            self.currentInfo['to_station'] = self.dictionary.get('to_station')
            self.currentInfo['to_crs'] = self.dictionary.get('to_crs')
            yield Fact(arrival_location=self.dictionary.get('to_station'),
                       arriveCRS=self.dictionary.get('to_crs'))

        if self.currentInfo.get("outward_date") != "":
            self.currentInfo['outward_date'] = self.dictionary.get('outward_date')
            yield Fact(departure_date=self.dictionary.get('outward_date'))

        if self.currentInfo.get("outward_time") != "":
            self.currentInfo['outward_time'] = self.dictionary.get('outward_time')
            yield Fact(leaving_time=self.dictionary.get('outward_time'))

        if self.currentInfo.get("confirmation") != "":       # can only be true (yes) or false (no)
            if self.dictionary.get("confirmation"):
                self.currentInfo['confirmation'] = self.dictionary.get('confirmation')
                yield Fact(return_or_not="yes")
            else:
                self.currentInfo['confirmation'] = self.dictionary.get('confirmation')
                yield Fact(return_or_not="no")

        if self.currentInfo.get("return_date") != "" and \
                self.dictionary.get("outward_date") <= self.dictionary.get("return_date"):
            self.currentInfo['return_date'] = self.dictionary.get('return_date')
            yield Fact(return_date=self.dictionary.get('return_date'))

        if self.currentInfo.get("return_time") != "":
            if self.dictionary.get("outward_date") == self.dictionary.get("return_date") and \
                    self.dictionary.get("outward_time") < self.dictionary.get("return_time"):
                self.currentInfo['return_time'] = self.dictionary.get('return_time')
                yield Fact(return_time=self.dictionary.get('return_time'))

        if self.currentInfo.get("no_category"):      # if list has is populated
            self.currentInfo['no_category'] = self.dictionary.get('no_category')'''

    @Rule(Fact(action='begin'))
    def ask_query_type(self):
        print("Hello, how may I help you today? \nI can assist you with booking tickets, "
              "provide general information regarding train services or predict the arrival "
              "of your delayed train.")  # sees this in the ui
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'intent':
                self.declare(Fact(queryType=v))
                break
            else:
                print("")  # TODO error message goes here

    @Rule(Fact(queryType='help'))
    def ask_help_type(self):
        print("What would you like help with?")
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'intent':
                self.declare(Fact(queryType=v))
                break
            else:
                print("")  # TODO error message goes here

    @Rule(Fact(queryType=L('ticket') | L('delay')))
    def ask_departure_station(self):
        print("Where are you departing from?")  # sees this in the ui
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'from_station' and v != '':
                self.declare(Fact(departure_location=v))
            elif k == 'from_crs' and v != '':
                self.declare(Fact(departCRS=v))
                break
            elif k == 'no_category':
                conn = sqlite3.connect(r'..\data\db.sqlite')
                c = conn.cursor()
                c.execute("SELECT crs FROM stations WHERE name=:location", {'location': v[0]})
                crs = c.fetchone()
                if crs is None:  # if the user enters the wrong station
                    print("Please enter a valid station.")
                else:
                    self.declare(Fact(departure_location=v[0], departCRS=crs))
                break

    @Rule(Fact(departure_location=W()))
    def ask_arrival_station(self):
        print("Where is your destination?")
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'to_station' and v != '':
                self.declare(Fact(arrival_location=v))
            elif k == 'to_crs' and v != '':
                self.declare(Fact(arriveCRS=v))
                break
            elif k == 'no_category':
                conn = sqlite3.connect(r'..\data\db.sqlite')
                c = conn.cursor()
                c.execute("SELECT crs FROM stations WHERE name=:location", {'location': v[0]})
                crs = c.fetchone()
                if crs is None:  # if the user enters the wrong station
                    print("Please enter a valid station.")
                else:
                    self.declare(Fact(arrival_location=v[0], arriveCRS=crs))
                break

    @Rule(Fact(departure_location=MATCH.departure_location),
          Fact(arrival_location=MATCH.arrival_location),
          Fact(queryType='delay')
          )
    def ask_time_delayed(self, departure_location, arrival_location):
        print("How long were you delayed by?")
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'raw_message' and v != '':
                delayTime = v.split()
                for minutes in delayTime:
                    if minutes.isdigit():

            else:
                pass
        delayedTime = input()  # input integer in minutes? maybe add way to convert hours into mins for longer delays

        print("time delayed:", delayedTime)
        print("departure location:", departure_location)
        print("arrival_location:", arrival_location)
        # TODO use prediction model here
        # self.declare(Fact(delay_time=delayedTime))  may need to declare delay time fact?
        # prediction_model(departure_location, arrival_location, delayedTime)
        print(engine.facts)  # TODO reset conversation, remove print statement later

    @Rule(Fact(arrival_location=W()),
          Fact(queryType=L('ticket'))
          )
    def ask_depart_date(self):
        print("What date are you leaving?")  # TODO plan nlp does the job in figuring out date, must leave it in
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'outward_date' and v != '':
                if datetime.date.today() > v:
                    print(
                        "Please enter a date that is %s or later." % datetime.date.today())  # TODO notify user they have to enter a date later than today or today
                else:
                    self.declare(Fact(departure_date=v))
                break
            elif k == 'no_category' and v:
                self.declare(Fact(departure_date=v[0]))
                break

    @Rule(Fact(departure_date=MATCH.departure_date), NOT(Fact()))
    def ask_depart_time(self, departure_date):
        print("What time are you leaving?")  # read as 24hr clock
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == 'outward_time' and v != '':
                now = datetime.datetime.now()
                current_hour_minute = datetime.time(now.hour, now.minute)
                if datetime.date.today() == departure_date and v < current_hour_minute:  # if booking is on same day, check if time entered is past current time
                    print(
                        "Please enter a time after %s" % current_hour_minute)  # TODO notify user they have to enter a time after current time
                else:
                    self.declare(Fact(leaving_time=v))
                    break
            elif k == 'no_category':
                self.declare(Fact(leaving_time=v[1]))
                break

    @Rule(Fact(leaving_time=W()), NOT(Fact(return_or_not=W())))
    def ask_return(self):
        print("Are you planning to return?")
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k == "confirmation" and v != '':
                if v:
                    self.declare(Fact(return_or_not="yes"))
                    break
                elif not v:
                    self.declare(Fact(return_or_not="no"))
                    self.declare(Fact(return_date=' '))
                    self.declare(Fact(return_time=' '))
                    break

    @Rule(Fact(return_date=MATCH.return_date), Fact(return_or_not='yes'))
    def missing(self, return_date):
        if return_date == '':
            print('what date would you like to return?')

    @Rule(Fact(return_or_not='yes'),
          Fact(departure_date=MATCH.departure_date)
          )
    def ask_return_date(self, departure_date):
        print("What date are you returning?") # send message
        for k, v in self.currentInfo.items():  # dictionary coming in
            if k in ['return_date', 'no_category'] and (v != '' or v):
                if isinstance(v, list):
                    if departure_date <= v[0]:
                        self.declare(Fact(return_date=v[0]))
                        break
                elif isinstance(v, datetime.date):
                    if departure_date <= v:
                        self.declare(Fact(return_date=v))
                        break
                else:
                    print("Please enter a date that is %s or later." % departure_date)

    @Rule(Fact(return_date=MATCH.return_date),
          Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time)
          )
    def ask_return_time(self, return_date, departure_date, leaving_time):
        print("What time would you like to return?")

        for k, v in self.currentInfo.items():  # dictionary coming in
            if k in ['return_time', 'no_category'] and (v != '' or v):
                if isinstance(v, list):
                    if departure_date != return_date and v[1] > leaving_time:  # if booking is on same day, check if time entered is past current time
                        self.declare(
                            Fact(return_time=v[1]))  # TODO notify user they have to enter a time after current time
                        break
                elif isinstance(v, datetime.time):
                    if departure_date != return_date and v > leaving_time:
                        self.declare(Fact(return_time=v))
                        break
                else:
                    print("Please enter a time after %s" % leaving_time)

    @Rule(Fact(return_or_not=MATCH.return_or_not),
          Fact(departure_location=MATCH.departure_location, departCRS=MATCH.departCRS),
          Fact(arrival_location=MATCH.arrival_location, arriveCRS=MATCH.arriveCRS),
          Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time),
          Fact(return_date=MATCH.return_date),
          Fact(return_time=MATCH.return_time)
          )
    def ask_confirmation(self, return_or_not, departure_location, departCRS,
                         arrival_location, arriveCRS, departure_date, leaving_time,
                         return_date, return_time):
        print("Please confirm your booking..."
              "\nDeparture datetime: ", departure_date, "at", leaving_time,
              "\nDeparting from: ", departure_location,
              "\nArriving at: ", arrival_location)
        if return_or_not == 'yes':
            print("Returning datetime: ", return_date, "at", return_time)
        print("Is this correct?")
        for k, v in self.currentInfo.items():
            if k == "confirmation" and v != '':
                if v:
                    print("CRS CODES BELONG HERE, DEPARTURE CRS:", departCRS, "ARRIVAL CRS:", arriveCRS)

                    print("SCRAPING...")
                    self.declare(Fact(correct_booking='yes'))
                elif not v:
                    self.declare(Fact(correct_booking='no'))
                else:
                    print("Sorry, I did not understand that.")

    @Rule(Fact(correct_booking='no'))
    def ask_adjustment(self):
        print("What would you like to adjust?")
        ticketInfo = input()
        if ticketInfo == 'station':  # redo station location
            print(engine.facts)  # TODO use reset engine
            engine.reset()

        elif ticketInfo == 'return':
            pass
        elif ticketInfo == 'date':
            pass
        elif ticketInfo == 'time':
            pass
        else:
            print("Sorry, I did not understand that.")

    @Rule(Fact(correct_booking='yes'))
    def end_query(self):
        print("Is there anything else I can help you with?")
        print("What else can I help you with?")
        engine.reset()
        print(engine.facts)
        for k, v in self.currentInfo.items():
            if k == "confirmation" and v != '':
                if ans in ['ticket', 'delay', 'help']:
                    engine.reset()
                    engine.declare(Fact(queryType=ans))
                    engine.run()
                elif not v:
                    engine.reset()  # decided to have the engine to be reset. not sure what else to do
                    engine.run()
                else:
                    print("Sorry, I did not understand that.")


engine = Chatbot()
engine.currentInfo = {}


def process_user_input(info):
    engine.dictionary = info
    print(engine.facts)
    engine.reset()
    engine.run()

processed_input_full = {  # example : i would like to book a ticket
    "intent": "ticket",
    "from_station": "Norwich",
    "from_crs": "NRW",
    "to_station": "London Liverpool Street",
    "to_crs": "LST",
    "outward_date": datetime.date(2021, 9, 1),
    "outward_time": datetime.time(20, 0),
    "return_date": '',  # datetime.date(2021, 9, 1)
    "return_time": '',  # datetime.time(19, 0)
    "confirmation": True,
    "no_category": [],
    "raw_message": "I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes"
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input7 = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [datetime.date(2021, 9, 20), datetime.time(0, 0)],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

process_user_input(processed_input_full)
process_user_input(processed_input7)

'''processed_input = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input1 = {  # example : i would like to book a ticket
    'intent': 'ticket',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input2 = {  # example : i would like to book a ticket
    "intent": "",
    "from_station": "",
    "from_crs": "",
    "to_station": "",
    "to_crs": "",
    "outward_date": "",
    "outward_time": "",
    "return_date": "",
    "return_time": "",
    "confirmation": "",
    "no_category": ["Norwich"],
    "raw_message": "norwich"
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input3 = {  # example : i would like to book a ticket
    "intent": "",
    "from_station": "",
    "from_crs": "",
    "to_station": "",
    "to_crs": "",
    "outward_date": "",
    "outward_time": "",
    "return_date": "",
    "return_time": "",
    "confirmation": "",
    "no_category": ["London Liverpool Street"],
    "raw_message": "london liverpool street"
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input4 = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [datetime.date(2021, 1, 20), datetime.time(0, 0)],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input5 = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [datetime.date.today(), datetime.time(2, 0)],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input6 = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': True,
    'no_category': [],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input8 = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [datetime.date.today(), datetime.time(21, 0)],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input9 = {  # example : i would like to book a ticket
    'intent': '',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': True,
    'no_category': [],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly

processed_input10 = {  # example : i would like to book a ticket
    'intent': 'ticket',
    'from_station': '', 'from_crs': '',
    'to_station': '', 'to_crs': '',
    'outward_date': '',  # datetime.date(2020, 1, 1),
    'outward_time': '',  # datetime.date(2020, 1, 1),
    'return_date': '',
    'return_time': '',
    'confirmation': '',
    'no_category': [],
    'raw_message': 'I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes'
}  # TODO change sql statement to use the crs code because some stations may be spelt incorrectly'''
