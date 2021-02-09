import unittest
import datetime
from datetime import  timedelta
from chatbot.nlp import parse_user_input,check_spellings,remove_punctuation,sanitize_input

class MyTestCase(unittest.TestCase):
    date_today = datetime.date.today()

    def test_process_intent(self):
        text_example = "book tickets"
        expected_output = {
            "intent": "ticket",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "book tickets",
            "raw_message": "book tickets"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "delayed"
        expected_output = {
            "intent": "delay",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "delayed",
            "raw_message": "delayed"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "help"
        expected_output = {
            "intent": "help",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "help",
            "raw_message": "help"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "change my ticket"
        expected_output = {
            "intent": "change",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "change my ticket",
            "raw_message": "change my ticket"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "cancellation"
        expected_output = {
            "intent": "cancel",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "cancellation",
            "raw_message": "cancellation"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_reset(self):
        text_example = "reset"
        expected_output = {
            "intent": "",
            "reset": True,
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
            "suggestion": [],
            "sanitized_message": "reset",
            "raw_message": "reset"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_depart(self):
        text_example = "norwich"
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "norwich",
            "raw_message": "norwich"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
    def test_process_destination(self):
        text_example = "london liverpool street"
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [{'station': 'London Liverpool Street'}],
            "sanitized_message": "london liverpool street",
            "raw_message": "london liverpool street"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_date_depart(self):
        text_example = "04/02/2021"
        expected_outward_date = datetime.date(2021, 2, 4)
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "04022021",
            "raw_message": "04/02/2021"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_time_depart(self):
        text_example = "14:00"

        expected_outward_time = datetime.time(14,0)
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "1400",
            "raw_message": "14:00"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_is_returning(self):
        text_example = "yes"
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "yes",
            "raw_message": "yes"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_return_date(self):
        text_example = "18/01/2021"
        expected_return_date = datetime.date(2021,1,18)
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "18012021",
            "raw_message": "18/01/2021"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

        text_example = "tomorrow"
        expected_return_date = datetime.date.today() + timedelta(1)
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "tomorrow",
            "raw_message": "tomorrow"
        }
        resulting_dict = parse_user_input(text_example)
        print(resulting_dict)
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "today"
        expected_return_date = datetime.date.today()
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "today",
            "raw_message": "today"
        }

        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_return_time(self):
        text_example = "7pm"
        expected_return_time = datetime.time(19,0)
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "7pm",
            "raw_message": "7pm"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_confirm_correct(self):
        text_example = "no"
        expected_output = {
            "intent": "",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "no",
            "raw_message": "no"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_process_input_long(self):
        self.maxDiff = None
        text_example = "I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes"
        expected_outward_date = datetime.date(2020,1,1)
        expected_outward_time = datetime.time(12,0)
        expected_return_date = ""
        expected_return_time = ""
        expected_output = {
            "intent": "ticket",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "i want to travel from norwich to london liverpool street on 01012020 at 12pm nrw yes",
            "raw_message": "I want to travel from norwich to london liverpool street on 01/01/2020 at 12pm nrw yes"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_tomorrow(self):
        text_example = "i want a ticket from norwich to forest gate tomorrow"
        expected_outward_date = datetime.date.today() + timedelta(1)
        expected_output = {
            "intent": "ticket",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "i want a ticket from norwich to forest gate tomorrow",
            "raw_message": "i want a ticket from norwich to forest gate tomorrow"
        }

        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_today(self):
        text_example = "I want a ticket from norwich to forest gate today"
        expected_outward_date = datetime.date.today()
        expected_output = {
            "intent": "ticket",
            "reset": False,
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
            "suggestion": [],
            "sanitized_message": "i want a ticket from norwich to forest gate today",
            "raw_message": "I want a ticket from norwich to forest gate today"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_process_input_crs(self):
        text_example = "nrw to FOG"
        expected_outward_date = datetime.date.today()
        expected_output = {
            "intent": "",
            "reset": False,
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "Forest Gate",
            "to_crs": "FOG",
            "outward_date": "",
            "outward_time": "",
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "suggestion": [],
            "sanitized_message": "nrw to fog",
            "raw_message": "nrw to FOG"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
    def test_process_input_multiple(self):
        text_example = "i want a Ticket to lodnon"
        expected_output = {
            "intent": "ticket",
            "reset": False,
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
            "suggestion": [{'location': 'Greater London'}],
            "sanitized_message": "i want a ticket to london",
            "raw_message": "i want a Ticket to lodnon"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_sepdate(self):
        self.maxDiff = None
        text_example = "I want to travel from Norwich to London Liverpool street tomorrow at 5pm"
        expected_outward_date = datetime.date.today() + timedelta(1)
        expected_outward_time = datetime.time(17, 0)
        expected_output = {
            "intent": "ticket",
            "reset": False,
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "London Liverpool Street",
            "to_crs": "LST",
            "outward_date": expected_outward_date,
            "outward_time": expected_outward_time,
            "return_date": "",
            "return_time": "",
            "confirmation": "",
            "no_category": [],
            "suggestion": [],
            "sanitized_message": "i want to travel from norwich to london liverpool street tomorrow at 5pm",
            "raw_message": "I want to travel from Norwich to London Liverpool street tomorrow at 5pm"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_process_input_long_fog(self):
        self.maxDiff = None
        text_example = "I would like to book a ticket from Norwich to Forest Gate on 09/09/2021 at 12:00 and " \
                       "return on 09/09/2021 at 20:00"
        expected_outward_date = datetime.date(2021, 9, 9)
        expected_outward_time = datetime.time(12, 0)
        expected_return_date = datetime.date(2021, 9, 9)
        expected_return_time = datetime.time(20, 0)

        expected_output = {
            "intent": "ticket",
            "reset": False,
            "includes_greeting": False,
            "from_station": "Norwich",
            "from_crs": "NRW",
            "to_station": "Forest Gate",
            "to_crs": "FOG",
            "outward_date": datetime.date(2021, 9, 9),
            "outward_time": datetime.time(12, 0),
            "return_date": datetime.date(2021, 9, 9),
            "return_time": datetime.time(20, 0),
            "confirmation": "",
            "no_category": [],
            "suggestion": [],
            "sanitized_message": "i would like to book a ticket from norwich to forest gate on 09092021 at 1200 "
                                 "and return on 09092021 at 2000",
            "raw_message": "I would like to book a ticket from Norwich to Forest Gate on 09/09/2021 at 12:00 and " \
                       "return on 09/09/2021 at 20:00"
        }

        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_location_specific(self):
        text_example = "Tonbridge"
        expected_output = {
            "intent": "",
            "reset": False,
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
            "no_category": ["Tonbridge"],
            "suggestion": [{'station': 'Tonbridge'}],
            "sanitized_message": "tonbridge",
            "raw_message": "Tonbridge"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_location_specific_two(self):
        text_example = "Ipswitch"
        expected_output = {
            "intent": "",
            "reset": False,
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
            "no_category": ["Ipswich"],
            "suggestion": [{'station': 'Ipswich'}],
            "sanitized_message": "ipswich",
            "raw_message": "Ipswitch"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_spellcheck(self):
        text_example = "I want to travle to lodnon"
        expected_result = "I want to travel to london"
        corrected_text = check_spellings(text_example)
        self.assertEqual(expected_result,corrected_text)

    def test_spellcheck_two(self):
        text_example = "ipswiche"
        loaded_words = ['ipswich']
        expected_result = "ipswich"
        corrected_text = check_spellings(text_example, loaded_words)
        self.assertEqual(expected_result,corrected_text)
    def test_strip(self):
        text_example = "^$£%^&''I want! to tra!vel to (london)"
        expected_result = "I want to travel to london"
        self.assertEqual(expected_result,remove_punctuation(text_example))

    def test_sanitize(self):
        text_example = "^$£%^&''I want! to <b>tra!vEl</b> to (lodn&on)"
        expected_result = "i want to travel to london"
        self.assertEqual(expected_result, sanitize_input(text_example))
if __name__ == '__main__':
    unittest.main()
