#!/usr/bin/env python3

from flask import Flask, request, Response, render_template, redirect
from os import path
from datetime import datetime
import json
import pickle
import toolforge

app = Flask(__name__)

namespace_names = {0:"Main", 1:"Talk", 2:"User", 3:"User talk", 4:"Project", 5:"Project talk", 6:"File", 7:"File talk", 8:"MediaWiki", 9:"MediaWiki talk", 10:"Template", 11:"Template talk", 12:"Help", 13:"Help talk", 14:"Category", 15:"Category talk", 100:"Portal", 101:"Portal talk", 108:"Book", 109:"Book talk", 118:"Draft", 119:"Draft talk", 446:"Education Program", 447:"Education Program talk", 710:"TimedText", 711:"TimedText talk", 828:"Module", 829:"Module talk", 2300:"Gadget", 2301:"Gadget talk", 2302:"Gadget definition", 2303:"Gadget definition talk"}

#with open('config.json') as f:
#    conf = json.load(f)

def render_from_pickle_data(wiki, data_file_name, template_name, no_main=False):
    data_file_path = "data/{}_{}.dat".format(data_file_name, wiki)
    data_file_mtime = path.getmtime(data_file_path)
    linter_data = pickle.load(open(data_file_path, "rb"))
    if no_main:
        namespace_names[0] = ""
    return render_template(template_name, entries=linter_data, namespace_names=namespace_names, wiki=wiki, timestamp=datetime.utcfromtimestamp(data_file_mtime).strftime("%Y-%m-%d %H:%M:%S"))

@app.template_filter()
def number_format(value):
    return "{:,}".format(value)

@app.route('/linter/<wiki>')
def linter(wiki):
    return render_from_pickle_data(wiki, "linter_counts", "linter_counts.html")

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

@app.route('/draftdiff/lastreview/<draft_title>')
def draftdiff_lastreview(draft_title):
    conn = toolforge.connect("enwiki")
    with conn.cursor() as cur:
        review_diff_id_q = 'select rev_id from revision where rev_page=(select page_id from page where page_title="{}" and page_namespace=118) and rev_comment like "Declining submission%" order by rev_timestamp desc;'.format(draft_title.replace(r"Draft:",r'').replace(r"draft:",r""))
        cur.execute(review_diff_id_q)
        review_diff_id = cur.fetchone()[0]
        cur_diff_id_q = 'select rev_id from revision where rev_page=(select page_id from page where page_title="{}" and page_namespace=118) order by rev_timestamp desc limit 1;'.format(draft_title.replace(r"Draft:",r'').replace(r"draft:",r""))
        cur.execute(cur_diff_id_q)
        cur_diff_id = cur.fetchone()[0]
    return redirect("https://en.wikipedia.org/wiki/Special:Diff/{}/{}".format(review_diff_id, cur_diff_id), code=303)
    
