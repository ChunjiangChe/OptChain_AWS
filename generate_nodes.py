import server_utility
import sys
import random
import os

def get_protocol_config(protocol, exper_id, nodes):
    if protocol == "optchain":
        exper_config = server_utility.load_config("./expers/optchain/exper_{}/config.json".format(exper_id))
    
        shard_num = exper_config["shard_num"]
        shard_size = exper_config["shard_size"]
        block_size = exper_config["block_size"]
        symbol_size = exper_config["symbol_size"]
        prop_size = exper_config["prop_size"]
        avai_size = exper_config["avai_size"]
        ex_req_num = exper_config["ex_req_num"]
        in_req_num = exper_config["in_req_num"]
        confirmation_depth = exper_config["confirmation_depth"]
        tx_dff = exper_config["tx_diff"]
        prop_dff = exper_config["prop_diff"]
        avai_dff = exper_config["avai_diff"]
        in_avai_dff = exper_config["in_avai_diff"]
        bandwidths = exper_config["bandwidths"]

        nodes_config = []
        for i in range(shard_num):
            for j in range(shard_size):
                node_id = i * shard_size + j
                node_ip, node_p2p_port, node_api_port, node_key, region_name = nodes[node_id]
                bandwidth = bandwidths[node_id]

                peers = []
                for k in range(i+1):
                    h_range = j if k == i else shard_size
                    for h in range(h_range):
                        past_node_id = k * shard_size + h
                        past_node_ip, past_node_p2p_port, past_node_api_port, past_node_key, past_region_name = nodes[past_node_id]
                        peers.append("{}:{}".format(past_node_ip, past_node_p2p_port))
                print("peer size: {}".format(len(peers)))
                peers_parameter = ""
                if len(peers) > 0:
                    for peer in peers:
                        peers_parameter = "{}{},".format(peers_parameter, peer)
                    peers_parameter = peers_parameter[0:len(peers_parameter)-1]
                # generate the parameters
                parameters = [\
                        "-p {}:{}".format(node_p2p_port, node_p2p_port),\
                        "-p {}:{}".format(node_api_port, node_api_port),\
                        "-e PROTOCOL='optchain'",\
                        "-e P2P='0.0.0.0:{}'".format(node_p2p_port),\
                        "-e API='0.0.0.0:{}'".format(node_api_port),\
                        "-e PEERS='{}'".format(peers_parameter),\
                        "-e SHARD_ID='{}'".format(i),\
                        "-e NODE_ID='{}'".format(j),\
                        "-e EXPER_NUMBER='{}'".format(exper_id),\
                        "-e EXPER_ITER='{}'".format(exper_iter),\
                        "-e SHARD_NUM='{}'".format(shard_num),\
                        "-e SHARD_SIZE='{}'".format(shard_size),\
                        "-e BLOCK_SIZE='{}'".format(block_size),\
                        "-e SYMBOL_SIZE='{}'".format(symbol_size),\
                        "-e PROP_SIZE='{}'".format(prop_size),\
                        "-e AVAI_SIZE='{}'".format(avai_size),\
                        "-e EX_REQ_NUM='{}'".format(ex_req_num),\
                        "-e IN_REQ_NUM='{}'".format(in_req_num),\
                        "-e K='{}'".format(confirmation_depth),\
                        "-e TX_DIFF='{}'".format(tx_dff),\
                        "-e PROP_DIFF='{}'".format(prop_dff),\
                        "-e AVAI_DIFF='{}'".format(avai_dff),\
                        "-e IN_AVAI_DIFF='{}'".format(in_avai_dff)\
                        ]

                # generate the node config
                node_config = {\
                            "region": region_name,\
                            "ip": node_ip,\
                            "p2p_port": node_p2p_port,\
                            "api_port": node_api_port,\
                            "user": user_name,\
                            "node_id": node_id,\
                            "ssh_key": node_key,\
                            "bandwidth": bandwidth, \
                            "parameters": parameters\
                            }
                nodes_config.append(node_config)
        return nodes_config
    elif protocol == "manifoldchain":
        exper_config = server_utility.load_config("./expers/manifoldchain/exper_{}/config.json".format(exper_id))
    
        shard_num = exper_config["shard_num"]
        shard_size = exper_config["shard_size"]
        block_size = exper_config["block_size"]
        confirmation_depth = exper_config["confirmation_depth"]
        domestic_rate = exper_config["domestic_rate"]
        ex_diffs = exper_config["ex_diffs"]
        in_diff = exper_config["in_diff"]

        nodes_config = []
        for i in range(shard_num):
            for j in range(shard_size):
                node_id = i * shard_size + j
                node_ip, node_p2p_port, node_api_port,node_key, region_name = nodes[node_id]
                ex_diff = ex_diffs[i]
                peers = []
                for k in range(i+1):
                    h_range = j if k == i else shard_size
                    for h in range(h_range):
                        past_node_id = k * shard_size + h
                        past_node_ip, past_node_p2p_port, past_node_api_port, past_node_key, past_region_name = nodes[past_node_id]
                        peers.append("{}:{}".format(past_node_ip, past_node_p2p_port))
                print("peer size: {}".format(len(peers)))
                peers_parameter = ""
                if len(peers) > 0:
                    for peer in peers:
                        peers_parameter = "{}{},".format(peers_parameter, peer)
                    peers_parameter = peers_parameter[0:len(peers_parameter)-1]
                # generate the parameters
                parameters = [\
                        "-p {}:{}".format(node_p2p_port, node_p2p_port),\
                        "-p {}:{}".format(node_api_port, node_api_port),\
                        "-e PROTOCOL='manifoldchain'",\
                        "-e P2P='0.0.0.0:{}'".format(node_p2p_port),\
                        "-e API='0.0.0.0:{}'".format(node_api_port),\
                        "-e PEERS='{}'".format(peers_parameter),\
                        "-e SHARD_ID='{}'".format(i),\
                        "-e NODE_ID='{}'".format(j),\
                        "-e EXPER_NUMBER='{}'".format(exper_id),\
                        "-e EXPER_ITER='{}'".format(exper_iter),\
                        "-e SHARD_NUM='{}'".format(shard_num),\
                        "-e SHARD_SIZE='{}'".format(shard_size),\
                        "-e BLOCK_SIZE='{}'".format(block_size),\
                        "-e K='{}'".format(confirmation_depth),\
                        "-e DOMESTIC_RATE='{}'".format(domestic_rate),\
                        "-e EX_DIFF='{}'".format(ex_diff),\
                        "-e IN_DIFF='{}'".format(in_diff)\
                        ]

                # generate the node config
                node_config = {\
                            "region": region_name,\
                            "ip": node_ip,\
                            "p2p_port": node_p2p_port,\
                            "api_port": node_api_port,\
                            "user": user_name,\
                            "node_id": node_id,\
                            "ssh_key": node_key,\
                            "parameters": parameters\
                            }
                nodes_config.append(node_config)
        return nodes_config
    else:
        print("protocol not supported")
        sys.exit(1)

