#!/usr/bin/env python

import toolforge
import pickle
import argparse

from datetime import datetime

parser = argparse.ArgumentParser(description="Assess candidates against arbitrary set of adminship criteria")
parser.add_argument("input_file", help="Input file of candidates, one per line")
args = parser.parse_args()

input_file = args.input_file

conn = toolforge.connect("enwiki")

with conn.cursor() as cur:
	with open(input_file, 'r') as fh:
		for line in fh:
			candidate = line.strip()
			cur.execute("select distinct user_name,ufg_group from user left join user_former_groups on ufg_user=user_id where user_name=%s and ufg_group='sysop'", candidate)
			former_admin = (len(cur.fetchall()) > 0)
			
			cur.execute("select distinct user_name,ipb_id from user left join ipblocks on ipb_user=user_id where user_name=%s and (ipb_expiry='infinity' or ipb_expiry>(NOW() - INTERVAL 2 YEAR))", candidate)
			recent_block = (len(cur.fetchall()) > 0)

			cur.execute("select(select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20210201' and rev_timestamp < '20210301') as 'feb', (select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20210101' and rev_timestamp < '20210201') as 'jan', (select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20201201' and rev_timestamp < '20210101') as 'dec', (select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20201101' and rev_timestamp < '20201201') as 'nov', (select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20201001' and rev_timestamp < '20201101') as 'oct', (select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20200901' and rev_timestamp < '20201001') as 'sep', (select (count(*) > 100) from revision_userindex where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and rev_timestamp > '20200801' and rev_timestamp < '20200901') as 'aug'", [candidate]*7)
			not_active_enough = (sum([int(x) for x in list(cur.fetchone())]) < 6)

			cur.execute("select (count(*) > 10) from revision_userindex inner join page on rev_page=page_id where rev_actor=(select actor_id from actor inner join user on actor_user=user_id where user_name=%s) and (page_namespace=4 or page_namespace=5) and rev_timestamp > '20200801' and rev_timestamp < '20210301'", candidate)
			not_active_projectspace = (int(cur.fetchone()[0]) == 0)

			print("{} - Former admin: {} - Recent block: {} - Inactive: {} - Inactive in project space: {}".format(candidate, former_admin, recent_block, not_active_enough, not_active_projectspace))
			

