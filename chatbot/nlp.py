#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spacy
import sqlite3
import datefinder
import datetime
from datetime import timedelta
from spacy.matcher import PhraseMatcher

__author__ = "Sam Humphreys"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Sam Humphreys"
__email__ = "s.humphreys@uea.ac.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"


def parse_user_input(user_input):
    # variables
    processed_input = {
        "intent": "",  # e.g tickets, help, delays
        "from_station": "",  # e.g Norwich
        "from_crs": "",  # e.g NRW
        "to_station": "",  # e.g London Liverpool Street
        "to_crs": "",  # e.g LST
        "outward_date": "",  # e.g 20/01/2021
        "outward_time": "",  # e.g 10:00
        "return_date": "",  # e.g 20/01/2021 (checks done in RE for future date etc)
        "return_time": "",  # e.g 10:00
        "confirmation": "",  # e.g true / false response for bot asking confirmation
        "no_category": [],  # any extra data NLP can't work out intent for
        "raw_message": ""  # raw message input by user for history etc
    }
    station_names = []
    station_crs = []
    station_pairs = {}
    book_ticket = ["book", "TICKET", "travel", "go"]  # maybe get from db
    get_help = ["help", "assistance"]
    delays = ["delay", "late", "behind schedule"]
    confirm_yes = ["correct", "yes", "yep", "y"]
    confirm_no = ["incorrect", "no", "wrong"]

    # populate lists from db
    conn = sqlite3.connect(r'..\data\db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT name,crs FROM stations WHERE NOT crs = 'none'")
    rows = cursor.fetchall()
    for row in rows:
        station_names.append(row[0])
        station_crs.append(row[1])
        station_pairs[row[0]] = row[1]

    nlp = spacy.load("en_core_web_sm")
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # build patterns
    station_names_pattern = [nlp.make_doc(text) for text in station_names]
    station_crs_pattern = [nlp.make_doc(text) for text in station_crs]
    intents_ticket_pattern = [nlp.make_doc(text) for text in book_ticket]
    intents_help_pattern = [nlp.make_doc(text) for text in get_help]
    intents_delays_pattern = [nlp.make_doc(text) for text in delays]
    confirm_yes_pattern = [nlp.make_doc(text) for text in confirm_yes]
    confirm_no_pattern = [nlp.make_doc(text) for text in confirm_no]

    # add match rules
    def on_match_intent(match_matcher, match_doc, match_id, match_matches):
        intent = nlp.vocab.strings[match_matches[match_id][0]]
        processed_input['intent'] = intent

    def on_match_station_name(match_matcher, match_doc, match_id, match_matches):
        matched_station = match_matches[match_id]
        matched_span_start = matched_station[1]
        matched_span_end = matched_station[2]
        first_word = match_doc[matched_span_start]
        matched_span = match_doc[matched_span_start:matched_span_end]
        for token in match_doc:
            if token.text == str(first_word):
                capitalised_span = str(matched_span).title()
                head = str(token.head)
                prev_word = ""
                next_word = ""
                if len(doc) >= 3:
                    prev_word = doc[matched_span_start - 1].text
                    next_word = doc[matched_span_start + 1].text
                if head == "from" or prev_word == "from" or next_word == "to":
                    processed_input["from_station"] = capitalised_span
                    processed_input["from_crs"] = station_pairs[capitalised_span]
                elif head == "to" or prev_word == "to" or next_word == "from":
                    processed_input["to_station"] = capitalised_span
                    processed_input["to_crs"] = station_pairs[capitalised_span]
                else:
                    processed_input['no_category'].append(capitalised_span)
                break

    def on_match_station_crs(match_matcher, match_doc, match_id, match_matches):
        doc_position = match_matches[match_id][1]
        matched_station_crs = str(doc[doc_position]).upper()
        prev_word = ""
        next_word = ""
        if len(doc) >= 3:
            prev_word = doc[doc_position - 1].text
            next_word = doc[doc_position + 1].text
        for name, crs in station_pairs.items():
            if crs == matched_station_crs:
                matched_station_name = name
                if processed_input['from_station'] != "" and prev_word == "from" or next_word == "to":
                    processed_input["from_station"] = matched_station_name
                    processed_input["from_crs"] = matched_station_crs
                elif processed_input['to_station'] != "" and prev_word == "to" or next_word == "from":
                    processed_input["to_station"] = matched_station_name
                    processed_input["to_crs"] = matched_station_crs

                break

    def on_match_confirm_true(match_matcher, match_doc, match_id, match_matches):
        if processed_input['confirmation'] is not False:
            processed_input['confirmation'] = True
        else:
            processed_input['confirmation'] = ""

    def on_match_confirm_false(match_matcher, match_doc, match_id, match_matches):
        if processed_input['confirmation'] is not True:
            processed_input['confirmation'] = False
        else:
            processed_input['confirmation'] = ""

    # add patterns
    phrase_matcher.add("ticket", on_match_intent, *intents_ticket_pattern)
    phrase_matcher.add("help", on_match_intent, *intents_help_pattern)
    phrase_matcher.add("delay", on_match_intent, *intents_delays_pattern)
    phrase_matcher.add("station_names", on_match_station_name, *station_names_pattern)
    phrase_matcher.add("station_crs", on_match_station_crs, *station_crs_pattern)
    phrase_matcher.add("confirm_yes", on_match_confirm_true, *confirm_yes_pattern)
    phrase_matcher.add("confirm_no", on_match_confirm_false, *confirm_no_pattern)


    # find dates
    def match_dates():
        found_dates = []
        midnight_vars = ['midnight', '12am', '00:00']
        midnight_requested = False
        midnight_time = datetime.time(0,0)

        for token in doc:
            if token.text.lower in midnight_vars:
                midnight_requested = True
            if token.text.lower() == "today":
                today_date = datetime.datetime.today()
                today_date = today_date.replace(hour=0,minute=0,second=0,microsecond=0)
                found_dates.append(today_date)
            elif token.text.lower() == "tomorrow":
                date_tomorrow = (datetime.datetime.today() + timedelta(1))
                date_tomorrow = date_tomorrow.replace(hour=0,minute=0,second=0,microsecond=0)
                found_dates.append(date_tomorrow)


        date_matches = datefinder.find_dates(user_input)
        for dateMatch in date_matches:
            found_dates.append(dateMatch)
        number_of_dates = len(found_dates)
        outward_date = ""
        outward_time = ""
        return_date = ""
        return_time = ""
        if processed_input['from_station'] != "" and 0 < number_of_dates < 3:
            outward_date = found_dates[0].date()
            if found_dates[0].time() != midnight_time or midnight_requested:
                outward_time = found_dates[0].time()
            if number_of_dates == 2:
                return_date = found_dates[1].date()
                if found_dates[1].time() != midnight_time or midnight_requested:
                    return_time = found_dates[1].time()

            processed_input['outward_date'] = outward_date
            processed_input['outward_time'] = outward_time
            processed_input['return_date'] = return_date
            processed_input['return_time'] = return_time

        else:
            for date in found_dates:
                misc_date = date.date()
                misc_time = date.time()
                processed_input['no_category'].append(misc_date)
                if date.time() != midnight_time or midnight_requested:
                    processed_input['no_category'].append(misc_time)


    doc = nlp(user_input)

    phrase_matcher(doc)
    match_dates()
    processed_input['raw_message'] = user_input
    return processed_input
