#!/bin/bash
cd /data/project/fireflytools
source $HOME/sge-venv/bin/activate
./long_redirects.py enwiki 1000 &
wait

