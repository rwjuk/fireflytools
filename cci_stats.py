#!/usr/bin/env python

import toolforge
import pickle
import argparse
import pywikibot
import mwparserfromhell
import argparse

from datetime import datetime
from db_handle_cci import *

parser = argparse.ArgumentParser(description="Dump user pages of non-existent users to a pickle file")
parser.add_argument("--updateclosedonly", help="Only update the 'closed' status of cases in the DB (skip updating stats)", action="store_true")
args = parser.parse_args()

closed_only = args.updateclosedonly

wiki = "enwiki"

site = pywikibot.Site()

cci_template_name = "Template:CCIlist"

cci_template = pywikibot.Page(site, cci_template_name)

cci_wikitext = mwparserfromhell.parse(cci_template.get())

def get_counts_for_cci_page(page_name):
        case_page = pywikibot.Page(site, page_name)
        case_wikitext = mwparserfromhell.parse(case_page.get())
        page_count = len(case_wikitext.filter_wikilinks(matches="\[\[:"))
        diff_count = len(case_wikitext.filter_wikilinks(matches="Diff")) + len(case_wikitext.filter_templates(matches="{dif"))
        pages_with_diffs = sum([ 1 if (("Diff/" in x) or ("{{dif" in x)) else 0 for x in case_wikitext.split("\n")])
        return (page_count, diff_count, pages_with_diffs)

def is_case_closed(case_name):
        case_page_name = "Wikipedia:Contributor_copyright_investigations/{}".format(case_name)
        case_page = pywikibot.Page(site, case_page_name)
        case_wikitext = mwparserfromhell.parse(case_page.get())
        return len(case_wikitext.filter_wikilinks(matches="Courtesy blanking")) > 0

def insert_cci_case(case_name, date_opened, description):
        cur = conn.cursor()
        ret = cur.execute("select id from cci_case where name='{}'".format(case_name))
        if ret == 0:
                cur.execute("insert ignore into cci_case (name, closed, date_opened, description) values ('{}', False, '{}', '{}')".format(case_name, date_opened, description.replace("'", "''")))
                conn.commit()

def insert_cci_data(case_name, page_count, diff_count, pages_with_diffs):
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "insert into cci_data (cci_id, run_time, page_count, diff_count, pages_with_diffs) values((select id from cci_case where name='{}'), '{}', {}, {}, {});".format(case_name, now, page_count, diff_count, pages_with_diffs)
        cur.execute(query)
        conn.commit()

def get_open_cases_in_db():
        cur = conn.cursor()
        query = "select name from cci_case where closed=0;"
        cur.execute(query)

        return [x[0] for x in cur.fetchall()]

def mark_case_as_closed(case_name):
        cur = conn.cursor()
        query = "update cci_case set closed=1 where name='{}';"
        cur.execute(query.format(case_name))
        conn.commit()

if not closed_only:
        for case in cci_wikitext.filter_templates()[1:-2]:
                case_name,date_opened,topic = case.params
                case_page_name = "Wikipedia:Contributor_copyright_investigations/{}".format(case_name)
                case_page = pywikibot.Page(site, case_page_name)
                case_wikitext = mwparserfromhell.parse(case_page.get())
                subpages = case_wikitext.filter_wikilinks(matches="{}[^]]+".format(case_page_name.replace("_","[ _]")))
                page_count, diff_count, pages_with_diffs = get_counts_for_cci_page(case_page_name)
        
                for subpage in subpages:
                        sub_pc, sub_dc, sub_pwd = get_counts_for_cci_page(subpage.title)
                        page_count += sub_pc
                        diff_count += sub_dc
                        pages_with_diffs += sub_pwd

                date_opened_fmt = datetime.strptime(str(date_opened), "%d %B %Y").strftime("%Y-%m-%d")
                insert_cci_case(case_name, date_opened_fmt, topic)
                insert_cci_data(case_name, page_count, diff_count, pages_with_diffs)

for open_case in get_open_cases_in_db():
        if is_case_closed(open_case):
                mark_case_as_closed(open_case)

