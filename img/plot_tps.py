import json
import re
import os
import ast
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# 1. THEORETICAL CALCULATION CONFIGURATION
# ==========================================
block_size_theoretical = 8192
shard_nums = [1, 2, 4, 8, 16]
honest_node_num = 64
base_error = 1e-50

# Bandwidth data (Download blocks)
download_blocks = [
    0.02, 0.03, 0.12, 0.13, 0.10, 0.10, 0.13, 0.12, 0.05, 0.27, 
    0.12, 0.03, 0.08, 0.18, 0.15, 0.12, 0.07, 0.08, 0.17, 0.03, 
    0.08, 0.07, 0.15, 0.05, 0.03, 0.10, 0.12, 0.07, 0.10, 0.08, 
    0.15, 0.08, 0.02, 0.13, 0.13, 0.05, 0.07, 0.17, 0.07, 0.15, 
    0.07, 0.05, 0.08, 0.05, 0.07, 0.13, 0.03, 0.15, 0.10, 0.30, 
    0.03, 0.12, 0.03, 0.13, 0.05, 0.18, 0.07, 0.12, 0.05, 0.05, 
    0.13, 0.12, 0.03
]

# ==========================================
# 2. LOG ANALYSIS CONFIGURATION
# ==========================================
# Update these lists to match your specific experiment IDs
EXPERIMENTS_MANIFOLD = [9, 8, 10, 7, 6]  
ITERATIONS_MANIFOLD = [0, 0, 0, 0, 0]

EXPERIMENTS_OPTCHAIN = [39, 38, 40, 37, 36] 
ITERATIONS_OPTCHAIN = [0, 0, 0, 0, 0]

# Paths
CONFIG_PATH_TEMPLATE = "../expers/{protocol}/exper_{exper_id}/iter_{iter_id}/config.json"
LOG_PATH_TEMPLATE = "../exper_log/{protocol}/exper_{exper_id}/iter_{iter_id}/node_{node_id}.txt"

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def load_config(protocol, exper_id, iter_id):
    path = CONFIG_PATH_TEMPLATE.format(protocol=protocol, exper_id=exper_id, iter_id=iter_id)
    if not os.path.exists(path):
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
                shard_tput = (ex_rate + (in_rate / shard_num)) * block_size * avai_size
                total_throughput += shard_tput

    return total_throughput

# ==========================================
# 4. MAIN EXECUTION & PLOTTING
# ==========================================

# A. Theoretical Calculation
sorted_throughput = sorted(download_blocks, reverse=True)
errors_x = []
theo_y = []
mani_y = []
opt_y = []

print(f"{'Shards':<8} | {'Error':<10} | {'Theoretical':<15} | {'Manifold':<15} | {'Optchain':<15}")
print("-" * 80)

for idx, shard_num in enumerate(shard_nums):
    # 1. Error
    if shard_num == 1:
        err = base_error
    else:
        err = (1 - (1 / shard_num)) ** honest_node_num + base_error
    errors_x.append(err)
    
    # 2. Theoretical
    optimal_val = sum(sorted_throughput[:shard_num])
    t_tput = optimal_val * block_size_theoretical
    theo_y.append(t_tput)
    
    # 3. Manifoldchain
    m_exp = EXPERIMENTS_MANIFOLD[idx]
    m_iter = ITERATIONS_MANIFOLD[idx]
    m_tput = analyze_manifold_throughput(m_exp, m_iter, shard_num)
    mani_y.append(m_tput)
    
    # 4. Optchain
    o_exp = EXPERIMENTS_OPTCHAIN[idx]
    o_iter = ITERATIONS_OPTCHAIN[idx]
    o_tput = analyze_optchain_throughput(o_exp, o_iter, shard_num)
    opt_y.append(o_tput)
    
    print(f"{shard_num:<8} | {err:.2e}   | {t_tput:<15.2f} | {m_tput:<15.2f} | {o_tput:<15.2f}")

# Plotting
plt.figure(figsize=(10, 6))

plt.plot(errors_x, theo_y, marker='^', linestyle='-', color='black', label='Theoretical Optimal', linewidth=1.5)
plt.plot(errors_x, mani_y, marker='o', linestyle='-', color='blue', label='Manifoldchain', linewidth=2)
plt.plot(errors_x, opt_y, marker='s', linestyle='--', color='green', label='Optchain', linewidth=2)

plt.xscale('log')
plt.xlabel("Error Probability (log scale)")
plt.ylabel("Throughput (bytes/s)")
plt.title("Throughput vs Error Probability: Manifoldchain vs Optchain vs Theoretical")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)

output_file = 'throughput_comparison_per_shard.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nFigure saved to {output_file}")
plt.show()