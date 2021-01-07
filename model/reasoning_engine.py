"""

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : reasoning_engine.py
Date    : Friday 1 January 2021
Desc.   : Methods to handle conversation between user and bot.
History : 01/01/2021 - v1.0 - Created project file
          03/01/2021 - v1.1 - Completed handling ticket request from user
          05/01/2021 - v1.2 - Finished validation of information for ticket
          06/01/2021 - v1.3 - Completed option for return ticket
"""

from datetime import date, time, datetime
from experta import *

__author__     = "Steven DIep"
__credits__    = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Steven Diep"
__email__      = "steven_diep@hotmail.co.uk"
__status__     = "Prototype"  # "Development" "Prototype" "Production"

class Chatbot(KnowledgeEngine):
    @DefFacts()
    def initial_action(self):
        yield Fact(action="greet")

    @Rule(Fact(action='greet'))
    def start_convo(self):
        print("Hello, how may I help you today? \nI can assist you with booking tickets, "
              "provide general information regarding train services or predict the arrival "
              "of your delayed train.")
        while True:
            queryChoice = input()
            if queryChoice in ['ticket', 'help', 'delay']:  # TODO nlp must turn everything into lower case
                self.declare(Fact(query=queryChoice))
                break
            else:
                print("Please enter a suitable query.")

    @Rule(Fact(query='delay'))
    def delay_convo(self):
        print("What station are you at now?")

    @Rule(Fact(query='help'))
    def help_convo(self):
        print("Changing or cancelling ticket")

    @Rule(Fact(query='ticket'))
    def ticket_convo(self):
        print("Where are you departing from?")  # TODO
        departure_location = input()
        self.declare(Fact(departure_location=departure_location))

        print("Where is your destination?")  # TODO
        chosenArrival = input()
        self.declare(Fact(arrival_location=chosenArrival))

        print("What date are you leaving?")  # TODO plan nlp does the job in figuring out date, must leave it in
        while True:  # YYYY-MM-DD format. then datetime.date class gets filtered into the fact base
            try:
                dateChoice = input()  # cant accept dates in the past or out of bounds months/days/years
                year, month, day = map(int, dateChoice.split('-'))
                chosenDate = date(year, month, day)
                if date.today() <= chosenDate:
                    self.declare(Fact(departure_date=chosenDate))
                    break
                else:
                    print("Please enter a date that is %s or later." % date.today())
            except ValueError:
                print("Please enter a valid date.")

        print("What time are you leaving?")  # read as 24hr clock
        while True:
            try:
                timeEntry = input()
                hour, minute = map(int, timeEntry.split(':'))
                chosenTime = time(hour, minute)
                now = datetime.now()
                current_hour_minute = time(now.hour, now.minute)
                if date.today() == chosenDate and chosenTime < current_hour_minute:  # if booking is on same day, check if time entered is past current time
                    print("Please enter a time after %s" % current_hour_minute)
                    continue
                else:
                    self.declare(Fact(leaving_time=chosenTime))
                    break
            except ValueError:
                print("Please enter a valid time.")

        print(
            "Are you planning to return?")  # TODO this is optional whether the customer would like to return. yes or no question
        while True:
            ans = input()
            if ans == 'yes':
                print("What date are you returning?")  # TODO
                while True:
                    try:
                        return_date = input()  # cant accept dates in the past or out of bounds months/days/years
                        year, month, day = map(int, return_date.split('-'))
                        chosenReturnDate = date(year, month, day)
                        if chosenDate <= chosenReturnDate:
                            self.declare(Fact(return_date=chosenDate))
                            break
                        else:
                            print("Please enter a date that is %s or later." % chosenDate)
                    except ValueError:
                        print("Please enter a valid date.")

                print("What time would you like to return?")
                while True:
                    return_time = input()
                    hour, minute = map(int, return_time.split(':'))
                    chosenReturnTime = time(hour, minute)
                    now = datetime.now()
                    current_hour_minute = time(now.hour, now.minute)
                    if chosenDate == chosenReturnDate and chosenReturnTime < chosenTime:  # if booking is on same day, check if time entered is past current time
                        print("Please enter a time after %s" % chosenTime)
                        continue
                    else:
                        self.declare(Fact(return_time=chosenReturnTime))
                        break
                self.declare(Fact(return_or_not=ans))
                break
            elif ans == 'no':
                self.declare(Fact(return_or_not=ans))
                break
            else:
                print("Sorry I did not understand that.")

    @Rule(Fact(return_or_not='no'),
          Fact(departure_location=MATCH.departure_location), Fact(arrival_location=MATCH.arrival_location),
          Fact(departure_date=MATCH.departure_date), Fact(leaving_time=MATCH.leaving_time)
          )
    def confirmation_no_return(self, departure_location, arrival_location, departure_date, leaving_time):
        print("Please confirm your booking..."
              "\nDeparture datetime: ", departure_date, "at", leaving_time,
              "\nDeparting from: ", departure_location,
              "\nArriving at: ", arrival_location)
        print("Would you like to book another ticket?")

    @Rule(Fact(return_or_not='yes'),
          Fact(departure_location=MATCH.departure_location), Fact(arrival_location=MATCH.arrival_location),
          Fact(departure_date=MATCH.departure_date), Fact(leaving_time=MATCH.leaving_time),
          Fact(return_date=MATCH.return_date), Fact(return_time=MATCH.return_time)
          )
    def confirmation_return(self, departure_location, arrival_location, departure_date, leaving_time,
                            return_date, return_time):
        print("Please confirm your booking..."
              "\nDeparture datetime: ", departure_date, "at", leaving_time,
              "\nDeparting from: ", departure_location,
              "\nArriving at: ", arrival_location,
              "\nReturning datetime: ", return_date, "at", return_time)
        print("Is this correct?")
        while True:
            scape_or_not = input()
            if scape_or_not == 'yes':

                print("Would you like to book another ticket?")
            elif scape_or_not == 'no':
                pass


engine = Chatbot()
engine.reset()  # Prepare the engine for the execution.
engine.run()  # Run it
