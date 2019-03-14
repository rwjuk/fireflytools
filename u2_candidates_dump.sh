#!/bin/bash
cd /data/project/fireflytools
source $HOME/sge-venv/bin/activate
./u2_candidates.py enwiki 1000 &
wait
