#!/bin/bash
cd /data/project/fireflytools
source www/python/venv/bin/activate
./empty_pages.py enwiki 1000 &
wait

