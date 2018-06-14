#!/bin/bash
cd /data/project/fireflytools
source www/python/venv/bin/activate
./u2_candidates.py enwiki 1000 &
wait
