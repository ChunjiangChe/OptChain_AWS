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
    0.03, 0.05, 0.05, 0.06, 0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.09, 0.11, 0.11, 0.13, 0.14, 0.14, 
    0.04, 0.05, 0.05, 0.06, 0.07, 0.07, 0.08, 0.08, 0.09, 0.09, 0.10, 0.11, 0.11, 0.11, 0.14, 0.14, 
    0.04, 0.05, 0.05, 0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.11, 0.11, 0.13, 0.12, 0.14, 0.17, 
    0.04, 0.05, 0.06, 0.07, 0.06, 0.07, 0.08, 0.08, 0.10, 0.10, 0.11, 0.12, 0.13, 0.15, 0.15, 0.20
]

# ==========================================
# 2. LOG ANALYSIS CONFIGURATION
# ==========================================
# UPDATE: These are now lists of lists. 
# Each inner list contains the iteration IDs to average for that specific experiment.

EXPERIMENTS_MANIFOLD = [9, 8, 10, 7, 6]  
# Add your iterations here, e.g., [0, 1, 2]
ITERATIONS_MANIFOLD = [
    [0],    # Iterations for Exp 9 (Shard 1)
    [0],    # Iterations for Exp 8 (Shard 2)
    [0],    # Iterations for Exp 10 (Shard 4)
    [0],    # Iterations for Exp 7 (Shard 8)
    [0]     # Iterations for Exp 6 (Shard 16)
]

EXPERIMENTS_OPTCHAIN = [39, 38, 40, 37, 54] 
# Add your iterations here
ITERATIONS_OPTCHAIN = [
    [1],    # Iterations for Exp 39 (Shard 1)
    [2],    # Iterations for Exp 38 (Shard 2)
    [1],    # Iterations for Exp 40 (Shard 4)
    [0],    # Iterations for Exp 37 (Shard 8)
    [0, 1]     # Iterations for Exp 54 (Shard 16)
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
        # Fallback to experiment level config if iteration config doesn't exist
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
    Calculates throughput for a single iteration of Manifoldchain.
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
    Calculates throughput for a single iteration of Optchain.
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
                shard_tput = (ex_rate + in_rate) * block_size * avai_size
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

print(f"{'Shards':<8} | {'Error':<10} | {'Theoretical':<15} | {'Manifold (Avg)':<15} | {'Optchain (Avg)':<15}")
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
    
    # 3. Manifoldchain (Average across iterations)
    m_exp = EXPERIMENTS_MANIFOLD[idx]
    m_iters = ITERATIONS_MANIFOLD[idx]
    m_results = []
    
    for iter_id in m_iters:
        res = analyze_manifold_throughput(m_exp, iter_id, shard_num)
        m_results.append(res)
    
    m_tput_avg = np.mean(m_results) if m_results else 0.0
    mani_y.append(m_tput_avg)
    
    # 4. Optchain (Average across iterations)
    o_exp = EXPERIMENTS_OPTCHAIN[idx]
    o_iters = ITERATIONS_OPTCHAIN[idx]
    o_results = []
    
    for iter_id in o_iters:
        res = analyze_optchain_throughput(o_exp, iter_id, shard_num)
        o_results.append(res)

    o_tput_avg = np.mean(o_results) if o_results else 0.0
    opt_y.append(o_tput_avg)
    
    print(f"{shard_num:<8} | {err:.2e}   | {t_tput:<15.2f} | {m_tput_avg:<15.2f} | {o_tput_avg:<15.2f}")

# Plotting
# 1. Setup the figure with a clean, academic style
# ... [Keep your calculation loops exactly the same] ...

# ==========================================
# 4. MODIFIED PLOTTING (Double Log Scale)
# ==========================================
# Transformation: log10 of the negative log10 of the error.
# This compresses the gap between 10^-50 and 10^-20.
# P = 10^-50 -> -log10(P) = 50 -> log10(50) ≈ 1.7
# P = 10^-2  -> -log10(P) = 2  -> log10(2)  ≈ 0.3
errors_x_transformed = [np.log2(-np.log10(e)) for e in errors_x]

plt.figure(figsize=(11, 7))
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = ['Gill Sans MT', 'Gill Sans', 'Arial']

style_configs = [
    {
        "data": theo_y,
        "label": "Theoretical Optimal",
        "color": "#4C72B0",
        "linestyle": "--",
        "marker": ".",
        "markersize": 12
    },
    {
        "data": opt_y,
        "label": "Optchain (Avg)",
        "color": "#55A868",
        "linestyle": "-.",
        "marker": ".",
        "markersize": 12
    },
    {
        "data": mani_y,
        "label": "Manifoldchain (Avg)",
        "color": "#C44E52",
        "linestyle": "-",
        "marker": "+",
        "markersize": 10
    }
]

# B. Plot using the Transformed X
for config in style_configs:
    plt.plot(errors_x_transformed, config["data"], 
             label=config["label"], 
             color=config["color"], 
             linestyle=config["linestyle"], 
             marker=config["marker"], 
             linewidth=1.5,
             markersize=config["markersize"])

# C. Generate Custom Labels
#    Format: 10^{-(2^x)}
#    This shows the x-value (e.g., 5.64) inside the expression 
#    that recovers the original probability.
tick_labels = []
for val in errors_x_transformed:
    # val is the transformed x (e.g., 5.64)
    # We format it to 2 decimal places inside the LaTeX string
    label = f"$10^{{-(2^{{{val:.2f}}})}}$"
    tick_labels.append(label)

# D. Axis Formatting
# 1. Set ticks at the transformed positions (x)
plt.xticks(errors_x_transformed, tick_labels, rotation=30, fontsize=11)

# 2. Invert X axis?
#    x=5.64 corresponds to Error=10^-50 (Small error)
#    x=1.00 corresponds to Error=10^-2 (Large error)
#    Usually we want Small Error on the LEFT.
#    So we want 5.64 on Left, 1.00 on Right.
plt.gca().invert_xaxis()

# 3. Y-Axis
plt.yscale('log')
plt.ylabel("Throughput (bytes/s)", fontsize=12, fontweight='bold')

# 4. X-Axis Label
#    Explains that 'x' is the exponent in the formula
plt.xlabel(r"Error Probability as Function of Transformed Value $x$" + "\n" + r"$\text{Error} = 10^{-(2^x)}$", 
           fontsize=12, fontweight='bold', labelpad=10)

# 5. Spines and Grid
ax = plt.gca()
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)
ax.grid(False)

plt.legend(loc='upper left', frameon=True, fontsize=11, framealpha=1, edgecolor='#cccccc')

output_file = 'exper_1_2.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nFigure saved to {output_file}")
plt.show()