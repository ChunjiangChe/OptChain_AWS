import json
import re
import os
import ast
import statistics
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random

# ==========================================
# 1. THEORETICAL CALCULATION CONFIGURATION
# ==========================================
block_size_theoretical = 8192
base_error = 0.0000000000000000000000000000000000000000000000000001
given_error = 1e-6
honest_node_nums = []
shard_nums = [1, 2, 3, 4, 5]
for shard_num in shard_nums:
    honest_node_num = 1
    while True:
        error = (1 - (1 / shard_num)) ** honest_node_num + base_error
        if error <= given_error:
            break
        honest_node_num += 1
    honest_node_nums.append(honest_node_num)

# Bandwidth data (Download blocks)
download_blocks = [
    0.02, 0.03, 0.12, 0.13, 0.10, 0.10, 0.13, 0.12, 0.05, 0.15, 
    0.12, 0.03, 0.08, 0.15, 0.15, 0.12, 0.07, 0.08, 0.15, 0.03, 
    0.08, 0.07, 0.15, 0.05, 0.03, 0.10, 0.12, 0.07, 0.10, 0.08, 
    0.15, 0.08, 0.02, 0.13, 0.13, 0.05, 0.07, 0.15, 0.07, 0.15, 
    0.07, 0.05, 0.08, 0.05, 0.07, 0.13, 0.03, 0.15, 0.10, 0.15, 
    0.03, 0.12, 0.03, 0.13, 0.05, 0.15, 0.07, 0.12, 0.05, 0.05, 
    0.13, 0.12, 0.03
]

# ==========================================
# 2. LOG ANALYSIS CONFIGURATION
# ==========================================
# MODIFIED: Iterations are now lists of lists. 
# Each sub-list corresponds to the experiment ID at the same index.

EXPERIMENTS_MANIFOLD = [9, 8, 10, 7, 6]  
# Example: [ [0, 1], [0], ... ] means Exp 9 uses iter 0 & 1, Exp 8 uses iter 0
ITERATIONS_MANIFOLD = [
    [0],    # Iterations for Exp 9
    [0],    # Iterations for Exp 8
    [0],    # Iterations for Exp 10
    [0],    # Iterations for Exp 7
    [0]     # Iterations for Exp 6
]

EXPERIMENTS_OPTCHAIN = [42, 43, 44, 45] 
ITERATIONS_OPTCHAIN = [
    [0, 2], # Iterations for Exp 42
    [1],    # Iterations for Exp 43
    [0],    # Iterations for Exp 44
    [1]     # Iterations for Exp 45
]

# Paths
CONFIG_PATH_TEMPLATE = "../expers/{protocol}/exper_{exper_id}/iter_{iter_id}/config.json"
LOG_PATH_TEMPLATE = "../exper_log/{protocol}/exper_{exper_id}/iter_{iter_id}/node_{node_id}.txt"

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def load_config(protocol, exper_id, iter_id):
    path = CONFIG_PATH_TEMPLATE.format(protocol=protocol, exper_id=exper_id, iter_id=iter_id)
    if not os.path.exists(path):
        # Fallback to experiment level config if iter config missing
        path = f"../expers/{protocol}/exper_{exper_id}/config.json"
    
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def parse_timestamp(ts_str):
    try:
        if "." in ts_str:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
        else:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def analyze_manifold_throughput(exper_id, iter_id, shard_num):
    """
    Calculates throughput by summing independent mining rates of each shard.
    """
    protocol = "manifoldchain"
    config = load_config(protocol, exper_id, iter_id)
    block_size = config.get("block_size", 1024)
    shard_size = config.get("shard_size", 1)

    total_mining_rate = 0.0

    # Iterate over each shard independently
    for i in range(shard_num):
        node_id = i * shard_size
        file_path = LOG_PATH_TEMPLATE.format(protocol=protocol, exper_id=exper_id, iter_id=iter_id, node_id=node_id)
        
        if not os.path.exists(file_path):
            continue

        shard_timestamps = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()

            match = re.search(r"longest chain:\s*b'(\[.*\])'", content)
            if not match:
                match = re.search(r"b'(\[.*\])'", content)
            
            if match:
                chain_str = match.group(1).replace('\\"', '"').replace("\\'", "'")
                chain_list = ast.literal_eval(chain_str)

                for block in chain_list:
                    if not isinstance(block, str): continue
                    if "1970-01-01" in block or "forking_rate" in block:
                        continue
                    
                    ts_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)", block)
                    if ts_match:
                        dt = parse_timestamp(ts_match.group(1))
                        if dt:
                            shard_timestamps.append(dt)
        except Exception:
            pass

        # Calculate rate for this specific shard
        if len(shard_timestamps) >= 2:
            duration = (max(shard_timestamps) - min(shard_timestamps)).total_seconds()
            if duration > 0:
                # Mining rate = Count / Duration
                shard_rate = len(shard_timestamps) / duration
                total_mining_rate += shard_rate

    # Final Throughput = Sum(Rates) * BlockSize
    return total_mining_rate * block_size

