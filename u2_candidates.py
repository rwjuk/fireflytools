#!/usr/bin/env python

import toolforge
import pickle
import argparse

from datetime import datetime

parser = argparse.ArgumentParser(description="Dump user pages of non-existent users to a pickle file")
parser.add_argument("wiki", help="Wiki database code")
parser.add_argument("limit", help="Return at most this many rows")
args = parser.parse_args()

wiki = args.wiki
limit = int(args.limit)

conn = toolforge.connect(wiki)

g8 = []

with conn.cursor() as cur:
	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("{} - Running CSD U2 candidate query on wiki {}".format(now, wiki))
	cur.execute('select page_title from page left outer join user on (user.user_name = replace(page.page_title,"_"," ")) where user.user_name is null and page_namespace=2 and page_title not like "%/%" and page_title not like "%.%.%.%" and page_title not like "%:%:%" and page_is_redirect=False; limit {}'.format(limit))
	g8 = [(ns, e.decode("utf-8")) for ns, e in list(cur.fetchall())]

pickle.dump(g8, open("/data/project/fireflytools/www/python/src/data/u2_candidates_{}.dat".format(wiki), "wb"))
