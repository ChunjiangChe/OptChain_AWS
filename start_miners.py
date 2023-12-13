import server_utility
import requests

if __name__ == "__main__":
    config = server_utility.load_config('config.json')
    for instance in config['instances']:
        api_addr = "{}:7000".format(instance['ip'])
        mining_interval = 5000000
        #url = "https://{}/network/ping".format(api_addr)
        url = "http://{}/miner/start?lambda={}".format(api_addr, mining_interval)
        print(url)
        res = requests.get(url)
        print(res.status_code)
        print(res.content)

