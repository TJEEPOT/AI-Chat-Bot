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
import random
from fuzzywuzzy import process
from chatbot.presenter import send_message
from model.scraper import single_fare, return_fare

__author__ = "Steven Diep"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Steven Diep"
__email__ = "steven_diep@hotmail.co.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"

# TODO integrate dictionary bot_feedback
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
    'ask_time_delayed': [
        "How long are you delayed by?"
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
        "Please enter a valid date.",
        "The date you entered is invalid.",
        "Your chosen date is invalid."
    ],
    'past_date': [
        "The date you entered is a date that has already passed.",
        "Please enter today's date or later.",
        "Please enter a date either today or beyond.",
        "Your date should be today or later."
    ],
    'past_departure_date': [
        "Please enter the date of departure or later",
        ""
    ],
    'ask_correct_booking': [
        "Is this the correct booking?"
    ],
    'found_single_ticket': [
        "Here is your single ticket"
    ],
    'found_return_ticket': [
        "Here is your return ticket"
    ],
    'no_ticket_found': [
        "Sorry we could not find your ticket"
    ],
    'show_gratitude': [
        "Thank you for using my service!"
    ],
    'ask_adjustment': [
        "What would you like to adjust?"
    ],
    'next_query': [
        "Is there anything else I can help you with?",
        "What else can I help you with?"
    ]
}


