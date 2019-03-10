#!/bin/bash
cd /data/project/fireflytools
source /venv/bin/activate
./long_redirects.py enwiki 1000 &
wait

