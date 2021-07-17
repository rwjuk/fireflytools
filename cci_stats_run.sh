#!/bin/bash
cd /data/project/fireflytools
source www/python/venv3/bin/activate
./cci_stats.py &
wait
