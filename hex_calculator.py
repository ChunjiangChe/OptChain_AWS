import math
# Input hex string (with leading zeros preserved)
prop_size = 64
avai_size = prop_size
shard_num = 16
tx_hex = "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffdc00"
alpha = 0.67
alpha_var = 0.42
lambda_p = 0.08
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
tx_num = int(tx_hex, 16)

prop_num = tx_num // (prop_size + 1)
avai_num = prop_num // (1+1)
in_avai_num = avai_num // (in_multi_factor_round * shard_num + 1)
# quotient = num // 5
manifoldchain_in_num = in_avai_num * avai_size
manifoldchain_ex_num = avai_num * avai_size


# Format back to hex, padded to the same length
prop_hex = f"{prop_num:0{len(tx_hex)}x}"
avai_hex = f"{avai_num:0{len(tx_hex)}x}"
in_avai_hex = f"{in_avai_num:0{len(tx_hex)}x}"
manifoldchain_in_hex = f"{manifoldchain_in_num:0{len(tx_hex)}x}"
manifoldchain_ex_hex = f"{manifoldchain_ex_num:0{len(tx_hex)}x}"


print("Tx diff :", tx_hex)
print("Proposer diff :", prop_hex)
print("Availability diff :", avai_hex)
print("Inclusive Availability diff :", in_avai_hex)
print("Manifoldchain Inclusive diff :", manifoldchain_in_hex)
print("Manifoldchain Exclusive diff :", manifoldchain_ex_hex)


# tx_num_2 = tx_num * 2
# tx_num_2_hex = f"{tx_num_2:0{len(tx_hex)}x}"
# print("Tx diff 2x :", tx_num_2_hex)


