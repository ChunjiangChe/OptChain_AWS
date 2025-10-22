import server_utility
import requests
import sys
import threading

def ask_log(instance, protocol, exper_id, exper_iter):
    ip = instance['ip']
    node_id = instance["node_id"]
    api_port = instance['api_port']
    api_addr = "{}:{}".format(ip, api_port)
    #url = "https://{}/network/ping".format(api_addr)
    if protocol == "optchain":
        prop_url = "http://{}/blockchain/proposer-chain".format(api_addr)
        print(prop_url)
        prop_blocks = requests.get(prop_url)
        print(prop_blocks.status_code)
        # print(prop_blocks.content)

        avai_url = "http://{}/blockchain/availability-chain".format(api_addr)
        print(avai_url)
        avai_blocks = requests.get(avai_url)
        print(avai_blocks.status_code)
        # print(avai_blocks.content)

        log_file_path = "./exper_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id)
        with open(log_file_path, "w") as log_file:
            log_file.write("proposer chain: {}\navailability chain: {}".format(prop_blocks.content, avai_blocks.content))
        print("Exper logs for node on instance {} saved to {}".format(ip, log_file_path))
    elif protocol == "manifoldchain":
        chain_url = "http://{}/blockchain/longest-chain-with-time".format(api_addr)
        print(chain_url)
        blocks = requests.get(chain_url)
        print(blocks.status_code)
        # print(blocks.content)

        log_file_path = "./exper_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id)
        with open(log_file_path, "w") as log_file:
            log_file.write("longest chain: {}".format(blocks.content))
        print("Exper logs for node on instance {} saved to {}".format(ip, log_file_path))
    else:
        print("protocol not supported")
        return


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/{}/exper_{}/nodes.json".format(protocol, exper_id))
    
    
    
    tds = []

    for instance in nodes_config['instances']:
        t = threading.Thread(target=ask_log, args=(instance, protocol, exper_id, exper_iter))
        t.start()
        tds.append(t)
        # t.join()
    
    for td in tds:
        td.join()
