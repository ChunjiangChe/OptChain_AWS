import server_utility
import sys
import random
import os

if __name__ == "__main__":
    # get the experiment id
    exper_id = sys.argv[1]
    
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    # some basic configuation
    image = hyperparameters["image"]
    container = hyperparameters["container"]
    network_interface = hyperparameters["network_interface"]
    p2p_port = hyperparameters["p2p_port"]
    api_port = hyperparameters["api_port"]

    # load instances
    instances_config = server_utility.load_config("./instances.json")
    user_name = instances_config["user"]
    nodes = []
    for region in instances_config["instances"]:
        ssh_key = region["ssh_key"]
        region_name = region["region"]
        for ip in region["ips"]:
            nodes.append((ip, ssh_key, region_name))
    random.shuffle(nodes)


    exper_config = server_utility.load_config("./expers/exper_{}/config.json".format(exper_id))
    
    shard_num = exper_config["shard_num"]
    shard_size = exper_config["shard_size"]
    block_size = exper_config["block_size"]
    confirmation_depth = exper_config["confirmation_depth"]
    mining_interval = exper_config["mining_interval"]
    tx_generation_interval = exper_config["tx_generation_interval"]
    runtime = exper_config["runtime"]
    iteration = exper_config["iteration"]
    idff = exper_config["inclusive_diff"]
    edffs = exper_config["exclusive_diffs"]
    propagation_delay = exper_config["propagation_delay"] #no need
    bandwidths = exper_config["bandwidths"]

    # create the relevant path
    exper_log_path = "./exper_log/exper_{}/iter_{}/".format(exper_id, iteration)
    exper_log_folder = os.path.exists(exper_log_path)
    if not exper_log_folder:
        os.makedirs(exper_log_path)
        print("create exper log folder")
    else:
        print("exper folder already exits")
    exec_log_path = "./exec_log/exper_{}/iter_{}/".format(exper_id, iteration)
    exec_log_folder = os.path.exists(exec_log_path)
    if not exec_log_folder:
        os.makedirs(exec_log_path)
        print("create exec log folder")
    else:
        print("exec folder already exits")


    nodes_config = []
    for i in range(shard_num):
        for j in range(shard_size):
            node_id = i * shard_size + j
            node_ip, node_key, region_name = nodes[node_id]
            bandwidth = bandwidths[i][j]
            edff = edffs[i]
            peers = []
            # add inter peers
            for k in range(j):
                past_inter_node_id = i * shard_size + k
                peers.append("{}:{}".format(nodes[past_inter_node_id][0], p2p_port))
            # add outer peers
            for h in range(i):
                past_outer_node_id = h * shard_size + j
                peers.append("{}:{}".format(nodes[past_outer_node_id][0], p2p_port))
            peers_parameter = ""
            if len(peers) > 0:
                for peer in peers:
                    peers_parameter = "{}{},".format(peers_parameter, peer)
                peers_parameter = peers_parameter[0:len(peers_parameter)-1]
            # generate the parameters
            parameters = [\
                          "-p {}:{}".format(p2p_port, p2p_port),\
                          "-p {}:{}".format(api_port, api_port),\
                          "-e P2P='0.0.0.0:{}'".format(p2p_port),\
                          "-e API='0.0.0.0:{}'".format(api_port),\
                          "-e PEERS='{}'".format(peers_parameter),\
                          "-e SHARD_ID='{}'".format(i),\
                          "-e NODE_ID='{}'".format(node_id),\
                          "-e EXPER_NUMBER='{}'".format(exper_id),\
                          "-e SHARD_NUM='{}'".format(shard_num),\
                          "-e SHARD_SIZE='{}'".format(shard_size),\
                          "-e BLOCK_SIZE='{}'".format(block_size),\
                          "-e K='{}'".format(confirmation_depth),\
                          "-e EDIFF='{}'".format(edff),\
                          "-e IDIFF='{}'".format(idff),\
                          ]

            # generate the node config
            node_config = {\
                           "region": region_name,\
                           "ip": node_ip,\
                           "user": user_name,\
                           "node_id": node_id,\
                           "ssh_key": node_key,\
                           "bandwidth": bandwidth,\
                           "parameters": parameters\
                           }
            nodes_config.append(node_config)

    # generate the whole config
    config = {\
              "image": image,\
              "container": container,\
              "network_interface": network_interface,\
              "mining_interval": mining_interval,\
              "tx_generation_interval": tx_generation_interval,\
              "runtime": runtime,\
              "iteration": iteration,\
              "instances": nodes_config\
              }
    server_utility.write_config("./expers/exper_{}/nodes.json".format(exper_id), config)

