import numpy as np
import matplotlib.pyplot as plt
import read_log
import server_utility

shard_nums = [1, 2, 4, 8, 16]
exper_ids = [25, 24, 15, 23, 20]
iters = [0, 0, 0, 0, 0]
# shard_sizes = [2, 4, 8, 16]
honest_node_num = 64
base_error = 0.0000000000000000000000000000000000000000000000000001
# highest_bandwidth = 60


optimal_throughputs = []
errors = []
protocol = "optchain"

for j in range(len(shard_nums)):
    shard_num = shard_nums[j]
    shard_size = honest_node_num // shard_num
    error_1 = (1 - (1 / shard_num)) ** honest_node_num + base_error
    errors.append(error_1)

    exper_id = exper_ids[j]
    exper_iter = iters[j]
    nodes_config = server_utility.load_config("./expers/{}/exper_{}/config.json".format(protocol, exper_id))
    shard_num = nodes_config["shard_num"]
    avai_size = nodes_config["avai_size"]

    throughput = 0
    for i in range(shard_num):
        node_id = i * shard_size
        excl_cnt, incl_cnt = read_log.analyze_chain_log("./exper_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id))
        throughput += (excl_cnt + (incl_cnt / shard_num)) * avai_size

    optimal_throughputs.append(throughput)

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
plt.savefig('./img/optimal_throughput_vs_error.png', dpi=300, bbox_inches='tight')

# error = (((64+1)/(64*4+1))**4) * ((64+1)/(64*4*3))
# print("error: {}", error)