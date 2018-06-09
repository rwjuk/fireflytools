#!/usr/bin/env python

import toolforge
import pickle
import argparse

from datetime import datetime

parser = argparse.ArgumentParser(description="Dump empty pages to a pickle file")
parser.add_argument("wiki", help="Wiki database code")
parser.add_argument("limit", help="Return at most this many rows")
args = parser.parse_args()

wiki = args.wiki
limit = int(args.limit)

conn = toolforge.connect(wiki)

empties = []

with conn.cursor() as cur:
	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("{} - Running long redirect query on wiki {}".format(now, wiki))
	cur.execute("select page_namespace, page_title from page where page_is_redirect=False and page_len=0 and page_namespace in (0,4,6,8,10,100) and page_title not like '%/%'  order by page_len limit {};".format(limit))
	empties = [ns, e.decode("utf-8") for ns, e in  list(cur.fetchall())]

pickle.dump(empties, open("/data/project/fireflytools/www/python/src/data/empty_pages_{}.dat".format(wiki), "wb"))
