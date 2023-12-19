import server_utility

def remove_limitation(ins, network_interface):
    cmd = "sudo tc qdisc del dev {} root".format(network_interface)
    server_utility.run_cmd_in_ins(ins, cmd)

if __name__=="__main__":
    network_interface = "ens5"
    config = server_utility.load_config("test_config.json")
    for instance in config["instances"]:
        ins_handle = server_utility.ssh_connect(instance["ip"], instance["user"], instance["ssh_key"])
        remove_limitation(ins_handle, network_interface)
        ins_handle.close()
