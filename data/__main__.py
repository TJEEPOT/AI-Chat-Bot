"""
Data processing entry point.
Run this as python -m data [table].
"""
import data.process_data
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("table", help="name of the table to insert scraped data into")
parser.add_argument("--darwin", help="scrape from DARWIN data (a51 or rdg files)", action="store_true")
parser.add_argument("--hsp", help="scrape from HSP data (hsp files)", action="store_true")


args = parser.parse_args()
table = args.table

if args.darwin:
    print("Attempting to load DARWIN data from scraped folder and insert into", table, "table on database db")
    data.process_data.raw(table, "DARWIN")
elif args.hsp:
    print("Attempting to load HSP data from scraped folder and insert into", table, "table on database db")
    data.process_data.raw(table, "HSP")
else:
    print("Data source --darwin or --hsp must be specified.")




