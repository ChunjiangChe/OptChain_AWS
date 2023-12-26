import server_utility
import sys

def remove_limitation(ins, network_interface):
    cmd = "sudo tc qdisc del dev {} root".format(network_interface)
    server_utility.run_cmd_in_ins(ins, cmd, True)

if __name__=="__main__":
    exper_id = sys.argv[1]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    nodes_config = server_utility.load_config("./expers/exper_{}/nodes.json".format(exper_id))

    network_interface = hyperparameters["network_interface"]

    for instance in nodes_config["instances"]:
        ip = instance["ip"]
        user = instance["user"]
        ssh_key = instance["ssh_key"]
        ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
        remove_limitation(ins_handle, network_interface)
        ins_handle.close()
