import server_utility
import requests
import sys


if __name__ == "__main__":
    exper_id = sys.argv[1]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/exper_{}/nodes.json".format(exper_id))
    
    api_port = hyperparameters["api_port"]
    iteration = nodes_config["iteration"]

    for instance in nodes_config['instances']:
        ip = instance['ip']
        node_id = instance["node_id"]
        api_addr = "{}:{}".format(ip, api_port)
        #url = "https://{}/network/ping".format(api_addr)
        url = "http://{}/blockchain/longest-chain-with-time".format(api_addr)
        print(url)
        res = requests.get(url)
        print(res.status_code)
        print(res.content)
        log_file_path = "./exper_log/exper_{}/iter_{}/node_{}.txt".format(exper_id, iteration, node_id)
        with open(log_file_path, "w") as log_file:
            log_file.write("longest chain: {}".format(res.content))
        print("Exper logs for node on instance {} saved to {}".format(ip, log_file_path))
