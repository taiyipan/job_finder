#!/bin/sh
directory_path=/home/taiyi/job_finder/data_miner

export DISPLAY=:0.0 && \
python3 $directory_path/targeted_mine.py \
> $directory_path/log/$(date +%F_%H-%M).log