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
    honest_node_num = 10
    while True:
        error = (1 - (1 / shard_num)) ** honest_node_num + base_error
        if error <= given_error:
            break
        honest_node_num += 1
    honest_node_nums.append(honest_node_num)
  # Scale by 2 for better visualization

print(honest_node_nums)
# Bandwidth data (Download blocks)
download_blocks = [
    0.03, 0.05, 0.05, 0.06, 0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.09, 0.11, 0.11, 0.13, 0.14, 0.14, 
    0.04, 0.05, 0.05, 0.06, 0.07, 0.07, 0.08, 0.08, 0.09, 0.09, 0.10, 0.11, 0.11, 0.11, 0.14, 0.14, 
    0.04, 0.05, 0.05, 0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.11, 0.11, 0.13, 0.12, 0.14, 0.17, 
    0.04, 0.05, 0.06, 0.07, 0.06, 0.07, 0.08, 0.08, 0.10, 0.10, 0.11, 0.12, 0.13, 0.15, 0.15, 0.20
]

# ==========================================
# 2. LOG ANALYSIS CONFIGURATION
# ==========================================
EXPERIMENTS_MANIFOLD = [20, 21, 22, 23, 24]  
ITERATIONS_MANIFOLD = [
    [0, 1, 2],       # Iterations for Exp 11
    [0, 1],       # Iterations for Exp 11
    [0],       # Iterations for Exp 12
    [0, 1, 2],       # Iterations for Exp 13
    [0, 1, 2],    # Iterations for Exp 14
]

