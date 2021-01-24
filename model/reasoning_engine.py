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

now = datetime.datetime.now()
current_hour_minute = datetime.time(now.hour, now.minute)

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
    'ask_help': [
        "What would you like help with?",
        "How can I help you?",
        "How may I help you?",
        "Please enter your query so I can assist you."
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
        "Please tell me the station you are arriving at.",
        "What station are you going to?",
        "What station are you travelling to",
        "Where is the station you are arriving at?"
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
        "Thank you for using my service!"
    ],
    'ask_adjustment': [
        "What would you like to adjust?"
    ],
    'next_query': [
        "Is there anything else I can help you with?",
        "What else can I help you with?"
    ],
    'passive_aggressive_feedback': [
        "Good evening, you dense bastard. Did you get kicked in the head by a horse? "
        "Hurry up and answer appropriately, you silly imbecile. I am giving you five seconds to respond "
        "or else I will step out your screen to blow off your kneecaps"
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

    # TODO when sam finishes 'reset' in dict all_current info may have to be global

    @Rule(Fact(action='begin'),
          NOT(Fact(queryType=W())),
          salience=50)
    def ask_query_type(self):
        if 'intent' in self.dictionary and self.dictionary.get('intent') != '':
            self.currentInfo['intent'] = self.dictionary.get('intent')
            self.declare(Fact(queryType=self.dictionary.get('intent')))
            '''if self.dictionary.get('intent') == 'help':
                self.dictionary['intent'] = '''''
        else:
            if self.dictionary.get('includes_greeting'):
                send_message(random.choice(bot_feedback['greeting']))
            else:
                if self.dictionary.get('intent') != '':
                    send_message(random.choice(bot_feedback['query']))
                else:
                    send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(queryType=L('help') | L('cancel') | L('change')),
          salience=48)
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
                send_message("For more information on cancelling your ticket please visit "
                             "<a href=https://www.greateranglia.co.uk/contact-us/faqs/refunds>Link</a> ")
            elif self.dictionary.get('intent') == 'change':
                send_message("If you would like to make adjustments to your ticket please use the link provided: "
                             "<a href=https://www.greateranglia.co.uk/contact-us/faqs/tickets>Link</a>")
        else:
            if self.dictionary.get('intent') == 'help':
                send_message(random.choice(bot_feedback['ask_help']))
            else:
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(queryType=L('ticket') | L('delay')),
          NOT(Fact(departure_location=W())),
          salience=46)
    def ask_departure_station(self):
        if 'from_station' in self.dictionary and self.dictionary.get('from_station') != '':
            self.currentInfo['from_station'] = self.dictionary.get('from_station')
            self.currentInfo['from_crs'] = self.dictionary.get('from_crs')
            self.declare(Fact(departure_location=self.dictionary.get('from_station')))
        elif 'from_station' not in self.currentInfo and self.dictionary.get('no_category'):
            conn = sqlite3.connect(r'..\data\db.sqlite')
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
        else:
            if self.dictionary.get('intent') != '' or self.dictionary.get('no_category'):
                send_message(random.choice(bot_feedback['ask_from_location']))
            else:
                self.dictionary.get('raw_message')
                # check raw message
                # start fuzzy matching
                # if cant find anything send message below
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(departure_location=W()),
          NOT(Fact(arrival_location=W())),
          salience=44)
    def ask_arrival_station(self):
        if 'to_station' in self.dictionary and self.dictionary.get('to_station') != '':
            self.currentInfo['to_station'] = self.dictionary.get('to_station')
            self.currentInfo['to_crs'] = self.dictionary.get('to_crs')
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
                send_message(random.choice(bot_feedback['show_wrong_station']))
        else:
            if self.dictionary.get('from_station') != '' or self.dictionary.get('no_category'):
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
            delay_time = self.dictionary.get('raw_message').split()
            for minutes in delay_time:
                if minutes.isdigit():
                    print("time delayed:", minutes)
                    print("departure location:", departure_location)
                    print("arrival_location:", arrival_location)
        else:
            if self.dictionary.get('to_station') != '':
                send_message(random.choice(bot_feedback['ask_time_delayed']))  # TODO reset here
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
                self.currentInfo['outward_date'] = self.dictionary.get('outward_date')
                self.declare(Fact(departure_date=self.dictionary.get('outward_date')))
            else:
                send_message(random.choice(bot_feedback['past_date']))
        elif 'outward_date' not in self.currentInfo and self.dictionary.get('no_category') and \
                self.dictionary.get('no_category')[0] != self.currentInfo.get('to_station'):
            if datetime.date.today() <= self.dictionary.get('no_category')[0]:
                self.currentInfo['outward_date'] = self.dictionary.get('no_category')[0]
                self.declare(Fact(departure_date=self.dictionary.get('no_category')[0]))
            else:
                send_message(random.choice(bot_feedback['past_date']))
        else:
            if self.dictionary.get('to_from') != '' or self.dictionary.get('no_category'):
                send_message(random.choice(bot_feedback['ask_date']))
            else:
                self.dictionary.get('raw_message')
                send_message(random.choice(bot_feedback['invalid_date']))

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
                self.currentInfo['return_date'] = self.dictionary.get('return_date')
                self.declare(Fact(return_date=self.dictionary.get('return_date')))
            else:
                send_message(random.choice(bot_feedback['past_departure_date']))
        elif 'return_date' not in self.currentInfo and self.dictionary.get('no_category'):
            if departure_date <= self.dictionary.get('no_category')[0]:
                self.currentInfo['return_date'] = self.dictionary.get('no_category')[0]
                self.declare(Fact(return_date=self.dictionary.get('no_category')[0]))
            else:
                send_message(random.choice(bot_feedback['past_departure_date']))
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
                                 + "<br>URL: " + "<a href=" + str(url) + ">Link to ticket</a>")
                    # TODO if theres no ticket? maybe list multiple tickets in a 30 min range
                else:
                    cost, time, url = single_fare(departCRS, arriveCRS,
                                                  str(departure_date).replace('-', '/'),
                                                  leaving_time.strftime("%H:%M"))
                    send_message(random.choice(bot_feedback['found_single_ticket'])
                                 + "<br>Total cost: " + str(cost)
                                 + "<br>Time: " + str(time)
                                 + "<br>URL: " + "<a href=" + str(url) + ">Link to ticket</a>")
                self.declare(Fact(correct_booking=self.dictionary.get('confirmation')))  # go to next query
                self.dictionary['confirmation'] = ''
            else:
                self.declare(Fact(correct_booking=self.dictionary.get('confirmation')))  # go to ask adjustment
                self.dictionary['confirmation'] = ''
        else:
            if self.dictionary.get('return_time') != '' or self.dictionary.get('confirmation') != '' or \
                    self.dictionary.get('no_category'):
                no_return = "Please confirm your booking..." \
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
    #TODO still need to figure out to adjust info
    @Rule(Fact(correct_booking=False),
          salience=28)
    def ask_adjustment(self):
        if self.dictionary.get('intent') == 'change' and self.dictionary.get('from_station') != '' or self.dictionary.get('to_station') != '' or \
                self.dictionary.get('outward_date') != '' or self.dictionary.get('outward_time') != '' or \
                self.dictionary.get('return_date') != '' or self.dictionary.get('return_time') != '':
            pass
        else:
            if self.dictionary.get('confirmation') != '':
                send_message("What would you like to adjust?")
            else:
                send_message(random.choice(bot_feedback['no_answer']))

    @Rule(Fact(correct_booking=True),
          salience=26)
    def next_query(self):
        if 'confirmation' in self.dictionary and \
                (self.dictionary.get('confirmation') != '' or self.dictionary.get('intent') != ''):
            all_current_info = ['intent', 'from_station', 'to_station', 'from_crs', 'to_crs', 'outward_date',
                                'outward_time', 'return_date', 'return_time', 'confirmation_return',
                                'correct_booking']
            if self.dictionary.get('confirmation'):
                send_message("What can I help you with?")
            elif not self.dictionary.get('confirmation'):
                for key in all_current_info:
                    if key in self.currentInfo:
                        del self.currentInfo[key]
                send_message("Thank you for using our service!")
                engine.reset()
            elif self.dictionary.get('intent') == 'ticket':
                all_current_info.pop(0)
                for key in all_current_info:
                    if key in self.currentInfo:
                        del self.currentInfo[key]
                engine.reset()
            elif self.dictionary.get('intent') == 'help':
                for key in all_current_info:
                    if key in self.currentInfo:
                        del self.currentInfo[key]
                self.currentInfo['intent'] = self.dictionary.get('intent')
                engine.reset()
            elif self.dictionary.get('intent') == 'cancellation':
                for key in all_current_info:
                    if key in self.currentInfo:
                        del self.currentInfo[key]
                self.currentInfo['intent'] = self.dictionary.get('intent')
                engine.reset()
            elif self.dictionary.get('intent') == 'change':
                for key in all_current_info:
                    if key in self.currentInfo:
                        del self.currentInfo[key]
                self.currentInfo['intent'] = self.dictionary.get('intent')
                engine.reset()
        else:
            if self.dictionary.get('confirmation') == '':
                send_message("Is there anything else I can help you with?")
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
