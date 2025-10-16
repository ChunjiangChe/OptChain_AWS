import server_utility
import sys
import threading

def view_nodes(instance, container, exper_id, exper_iter):
    ip = instance["ip"]
    user = instance["user"]
    ssh_key = instance["ssh_key"]
    node_id = instance["node_id"]
    container_name = "{}{}".format(container, node_id)
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    output, error = server_utility.get_docker_logs(ins_handle, container_name, False)
    log_file_path = "./exec_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id)
    with open(log_file_path, "w") as log_file:
        log_file.write("output: {}".format(output))
        log_file.write("err: {}".format(error))
    print("Logs for {} on node {} saved to {}".format(container, node_id, log_file_path))
    ins_handle.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    nodes_config = server_utility.load_config('./expers/{}/exper_{}/nodes.json'.format(protocol, exper_id))
    hyperparameters = server_utility.load_config("./hyperparameter.json")

    container = hyperparameters["container"]

    tds = []

    for instance in nodes_config['instances']:
        t = threading.Thread(target=view_nodes, args=(instance, container, exper_id, exper_iter))
        t.start()
        tds.append(t)
    for td in tds:
        td.join()
