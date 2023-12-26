import server_utility
import sys

if __name__ == "__main__":
    exper_id = sys.argv[1]

    nodes_config = server_utility.load_config('./expers/exper_{}/nodes.json'.format(exper_id))
    hyperparameters = server_utility.load_config("./hyperparameter.json")

    container = hyperparameters["container"]

    for instance in nodes_config['instances']:
        ip = instance["ip"]
        user = instance["user"]
        ssh_key = instance["ssh_key"]
        ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
        output, error = server_utility.get_docker_logs(ins_handle, container, False)
        print("Output: {}".format(output))
        print("Error: {}".format(error))
        ins_handle.close()
