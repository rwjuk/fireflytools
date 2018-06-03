#!/bin/bash
cd /data/project/fireflytools
source www/python/venv/bin/activate
./linter_counts.py enwiki &
./linter_counts.py dewiki &
./linter_counts.py commonswiki &
./linter_counts.py simplewiki &
wait
./linter_counts.py wikidatawiki &
./linter_counts.py metawiki &
./linter_counts.py enwikivoyage &
./linter_counts.py enwiktionary &
wait
