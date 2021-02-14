#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spacy
import sqlite3
import datefinder
import datetime
from datetime import timedelta
from spacy.matcher import PhraseMatcher
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from spellchecker import SpellChecker
import re

__author__ = "Sam Humphreys"
__credits__ = ["Martin Siddons", "Steven Diep", "Sam Humphreys"]
__maintainer__ = "Sam Humphreys"
__email__ = "s.humphreys@uea.ac.uk"
__status__ = "Prototype"  # "Development" "Prototype" "Production"


def parse_user_input(user_input):
    # variables
    processed_input = {
        "intent": "",  # e.g tickets, help, delays
        "reset": False,  # e.g True False if user wants to reset dict
        "includes_greeting": False,  # True if message contained a greeting
        "from_station": "",  # e.g Norwich
        "from_crs": "",  # e.g NRW
        "to_station": "",  # e.g London Liverpool Street
        "to_crs": "",  # e.g LST
        "outward_date": "",  # e.g 20/01/2021
        "outward_time": "",  # e.g 10:00
        "return_date": "",  # e.g 20/01/2021 (checks done in RE for future date etc)
        "return_time": "",  # e.g 10:00
        "confirmation": "",  # e.g true / false response for bot asking confirmation
        "no_category": [],  # any extra data NLP can't work out
        "suggestion": [],   # for station / location fuzzy matching
        "sanitized_message": "",  # raw message after being sanitized
        "raw_message": ""  # raw message input by user for history etc
    }
    station_names = []
    station_crs = []
    station_pairs = {}
    station_locations = []
    book_ticket = ["book", "ticket", "travel", "go"]  # maybe get from db
    greetings = ["hi", "hello", "hey"]
    get_help = ["help", "assistance"]
    delays = ["delay", "late", "behind schedule"]
    cancellation = ["cancel", "cancellation"]
    changes = ["change", "alter"]
    confirm_yes = ["correct", "yes", "yep", "y"]
    confirm_no = ["incorrect", "no", "wrong", "nothing", "that is all"]
    reset = ["reset", "re do", "start again", "start over", "restart"]

    # populate lists from db
    conn = sqlite3.connect(r'..\data\db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT name,crs,county FROM stations WHERE NOT crs = 'none'")
    rows = cursor.fetchall()
    for row in rows:
        station_names.append(row[0])
        station_crs.append(row[1])
        station_pairs[row[0]] = row[1]
        if row[2] and row[2] not in station_locations:
            station_locations.append(row[2])

    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    phrase_matcher2 = PhraseMatcher(nlp.vocab, attr="LOWER")
    # build patterns
    station_names_pattern = [nlp.make_doc(text) for text in station_names]
    station_crs_pattern = [nlp.make_doc(text) for text in station_crs]
    intents_cancel_pattern = [nlp.make_doc(text) for text in cancellation]
    intents_change_pattern = [nlp.make_doc(text) for text in changes]
    intents_ticket_pattern = [nlp.make_doc(text) for text in book_ticket]
    intents_help_pattern = [nlp.make_doc(text) for text in get_help]
    intents_delays_pattern = [nlp.make_doc(text) for text in delays]
    confirm_yes_pattern = [nlp.make_doc(text) for text in confirm_yes]
    confirm_no_pattern = [nlp.make_doc(text) for text in confirm_no]
    is_greeting_pattern = [nlp.make_doc(text) for text in greetings]
    reset_pattern = [nlp.make_doc(text) for text in reset]

    # add match rules
    def on_match_intent(match_matcher, match_doc, match_id, match_matches):
        intent = nlp.vocab.strings[match_matches[match_id][0]]
        if len(match_matches) > 1:
            for match in match_matches:
                current_match_intent = nlp.vocab.strings[match[0]]
                if current_match_intent == "cancel" or current_match_intent == "change":
                    intent = current_match_intent
                    break
        processed_input['intent'] = intent

    def on_match_greeting(match_matcher, match_doc, match_id, match_matches):
        processed_input['includes_greeting'] = True

    def on_match_reset(match_matcher, match_doc, match_id, match_matches):
        processed_input['reset'] = True

    def on_match_station_name(match_matcher, match_doc, match_id, match_matches):
        matched_station = match_matches[match_id]
        matched_span_start = matched_station[1]
        matched_span_end = matched_station[2]
        length_of_doc = len(doc)
        first_word = match_doc[matched_span_start]
        matched_span = match_doc[matched_span_start:matched_span_end]
        for token in match_doc:
            if token.text == str(first_word):
                capitalised_span = str(matched_span).title()
                head = str(token.head)
                prev_word = ""
                next_word = ""
                if matched_span_start > 0:
                    prev_word = doc[matched_span_start - 1].text
                if matched_span_end < length_of_doc:
                    next_word = doc[matched_span_end].text
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
        matched_crs = match_matches[match_id]
        matched_span_start = matched_crs[1]
        matched_span_end = matched_crs[2]
        matched_station_crs = str(doc[matched_span_start]).upper()
        length_of_doc = len(doc)
        prev_word = ""
        next_word = ""
        if matched_span_start > 0:
            prev_word = doc[matched_span_start - 1].text
        if matched_span_end < length_of_doc:
            next_word = doc[matched_span_end].text
        for name, crs in station_pairs.items():
            if crs == matched_station_crs:
                matched_station_name = name
                if processed_input['from_station'] == "" and prev_word == "from" or next_word == "to":
                    processed_input["from_station"] = matched_station_name
                    processed_input["from_crs"] = matched_station_crs
                elif processed_input['to_station'] == "" and prev_word == "to" or next_word == "from":
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
    phrase_matcher2.add("change", on_match_intent, *intents_change_pattern)
    phrase_matcher2.add("cancel", on_match_intent, *intents_cancel_pattern)
    phrase_matcher2.add("ticket", on_match_intent, *intents_ticket_pattern)
    phrase_matcher2.add("help", on_match_intent, *intents_help_pattern)
    phrase_matcher2.add("delay", on_match_intent, *intents_delays_pattern)
    phrase_matcher2.add("reset", on_match_reset, *reset_pattern)
    phrase_matcher.add("station_names", on_match_station_name, *station_names_pattern)
    phrase_matcher.add("station_crs", on_match_station_crs, *station_crs_pattern)
    phrase_matcher2.add("confirm_yes", on_match_confirm_true, *confirm_yes_pattern)
    phrase_matcher2.add("confirm_no", on_match_confirm_false, *confirm_no_pattern)
    phrase_matcher2.add("greeting", on_match_greeting, *is_greeting_pattern)

    # find dates
    def match_dates():
        found_dates = []
        midnight_vars = ['midnight', '12am', '00:00']
        midnight_requested = False
        midnight_time = datetime.time(0, 0)
        input_string = user_input.lower()

        for token in doc:
            if token.text.lower in midnight_vars:
                midnight_requested = True
            if token.text.lower() == "today":
                today_date = datetime.datetime.today().date()
                input_string = input_string.replace(token.text, today_date.strftime('%d/%m/%Y'))
            elif token.text.lower() == "tomorrow":
                date_tomorrow = (datetime.datetime.today() + timedelta(1)).date()
                input_string = input_string.replace(token.text, date_tomorrow.strftime('%d/%m/%Y'))

        date_matches = datefinder.find_dates(input_string)
        for dateMatch in date_matches:
            found_dates.append(dateMatch)
            print(dateMatch)
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
                if len(doc) == 1 and date.time() == midnight_time and not midnight_requested:   # must be a date
                    processed_input['no_category'].append(misc_date)
                if date.time() != midnight_time or midnight_requested:
                    processed_input['no_category'].append(misc_time)

    def fuzzy_match_stations():
        ignored_words = ['ticket', 'i']
        for token in doc:
            if token.text.lower() in ignored_words:
                continue
            token_position = token.i
            to_from_found = False
            if token.i - 1 >= 0:
                previous_token = doc[token_position-1]
                previous_token_text = previous_token.text.lower()
                if previous_token_text == "to" or previous_token_text == "from":
                    to_from_found = True
            if token_position + 1 < len(doc):
                next_token = doc[token_position+1]
                next_token_text = next_token.text.lower()
                if next_token_text == "to" or next_token_text == "from":
                    to_from_found = True
            if token.pos_ == "NOUN" or token.pos_ == "PROPN" or to_from_found \
                    and token.text.lower() not in ignored_words:
                token_name = token.text
                current_token = token
                ok_to_continue = True
                while current_token.i < (len(doc) - 1) and ok_to_continue:
                    neighbour_token = current_token.nbor()
                    if neighbour_token.pos_ == "NOUN" or neighbour_token.pos_ == "PROPN":
                        token_name = token_name + " " + current_token.nbor().text
                        current_token = neighbour_token
                    else:
                        ok_to_continue = False

                top_10_results_station_name = process.extract(token_name, station_names, limit=1, scorer=fuzz.ratio)
                top_10_results_station_locations = \
                    process.extract(token_name, station_locations, limit=1, scorer=fuzz.partial_ratio)
                top_station = top_10_results_station_name[0]
                top_station_name = top_station[0]
                top_station_score = top_station[1]
                top_location = top_10_results_station_locations[0]
                top_location_name = top_location[0]
                top_location_score = top_location[1]
                suggestion = {}
                suggestion_value = ""
                if top_station_score >= 80:
                    if top_location_score >= 80:
                        if top_station_score >= top_location_score:     # use station
                            suggestion = {'station': top_station_name}
                            suggestion_value = top_station_name
                        else:   # use location
                            suggestion = {'location': top_location_name}
                            suggestion_value = top_location_name
                    else:   # station valid location not
                        suggestion = {'station': top_station_name}
                        suggestion_value = top_station_name
                elif top_location_score >= 80:  # location valid station not
                    suggestion = {'location': top_location_name}
                    suggestion_value = top_location_name
                else:
                    pass
                current_from_station = processed_input['from_station']
                current_to_station = processed_input['to_station']
                if current_to_station == "" or current_from_station == "":
                    if suggestion and current_to_station != suggestion_value or \
                            current_from_station != suggestion_value:
                        processed_input['suggestion'].append(suggestion)
                if current_token.i == (len(doc) - 1):    # early exit if entire string matched (prevent repeat)
                    break

    corrected_input = sanitize_input(user_input, station_crs + station_names)
    doc = nlp(corrected_input)
    lemma_string = get_lemma_string(doc)
    doc2 = nlp(lemma_string)
    phrase_matcher2(doc2)
    phrase_matcher(doc)
    match_dates()
    processed_input['sanitized_message'] = corrected_input
    processed_input['raw_message'] = user_input
    fuzzy_match_stations()
    return processed_input


def get_lemma_string(spacy_doc):
    lemma_string = ""
    for token in spacy_doc:
        lemma_string += " " + token.lemma_.lower()
    return lemma_string


def check_spellings(raw_input, known_words=None):
    if known_words is None:
        known_words = []
    spell = SpellChecker(distance=2)
    known_lower = []
    for word in known_words:
        known_lower.append(word.lower())
    spell.word_frequency.load_words(known_lower)
    corrected_user_input_string = str(raw_input)
    spelling_mistakes = spell.unknown(str(raw_input).split(" "))
    for mistake in spelling_mistakes:
        if mistake not in known_lower and not re.match(r'[0-9]*(am|pm)', mistake):
            correction = spell.correction(mistake)
            corrected_user_input_string = corrected_user_input_string.replace(mistake, correction)
    return corrected_user_input_string


def remove_punctuation(raw_input):
    stripped_input = re.sub(r'[^\w\s]', '', raw_input)
    return stripped_input


def sanitize_input(raw_input, known_words=None):
    if known_words is None:
        known_words = []
    sanitized_input = remove_punctuation(raw_input)
    sanitized_input = sanitized_input.lower()
    sanitized_input = check_spellings(sanitized_input, known_words)
    return sanitized_input
