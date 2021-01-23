import unittest
import datetime
from datetime import  timedelta
from chatbot.nlp import parse_user_input


class MyTestCase(unittest.TestCase):
    date_today = datetime.date.today()
    processed_input_base = {
        "intent": "",                     # e.g tickets, help, delays
        "includes_greeting": False,
        "from_station": "",               # e.g Norwich
        "from_crs": "",                   # e.g NRW
        "to_station": "",                 # e.g London Liverpool Street
        "to_crs": "",                     # e.g LST
        "outward_date": "",               # e.g 20/01/2021
        "outward_time": "",               # e.g 10:00
        "return_date": "",                # e.g 20/01/2021 (checks done in RE for future date etc)
        "return_time": "",                # e.g 10:00
        "confirmation": "",               # e.g true / false response for bot asking confirmation
        "no_category": [],                # any extra data NLP can't work out intent for
        "raw_message": ""                 # raw message input by user for history etc
    }
    def test_process_intent(self):
        text_example = "book tickets"
        expected_output = {
            "intent": "ticket",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "book tickets"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "late"
        expected_output = {
            "intent": "delay",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "late"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "help"
        expected_output = {
            "intent": "help",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "help"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "change my ticket"
        expected_output = {
            "intent": "change",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "change my ticket"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "cancel a ticket"
        expected_output = {
            "intent": "cancel",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "cancel a ticket"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
    def test_process_depart(self):
        text_example = "norwich"
        expected_output = {
            "intent": "",
            "includes_greeting": False,
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
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
    def test_process_destination(self):
        text_example = "london liverpool street"
        expected_output = {
            "intent": "",
            "includes_greeting": False,
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
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_date_depart(self):
        text_example = "17/01/2021"
        expected_outward_date = datetime.date(2021, 1, 17)
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [expected_outward_date],
            "raw_message": "17/01/2021"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_time_depart(self):
        text_example = "14:00"

        expected_outward_time = datetime.time(14,0)
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [expected_outward_time],
            "raw_message": "14:00"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_is_returning(self):
        text_example = "yes"
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": True,
            "no_category": [],
            "raw_message": "yes"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_return_date(self):
        text_example = "18/01/2021"
        expected_return_date = datetime.date(2021,1,18)
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [expected_return_date],
            "raw_message": "18/01/2021"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

        text_example = "tomorrow"
        expected_return_date = datetime.date.today() + timedelta(1)
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [expected_return_date],
            "raw_message": "tomorrow"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "today"
        expected_return_date = datetime.date.today()
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [expected_return_date],
            "raw_message": "today"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_return_time(self):
        text_example = "7pm"
        expected_return_time = datetime.time(19,0)
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [expected_return_time],
            "raw_message": "7pm"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_confirm_correct(self):
        text_example = "no"
        expected_output = {
            "intent": "",
            "includes_greeting": False,
            "from_station": "",
            "from_crs": "",
            "to_station": "",
            "to_crs": "",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": False,
            "no_category": [],
            "raw_message": "no"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_process_input_long(self):
        text_example = "I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes"
        expected_outward_date = datetime.date(2020,1,1)
        expected_outward_time = datetime.time(12,0)
        expected_return_date = ""
        expected_return_time = ""
        expected_output = {
            "intent": "ticket",
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "London Liverpool Street",
            "to_crs": "LST",
            "outward_date": expected_outward_date,
            "outward_time": expected_outward_time,
            "return_date": expected_return_date,
            "return_time": expected_return_time,
            "confirmation": True,
            "no_category": [],
            "raw_message": "I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_tomorrow(self):
        text_example = "i want a ticket from norwich to forest gate tomorrow"
        expected_outward_date = datetime.date.today() + timedelta(1)
        expected_output = {
            "intent": "ticket",
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "Forest Gate",
            "to_crs": "FOG",
            "outward_date": expected_outward_date,
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "i want a ticket from norwich to forest gate tomorrow"
        }

        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_today(self):
        text_example = "i want a ticket from norwich to forest gate today"
        expected_outward_date = datetime.date.today()
        expected_output = {
            "intent": "ticket",
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "Forest Gate",
            "to_crs": "FOG",
            "outward_date": expected_outward_date,
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "raw_message": "i want a ticket from norwich to forest gate today"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_long_fog(self):
        text_example = "I would like to book a ticket from Norwich to Forest Gate on 2021/09/09 at 12:00 and returning on 2021/09/09 at 20:00"
        expected_outward_date = datetime.date(2021, 9, 9)
        expected_outward_time = datetime.time(12, 0)
        expected_return_date = datetime.date(2021, 9 ,9)
        expected_return_time = datetime.time(20,0)
        expected_output = {
            "intent": "ticket",
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "Forest Gate",
            "to_crs": "FOG",
            "outward_date": expected_outward_date,
            "outward_time": expected_outward_time,
            "return_date": expected_return_date,
            "return_time": expected_return_time,
            "confirmation": "",
            "no_category": [],
            "raw_message": "I would like to book a ticket from Norwich to Forest Gate on 2021/09/09 at 12:00 and returning on 2021/09/09 at 20:00"
        }
        print (expected_output)
        print (parse_user_input(text_example))
        self.assertDictEqual(expected_output, parse_user_input(text_example))
if __name__ == '__main__':
    unittest.main()
