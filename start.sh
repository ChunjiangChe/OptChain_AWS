#!/bin/bash


exper_id=0
runtime=10

python3 start_nodes.py $exper_id

sleep 120

python3 start_tx_generators.py $exper_id
python3 start_miners.py $exper_id

c=0
while [ $c -lt $runtime ]; do
  sleep 10
  c=$[$c+1]
  echo "$c"
done

python3 ask_nodes_log.py $exper_id
python3 stop_containers.py $exper_id
python3 remove_limitation.py $exper_id

