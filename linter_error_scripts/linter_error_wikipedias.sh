#!/bin/bash
cd /data/project/fireflytools
source www/python/venv3/bin/activate
./linter_counts.py dewiki &
./linter_counts.py simplewiki &
./linter_counts.py ptwiki &
./linter_counts.py zhwiki &
./linter_counts.py srwiki &
./linter_counts.py arwiki &
./linter_counts.py viwiki &
./linter_counts.py plwiki &
wait
echo "--Complete--"
