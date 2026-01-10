#!/bin/bash

# Arguments: $1=Iteration, $2=ExperimentID, $3=Protocol
exper_iter=${1:-1}
exper_id=${2:-42}
protocol=${3:-"optchain"} # Defaults to optchain if not provided

runtime=200

echo "--- Starting: $protocol | ID $exper_id | Iteration $exper_iter ---"

# Note: Added ${protocol} to the log filename to keep logs distinct if you change protocols
python3 limit_bandwidth.py $protocol $exper_id $exper_iter > bandwidth_monitor.txt
python3 start_nodes.py $protocol $exper_id $exper_iter

sleep 120
python3 start_miners.py $protocol $exper_id $exper_iter

c=0
while [ $c -lt $runtime ]; do
  sleep 10
  c=$[$c+1]
  # Optional: Print progress on the same line
  echo -ne "Runtime progress: $c / $runtime \r"
done
echo ""

# python3 stop_miners.py optchain $exper_id $exper_iter
python3 ask_nodes_log.py $protocol $exper_id $exper_iter
python3 stop_containers.py
python3 remove_limitation.py $protocol $exper_id $exper_iter
python3 view_node.py $protocol $exper_id $exper_iter
python3 rm_containers.py

echo "--- Iteration $exper_iter Completed ---"