#!/bin/bash
cd /data/project/fireflytools
source www/python/venv3/bin/activate
./linter_counts.py enwiki
echo "--Complete--"
