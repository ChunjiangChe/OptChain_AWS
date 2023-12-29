import server_utility
import requests
import sys
import threading

def start_tx_generators(instance, api_port, tx_generation_interval):
    ip = instance["ip"]
    api_addr = "{}:{}".format(ip, api_port)
    #url = "https://{}/network/ping".format(api_addr)
    url = "http://{}/tx-generator/start?theta={}".format(api_addr, tx_generation_interval)
    print(url)
    res = requests.get(url)
    print(res.status_code)
    print(res.content)


if __name__ == "__main__":
    exper_id = sys.argv[1]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/exper_{}/nodes.json".format(exper_id))

    api_port = hyperparameters["api_port"]
    tx_generation_interval = nodes_config["tx_generation_interval"]


    tds = []
    for instance in nodes_config['instances']:
        t = threading.Thread(target=start_tx_generators, args=(instance, api_port, tx_generation_interval))
        t.start()
        tds.append(t)


    for td in tds:
        td.join()

