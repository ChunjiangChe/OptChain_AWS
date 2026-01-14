#!/bin/bash

# --- Configuration ---
protocol="optchain"

# List your experiments below in the format: "exper_id:num_iterations"
# Example: "14:2" means Experiment 14 will run iterations 0 and 1.
batch_config=(
    "0:3"  
)
# ---------------------

echo "========================================"
echo "Starting Multi-Experiment Batch Processing"
echo "Protocol: $protocol"
echo "========================================"

# Loop through each configuration entry
for entry in "${batch_config[@]}"
do
    # Split the string "ID:Count" into variables
    exp_id="${entry%%:*}"
    total_iterations="${entry##*:}"

    echo ""
    echo "----------------------------------------"
    echo "Processing Experiment ID: $exp_id"
    echo "Total Iterations to run: $total_iterations"
    echo "----------------------------------------"

    # Inner loop for iterations
    for (( i=0; i<total_iterations; i++ ))
    do
        echo "[Exp $exp_id] Triggering Iteration $i of $total_iterations..."
        
        python3 generate_nodes.py $protocol $exp_id $i
        
        # Passes: Iteration, ID, Protocol
        ./start_multi_iterations.sh $i $exp_id $protocol
        
        echo "[Exp $exp_id] Iteration $i complete. Cooling down..."
        sleep 30
    done
done

echo "========================================"
echo "All experiments finished successfully."
echo "========================================"