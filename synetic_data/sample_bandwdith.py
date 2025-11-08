import pandas as pd
import numpy as np
import json

# Load dataset
df = pd.read_csv("ethereum_node_bandwidth_synthetic_samples.csv")

# Filter out samples with bandwidth < 5 Mbps
df = df[df['mbps'] >= 5].reset_index(drop=True)

num_trials = 100
sample_size = 64
shard_num = 8

# Step 1: 100 trials, each sampling 64 data points and sorting them
sorted_bandwidths = np.zeros((num_trials, sample_size))
for t in range(num_trials):
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
print("Original 64 average bandwidths:")
print(json.dumps(avg_bandwidth_per_rank.tolist()))

print("\nBalanced distribution (round-robin, flattened):")
print(json.dumps(balanced_flat))

print("\nGrouped distribution (similar bandwidths together, flattened):")
print(json.dumps(grouped_flat))