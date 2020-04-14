#!/bin/sh
directory_path=/home/taiyi/job_finder/indeed_crawler

export DISPLAY=:0.0 && \
python3 $directory_path/browse.py \
> $directory_path/log/$(date +%F_%H-%M).log