class Chatbot(KnowledgeEngine):
    @DefFacts()
    def initial_action(self):
        yield Fact(action="begin")

        print(self.currentInfo)

        if 'intent' in self.currentInfo:  # when the bot receives a new input the re will check the current info what it already has
            yield Fact(queryType=self.currentInfo.get('intent'))

        if 'from_station' in self.currentInfo:  # when the bot receives a new input the re will check the current info it already has
            yield Fact(departure_location=self.currentInfo.get('from_station'),
                       departCRS=self.currentInfo.get('from_crs'))

        if 'to_station' in self.currentInfo:  # when the bot receives a new input the re will check the current info it already has
            yield Fact(arrival_location=self.currentInfo.get('to_station'),
                       arriveCRS=self.currentInfo.get('to_crs'))

        if 'outward_date' in self.currentInfo:  # when the bot receives a new input the re will check the current info it already has
            yield Fact(departure_date=self.currentInfo.get('outward_date'))

        if 'outward_time' in self.currentInfo:  # when the bot receives a new input the re will check the current info it already has
            yield Fact(leaving_time=self.currentInfo.get('outward_time'))

        if 'confirmation_return' in self.currentInfo:
            yield Fact(return_or_not=self.currentInfo.get('confirmation_return'))

        if 'return_date' in self.currentInfo:
            yield Fact(return_date=self.currentInfo.get('return_date'))

        if 'return_time' in self.currentInfo:
            yield Fact(return_time=self.currentInfo.get('return_time'))

        if 'correct_booking' in self.currentInfo:
            yield Fact(correct_booking=self.currentInfo.get('correct_booking'))

        '''if 'no_category' in self.currentInfo:
            yield Fact(return_time=self.currentInfo.get('no_category'))'''

    @Rule(Fact(action='begin'),
          NOT(Fact(queryType=W())),
          salience=50
          )
    def ask_query_type(self):
        if 'intent' in self.dictionary and self.dictionary.get('intent') != '':
            self.currentInfo['intent'] = self.dictionary.get('intent')
            self.declare(Fact(queryType=self.dictionary.get('intent')))
        else:
            send_message("Hello, how may I help you today? <br>I can assist you with booking tickets, "
                         "provide general information regarding train services or predict the arrival "
                         "of your delayed train.")  # sees this in the ui.
        '''for k, v in self.dictionary.items():  # dictionary coming in
            if k == 'intent':
                self.declare(Fact(queryType=v))
                break
            else:
                print("")  # TODO error message goes here'''

    @Rule(Fact(queryType='help'),
          salience=48
          )
    def ask_help_type(self):
        send_message("What would you like help with?")
        for k, v in self.dictionary.items():  # dictionary coming in
            if k == 'intent':
                self.declare(Fact(queryType=v))
                break
            else:
                print("")  # TODO error message goes here

    @Rule(Fact(queryType=L('ticket') | L('delay')),
          NOT(Fact(departure_location=W())),
          salience=46
          )
    def ask_departure_station(self):
        if 'from_station' in self.dictionary and self.dictionary.get('from_station') != '':
            self.currentInfo['from_station'] = self.dictionary.get('from_station')
            self.declare(Fact(departure_location=self.dictionary.get('from_station')))
        elif 'from_station' not in self.currentInfo and self.dictionary.get('no_category'):
            conn = sqlite3.connect(r'..\data\db.sqlite')
            c = conn.cursor()
            c.execute("SELECT crs FROM stations WHERE name=:location",
                      {'location': self.dictionary.get('no_category')[0]})
            crs = c.fetchone()
            if crs is not None:
                self.currentInfo['from_station'] = self.dictionary.get('no_category')[
                    0]  # this will prevent other no_category items from entering
                self.currentInfo['from_crs'] = crs[0]
                self.declare(Fact(departure_location=self.dictionary.get('no_category')[0], departCRS=crs[0]))
            else:
                send_message("Please enter a valid station.")
        else:
            if self.dictionary.get('intent') != '':
                send_message("Where are you departing from?")
            else:
                self.dictionary.get('raw_message')
                # check raw message
                # start fuzzy matching
                # if cant find anything send message below
                send_message("Please enter a valid station.")

    @Rule(Fact(departure_location=W()),
          NOT(Fact(arrival_location=W())),
          salience=44
          )
    def ask_arrival_station(self):
        if 'to_station' in self.dictionary and self.dictionary.get('to_station') != '':
            self.currentInfo['to_station'] = self.dictionary.get('to_station')
            self.declare(Fact(arrival_location=self.dictionary.get('to_station')))
        elif 'to_station' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('from_station'):
            conn = sqlite3.connect(r'..\data\db.sqlite')
            c = conn.cursor()
            c.execute("SELECT crs FROM stations WHERE name=:location",
                      {'location': self.dictionary.get('no_category')[0]})
            crs = c.fetchone()
            if crs is not None:
                self.currentInfo['to_station'] = self.dictionary.get('no_category')[0]
                self.currentInfo['to_crs'] = crs[0]
                self.declare(Fact(arrival_location=self.dictionary.get('no_category')[0], arriveCRS=crs[0]))
            else:
                send_message("Please enter a valid station")
        else:
            if self.currentInfo.get('from_station') != '':
                send_message("Where is your destination?")
            else:
                self.dictionary.get('raw_message')
                send_message("Please enter a valid station")

    @Rule(Fact(departure_location=MATCH.departure_location),
          Fact(arrival_location=MATCH.arrival_location),
          Fact(queryType='delay'),
          salience=42
          )
    def ask_time_delayed(self, departure_location, arrival_location):
        if 'raw_message' in self.dictionary and self.dictionary.get('raw_message') != '' and \
                not self.dictionary.get('no_category'):
            delay_time = self.dictionary.get('raw_message').split()
            for minutes in delay_time:
                if minutes.isdigit():
                    print("time delayed:", minutes)
                    print("departure location:", departure_location)
                    print("arrival_location:", arrival_location)
        else:
            send_message("How long were you delayed by?")  # TODO reset here

    @Rule(Fact(arrival_location=W()),
          Fact(queryType=L('ticket')),
          NOT(Fact(departure_date=W())),
          salience=40
          )
    def ask_depart_date(self):
        if 'outward_date' in self.dictionary and self.dictionary.get('outward_date') != '':
            if datetime.date.today() <= self.dictionary.get('outward_date'):
                self.currentInfo['outward_date'] = self.dictionary.get('outward_date')
                self.declare(Fact(departure_date=self.dictionary.get('outward_date')))
            else:
                send_message("Please enter a date that is " + str(datetime.date.today()) + " or later.")
        elif 'outward_date' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('to_station'):
            if datetime.date.today() <= self.dictionary.get('no_category')[0]:
                self.currentInfo['outward_date'] = self.dictionary.get('no_category')[0]
                self.declare(Fact(departure_date=self.dictionary.get('no_category')[0]))
            else:
                send_message("Please enter a date that is " + str(datetime.date.today()) + " or later.")
        else:
            send_message("What date are you leaving?")  # TODO if answer is not a date format

    @Rule(Fact(departure_date=MATCH.departure_date),
          NOT(Fact(leaving_time=W())),
          salience=38
          )
    def ask_depart_time(self, departure_date):
        now = datetime.datetime.now()
        current_hour_minute = datetime.time(now.hour, now.minute)
        if 'outward_time' in self.dictionary and self.dictionary.get('outward_time') != '':
            if datetime.date.today() == departure_date and self.dictionary.get('outward_time') < current_hour_minute:
                send_message("Please enter a time after " + str(current_hour_minute))
            else:
                self.currentInfo['outward_time'] = self.dictionary.get('outward_time')
                self.declare(Fact(leaving_time=self.dictionary.get('outward_time')))
        elif 'outward_time' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get(
            'outward_date'):  # TODO problem when you enter todays date when departing
            if datetime.date.today() == departure_date and self.dictionary.get('no_category')[1] < current_hour_minute:
                send_message("Please enter a time after " + str(current_hour_minute))
            else:
                self.currentInfo['outward_time'] = self.dictionary.get('no_category')[1]
                self.declare(Fact(leaving_time=self.dictionary.get('no_category')[1]))
        else:
            send_message("What time are you leaving?")  # TODO if answer is not a time format

    @Rule(Fact(leaving_time=W()),
          NOT(Fact(return_or_not=W())),
          salience=36
          )
    def ask_return(self):
        if 'confirmation' in self.dictionary and self.dictionary.get('confirmation') != '':
            self.currentInfo['confirmation_return'] = self.dictionary.get('confirmation')
            if not self.dictionary.get('confirmation'):  # if no
                self.currentInfo['return_date'] = self.dictionary.get('return_date')
                self.currentInfo['return_time'] = self.dictionary.get('return_time')
                self.declare(Fact(return_or_not=self.dictionary.get('confirmation')))
                self.declare(Fact(return_date=' '))
                self.declare(Fact(return_time=' '))
                self.dictionary['confirmation'] = ''
            else:
                self.declare(Fact(return_or_not=self.dictionary.get('confirmation')))
        else:
            send_message("Are you planning to return?")

    @Rule(Fact(return_or_not=True),
          Fact(departure_date=MATCH.departure_date),
          NOT(Fact(return_date=W())),
          salience=34
          )
    def ask_return_date(self, departure_date):
        if 'return_date' in self.dictionary and self.dictionary.get('return_date') != '':
            if departure_date <= self.dictionary.get('return_date'):
                self.currentInfo['return_date'] = self.dictionary.get('return_date')
                self.declare(Fact(return_date=self.dictionary.get('return_date')))
            else:
                send_message("Please enter a date that is " + str(departure_date) + " or later.")
        elif 'return_date' not in self.currentInfo and self.dictionary.get('no_category'):
            if departure_date <= self.dictionary.get('no_category')[0]:
                self.currentInfo['return_date'] = self.dictionary.get('no_category')[0]
                self.declare(Fact(return_date=self.dictionary.get('no_category')[0]))
            else:
                send_message("Please enter a date that is " + str(departure_date) + " or later.")
        else:
            send_message("What date are you returning?") # send message

    @Rule(Fact(return_date=MATCH.return_date),
          Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time),
          NOT(Fact(return_time=W())),
          salience=32
          )
    def ask_return_time(self, return_date, departure_date, leaving_time):
        if 'return_time' in self.dictionary and self.dictionary.get('return_time') != '':
            if departure_date == return_date and self.dictionary.get('return_time') < leaving_time:
                send_message("Please enter a time after " + leaving_time)
            else:
                self.currentInfo['return_time'] = self.dictionary.get('return_time')
                self.declare(Fact(return_time=self.dictionary.get('return_time')))
        elif 'return_time' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('return_date'):
            if departure_date == return_date and self.dictionary.get('no_category')[1] < leaving_time:
                send_message("Please enter a time after " + leaving_time)
            else:
                self.currentInfo['return_time'] = self.dictionary.get('no_category')[1]
                self.declare(Fact(return_time=self.dictionary.get('no_category')[1]))
        else:
            send_message("What time would you like to return?")

    @Rule(Fact(return_or_not=MATCH.return_or_not),
          Fact(departure_location=MATCH.departure_location, departCRS=MATCH.departCRS),
          Fact(arrival_location=MATCH.arrival_location, arriveCRS=MATCH.arriveCRS),
          Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time),
          Fact(return_date=MATCH.return_date),
          Fact(return_time=MATCH.return_time),
          NOT(Fact(correct_booking=W())),
          salience=30
          )
    def ask_correct_booking(self, return_or_not, departure_location, departCRS,
                            arrival_location, arriveCRS, departure_date, leaving_time,
                            return_date, return_time):
        if 'confirmation' in self.dictionary and self.dictionary.get('confirmation') != '':
            self.currentInfo['correct_booking'] = self.dictionary.get('confirmation')
            if self.dictionary.get('confirmation'):  # if confirmation is correct
                if return_or_not:  # is a return ticket
                    cost, time_out, time_ret, url = return_fare(departCRS, arriveCRS,
                                                                str(departure_date).replace('-', '/'),
                                                                leaving_time.strftime("%H:%M"),
                                                                str(return_date).replace('-', '/'),
                                                                return_time.strftime("%H:%M"))
                    send_message("Here is the return ticket that we could find for you: "
                                 + "<br>Total cost: " + str(cost)
                                 + "<br>Time outward: " + str(time_out)
                                 + "<br>Time return: " + str(time_ret)
                                 + "<br>URL: " + "<a href=" + str(url) + ">Link to ticket</a>")  # TODO if theres no ticket? maybe list multiple tickets in a 30 min range
                else:
                    cost, time, url = single_fare(departCRS, arriveCRS,
                                                  str(departure_date).replace('-', '/'),
                                                  leaving_time.strftime("%H:%M"))
                    send_message("Here is the single ticket that we could find for you: "
                                 + "<br>Total cost: " + str(cost)
                                 + "<br>Time: " + str(time)
                                 + "<br>URL: " + "<a href=" + str(url) + ">Link to ticket</a>")
                self.declare(Fact(correct_booking=self.dictionary.get('confirmation'))) # go to next query
                self.dictionary['confirmation'] = ''
            else:
                self.declare(Fact(correct_booking=self.dictionary.get('confirmation'))) # go to ask adjustment
                self.dictionary['confirmation'] = ''
        else:
            no_return = "Please confirm your booking...<br>Departure datetime: " + str(departure_date) + " at " \
                        + leaving_time.strftime("%H:%M") + "<br>Departing from: " + str(departure_location) \
                        + "<br>Arriving at: " + str(arrival_location)
            if return_or_not:
                returning = no_return \
                            + "<br>Returning datetime: " + str(return_date) \
                            + " at " + return_time.strftime("%H:%M")
                send_message(returning)
            else:
                send_message(no_return)

    @Rule(Fact(correct_booking=False),
          salience=28
          )
    def ask_adjustment(self):
        if self.dictionary.get('from_station') != '' or self.dictionary.get('to_station') != '' or \
                self.dictionary.get('outward_date') != '' or self.dictionary.get('outward_time') != '' or \
                self.dictionary.get('return_date') != '' or self.dictionary.get('return_time') != '':
            pass
        else:
            send_message("What would you like to adjust?")
        '''ticketInfo = input()
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
            print("Sorry, I did not understand that.")'''

    @Rule(Fact(correct_booking=True),
          salience=26
          )
    def next_query(self):
        if 'confirmation' in self.dictionary and self.dictionary.get('confirmation') != '':
            if self.dictionary.get('confirmation'):
                pass
            else:
                all_current_info = ['intent', 'from_station', 'to_station', 'from_crs', 'to_crs', 'outward_date',
                                      'outward_time', 'return_date', 'return_time', 'confirmation_return',
                                      'correct_booking']
                for key in all_current_info:
                    if key in self.currentInfo:
                        del self.currentInfo[key]
                send_message("Thank you for using our service!")
                engine.reset()
        else:
            send_message("Is there anything else I can help you with?")

engine = Chatbot()
engine.currentInfo = {}


def process_user_input(info):
    engine.dictionary = info
    print(engine.facts)
    print(engine.dictionary)
    print(engine.currentInfo)
    engine.reset()
    engine.run()
