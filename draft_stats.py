#!/usr/bin/env python

import toolforge
import pickle
import argparse
import statistics

from datetime import datetime

parser = argparse.ArgumentParser(description="Dump stats about G13able drafts and those soon to be eligible to a pickle file")
parser.add_argument("wiki", help="Wiki database code")
args = parser.parse_args()

wiki = args.wiki

conn = toolforge.connect(wiki)

import pymysql.cursors

conn_local = pymysql.connect(
    host ="tools.db.svc.eqiad.wmflabs",
    user='s53758',
    password='YeQ2uFKXCexU38Oa',
    db = 's53758__draftstats',
    charset='utf8',
    use_unicode=True
)


draft_stats = {
"stale_draft_count": None,
"oldest_draft_age":None,
"mean_edits":None,
"median_edits":None,
"mode_edits":None,
}

with conn.cursor() as cur:
	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("{} - Running draft stats queries on {}".format(now, wiki))
	cur.execute("SELECT DISTINCT CONCAT('Draft:',page_title), (select rev_timestamp from revision where rev_page=page_id order by rev_timestamp desc limit 1) as rev_timestamp_, (select COUNT(rev_timestamp) from revision where rev_page=page_id) as revision_count FROM page WHERE page_namespace = 118 AND page_is_redirect = 0 AND (select rev_timestamp from revision where rev_page=page_id order by rev_timestamp desc limit 1) < (NOW() - INTERVAL 5 MONTH) ORDER BY rev_timestamp_;")
	data = [(title.decode("utf-8"), last_rev.decode("utf-8"), edit_count) for title, last_rev, edit_count in list(cur.fetchall())]

	cur.execute("SELECT COUNT(page_title) FROM page WHERE page_namespace = 118 AND page_is_redirect = 0 AND (select rev_timestamp from revision where rev_page=page_id order by rev_timestamp desc limit 1) < (NOW() - INTERVAL 6 MONTH);")
	g13_count = cur.fetchone()[0]
	
oldest_draft_timestamp = data[0][1]
stale_count = len(data)

edits_list = [d[2] for d in data]
mean_edits = sum(edits_list)/stale_count
median_edits = statistics.median(edits_list)
single_edit_drafts = len([d[2] for d in data if d[2] == 1])


cur = conn_local.cursor()
oldest_draft_format = datetime.strptime(oldest_draft_timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
sql_string = "INSERT INTO stalestats (run_time, stale_draft_count, g13able_count, mean_edits, median_edits, oldest_draft, single_edit_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"
cur.execute(sql_string, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stale_count, g13_count, mean_edits, median_edits, oldest_draft_format, single_edit_drafts))
conn_local.commit()
