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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "book tickets", #raw message after being sanitized
            "raw_message": "book tickets"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "late"
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "late", #raw message after being sanitized
            "raw_message": "late"
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "help", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "change my ticket", #raw message after being sanitized
            "raw_message": "change my ticket"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
        text_example = "cancel a ticket"
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "cancel a ticket", #raw message after being sanitized
            "raw_message": "cancel a ticket"
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
            "suggestion": [],  # for station fuzzy matching
            "sanitized_message": "reset",  # raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "norwich", #raw message after being sanitized
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
            "suggestion": [{'station': 'London Liverpool Street'}], # for station fuzzy matching
            "sanitized_message": "london liverpool street", #raw message after being sanitized
            "raw_message": "london liverpool street"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_date_depart(self):
        text_example = "17/01/2021"
        expected_outward_date = datetime.date(2021, 1, 17)
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "17012021", #raw message after being sanitized
            "raw_message": "17/01/2021"
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "1400", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "yes", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "18012021", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "tomorrow", #raw message after being sanitized
            "raw_message": "tomorrow"
        }
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "today", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "7pm", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "no", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "i want to travel from norwich to london liverpool street on 01012020 at 12pm nrw yes", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "i want a ticket from norwich to forest gate tomorrow", #raw message after being sanitized
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "i want a ticket from norwich to forest gate today", #raw message after being sanitized
            "raw_message": "I want a ticket from norwich to forest gate today"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))

    def test_process_input_multiple(self):
        text_example = "i want a ticket to lodnon"
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
            "suggestion": [{'location': 'Greater London'}], # for station fuzzy matching
            "sanitized_message": "i want a ticket to london", #raw message after being sanitized
            "raw_message": "i want a ticket to lodnon"
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
            "suggestion": [],  # for station fuzzy matching
            "sanitized_message": "i want to travel from norwich to london liverpool street tomorrow at 5pm",  # raw message after being sanitized
            "raw_message": "I want to travel from Norwich to London Liverpool street tomorrow at 5pm"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))


    def test_process_input_long_fog(self):
        self.maxDiff = None
        text_example = "I would like to book a ticket from Norwich to Forest Gate on 2021/09/09 at 12:00 and returning on 2021/09/09 at 20:00"
        expected_outward_date = datetime.date(2021, 9, 9)
        expected_outward_time = datetime.time(12, 0)
        expected_return_date = datetime.date(2021, 9 ,9)
        expected_return_time = datetime.time(20,0)
        expected_output = {
            "intent": "ticket",
            "reset": False,
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
            "suggestion": [], # for station fuzzy matching
            "sanitized_message": "i would like to book a ticket from norwich to forest gate on 20210909 at 1200 and returning on 20210909 at 2000", #raw message after being sanitized
            "raw_message": "I would like to book a ticket from Norwich to Forest Gate on 2021/09/09 at 12:00 and returning on 2021/09/09 at 20:00"
        }
        print (expected_output)
        print (parse_user_input(text_example))
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
            "suggestion": [{'station': 'Tonbridge'}], # for station fuzzy matching
            "sanitized_message": "tonbridge", #raw message after being sanitized
            "raw_message": "Tonbridge"
        }
        self.assertDictEqual(expected_output, parse_user_input(text_example))
    def test_fuzzymatching(self):
        text_example = "match me"



    def test_spellcheck(self):
        text_example = "I want to travle to lodnon"
        print(f'Original: {text_example}')
        expected_result = "I want to travel to london"
        corrected_text = check_spellings(text_example)
        print(f'Fixed: {corrected_text}')
        self.assertEqual(expected_result,corrected_text)

    def test_strip(self):
        text_example = "^$£%^&''I want! to tra!vel to (london)"
        expected_result = "I want to travel to london"
        self.assertEqual(expected_result,remove_punctuation(text_example))

    def test_sanitize(self):
        text_example = "^$£%^&''I want! to <b>tra!vEl</b> to (lodn&on)"
        print(f'Original: {text_example}')
        expected_result = "i want to travel to london"
        print(f'Fixed: {expected_result}')
        self.assertEqual(expected_result, sanitize_input(text_example))
if __name__ == '__main__':
    unittest.main()