EXPERIMENTS_OPTCHAIN = [61, 42, 43, 44, 45] 
ITERATIONS_OPTCHAIN = [
    [0, 1],
    [0, 1, 2, 3, 4], # Iterations for Exp 42
    [0, 1, 2, 3, 4], # Iterations for Exp 43
    [0],             # Iterations for Exp 44
    [1]              # Iterations for Exp 45
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
    protocol = "manifoldchain"
    config = load_config(protocol, exper_id, iter_id)
    block_size = config.get("block_size", 1024)
    shard_size = config.get("shard_size", 1)

    total_mining_rate = 0.0

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

        if len(shard_timestamps) >= 2:
            duration = (max(shard_timestamps) - min(shard_timestamps)).total_seconds()
            if duration > 0:
                shard_rate = len(shard_timestamps) / duration
                total_mining_rate += shard_rate

    return total_mining_rate * block_size

def analyze_optchain_throughput(exper_id, iter_id, shard_num):
    protocol = "optchain"
    config = load_config(protocol, exper_id, iter_id)
    block_size = config.get("block_size", 1024)
    avai_size = config.get("avai_size", 1024)
    shard_size = config.get("shard_size", 1)

    total_throughput = 0.0

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

        if len(shard_timestamps) >= 2:
            duration = (max(shard_timestamps) - min(shard_timestamps)).total_seconds()
            if duration > 0:
                ex_rate = ex_count / duration
                in_rate = in_count / duration
                shard_tput = (ex_rate + in_rate) * block_size * avai_size
                total_throughput += shard_tput

    return total_throughput

# ==========================================
# 4. MAIN EXECUTION & PLOTTING
# ==========================================

# A. Theoretical Calculation & Data Collection
sorted_throughput = sorted(download_blocks, reverse=True)
theo_y = []
mani_y = []
opt_y = []

print(f"{'Shards':<8} | {'Number':<10} | {'Theoretical':<15} | {'Manifold':<15} | {'Optchain':<15}")
print("-" * 80)

for idx, shard_num in enumerate(shard_nums):
    honest_node_num = honest_node_nums[idx]
    
    # 2. Theoretical
    x = honest_node_num                
    iterations = 1000    

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
    
    # 3. Manifoldchain
    
    m_exp = EXPERIMENTS_MANIFOLD[idx]
    m_iters_list = ITERATIONS_MANIFOLD[idx]
    
    temp_sum_tput = 0.0
    valid_iter_count = 0
    
    for iter_id in m_iters_list:
        try:
            val = analyze_manifold_throughput(m_exp, iter_id, shard_num)
            temp_sum_tput += val
            valid_iter_count += 1
        except Exception as e:
            print(f"Warning: Failed to process Manifold Exp {m_exp} Iter {iter_id}: {e}")

    m_tput = temp_sum_tput / valid_iter_count if valid_iter_count > 0 else 0.0
    mani_y.append(m_tput)
    
    # 4. Optchain
    
    o_exp = EXPERIMENTS_OPTCHAIN[idx]
    o_iters_list = ITERATIONS_OPTCHAIN[idx]
    
    temp_sum_tput = 0.0
    valid_iter_count = 0

    for iter_id in o_iters_list:
        try:
            val = analyze_optchain_throughput(o_exp, iter_id, shard_num)
            temp_sum_tput += val
            valid_iter_count += 1
        except Exception as e:
                print(f"Warning: Failed to process Optchain Exp {o_exp} Iter {iter_id}: {e}")

    o_tput = temp_sum_tput / valid_iter_count if valid_iter_count > 0 else 0.0
    opt_y.append(o_tput)
    
    print(f"{shard_num:<8} | {honest_node_num:<10} | {t_tput:<15.2f} | {m_tput:<15.2f} | {o_tput:<15.2f}")


# ==========================================
# B. PLOTTING (Bar + Line Hybrid)
# ==========================================

# 1. Setup Data for Plotting
honest_node_nums = [x*2 for x in honest_node_nums]
x_indices = np.array(honest_node_nums)

# Calculate dynamic width: find the smallest gap between X values to ensure bars don't overlap
if len(x_indices) > 1:
    min_gap = np.min(np.diff(x_indices))
    # We have 3 bars. Let's make the total cluster width 60% of the gap
    bar_width = min_gap * 0.2 
else:
    bar_width = 5 # Default fallback if only 1 point

# 2. Setup Figure
plt.figure(figsize=(11, 7))
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Gill Sans MT', 'Arial', 'DejaVu Sans']

# Colors
color_theo = "#4C72B0" # Blue
color_opt = "#55A868"  # Green
color_mani = "#C44E52" # Red

# 3. Plot BARS (The Discrete Results)
# We shift the x-position for each bar so they stand side-by-side
# Order: Theoretical (Left), Optchain (Middle), Manifold (Right)
plt.bar(x_indices - bar_width, theo_y, width=bar_width, label='Theoretical', 
        color=color_theo, alpha=0.6, edgecolor='black', linewidth=0.5)

plt.bar(x_indices, opt_y, width=bar_width, label='Optchain (Avg)', 
        color=color_opt, alpha=0.6, edgecolor='black', linewidth=0.5)

plt.bar(x_indices + bar_width, mani_y, width=bar_width, label='Manifoldchain (Avg)', 
        color=color_mani, alpha=0.6, edgecolor='black', linewidth=0.5)


# 4. Plot LINES (The Trend) - FIXED ALIGNMENT
# Shift theoretical line/points LEFT to match the blue bars
plt.plot(x_indices - bar_width, theo_y, color=color_theo, linestyle='--', marker='o', 
         linewidth=2, markersize=6, alpha=1.0)

# Optchain line/points stay CENTERED to match the green bars
plt.plot(x_indices, opt_y, color=color_opt, linestyle='-.', marker='s', 
         linewidth=2, markersize=6, alpha=1.0)

# Shift Manifold line/points RIGHT to match the red bars
plt.plot(x_indices + bar_width, mani_y, color=color_mani, linestyle=':', marker='^', 
         linewidth=2.5, markersize=6, alpha=1.0)


# 5. Formatting
plt.yscale('log')
plt.xlabel("Number of Nodes", fontsize=13, fontweight='bold', labelpad=10)
plt.ylabel("Throughput (bytes/s)", fontsize=13, fontweight='bold', labelpad=10)

# Clean look adjustments
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.2)
ax.spines['left'].set_linewidth(1.2)

# Ensure tick labels match x_values exactly if they are sparse
ax.set_xticks(x_indices)
ax.tick_params(axis='both', which='major', length=5, width=1, labelsize=11)

# Legend
# Deduplicate the legend handles
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper left', frameon=True, fontsize=11, framealpha=0.9, edgecolor='#cccccc')

# Output
output_file = 'exper_2.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nFigure saved to {output_file}")
plt.show()