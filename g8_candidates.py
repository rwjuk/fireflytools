#!/usr/bin/env python

import toolforge
import pickle
import argparse

from datetime import datetime

parser = argparse.ArgumentParser(description="Dump orphaned talk pages to a pickle file")
parser.add_argument("wiki", help="Wiki database code")
parser.add_argument("limit", help="Return at most this many rows")
args = parser.parse_args()

wiki = args.wiki
limit = int(args.limit)

conn = toolforge.connect(wiki)

g8 = []

with conn.cursor() as cur:
	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("{} - Running orphaned talk/CSD G8 candidate query on wiki {}".format(now, wiki))
	cur.execute("SELECT page_namespace, page_title FROM page talkpage WHERE talkpage.page_title NOT LIKE '%/%' AND talkpage.page_namespace IN (1,5,11,15,101,119) AND NOT EXISTS ( SELECT 1 FROM page mainpage WHERE mainpage.page_namespace=talkpage.page_namespace-1 AND mainpage.page_title=talkpage.page_title ) AND NOT EXISTS ( SELECT 1 FROM templatelinks WHERE talkpage.page_id=tl_from AND tl_title='G8-exempt' ) LIMIT 1000".format(limit))
	g8 = [(ns, e.decode("utf-8")) for ns, e in list(cur.fetchall())]

pickle.dump(g8, open("/data/project/fireflytools/www/python/src/data/g8_candidates_{}.dat".format(wiki), "wb"))
