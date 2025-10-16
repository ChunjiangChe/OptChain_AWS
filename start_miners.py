import server_utility
import requests
import sys
import threading

def start_miners(instance, mining_interval):
    ip = instance["ip"]
    api_port = instance['api_port']
    api_addr = "{}:{}".format(ip, api_port)
    #url = "https://{}/network/ping".format(api_addr)
    url = "http://{}/miner/start?lambda={}".format(api_addr, mining_interval)
    print(url)
    res = requests.get(url)
    print(res.status_code)
    print(res.content)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/{}/exper_{}/nodes.json".format(protocol, exper_id))

    mining_interval = nodes_config["mining_interval"]

    tds = []

    for instance in nodes_config['instances']:
        t = threading.Thread(target=start_miners, args=(instance, mining_interval))
        t.start()
        tds.append(t)

    for td in tds:
        td.join()

