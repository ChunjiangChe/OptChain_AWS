import server_utility
import sys
import threading

def view_nodes(instance, container, exper_id, iteration):
    ip = instance["ip"]
    user = instance["user"]
    ssh_key = instance["ssh_key"]
    node_id = instance["node_id"]
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    output, error = server_utility.get_docker_logs(ins_handle, container, False)
    log_file_path = "./exec_log/exper_{}/iter_{}/node_{}.txt".format(exper_id, iteration, node_id)
    with open(log_file_path, "w") as log_file:
        log_file.write("output: {}".format(output))
        log_file.write("err: {}".format(error))
    print("Logs for {} on node {} saved to {}".format(container, node_id, log_file_path))
    ins_handle.close()

if __name__ == "__main__":
    exper_id = sys.argv[1]

    nodes_config = server_utility.load_config('./expers/exper_{}/nodes.json'.format(exper_id))
    hyperparameters = server_utility.load_config("./hyperparameter.json")

    container = hyperparameters["container"]
    iteration = nodes_config["iteration"]

    tds = []

    for instance in nodes_config['instances']:
        t = threading.Thread(target=view_nodes, args=(instance, container, exper_id, iteration))
        t.start()
        tds.append(t)
    for td in tds:
        td.join()
