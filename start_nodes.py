import server_utility
import remove_limitation
import limit_bandwidth
import sys
import time
import threading

def start_nodes(instance, exper_id, image, container, network_interface):
    ip = instance["ip"]
    user = instance["user"]
    node_id = instance["node_id"]
    ssh_key = instance["ssh_key"]
    # bandwidth = instance["bandwidth"]
    parameters = instance["parameters"]

    print("handle node {}".format(node_id))

    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    
    #configure the bandwidth of each node
    # remove_limitation.remove_limitation(ins_handle, network_interface)
    # limit_bandwidth.limit_bandwidth(ins_handle, bandwidth, p2p_port, network_interface)

    docker_run_command = (
        "sudo docker run -d --name {}{} ".format(container, node_id)
        + " ".join(parameters)
        + " {}".format(image)
    )       
    server_utility.run_cmd_in_ins(ins_handle, docker_run_command, True)
    ins_handle.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]
   
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/{}/exper_{}/nodes.json".format(protocol, exper_id))
    
    image = nodes_config["image"]
    container = nodes_config["container"]
    network_interface = nodes_config["network_interface"]

    tds = []
    
    for instance in nodes_config["instances"]:
        t = threading.Thread(target=start_nodes, args=(instance, exper_id, image, container, network_interface))
        t.start()
        t.join()
