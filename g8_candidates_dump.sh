#!/bin/bash
cd /data/project/fireflytools
source $HOME/sge-venv/bin/activate
./g8_candidates.py enwiki 1000 &
wait
