import server_utility
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    config = server_utility.load_config("./expers/{}/exper_{}/config.json".format(protocol, exper_id))
    shard_num = config["shard_num"]
    shard_size = config["shard_size"]

    for i in range(shard_num):
        for j in range(shard_size):
            node_id = i * shard_size + j
            file_path = "./exec_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id)
            f = open(file_path, "r")
            line_num = 0
            for line in f.readlines():
                line_num += 1
                if "unwrap" in line:
                    print("Erro occur in exper {} iter {} node {} line {}".format(exper_id, iteration, node_id, line_num))
                    break
                
                
                    
                

    
    

