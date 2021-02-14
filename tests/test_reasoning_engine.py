import datetime
import unittest
from tests.context import re


class TestReasoningEngine(unittest.TestCase):

    def test_intent_ticket(self):
        processed_nlp_output = {'intent': 'ticket',
                                'reset': False,
                                'includes_greeting': False,
                                'from_station': 'Norwich', 'from_crs': 'NRW',
                                'to_station': 'Forest Gate', 'to_crs': 'FOG',
                                'outward_date': datetime.date(2021, 2, 26),
                                'outward_time': datetime.time(12, 0),
                                'return_date': datetime.date(2021, 3, 1),
                                'return_time': datetime.time(20, 0),
                                'confirmation': '',
                                'no_category': [],
                                'suggestion': [],
                                'sanitized_message': 'i would like to book a ticket from norwich to forest gate on '
                                                     '20210226 at 12pm and returning on 20210301 at 2000',
                                'raw_message': 'i would like to book a ticket from norwich to forest gate on '
                                               '2021/02/26 at 12pm and returning on 2021/03/01 at 20:00'}

        self.assertEqual(True, re.process_user_input(processed_nlp_output))


if __name__ == '__main__':
    unittest.main()
