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
./linter_counts.py ptwiki &
./linter_counts.py zhwiki &
./linter_counts.py srwiki &
./linter_counts.py arwiki &
./linter_counts.py viwiki &
./linter_counts.py plwiki &
wait
