import pandas as pd
import numpy as np
import json

# --- Configuration Parameters ---
min_bandwidth = 10      # Minimum allowed bandwidth (Mbps)
max_bandwidth = 80   # Maximum allowed bandwidth (Mbps)
num_trials = 100
sample_size = 20
shard_num = 2
# --------------------------------

def get_group_maxes(grouped_flat, m):
    """
    Distributes a list into m groups and finds the max of each group.
    
    Args:
        grouped_flat (list): The input ordered list.
        m (int): The number of groups to split into.
        
    Returns:
        list: A list containing the maximal element from each of the m groups.
    """
    n = len(grouped_flat)
    
    # Validation
    if m <= 0:
        raise ValueError("Number of groups (m) must be greater than 0")
    if m > n:
        print("Warning: m is larger than the list size. Some groups will be empty.")

    max_values = []

    for i in range(m):
        # Calculate start and end indices for the i-th group
        # This formula distributes the remainder evenly across the groups
        start_index = (i * n) // m
        end_index = ((i + 1) * n) // m
        
        # Slice the group
        group = grouped_flat[start_index:end_index]
        
        # Calculate max (handle empty groups if m > len(list))
        if group:
            max_values.append(max(group))
        else:
            max_values.append(None) 
            
    return max_values

# Load dataset
# Ensure you have this file in your working directory
try:
    df = pd.read_csv("ethereum_node_bandwidth_synthetic_samples.csv")
except FileNotFoundError:
    # Creating dummy data for demonstration if file doesn't exist
    print("CSV not found, creating synthetic data for demonstration...")
    np.random.seed(42)
    df = pd.DataFrame({'mbps': np.random.lognormal(mean=2, sigma=1, size=1000)})

# --- Filtering Logic Updated ---
# Filter samples where bandwidth is >= min AND <= max
initial_count = len(df)
df = df[
    (df['mbps'] >= min_bandwidth) & 
    (df['mbps'] <= max_bandwidth)
].reset_index(drop=True)

print(f"Data filtered: {len(df)} samples remaining out of {initial_count} "
      f"(Range: {min_bandwidth}-{max_bandwidth} Mbps)")

if len(df) < sample_size:
    raise ValueError(f"Not enough data points ({len(df)}) to sample {sample_size} values. "
                     "Please widen the bandwidth range.")

# Step 1: 100 trials, each sampling data points and sorting them
sorted_bandwidths = np.zeros((num_trials, sample_size))
for t in range(num_trials):
    # Sample from the filtered dataframe
    sample = df['mbps'].sample(sample_size, replace=False).values
    sorted_bandwidths[t] = np.sort(sample)

# Step 2: compute average per rank and round
avg_bandwidth_per_rank = np.round(sorted_bandwidths.mean(axis=0)).astype(int)

# Step 3: build distributions
# (1) Balanced (round-robin)
balanced_shards = [[] for _ in range(shard_num)]
for i, bw in enumerate(avg_bandwidth_per_rank):
    balanced_shards[i % shard_num].append(int(bw))

# (2) Grouped (contiguous)
chunk_size = sample_size // shard_num
grouped_shards = [
    avg_bandwidth_per_rank[i * chunk_size:(i + 1) * chunk_size].tolist()
    for i in range(shard_num)
]

# Step 4: flatten both 2D shard lists into 1D lists
balanced_flat = [bw for shard in balanced_shards for bw in shard]
grouped_flat = [bw for shard in grouped_shards for bw in shard]

# Step 5: print results
print(f"\nOriginal {sample_size} average bandwidths:")
print(json.dumps(avg_bandwidth_per_rank.tolist()))

print("\nBalanced distribution (round-robin, flattened):")
print(json.dumps(balanced_flat))

print("\nGrouped distribution (similar bandwidths together, flattened):")
print(json.dumps(grouped_flat))

result = get_group_maxes(grouped_flat, shard_num)
print(f"\nMax of each group: {result}")