if __name__ == "__main__":
    # get the experiment id
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]
    
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    # some basic configuation
    image = hyperparameters["image"]
    container = hyperparameters["container"]
    network_interface = hyperparameters["network_interface"]
    p2p_ports = hyperparameters["p2p_ports"]
    api_ports = hyperparameters["api_ports"]

    # load instances
    instances_config = server_utility.load_config("./instances.json")
    user_name = instances_config["user"]
    nodes = []
    for region in instances_config["instances"]:
        ssh_key = region["ssh_key"]
        region_name = region["region"]
        for ip in region["ips"]:
            for i in range(hyperparameters["miners_per_instance"]):
                nodes.append((ip, p2p_ports[i], api_ports[i], ssh_key, region_name))
    random.shuffle(nodes)



    # create the relevant path
    exper_log_path = "./exper_log/{}/exper_{}/iter_{}/".format(protocol, exper_id, exper_iter)
    exper_log_folder = os.path.exists(exper_log_path)
    if not exper_log_folder:
        os.makedirs(exper_log_path)
        print("create exper log folder")
    else:
        print("exper folder already exits")
    exec_log_path = "./exec_log/{}/exper_{}/iter_{}/".format(protocol, exper_id, exper_iter)
    exec_log_folder = os.path.exists(exec_log_path)
    if not exec_log_folder:
        os.makedirs(exec_log_path)
        print("create exec log folder")
    else:
        print("exec folder already exits")
    

    exper_config = server_utility.load_config("./expers/{}/exper_{}/config.json".format(protocol, exper_id))
    mining_interval = exper_config["mining_interval"]
    runtime = exper_config["runtime"]

    nodes_config = get_protocol_config(protocol, exper_id, nodes)
    # generate the whole config
    config = {\
              "image": image,\
              "container": container,\
              "network_interface": network_interface,\
              "mining_interval": mining_interval,\
              "runtime": runtime,\
              "iteration": exper_iter,\
              "instances": nodes_config\
              }
    server_utility.write_config("./expers/{}/exper_{}/nodes.json".format(protocol, exper_id), config)

