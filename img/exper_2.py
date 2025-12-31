import numpy as np
import matplotlib.pyplot as plt


base_error = 0.0000000000000000000000000000000000000000000000000001
# highest_bandwidth = 60
given_error = 1e-6


shard_nums = [1, 2, 3, 4, 5]

for shard_num in shard_nums:
    honest_node_num = 1
    while True:
        error = (1 - (1 / shard_num)) ** honest_node_num + base_error
        if error <= given_error:
            break
        honest_node_num += 1
    print(f"shards: {shard_num} required honest nodes: {honest_node_num} Error {error:.2e}")

