import math
# Input hex string (with leading zeros preserved)
prop_size = 8
avai_size = prop_size
shard_num = 4
shard_size = 16
manifoldchain_avai_hex = "00000bfffffffffffffffffffffffffffffffffffffffffffffffffffffffffd"
manifoldchain_in_avai_hex = "0000026666666666666666666666666666666666666666666666666666666664"
base_shard_size = 4
alpha = 0.67
alpha_var = 0.42
lambda_p = 0.2
lambda_ex_plus_in = lambda_p / shard_num
propagation_delay = 0.1 #100ms
bandwidth_mbps = 6 #6Mbps
prop_avai_block_size_mb = 0.001 #0.001MB
block_size_mbit = prop_avai_block_size_mb * 8
delta = block_size_mbit / bandwidth_mbps + propagation_delay

manifoldchain_avai_num = int(manifoldchain_avai_hex, 16)
manifoldchain_in_avai_num = int(manifoldchain_in_avai_hex, 16)

optchain_avai_num = manifoldchain_avai_num // avai_size
optchain_in_avai_num = manifoldchain_in_avai_num // avai_size

# Format back to hex, padded to the same length
optchain_avai_hex = f"{optchain_avai_num:0{len(manifoldchain_avai_hex)}x}"
optchain_in_avai_hex = f"{optchain_in_avai_num:0{len(manifoldchain_in_avai_hex)}x}"


print("Manifoldchain Inclusive diff :", manifoldchain_in_avai_hex)
print("Manifoldchain Exclusive diff :", manifoldchain_avai_hex)
print("OptChain Inclusive diff :", optchain_in_avai_hex)
print("OptChain Exclusive diff :", optchain_avai_hex)


