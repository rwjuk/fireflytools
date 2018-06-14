#!/bin/bash
cd /data/project/fireflytools
source www/python/venv/bin/activate
./g8_candidates.py enwiki 1000 &
wait
