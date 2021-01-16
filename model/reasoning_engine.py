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

"""
import sqlite3
from datetime import date, time, datetime
from experta import *

__author__ = "Steven Diep"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Steven Diep"
__email__ = "steven_diep@hotmail.co.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"


class Chatbot(KnowledgeEngine):
    @DefFacts()
    def initial_action(self):
        yield Fact(action="begin")

    @Rule(Fact(action='begin'))
    def ask_query_type(self):
        print("Hello, how may I help you today? \nI can assist you with booking tickets, "
              "provide general information regarding train services or predict the arrival "
              "of your delayed train.")
        while True:
            queryChoice = input()
            if queryChoice in ['ticket', 'help', 'delay']:  # TODO nlp turns everything into lower case
                self.declare(Fact(queryType=queryChoice))
                break
            elif ',' in queryChoice:                         # if user already gives full info
                departure_location, arrival_location, departure_date, departure_time, \
                returning, return_date, return_time = queryChoice.split(',')                #example: Forest Gate,Abbey Wood,2021-09-09,13:00,yes,2021-09-09,21:00
                self.declare(Fact(departure_location=departure_location, departCRS='FOG'))  #TODO must figure out how to validate this part easily
                self.declare(Fact(arrival_location=arrival_location, arriveCRS='ABW'))      #TODO consult Sam
                self.declare(Fact(departure_date=departure_date))
                self.declare(Fact(leaving_time=departure_time))
                self.declare(Fact(return_or_not=returning))
                self.declare(Fact(return_date=return_date))
                self.declare(Fact(return_time=return_time))
                print(engine.facts)
                break
            else:                                           # should be in departure AND arrival AND depart_date AND depart_time AND returning AND return_date AND return_time format
                print("Please enter a suitable query.")

    @Rule(Fact(queryType='help'))
    def ask_help_type(self):
        print("What would you like help with?")
        helpChoice = input()
        if helpChoice in ['cancel', 'change', 'booking']:
            self.declare(Fact(helpType=helpChoice))
        else:
            print("Sorry, I did not understand that.")

    @Rule(Fact(queryType=L('ticket') | L('delay')))
    def ask_stations(self):
        ask_departure = True
        print("Where are you departing from?")
        while True:
            location = input()  # input string
            conn = sqlite3.connect(r'..\data\db.sqlite')
            c = conn.cursor()
            c.execute("SELECT crs FROM stations WHERE name=:location", {'location': location})
            crs = c.fetchone()
            if crs is None:
                print("Please enter a valid station.")
                continue
            if ask_departure:
                self.declare(Fact(departure_location=location, departCRS=crs[0]))
                ask_departure = False
                print("Where is your destination?")
                continue
            self.declare(Fact(arrival_location=location, arriveCRS=crs[0]))
            conn.close()
            break

    @Rule(Fact(departure_location=MATCH.departure_location), Fact(arrival_location=MATCH.arrival_location),
          Fact(queryType='delay'))
    def ask_time_delayed(self, departure_location, arrival_location):
        print("How long were you delayed by?")
        delayedTime = input()  # input integer in minutes? maybe add way to convert hours into mins for longer delays

        print("time delayed:", delayedTime)
        print("departure location:", departure_location)
        print("arrival_location:", arrival_location)
        # TODO use prediction model here
        # self.declare(Fact(delay_time=delayedTime))  may need to declare delay time fact?
        # prediction_model(departure_location, arrival_location, delayedTime)
        print(engine.facts)  # TODO reset conversation, remove print statement later

    @Rule(Fact(arrival_location=W()), Fact(queryType=L('ticket')))
    def ask_depart_date(self):
        print("What date are you leaving?")  # TODO plan nlp does the job in figuring out date, must leave it in
        while True:
            try:
                dateChoice = input()  # input YYYY/MM/DD
                year, month, day = map(int, dateChoice.split('-'))  # cant accept dates in the past or out of bounds months/days/years
                departure_date = date(year, month, day)
                if date.today() <= departure_date:
                    self.declare(Fact(departure_date=departure_date))
                    break
                else:
                    print("Please enter a date that is %s or later." % date.today())
            except ValueError:
                print("Please enter a valid date.")

    @Rule(Fact(departure_date=W()), Fact(departure_date=MATCH.departure_date))
    def ask_depart_time(self, departure_date):
        print("What time are you leaving?")  # read as 24hr clock
        while True:
            try:
                timeEntry = input()
                hour, minute = map(int, timeEntry.split(':'))
                departure_time = time(hour, minute)
                now = datetime.now()
                current_hour_minute = time(now.hour, now.minute)
                if date.today() == departure_date and departure_time < current_hour_minute:  # if booking is on same day, check if time entered is past current time
                    print("Please enter a time after %s" % current_hour_minute)
                    continue
                else:
                    self.declare(Fact(leaving_time=departure_time))
                    break
            except ValueError:
                print("Please enter a valid time.")

    @Rule(Fact(leaving_time=W()))
    def ask_return(self):
        print("Are you planning to return?")
        while True:
            ans = input()
            if ans == 'yes':
                self.declare(Fact(return_or_not=ans))
                break
            elif ans == 'no':
                self.declare(Fact(return_or_not=ans))
                self.declare(Fact(return_date=' '))
                self.declare(Fact(return_time=' '))
                break
            else:
                print("Sorry I did not understand that.")

    @Rule(Fact(return_or_not='yes'), Fact(departure_date=MATCH.departure_date))
    def ask_return_date(self, departure_date):
        print("What date are you returning?")
        while True:
            try:
                return_date = input()  # cant accept dates in the past or out of bounds months/days/years
                year, month, day = map(int, return_date.split('-'))
                chosenReturnDate = date(year, month, day)
                if departure_date <= chosenReturnDate:
                    self.declare(Fact(return_date=chosenReturnDate))
                    break
                else:
                    print("Please enter a date that is %s or later." % departure_date)
            except ValueError:
                print("Please enter a valid date.")

    @Rule(Fact(return_date=MATCH.return_date), Fact(departure_date=MATCH.departure_date),
          Fact(leaving_time=MATCH.leaving_time))
    def ask_return_time(self, return_date, departure_date, leaving_time):
        print("What time would you like to return?")
        while True:
            return_time = input()
            hour, minute = map(int, return_time.split(':'))
            chosenReturnTime = time(hour, minute)
            if departure_date == return_date and chosenReturnTime < leaving_time:  # if booking is on same day, check if time entered is past current time
                print("Please enter a time after %s" % leaving_time)
                continue
            else:
                self.declare(Fact(return_time=chosenReturnTime))
                break

    @Rule(Fact(return_or_not=MATCH.return_or_not),
          Fact(departure_location=MATCH.departure_location, departCRS=MATCH.departCRS),
          Fact(arrival_location=MATCH.arrival_location, arriveCRS=MATCH.arriveCRS),
          Fact(departure_date=MATCH.departure_date), Fact(leaving_time=MATCH.leaving_time),
          Fact(return_date=MATCH.return_date), Fact(return_time=MATCH.return_time)
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
        while True:
            ans = input()
            if ans == 'yes':
                print("CRS CODES BELONG HERE, DEPARTURE CRS:", departCRS, "ARRIVAL CRS:", arriveCRS)

                print("SCRAPING...")
                self.declare(Fact(correct_booking=ans))
                break
            elif ans == 'no':
                self.declare(Fact(correct_booking=ans))
                break
            else:
                print("Sorry, I did not understand that.")

    @Rule(Fact(correct_booking='no'))
    def ask_adjustment(self):
        print("What would you like to adjust?")
        while True:
            ticketInfo = input()
            if ticketInfo == 'station':         # redo station location
                print(engine.facts)#TODO use reset engine
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
        while True:
            ans = input()
            if ans in ['ticket', 'delay', 'help']:
                engine.reset()
                engine.declare(Fact(queryType=ans))
                engine.run()
            elif ans == 'no':
                engine.reset()          # decided to have the engine to be reset. not sure what else to do
                engine.run()
            else:
                print("Sorry, I did not understand that.")


engine = Chatbot()
engine.reset()
engine.run()
