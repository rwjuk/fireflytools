#!/bin/bash
cd /data/project/fireflytools
source www/python/venv3/bin/activate
./linter_counts.py commonswiki &
./linter_counts.py wikidatawiki &
./linter_counts.py metawiki &
./linter_counts.py enwikivoyage &
./linter_counts.py enwiktionary &
wait
echo "--Complete--"
