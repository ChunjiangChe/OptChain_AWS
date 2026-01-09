#!/bin/bash

# --- Configuration ---
total_iterations=2     # <--- Set total number of iterations here
exp_id=14
protocol="manifoldchain"       # <--- Set your protocol here
# ---------------------

echo "========================================"
echo "Batch Processing: $protocol"
echo "Total Iterations: $total_iterations"
echo "========================================"

for (( i=0; i<total_iterations; i++ ))
do
    echo "Triggering Iteration $i of $total_iterations..."
    python3 generate_nodes.py $protocol $exp_id $i
    # Passes: Iteration, ID, Protocol
    ./start_multi_iterations.sh $i $exp_id $protocol
    
    echo "Cooling down..."
    sleep 30
done

echo "========================================"
echo "Batch for $protocol finished."
echo "========================================"