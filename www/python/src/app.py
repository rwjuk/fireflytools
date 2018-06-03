#!/usr/bin/env python3

from flask import Flask, request, Response, render_template
from os import path
from datetime import datetime
import json
import pickle

app = Flask(__name__)

namespace_names = {0:"Main", 1:"Talk", 2:"User", 3:"User talk", 4:"Project", 5:"Project talk", 6:"File", 7:"File talk", 8:"MediaWiki", 9:"MediaWiki talk", 10:"Template", 11:"Template talk", 12:"Help", 13:"Help talk", 14:"Category", 15:"Category talk", 100:"Portal", 101:"Portal talk", 108:"Book", 109:"Book talk", 118:"Draft", 119:"Draft talk", 446:"Education Program", 447:"Education Program talk", 710:"TimedText", 711:"TimedText talk", 828:"Module", 829:"Module talk", 2300:"Gadget", 2301:"Gadget talk", 2302:"Gadget definition", 2303:"Gadget definition talk"}

#with open('config.json') as f:
#    conf = json.load(f)

@app.template_filter()
def number_format(value):
	return "{:,}".format(value)

@app.route('/linter/<wiki>')
def linter(wiki):
	data_file_path = "data/linter_counts_{}.dat".format(wiki)
	data_file_mtime = path.getmtime(data_file_path)
	linter_data = pickle.load(open(data_file_path, "rb"))
	return render_template("linter_counts.html", entries=linter_data, namespace_names=namespace_names, wiki=wiki, timestamp=datetime.utcfromtimestamp(data_file_mtime).strftime("%Y-%m-%d %H:%M:%S"))
