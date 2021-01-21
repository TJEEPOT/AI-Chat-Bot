"""
Data processing entry point.
Run this as python -m data [table].
"""
import data.process_data
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("table", help="name of the table to insert scraped data into")

args = parser.parse_args()
table = args.table
print("Attempting to load data from scraped folder and insert into", table, "table on database db")
data.process_data.raw(table)

