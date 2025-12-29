import numpy as np
import matplotlib.pyplot as plt

block_size = 8192
shard_nums = [1, 2, 4, 8, 16]
exper_ids = [25, 24, 15, 23, 20]
iters = [0, 0, 0, 0, 0]
# shard_sizes = [2, 4, 8, 16]
honest_node_num = 64
base_error = 0.0000000000000000000000000000000000000000000000000001
# highest_bandwidth = 60


# Full list of throughput values extracted from the figure
download_blocks = [
    0.02, 0.03, 0.12, 0.13, 0.10, 0.10, 0.13, 0.12, 0.05, 0.27, 
    0.12, 0.03, 0.08, 0.18, 0.15, 0.12, 0.07, 0.08, 0.17, 0.03, 
    0.08, 0.07, 0.15, 0.05, 0.03, 0.10, 0.12, 0.07, 0.10, 0.08, 
    0.15, 0.08, 0.02, 0.13, 0.13, 0.05, 0.07, 0.17, 0.07, 0.15, 
    0.07, 0.05, 0.08, 0.05, 0.07, 0.13, 0.03, 0.15, 0.10, 0.30, 
    0.03, 0.12, 0.03, 0.13, 0.05, 0.18, 0.07, 0.12, 0.05, 0.05, 
    0.13, 0.12, 0.03
]

# 1. Sort in descending order to prioritize highest performing nodes
sorted_throughput = sorted(download_blocks, reverse=True)

# 2. Define the specific shard counts we want to calculate
shard_nums = [1, 2, 4, 8, 16]

print(f"{'Shards':<10} | {'Optimal Throughput (A/s)'}")
print("-" * 35)
optimal_throughputs = []
errors = []


for j in range(len(shard_nums)):
    shard_num = shard_nums[j]
    shard_size = honest_node_num // shard_num
    error_1 = (1 - (1 / shard_num)) ** honest_node_num + base_error
    errors.append(error_1)


    # 3. Calculate sum of top N values for each shard count

    # Sum the top n values
    optimal_val = sum(sorted_throughput[:shard_num])
    opt_tps = optimal_val * block_size
    optimal_throughputs.append(opt_tps)


# Print results
for i in range(len(shard_nums)):
    print(f"shards: {shard_nums[i]} Error {errors[i]:.2e} Optimal Throughput: {optimal_throughputs[i]}")

# Plot
plt.figure(figsize=(8, 5))
plt.plot(errors, optimal_throughputs, marker='o', linestyle='-', color='b')

plt.xscale('log')  # logarithmic scale for exponential appearance
plt.xlabel("Error (exponential notation)")
plt.ylabel("Optimal Throughput")
plt.title("Optimal Throughput vs Error for Different Shard Sizes")
plt.grid(True, which="both", ls="--", lw=0.5)
plt.tight_layout()
plt.savefig('./optimal_throughput_vs_error.png', dpi=300, bbox_inches='tight')

# error = (((64+1)/(64*4+1))**4) * ((64+1)/(64*4*3))
# print("error: {}", error)