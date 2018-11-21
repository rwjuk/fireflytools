#!/usr/bin/env python

import toolforge
import pickle
import argparse

from datetime import datetime

parser = argparse.ArgumentParser(description="Dump long redirects to a pickle file")
parser.add_argument("wiki", help="Wiki database code")
parser.add_argument("limit", help="Return at most this many rows")
args = parser.parse_args()

wiki = args.wiki
limit = int(args.limit)

conn = toolforge.connect(wiki)

namespaces = list(range(0, 16)) + [100, 101, 108, 109, 118, 119, 446, 447, 710, 711, 828, 829, 2300, 2301, 2302, 2303]

redirects = []

with conn.cursor() as cur:
	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("{} - Running long redirect query on wiki {}".format(now, wiki))
	cur.execute("select page_namespace,page_title from page where page_is_redirect=True order by char_length(page_title) desc limit {};".format(limit))
	redirects = [(ns, redir.decode("utf-8")) for ns, redir in  list(cur.fetchall())]

pickle.dump(redirects, open("/data/project/fireflytools/www/python/src/data/long_redirects_{}.dat".format(wiki), "wb+"))
