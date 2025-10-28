#!/bin/bash


exper_id=1
exper_iter=0
runtime=100
protocol="optchain"

python3 start_nodes.py $protocol $exper_id $exper_iter

sleep 120

python3 start_miners.py $protocol $exper_id $exper_iter

c=0
while [ $c -lt $runtime ]; do
  sleep 10
  c=$[$c+1]
  echo "$c"
done

# python3 stop_miners.py optchain $exper_id $exper_iter
python3 ask_nodes_log.py $protocol $exper_id $exper_iter
python3 stop_containers.py
python3 view_node.py $protocol $exper_id $exper_iter
python3 rm_containers.py
# python3 remove_limitation.py $exper_id

