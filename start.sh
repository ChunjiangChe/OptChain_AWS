#!/bin/bash


exper_id=0
exper_iter=0
runtime=100

python3 start_nodes.py optchain $exper_id $exper_iter

sleep 120

python3 start_miners.py optchain $exper_id $exper_iter

c=0
while [ $c -lt $runtime ]; do
  sleep 10
  c=$[$c+1]
  echo "$c"
done

python3 ask_nodes_log.py optchain $exper_id $exper_iter
python3 stop_containers.py optchain $exper_id $exper_iter
# python3 remove_limitation.py $exper_id

