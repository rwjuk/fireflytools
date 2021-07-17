#!/bin/bash
cd /data/project/fireflytools
source www/python/venv3/bin/activate
./g8_candidates.py enwiki 1000 &
wait