def analyze_optchain_throughput(exper_id, iter_id, shard_num):
    """
    Calculates throughput by summing independent mining rates of each shard.
    Optchain Tput per shard = (ex_rate + in_rate/shard_num) * sizes
    """
    protocol = "optchain"
    config = load_config(protocol, exper_id, iter_id)
    block_size = config.get("block_size", 1024)
    avai_size = config.get("avai_size", 1024)
    shard_size = config.get("shard_size", 1)

    total_throughput = 0.0

    # Iterate over each shard independently
    for i in range(shard_num):
        node_id = i * shard_size
        file_path = LOG_PATH_TEMPLATE.format(protocol=protocol, exper_id=exper_id, iter_id=iter_id, node_id=node_id)
        
        if not os.path.exists(file_path):
            continue

        shard_timestamps = []
        ex_count = 0
        in_count = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            match = re.search(r"availability chain: b'(\\[.*?\\])'", content, flags=re.DOTALL)
            if not match:
                match = re.search(r"availability chain: b'(\[.*?\])'", content, flags=re.DOTALL)

            if match:
                try:
                    chain_json = json.loads(match.group(1))
                except:
                    chain_str = match.group(1).replace('\\"', '"').replace("\\'", "'")
                    chain_json = ast.literal_eval(chain_str)
                
                for entry in chain_json:
                    if "1970-01-01" in entry or "forking rate" in entry.lower():
                        continue
                    
                    ts_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)\((Exclusive|Inclusive)\)", entry)
                    if ts_match:
                        dt = parse_timestamp(ts_match.group(1))
                        b_type = ts_match.group(2)
                        
                        if dt:
                            shard_timestamps.append(dt)
                            if b_type == 'Exclusive':
                                ex_count += 1
                            elif b_type == 'Inclusive':
                                in_count += 1
        except Exception:
            pass

        # Calculate rate for this specific shard
        if len(shard_timestamps) >= 2:
            # Duration based on first and last block of ANY type in this shard
            duration = (max(shard_timestamps) - min(shard_timestamps)).total_seconds()
            
            if duration > 0:
                ex_rate = ex_count / duration
                in_rate = in_count / duration
                
                # Calculate throughput contribution for this shard
                # Formula: (ex_rate + in_rate / shard_num) * size_factors
                shard_tput = (ex_rate + in_rate) * block_size * avai_size
                total_throughput += shard_tput

    return total_throughput

# ==========================================
# 4. MAIN EXECUTION & PLOTTING
# ==========================================

# A. Theoretical Calculation
sorted_throughput = sorted(download_blocks, reverse=True)
theo_y = []
mani_y = []
opt_y = []

print(f"{'Shards':<8} | {'Number':<10} | {'Theoretical':<15} | {'Manifold':<15} | {'Optchain':<15}")
print("-" * 80)

for idx, shard_num in enumerate(shard_nums):
    honest_node_num = honest_node_nums[idx]
    
    # 2. Theoretical
    x = honest_node_num                # Size of each sample
    iterations = 1000    # How many times to repeat

    # 1. Collect all samples
    all_samples = []
    for _ in range(iterations):
        sample = random.sample(download_blocks, x)
        sample = sorted(sample, reverse=True)
        all_samples.append(sample)

    # 2. Calculate element-wise average
    final_averages = [sum(col) / iterations for col in zip(*all_samples)]
    sorted_values = sorted(final_averages, reverse=True)
    optimal_val = sum(sorted_values[:shard_num])
    t_tput = optimal_val * block_size_theoretical
    theo_y.append(t_tput)
    
    # 3. Manifoldchain - Calculate AVERAGE over iterations
    m_tput = 0.0
    if shard_num == 1:
        mani_y.append(t_tput) # Assuming theoretical for base case
    else:
        m_exp = EXPERIMENTS_MANIFOLD[idx-1]
        m_iters_list = ITERATIONS_MANIFOLD[idx-1] # This is now a list of iterations
        
        temp_sum_tput = 0.0
        valid_iter_count = 0
        
        for iter_id in m_iters_list:
            try:
                # Calculate for single iteration
                val = analyze_manifold_throughput(m_exp, iter_id, shard_num)
                temp_sum_tput += val
                valid_iter_count += 1
            except Exception as e:
                print(f"Warning: Failed to process Manifold Exp {m_exp} Iter {iter_id}: {e}")

        # Compute Average
        if valid_iter_count > 0:
            m_tput = temp_sum_tput / valid_iter_count
        
        mani_y.append(m_tput)
    
    # 4. Optchain - Calculate AVERAGE over iterations
    o_tput = 0.0
    if shard_num == 1:
        opt_y.append(t_tput) # Assuming theoretical for base case
    else:
        o_exp = EXPERIMENTS_OPTCHAIN[idx-1]
        o_iters_list = ITERATIONS_OPTCHAIN[idx-1] # This is now a list of iterations
        
        temp_sum_tput = 0.0
        valid_iter_count = 0

        for iter_id in o_iters_list:
            try:
                # Calculate for single iteration
                val = analyze_optchain_throughput(o_exp, iter_id, shard_num)
                temp_sum_tput += val
                valid_iter_count += 1
            except Exception as e:
                 print(f"Warning: Failed to process Optchain Exp {o_exp} Iter {iter_id}: {e}")

        # Compute Average
        if valid_iter_count > 0:
            o_tput = temp_sum_tput / valid_iter_count
            
        opt_y.append(o_tput)
    
    print(f"{shard_num:<8} | {honest_node_num:<10} | {t_tput:<15.2f} | {m_tput:<15.2f} | {o_tput:<15.2f}")

# Plotting
plt.figure(figsize=(10, 6))

plt.plot(honest_node_nums, theo_y, marker='^', linestyle='-', color='black', label='Theoretical Optimal', linewidth=1.5)
# plt.plot(honest_node_nums, mani_y, marker='o', linestyle='-', color='blue', label='Manifoldchain', linewidth=2)
plt.plot(honest_node_nums, opt_y, marker='s', linestyle='--', color='green', label='Optchain', linewidth=2)

plt.xlabel("Number of Honest Nodes")
plt.ylabel("Throughput (bytes/s)")
plt.title("Throughput vs Number of Honest Nodes: Manifoldchain vs Optchain vs Theoretical")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)

output_file = 'throughput_vs_honest_nodes.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nFigure saved to {output_file}")
plt.show()