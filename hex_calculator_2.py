import math
# Input hex string (with leading zeros preserved)
prop_size = 16
avai_size = prop_size
shard_num = 16
shard_size = 4
base_avai_hex = "00019c71c71c71c71c71c71c71c71c71c71c71c71c71c71c71c71c71c71c71c7"
base_shard_size = 2
alpha = 0.67
alpha_var = 0.42
lambda_p = 0.2
lambda_ex_plus_in = lambda_p / shard_num
propagation_delay = 0.1 #100ms
bandwidth_mbps = 6 #6Mbps
prop_avai_block_size_mb = 0.001 #0.001MB
block_size_mbit = prop_avai_block_size_mb * 8
delta = block_size_mbit / bandwidth_mbps + propagation_delay

max_lampda_p = (alpha / (1+alpha * delta)) * (1/(1-alpha))
print("Max Lambda_p :", max_lampda_p)

in_multi_factor = shard_num / (((alpha_var) / (alpha-0.5*((math.e)**(lambda_ex_plus_in * delta)))) - 1)
in_multi_factor_round = round(shard_num / (((alpha_var) / (alpha-0.5*((math.e)**(lambda_ex_plus_in * delta)))) - 1))
print("In Multi Factor :", in_multi_factor)
print("In Multi Factor Round :", in_multi_factor_round)
# Convert to integer
base_avai_num = int(base_avai_hex, 16)

avai_num = base_avai_num // (shard_size // base_shard_size)
prop_num = avai_num * (1+1)
tx_num = prop_num * (prop_size + 1)
in_avai_num = avai_num // (in_multi_factor_round * shard_num + 1)
# quotient = num // 5
manifoldchain_in_num = in_avai_num * avai_size
manifoldchain_ex_num = avai_num * avai_size

# Format back to hex, padded to the same length
tx_hex = f"{tx_num:0{len(base_avai_hex)}x}"
prop_hex = f"{prop_num:0{len(base_avai_hex)}x}"
avai_hex = f"{avai_num:0{len(base_avai_hex)}x}"
in_avai_hex = f"{in_avai_num:0{len(base_avai_hex)}x}"
manifoldchain_in_hex = f"{manifoldchain_in_num:0{len(base_avai_hex)}x}"
manifoldchain_ex_hex = f"{manifoldchain_ex_num:0{len(base_avai_hex)}x}"


print("Tx diff :", tx_hex)
print("Proposer diff :", prop_hex)
print("Availability diff :", avai_hex)
print("Inclusive Availability diff :", in_avai_hex)
print("Manifoldchain Inclusive diff :", manifoldchain_in_hex)
print("Manifoldchain Exclusive diff :", manifoldchain_ex_hex)


