import unittest
from context import re


class TestReasoningEngine(unittest.TestCase):

    def test_intent_ticket(self):
        processed_input = {  # example : i would like to book a ticket
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
        }
        self.assertEqual(True, False)

    def test_from_station(self):
        self.assertEqual(True, False)

    def test_to_station(self):
        self.assertEqual(True, False)

    def test_depart_date(self):
        self.assertEqual(True, False)

    def test_depart_time(self):
        self.assertEqual(True, False)

    def test_returning(self):
        self.assertEqual(True, False)

    def test_return_date(self):
        self.assertEqual(True, False)

    def test_return_time(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
