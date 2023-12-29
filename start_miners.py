import server_utility
import requests
import sys
import threading

def start_miners(instance, api_port, mining_interval):
    ip = instance["ip"]
    api_addr = "{}:{}".format(ip, api_port)
    #url = "https://{}/network/ping".format(api_addr)
    url = "http://{}/miner/start?lambda={}".format(api_addr, mining_interval)
    print(url)
    res = requests.get(url)
    print(res.status_code)
    print(res.content)

if __name__ == "__main__":
    exper_id = sys.argv[1]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/exper_{}/nodes.json".format(exper_id))

    api_port = hyperparameters["api_port"]
    mining_interval = nodes_config["mining_interval"]

    tds = []

    for instance in nodes_config['instances']:
        t = threading.Thread(target=start_miners, args=(instance, api_port, mining_interval))
        t.start()
        tds.append(t)

    for td in tds:
        td.join()

