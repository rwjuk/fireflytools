#!/bin/bash
cd /data/project/fireflytools
source www/python/venv3/bin/activate
./u2_candidates.py enwiki 1000 &
wait
