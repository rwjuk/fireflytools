#!/usr/bin/env python3

from flask import Flask, request, Response, render_template, redirect
from os import path
from datetime import datetime
import re
import glob
import json
import pickle
import toolforge
import pymysql.cursors

app = Flask(__name__)

namespace_names = {0:"Main", 1:"Talk", 2:"User", 3:"User talk", 4:"Project", 5:"Project talk", 6:"File", 7:"File talk", 8:"MediaWiki", 9:"MediaWiki talk", 10:"Template", 11:"Template talk", 12:"Help", 13:"Help talk", 14:"Category", 15:"Category talk", 100:"Portal", 101:"Portal talk", 108:"Book", 109:"Book talk", 118:"Draft", 119:"Draft talk", 446:"Education Program", 447:"Education Program talk", 710:"TimedText", 711:"TimedText talk", 828:"Module", 829:"Module talk", 2300:"Gadget", 2301:"Gadget talk", 2302:"Gadget definition", 2303:"Gadget definition talk"}

linter_cat_order = [7, 12, 17, 16, 14, 9, 6, 13, 10, 15, 3, 1, 8, 11, 18, 4, 2, 5]
linter_url_fragments = {7:"deletable-table-tag", 12:"html5-misnesting", 17:"misc-tidy-replacement-issues", 16:"multiline-html-table-in-list", 14:"multiple-unclosed-formatting-tags", 9:"pwrap-bug-workaround", 6:"self-closed-tag", 13:"tidy-font-bug", 10:"tidy-whitespace-bug", 15:"unclosed-quotes-in-heading", 3:"bogus-image-options", 1:"fostered", 8:"misnested-tag", 11:"multi-colon-escape", 18:"wikilink-in-extlink", 4:"missing-end-tag", 2:"obsolete-tag", 5:"stripped-tag"}

wiki_url_fragments = {"commonswiki": "https://commons.wikimedia.org/wiki/", "enwiktionary":"https://en.wiktionary.org/wiki/", "enwikivoyage":"https://en.wikivoyage.org/wiki/", "wikidatawiki": "https://wikidata.org/wiki/"}

def render_from_pickle_data(wiki, data_file_name, template_name, no_main=False, **kwargs):
    data_file_path = "data/{}_{}.dat".format(data_file_name, wiki)
    data_file_mtime = path.getmtime(data_file_path)
    linter_data = pickle.load(open(data_file_path, "rb"))
    if no_main:
        namespace_names[0] = ""
    return render_template(template_name, entries=linter_data, namespace_names=namespace_names, wiki=wiki, timestamp=datetime.utcfromtimestamp(data_file_mtime).strftime("%Y-%m-%d %H:%M:%S"), **kwargs)

def is_integer_num(n):
    if isinstance(n, int):
        return True
    if isinstance(n, float):
        return n.is_integer()
    return False

@app.template_filter()
def number_format(value):
    if not is_integer_num(value):
        value = 0
    
    return "{:,}".format(value)

@app.route("/botedits/<task>/<page>")
def bot_edits_page(task, page):
        html_path = "botedits/{}/{}.html".format(task, page)
        html_fh = open(html_path, "r")
        return html_fh.read()

@app.route("/botedits/<task>")
def bot_edits(task):
        page_list = [path.split(p)[-1].replace(".html","") for p in glob.glob("botedits/{}/*.html".format(re.sub(r"\W+", "", task)))]
        
        return render_template("bot_edits.html", task_name=task, page_list=page_list)

@app.route("/cci/stats")
def cci_stats():
        conn = pymysql.connect(
                host ="tools.db.svc.eqiad.wmflabs",
                user='s53758',
                password='YeQ2uFKXCexU38Oa',
                db = 's53758__ccistats',
                charset='utf8',
                use_unicode=True
        )
        cur = conn.cursor()
        query = "select name, (select page_count from cci_data where cci_id=cci_case.id order by cci_data.id desc limit 1) as 'page_count',(select pages_with_diffs from cci_data where cci_id=cci_case.id order by cci_data.id desc limit 1) as 'pages_with_diffs', (select diff_count from cci_data where cci_id=cci_case.id order by cci_data.id desc limit 1) as 'diff_count', closed from cci_case where hide_from_display=0;"
        cur.execute(query)
        data = cur.fetchall()

        timestamp_query = "select run_time from cci_data order by run_time desc limit 1;"
        cur.execute(timestamp_query)
        timestamp = cur.fetchone()[0]
        return render_template("cci_stats.html", cases=data, timestamp=timestamp)

@app.route('/linter/<wiki>')
def linter(wiki):
        try:
                wiki_url = wiki_url_fragments[wiki]
        except KeyError:
                wiki_url = "https://{}.wikipedia.org/wiki/".format(wiki.replace("wiki",""))
        return render_from_pickle_data(wiki, "linter_counts", "linter_counts.html", wiki_url=wiki_url, linter_url_fragments=linter_url_fragments, linter_cat_order=linter_cat_order)

@app.route('/longredirects/<wiki>')
def longredirects(wiki):
    return render_from_pickle_data(wiki, "long_redirects", "long_redirects.html", no_main=True)

@app.route('/emptypages/<wiki>')
def emptypages(wiki):
    return render_from_pickle_data(wiki, "empty_pages", "empty_pages.html", no_main=True)
    
@app.route('/orphanedtalks/<wiki>')
def orphanedtalks(wiki):
    return render_from_pickle_data(wiki, "g8_candidates", "g8_candidates.html", no_main=True)
    
@app.route('/baduserpages/<wiki>')
def baduserpages(wiki):
    return render_from_pickle_data(wiki, "u2_candidates", "u2_candidates.html", no_main=True)

@app.route('/testquery/<wiki>')
def testquery(wiki):
    return render_from_pickle_data(wiki, "test_query", "test_query.html", no_main=True)

@app.route('/draftdiff/lastreview/<draft_title>')
def draftdiff_lastreview(draft_title):
    conn = toolforge.connect("enwiki")
    with conn.cursor() as cur:
        review_diff_id_q = 'select rev_id from revision inner join comment on comment_id=rev_comment_id where rev_page=(select page_id from page where page_title="{}" and page_namespace=118) and comment_text like "Declining submission%" order by rev_timestamp desc;'.format(draft_title.replace(r"Draft:",r'').replace(r"draft:",r""))
        cur.execute(review_diff_id_q)
        review_diff_fetch = cur.fetchone()
        if review_diff_fetch is None:
            return Response("No previous review found", status=418)
        review_diff_id = review_diff_fetch[0]
        cur_diff_id_q = 'select rev_id from revision where rev_page=(select page_id from page where page_title="{}" and page_namespace=118) order by rev_timestamp desc limit 1;'.format(draft_title.replace(r"Draft:",r'').replace(r"draft:",r""))
        cur.execute(cur_diff_id_q)
        cur_diff_id = cur.fetchone()[0]
    return redirect("https://en.wikipedia.org/wiki/Special:Diff/{}/{}".format(review_diff_id, cur_diff_id), code=303)
    
@app.route('/draftdiff')
def draftdiff_form():
    return render_template("draft_diff.html")
    
