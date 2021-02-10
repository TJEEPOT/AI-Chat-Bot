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
from chatbot.presenter import send_message, send_list
from model.scraper import single_fare, return_fare
from data.process_data import user_to_query

__author__ = "Steven Diep"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Steven Diep"
__email__ = "steven_diep@hotmail.co.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"

now = datetime.datetime.now()
current_hour_minute = datetime.time(now.hour, now.minute)

all_current_info = ['intent', 'from_station', 'to_station', 'from_crs', 'to_crs', 'outward_date',
                    'outward_time', 'return_date', 'return_time', 'confirmation_return',
                    'correct_booking']

bot_feedback = {
    'greeting': [
        "Hello! How may I help you today?",
        "Welcome! Please ask me about tickets, help, or delays.",
        "Hello, how may I help you today?",
        "Hi! Please ask me about tickets, help, or delays.",
        "Hey! I currently offer assistance in booking tickets, "
        "providing help information, or estimate your train delay."
    ],
    'query': [
        "I can assist you with booking tickets, provide general information regarding train services "
        "or predict the arrival of your delayed train.",
        "Please ask me about booking tickets, train delay information, or help",
        "Would you like to book a ticket, see potential delays, or do you require general help?"
    ],
    'ask_help': [
        "What would you like help with? I can provide information regarding cancelling, "
        "how to book a ticket, and changing tickets.",
        "How can I help you today? The options I can provide you are cancellation, booking, changing tickets.",
        "How may I help you? I can answer questions related to cancellation, booking, and changing tickets",
        "Please enter either cancellation, booking, or changing tickets so I can assist you.",
        "I can help you with cancellation, ticket, and changing tickets"
    ],
    'ask_from_location': [
        "Where are you travelling from?",
        "Where are you departing from?",
        "What is your departure station?",
        "Please tell me the station you are departing from.",
        "What station are you going from?",
        "What station are you travelling from?"
    ],
    "ask_current_location": [
        "What station are you currently at now?",
        "Where are you currently?",
        "What station are you delayed at?"
    ],
    'ask_to_location': [
        "Where is your destination?",
        "Where are you travelling to?",
        "Please tell me the station you are arriving at.",
        "What station are you going to?",
        "What station are you travelling to?"
    ],
    'show_wrong_station': [
        "Please enter a valid station.",
        "Enter a valid station.",
        "Station not recognised, please enter again.",
        "Try again, I do not recognise this station."
    ],
    'ask_time_delayed': [
        "How long are you delayed by?",
        "How many minutes were you delayed by?",
        "How late is your train?"
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
    'past_departure_date': [
        "Please enter a date that is current departure date or later."
    ],
    'past_departure_time': [
        "Please enter a time after current departure time"
    ],
    'no_answer': [
        "Sorry, I did not understand that.",
        "Sorry, I have no answer.",
        "I did not understand that, please ask again.",
        "Oops, I did not get that.",
        "Sorry, I did not catch that",
        "Please respond appropriately."
    ],
    'invalid_date': [
        "Please enter a valid date.",
        "The date you entered is invalid.",
        "Your chosen date is invalid."
    ],
    'invalid_time': [
        "Please enter a valid time.",
        "The time you entered is invalid.",
        "Your chosen date is invalid."
    ],
    'past_date': [
        "Please enter a date that is " + str(datetime.date.today()) + " or later.",
        "The date you entered is a date that has already passed.",
        "Please enter " + str(datetime.date.today()) + " or later.",
        "Please enter a date either today or beyond.",
        "Your date should be today or later."
    ],
    'past_time': [
        "Please enter a time after " + str(current_hour_minute),
        "Enter a time after " + str(current_hour_minute),
        "Your time must be after " + str(current_hour_minute)
    ],
    'ask_correct_booking': [
        "Is this the correct booking?",
        "Do I have the correct booking?",
        "Is this the right booking?",
        "Please let me know if this is correct."
    ],
    'found_single_ticket': [
        "Here is your single ticket :",
        "Here is the single ticket that we could find for you: "
    ],
    'found_return_ticket': [
        "Here is your return ticket: ",
        "Here is the return ticket that we could find for you: "
    ],
    'no_ticket_found': [
        "Sorry we could not find your ticket"
    ],
    'show_gratitude': [
        "Thank you for using my service! If you need anything else, you can enter another query just like before.",
        "Thank you, please use my service again.",
        "If you need something similar, you can enter another query just like before."
    ],
    'ask_adjustment': [
        "What would you like to adjust?",
        "What do you need to adjust?"
    ],
    'next_query': [
        "Is there anything else I can help you with?",
        "Do you still need any help?"
    ],
    'reset': [
        "Okay I will forget everything you have entered.",
        "Forgetting what you just said!"
    ]
}


class Chatbot(KnowledgeEngine):
    @DefFacts()
    def initial_action(self):
        yield Fact(action="begin")
        # when the bot receives a new input the re will check the current info it already has
        if 'intent' in self.currentInfo:
            yield Fact(queryType=self.currentInfo.get('intent'))

        if 'from_station' in self.currentInfo:
            yield Fact(departure_location=self.currentInfo.get('from_station'),
                       departCRS=self.currentInfo.get('from_crs'))

        if 'to_station' in self.currentInfo:
            yield Fact(arrival_location=self.currentInfo.get('to_station'),
                       arriveCRS=self.currentInfo.get('to_crs'))

        if 'outward_date' in self.currentInfo:
            yield Fact(departure_date=self.currentInfo.get('outward_date'))

        if 'outward_time' in self.currentInfo:
            yield Fact(leaving_time=self.currentInfo.get('outward_time'))

        if 'confirmation_return' in self.currentInfo:
            yield Fact(return_or_not=self.currentInfo.get('confirmation_return'))

        if 'return_date' in self.currentInfo:
            yield Fact(return_date=self.currentInfo.get('return_date'))

        if 'return_time' in self.currentInfo:
            yield Fact(return_time=self.currentInfo.get('return_time'))

        if 'correct_booking' in self.currentInfo:
            yield Fact(correct_booking=self.currentInfo.get('correct_booking'))

    @Rule(Fact(action='begin'),
          NOT(Fact(queryType=W())),
          salience=52)
    def ask_query_type(self):
        if 'intent' in self.dictionary and self.dictionary.get('intent') != '':
            self.currentInfo['intent'] = self.dictionary.get('intent')
            self.declare(Fact(queryType=self.dictionary.get('intent')))
        else:
            if self.dictionary.get('includes_greeting'):
                send_message(random.choice(bot_feedback['greeting']))
            else:
                if self.dictionary.get('intent') != '':
                    send_message(random.choice(bot_feedback['query']))
                else:
                    send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(queryType=L('help') | L('cancel') | L('change')),
          salience=50)
    def ask_help_type(self):
        if 'intent' in self.dictionary and self.dictionary.get('intent') in ['ticket', 'cancel', 'change']:
            if self.dictionary.get('intent') == 'ticket':
                send_message('Basic directions on using this bot: You are probably here because you are unsure '
                             'how to use the bot. For ticket booking, the bot requires you to let it '
                             'know you would like to make a booking, i.e. "I would like to book a ticket".'
                             'The bot then require you to enter location of departure and arrival, departure datetime, '
                             'whether you are returning, and if you are returning, the return datetime. The bot would '
                             'then repeat the information you have given and provide you with a link to your '
                             'ticket<br><br>'
                             'Purpose of this bot: This bot was designed to answer user queries about train delays, '
                             'provide some form of extra assistance regarding ticket information (where you are now), '
                             'and most of all provides the cheapest train ticket through user input')
            elif self.dictionary.get('intent') == 'cancel':
                send_message("For more information on cancelling your ticket please visit: "
                             "<a href=https://www.greateranglia.co.uk/contact-us/faqs/refunds>Link</a>")
            elif self.dictionary.get('intent') == 'change':
                send_message("If you would like to make adjustments to your ticket please use the link provided: "
                             "<a href=https://www.greateranglia.co.uk/contact-us/faqs/tickets>Link</a>")
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('intent') == 'help':
                send_message(random.choice(bot_feedback['ask_help']))
            else:
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(queryType=L('ticket') | L('delay')),
          NOT(Fact(departure_location=W())),
          salience=48)
    def ask_departure_station(self):
        if 'from_station' in self.dictionary and self.dictionary.get('from_station') != '':
            self.currentInfo['from_station'] = self.dictionary.get('from_station')
            self.currentInfo['from_crs'] = self.dictionary.get('from_crs')
            self.declare(Fact(departure_location=self.dictionary.get('from_station'),
                              departCRS=self.dictionary.get('from_crs')))
        elif 'from_station' not in self.currentInfo and self.dictionary.get('no_category') and \
                isinstance(self.dictionary.get('no_category')[0], str): # checks if the from and to stations are
            conn = sqlite3.connect(r'..\data\db.sqlite')              # present in the dictionary given through the NLP
            c = conn.cursor()
            c.execute("SELECT crs FROM stations WHERE name=:location",
                      {'location': self.dictionary.get('no_category')[0]})
            crs = c.fetchone()
            if crs is not None:
                self.currentInfo['from_station'] = self.dictionary.get('no_category')[0]
                self.currentInfo['from_crs'] = crs[0]
                self.declare(Fact(departure_location=self.dictionary.get('no_category')[0], departCRS=crs[0]))
            else:
                send_message(random.choice(bot_feedback['show_wrong_station']))
        elif self.dictionary.get('confirmation'):   # confirmation if the suggest station is correct
            conn = sqlite3.connect(r'..\data\db.sqlite')
            c = conn.cursor()
            c.execute("SELECT crs FROM stations WHERE name=:location",
                      {'location': self.currentInfo.get('possible_from_station')})
            crs = c.fetchone()
            if crs is not None:
                self.currentInfo['to_station'] = self.currentInfo.get('possible_from_station')
                self.declare(Fact(departure_location=self.currentInfo.get('possible_from_station'), departCRS=crs[0]))
                self.dictionary['confirmation'] = ''
            else:
                send_message(random.choice(bot_feedback['show_wrong_station']))
        elif self.dictionary.get('suggestion') and (not self.dictionary.get('no_category') or
                                                    isinstance(self.dictionary.get('no_category'), str)):
            count = 0
            for station_or_location in range(len(self.dictionary.get('suggestion'))):
                count += 1
                if 'station' in self.dictionary.get('suggestion')[station_or_location] and \
                        self.dictionary.get('from_station') != \
                        self.dictionary.get('suggestion')[station_or_location]['station'] \
                        and self.dictionary.get('to_station') != \
                        self.dictionary.get('suggestion')[station_or_location]['station']:
                    send_message("Did you mean " + self.dictionary['suggestion'][station_or_location]['station'] + "?")
                    self.currentInfo['possible_from_station'] = \
                        self.dictionary['suggestion'][station_or_location]['station']
                    break
                elif 'location' in self.dictionary.get('suggestion')[station_or_location]:
                    conn = sqlite3.connect(r'..\data\db.sqlite')
                    c = conn.cursor()
                    c.execute("SELECT name FROM stations WHERE county=:location ORDER BY served_2019 DESC",
                              {'location': self.dictionary['suggestion'][station_or_location]['location']})
                    top_5_stations = c.fetchmany(5)
                    send_list("Here is a list of possible stations in " +
                              self.dictionary['suggestion'][station_or_location]['location'] +
                              " you may be referring to: ", top_5_stations)
                    if self.dictionary.get('to_station') != '':
                        self.currentInfo['to_station'] = self.dictionary.get('to_station')
                        self.currentInfo['to_crs'] = self.dictionary.get('to_crs')
                    break
                elif count == len(self.dictionary.get('suggestion')):
                    send_message(random.choice(bot_feedback['ask_from_location']))
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('intent') == 'ticket':  # or self.dictionary.get('no_category')
                send_message(random.choice(bot_feedback['ask_from_location']))
            elif self.dictionary.get('intent') == 'delay':
                send_message(random.choice(bot_feedback['ask_current_location']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(queryType=L('ticket') | L('delay')),
          NOT(Fact(arrival_location=W())),
          salience=46)
    def set_arrival_or_time(self):      # sets arrival before arrival gets deleted
        if self.dictionary.get('to_station') != '':
            self.currentInfo['to_station'] = self.dictionary.get('to_station')
            self.currentInfo['to_crs'] = self.dictionary.get('to_crs')

    @Rule(Fact(queryType=L('ticket') | L('delay')),
          Fact(departure_location=W()),
          NOT(Fact(arrival_location=W())),
          salience=44)
    def ask_arrival_station(self):
        if 'to_station' in self.dictionary and self.dictionary.get('to_station') != '':
            self.currentInfo['to_station'] = self.dictionary.get('to_station')
            self.currentInfo['to_crs'] = self.dictionary.get('to_crs')
            self.declare(Fact(arrival_location=self.dictionary.get('to_station'),
                              arriveCRS=self.dictionary.get('to_crs')))
        elif 'to_station' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('from_station') and \
                isinstance(self.dictionary.get('no_category')[0], str):
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
                send_message(random.choice(bot_feedback['show_wrong_station']))
        elif self.dictionary.get('confirmation'):
            conn = sqlite3.connect(r'..\data\db.sqlite')
            c = conn.cursor()
            c.execute("SELECT crs FROM stations WHERE name=:location",
                      {'location': self.currentInfo.get('possible_to_station')})
            crs = c.fetchone()
            if crs is not None:
                self.currentInfo['to_station'] = self.currentInfo.get('possible_to_station')
                self.declare(Fact(arrival_location=self.currentInfo.get('possible_to_station'), arriveCRS=crs[0]))
            else:
                send_message(random.choice(bot_feedback['show_wrong_station']))
        elif self.dictionary.get('suggestion') and (not self.dictionary.get('no_category') or
                                                    isinstance(self.dictionary.get('no_category'), str)):
            count = 0
            for station_or_location in range(len(self.dictionary.get('suggestion'))):
                count += 1
                if 'station' in self.dictionary.get('suggestion')[station_or_location] and \
                        self.dictionary.get('from_station') != \
                        self.dictionary.get('suggestion')[station_or_location]['station'] \
                        and self.dictionary.get('to_station') != \
                        self.dictionary.get('suggestion')[station_or_location]['station']:
                    send_message("Did you mean " + self.dictionary['suggestion'][station_or_location]['station'] + "?")
                    self.currentInfo['possible_to_station'] = \
                        self.dictionary['suggestion'][station_or_location]['station']
                    break
                elif 'location' in self.dictionary.get('suggestion')[station_or_location]:
                    conn = sqlite3.connect(r'..\data\db.sqlite')
                    c = conn.cursor()
                    c.execute("SELECT name FROM stations WHERE county=:location ORDER BY served_2019 DESC",
                              {'location': self.dictionary['suggestion'][station_or_location]['location']})
                    top_5_stations = c.fetchmany(5)
                    send_list("Here is a list of possible stations in " +
                                 self.dictionary['suggestion'][station_or_location]['location'] +
                                 " you may be referring to: ", top_5_stations)
                    break
                elif count == len(self.dictionary.get('suggestion')):
                    send_message(random.choice(bot_feedback['ask_to_location']))
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('from_station') != '' or self.dictionary.get('no_category') or \
                    self.dictionary.get('confirmation') == '':
                send_message(random.choice(bot_feedback['ask_to_location']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(departure_location=MATCH.departure_location),
          Fact(arrival_location=MATCH.arrival_location),
          Fact(queryType='delay'),
          salience=42)
    def ask_time_delayed(self, departure_location, arrival_location):
        if 'raw_message' in self.dictionary and self.dictionary.get('raw_message') != '' and \
                not self.dictionary.get('no_category'):
            stations = [departure_location, arrival_location]
            tpl_stations = []
            conn = sqlite3.connect(r'..\data\db.sqlite')
            c = conn.cursor()
            for find_tpl in stations:
                c.execute("SELECT tpl FROM stations WHERE name=:location", {'location': find_tpl})
                tpl = c.fetchone()
                tpl_stations.append(tpl[0])
            delay_time = self.dictionary.get('raw_message').split()
            for minutes in delay_time:
                if minutes.isdigit():
                    send_message("Departure location: " + departure_location + "<br>"
                                    "Arrival location: " + arrival_location + "<br>"
                                    "Time you were delayed by: " + minutes + " minutes<br>"
                                    "Time you will be delayed till your final destination: " +
                                 str(user_to_query(tpl_stations[0], tpl_stations[1], int(minutes))) + " minutes")
                    refresh_user_knowledge()
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('to_station') != '' or self.dictionary.get('no_category'):
                send_message(random.choice(bot_feedback['ask_time_delayed']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(arrival_location=W()),
          Fact(queryType=L('ticket')),
          NOT(Fact(departure_date=W())),
          salience=40)
    def ask_depart_date(self):
        if 'outward_date' in self.dictionary and self.dictionary.get('outward_date') != '':
            if datetime.date.today() <= self.dictionary.get('outward_date'):
                if datetime.date.today() + datetime.timedelta(weeks=11) > self.dictionary.get('outward_date'):
                    self.currentInfo['outward_date'] = self.dictionary.get('outward_date')
                    self.declare(Fact(departure_date=self.dictionary.get('outward_date')))
                else:
                    send_message("Date can not be more than 11 weeks in the future. "
                                 "Please enter a valid departure date.")
            else:
                send_message(random.choice(bot_feedback['past_date']))
        elif 'outward_date' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('to_station') and \
                isinstance(self.dictionary.get('no_category')[0], datetime.date):
            if datetime.date.today() <= self.dictionary.get('no_category')[0]:
                if datetime.date.today() + datetime.timedelta(weeks=11) > self.dictionary.get('no_category')[0]:
                    self.currentInfo['outward_date'] = self.dictionary.get('no_category')[0]
                    self.declare(Fact(departure_date=self.dictionary.get('no_category')[0]))
                else:
                    send_message("Date can not be more than 11 weeks in the future. "
                                 "Please enter a valid departure date.")
            else:
                send_message(random.choice(bot_feedback['past_date']))
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if 'from_station' in self.currentInfo and (
                    self.dictionary.get('to_from') != '' or self.dictionary.get('no_category')):
                send_message(random.choice(bot_feedback['ask_date']))
            elif 'from_station' not in self.currentInfo:
                pass
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(departure_date=MATCH.departure_date),
          NOT(Fact(leaving_time=W())),
          salience=38)
    def ask_depart_time(self, departure_date):
        if 'outward_time' in self.dictionary and self.dictionary.get('outward_time') != '':
            if datetime.date.today() == departure_date and self.dictionary.get('outward_time') < current_hour_minute:
                send_message(random.choice(bot_feedback['past_time']))
            else:
                self.currentInfo['outward_time'] = self.dictionary.get('outward_time')
                self.declare(Fact(leaving_time=self.dictionary.get('outward_time')))
        elif 'outward_time' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('outward_date'):
            if datetime.date.today() == departure_date and self.dictionary.get('no_category')[0] < current_hour_minute:
                send_message(random.choice(bot_feedback['past_time']))
            else:
                self.currentInfo['outward_time'] = self.dictionary.get('no_category')[0]
                self.declare(Fact(leaving_time=self.dictionary.get('no_category')[0]))
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('outward_date') != '' or self.dictionary.get('no_category'):
                send_message(random.choice(bot_feedback['ask_time']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['invalid_time']))

    @Rule(Fact(leaving_time=W()),
          NOT(Fact(return_or_not=W())),
          salience=36)
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
        elif self.dictionary.get('return_date') != '' and self.dictionary.get('return_time') != '':
            self.currentInfo['confirmation_return'] = True
            self.declare(Fact(return_or_not=True))
        elif self.dictionary.get('reset'):
            send_message(random.choice(bot_feedback['reset']))
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('outward_time') != '' or self.dictionary.get('no_category'):
                send_message(random.choice(bot_feedback['ask_return']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(return_or_not=True),
          Fact(departure_date=MATCH.departure_date),
          NOT(Fact(return_date=W())),
          salience=34)
    def ask_return_date(self, departure_date):
        if 'return_date' in self.dictionary and self.dictionary.get('return_date') != '':
            if departure_date <= self.dictionary.get('return_date'):
                if datetime.date.today() + datetime.timedelta(weeks=11) > self.dictionary.get('return_date'):
                    self.currentInfo['return_date'] = self.dictionary.get('return_date')
                    self.declare(Fact(return_date=self.dictionary.get('return_date')))
                else:
                    send_message("Date can not be more than 11 weeks in the future. "
                                 "Please enter a valid return date.")
            else:
                send_message(random.choice(bot_feedback['past_departure_date']))
        elif 'return_date' not in self.currentInfo and self.dictionary.get('no_category'):
            if departure_date <= self.dictionary.get('no_category')[0]:
                if datetime.date.today() + datetime.timedelta(weeks=11) > self.dictionary.get('no_category')[0]:
                    self.currentInfo['return_date'] = self.dictionary.get('no_category')[0]
                    self.declare(Fact(return_date=self.dictionary.get('no_category')[0]))
                else:
                    send_message("Date can not be more than 11 weeks in the future. "
                                 "Please enter a valid return date.")
            else:
                send_message(random.choice(bot_feedback['past_departure_date']))
        elif self.dictionary.get('reset'):
            send_message("Okay I will forget everything you have entered.")
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('confirmation') != '':
                send_message(random.choice(bot_feedback['ask_return_date']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['invalid_date']))

    @Rule(Fact(return_date=MATCH.return_date),
          Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time),
          NOT(Fact(return_time=W())),
          salience=32)
    def ask_return_time(self, return_date, departure_date, leaving_time):
        if 'return_time' in self.dictionary and self.dictionary.get('return_time') != '':
            if departure_date == return_date and self.dictionary.get('return_time') < leaving_time:
                send_message(random.choice(bot_feedback['past_departure_time']))
            else:
                self.currentInfo['return_time'] = self.dictionary.get('return_time')
                self.declare(Fact(return_time=self.dictionary.get('return_time')))
        elif 'return_time' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('return_date'):
            if departure_date == return_date and self.dictionary.get('no_category')[0] < leaving_time:
                send_message(random.choice(bot_feedback['past_departure_time']))
            else:
                self.currentInfo['return_time'] = self.dictionary.get('no_category')[0]
                self.declare(Fact(return_time=self.dictionary.get('no_category')[0]))
        elif self.dictionary.get('reset'):
            send_message("Okay I will forget everything you have entered.")
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('return_date') != '' or self.dictionary.get('no_category'):
                send_message(random.choice(bot_feedback['ask_return_time']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['invalid_time']))

    @Rule(Fact(return_or_not=MATCH.return_or_not),
          Fact(departure_location=MATCH.departure_location, departCRS=MATCH.departCRS),
          Fact(arrival_location=MATCH.arrival_location, arriveCRS=MATCH.arriveCRS),
          Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time),
          Fact(return_date=MATCH.return_date),
          Fact(return_time=MATCH.return_time),
          NOT(Fact(correct_booking=W())),
          salience=30)
    def ask_correct_booking(self, return_or_not, departure_location, departCRS,
                            arrival_location, arriveCRS, departure_date, leaving_time,
                            return_date, return_time):
        if 'confirmation' in self.dictionary and self.dictionary.get('confirmation') != '':
            self.currentInfo['correct_booking'] = self.dictionary.get('confirmation')
            if self.dictionary.get('confirmation'):  # if confirmation is correct
                try:  # look for errors coming back
                    if return_or_not:  # is a return ticket
                        cost, time_out, time_ret, url = return_fare(departCRS, arriveCRS,
                                                                    str(departure_date).replace('-', '/'),
                                                                    leaving_time.strftime("%H:%M"),
                                                                    str(return_date).replace('-', '/'),
                                                                    return_time.strftime("%H:%M"))
                        send_message(random.choice(bot_feedback['found_return_ticket'])
                                     + "<br>Total cost: " + str(cost)
                                     + "<br>Time outward: " + str(time_out)
                                     + "<br>Time return: " + str(time_ret)
                                     + "<br>URL: " + "<a href=" + str(url)
                                     + ' target="_blank" rel ="noopener noreferrer" >Link to ticket</a>')
                    else:
                        cost, time, url = single_fare(departCRS, arriveCRS,
                                                      str(departure_date).replace('-', '/'),
                                                      leaving_time.strftime("%H:%M"))
                        send_message(random.choice(bot_feedback['found_single_ticket'])
                                     + "<br>Total cost: " + str(cost)
                                     + "<br>Time: " + str(time)
                                     + "<br>URL: " + "<a href=" + str(url)
                                     + ' target="_blank" rel ="noopener noreferrer" >Link to ticket</a>')
                    self.declare(Fact(correct_booking=self.dictionary.get('confirmation')))  # go to next query
                    self.dictionary['confirmation'] = ''
                except ValueError as e:
                    send_message(str(e))
                except NotImplementedError as e:
                    send_message(str(e))
            else:
                self.declare(Fact(correct_booking=self.dictionary.get('confirmation')))  # go to ask adjustment
        elif self.dictionary.get('reset'):
            send_message("Okay I will forget everything you have entered.")
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('return_time') != '' or self.dictionary.get('confirmation') == '' or \
                    self.dictionary.get('no_category'):
                no_return = "Is this information correct?" \
                            "<br>Departure datetime: " + str(departure_date) + " at " + leaving_time.strftime("%H:%M") \
                            + "<br>Departing from: " + str(departure_location) \
                            + "<br>Arriving at: " + str(arrival_location)
                if return_or_not:
                    returning = no_return \
                                + "<br>Returning datetime: " + str(return_date) \
                                + " at " + return_time.strftime("%H:%M")
                    send_message(returning)
                else:
                    send_message(no_return)
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(correct_booking=False),
          Fact(return_or_not=MATCH.return_or_not),
          salience=28)
    def ask_adjustment(self, return_or_not):
        if self.dictionary.get('raw_message') in ['Departure location', 'Arrival location',
                                                  'Departure date', 'Departure time',
                                                  'Change to single/return',
                                                  'Return date', 'Return time']:
            del self.currentInfo['correct_booking']
            if self.dictionary.get('raw_message') == 'Departure location':
                engine.reset()
                del self.currentInfo['from_station']
                del self.currentInfo['from_crs']
                send_message(random.choice(bot_feedback['ask_from_location']))
            elif self.dictionary.get('raw_message') == 'Arrival location':
                engine.reset()
                del self.currentInfo['to_station']
                del self.currentInfo['to_crs']
                send_message(random.choice(bot_feedback['ask_to_location']))
            elif self.dictionary.get('raw_message') == 'Departure date':
                del self.currentInfo['outward_date']
                send_message(random.choice(bot_feedback['ask_date']))
            elif self.dictionary.get('raw_message') == 'Departure time':
                del self.currentInfo['outward_time']
                send_message(random.choice(bot_feedback['ask_time']))
            elif self.dictionary.get('raw_message') == 'Change to single/return':
                del self.currentInfo['confirmation_return']
                del self.currentInfo['return_date']
                del self.currentInfo['return_time']
                send_message(random.choice(bot_feedback['ask_return']))
            elif self.dictionary.get('raw_message') == 'Return date':
                del self.currentInfo['return_date']
                send_message(random.choice(bot_feedback['ask_return_date']))
            elif self.dictionary.get('raw_message') == 'Return time':
                del self.currentInfo['return_time']
                send_message(random.choice(bot_feedback['ask_return_time']))
            else:
                send_message(random.choice(bot_feedback['no_answer']))
        elif self.dictionary.get('reset'):
            send_message("Okay I will forget everything you have entered.")
            engine.reset()
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
                elif self.currentInfo == {}:
                    send_message(random.choice(bot_feedback['greeting']))
                    break
        else:
            if self.dictionary.get('confirmation') != '':
                no_return = "To change your ticket information, please choose what to adjust:"
                list_no_return = ["Departure location",
                                  "Arrival location",
                                  "Departure date",
                                  "Departure time",
                                  "Change to single/return"]
                if return_or_not:
                    returning = no_return
                    list_returning = ["Return date",
                                      "Return time"]
                    send_list(returning, list_returning)  # random.choice(bot_feedback['ask_adjustment'])
                else:
                    send_list(no_return, list_no_return)
            else:
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(correct_booking=True),
          salience=26)
    def next_query(self):
        if self.dictionary.get('confirmation'):
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
            send_message(random.choice(bot_feedback['next_query']))
        elif self.dictionary.get('confirmation') == False:
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
            send_message(random.choice(bot_feedback['show_gratitude']))
        elif self.dictionary.get('intent') != '':
            for key in all_current_info:
                if key in self.currentInfo:
                    del self.currentInfo[key]
            if self.dictionary.get('intent') == 'ticket' or 'delay':
                self.currentInfo['intent'] = self.dictionary.get('intent')
                send_message(random.choice(bot_feedback['ask_from_location']))
            elif self.dictionary.get('intent') == 'help':
                self.currentInfo['intent'] = self.dictionary.get('intent')
                send_message(random.choice(bot_feedback['ask_help']))
            elif self.dictionary.get('intent') == 'cancel':
                self.currentInfo['intent'] = self.dictionary.get('intent')
                send_message("For more information on cancelling your ticket please visit: "
                             "<a href=https://www.greateranglia.co.uk/contact-us/faqs/refunds>Link</a>")
            elif self.dictionary.get('intent') == 'change':
                self.currentInfo['intent'] = self.dictionary.get('intent')
                send_message("If you would like to make adjustments to your ticket please use the link provided: "
                             "<a href=https://www.greateranglia.co.uk/contact-us/faqs/tickets>Link</a>")
        elif self.dictionary.get('confirmation') == '':
            send_message(random.choice(bot_feedback['next_query']))
        else:
            send_message(random.choice(bot_feedback['no_answer']))


engine = Chatbot()
engine.currentInfo = {}


def process_user_input(info):
    engine.dictionary = info
    print(engine.facts)
    print(engine.dictionary)
    print(engine.currentInfo)
    engine.reset()
    engine.run()


def refresh_user_knowledge():
    engine.reset()
    for key in all_current_info:
        if key in engine.currentInfo:
            del engine.currentInfo[key]
        elif engine.currentInfo == {}:
            break
