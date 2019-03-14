#!/bin/bash
cd /data/project/fireflytools
source $HOME/sge-venv/bin/activate
./empty_pages.py enwiki 1000 &
wait
