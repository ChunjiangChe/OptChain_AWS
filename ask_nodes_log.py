import server_utility
import requests


if __name__ == "__main__":
    config = server_utility.load_config('config.json')
    for instance in config['instances']:
        ip = instance['ip']
        api_addr = "{}:7000".format(ip)
        #url = "https://{}/network/ping".format(api_addr)
        url = "http://{}/blockchain/longest-chain".format(api_addr)
        print(url)
        res = requests.get(url)
        print(res.status_code)
        print(res.content)
        log_file_path = "./exper_log/node_{}_log.txt".format(ip)
        with open(log_file_path, "w") as log_file:
            log_file.write("longest chain: {}".format(res.content))
        print("Exper logs for node on instance {} saved to {}".format(ip, log_file_path))
