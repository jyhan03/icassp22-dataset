#!/bin/bash 

set -eu
wav_path=./mix_lst/cv.lst
conf_path=./config
dump_dir=./dump_dir/tr
sample_rate=8000
num_process=64

python3 ./data_simu.py \
  --wav_path $wav_path \
  --conf_path $conf_path \
  --dump_dir $dump_dir \
  --sample_rate $sample_rate \
  --num_process $num_process \

echo "done"
