#!/usr/bin/env python

import toolforge
import pickle
import argparse

from datetime import datetime

parser = argparse.ArgumentParser(description="Dump lint error counts to a pickle file")
parser.add_argument("wiki", help="Wiki database code")
args = parser.parse_args()

wiki = args.wiki

conn = toolforge.connect(wiki)

namespaces = list(range(0, 17)) + [100, 101, 108, 109, 118, 119, 446, 447, 710, 711, 828, 829, 2300, 2301, 2302, 2303]

linter_cat_order = [7, 12, 17, 16, 14, 9, 6, 13, 10, 15, 3, 1, 8, 11, 4, 2, 5]

counts = {}

for ns in namespaces:
	counts[ns] = {}
	for lint in linter_cat_order:
		counts[ns][lint] = 0

with conn.cursor() as cur:
	for ns in namespaces:
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print("{} - Running queries for namespace {} on wiki {}".format(now, ns, wiki))
		for lint in linter_cat_order:
			cur.execute("select count(*) from linter inner join page on page.page_id=linter.linter_page where linter_cat={0} and page.page_namespace={1};".format(lint, ns))
			counts[ns][lint] = cur.fetchone()[0]

pickle.dump(counts, open("/data/project/fireflytools/www/python/src/data/linter_counts_{}.dat".format(wiki), "wb"))
