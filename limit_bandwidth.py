import server_utility

def limit_bandwidth(ins, bandwidth, port, network_interface):
    cmd1 = "sudo tc qdisc add dev {} root handle 1: htb default 2".format(network_interface)
    cmd2 = "sudo tc class add dev {} parent 1: classid 1:1 htb rate 200mbit".format(network_interface)
    cmd3 = "sudo tc class add dev {} parent 1:1 classid 1:2 htb rate 200mbit".format(network_interface)
    cmd4 = "sudo tc class add dev {} parent 1:1 classid 1:3 htb rate {}mbit".format(network_interface, bandwidth)
    cmd5 = "sudo tc filter add dev {} parent 1:0 prio 1 u32 match ip dport {} 0xffff flowid 1:3".format(network_interface, port)
    server_utility.run_cmd_in_ins(ins, cmd1)
    server_utility.run_cmd_in_ins(ins, cmd2)
    server_utility.run_cmd_in_ins(ins, cmd3)
    server_utility.run_cmd_in_ins(ins, cmd4)
    server_utility.run_cmd_in_ins(ins, cmd5)

if __name__ == "__main__":
    bandwidth = 20
    port = 6000
    network_interface = "ens5"
    config = server_utility.load_config("test_config.json")
    for instance in config["instances"]:
        ins_handle = server_utility.ssh_connect(instance["ip"], instance["user"], instance["ssh_key"])
        limit_bandwidth(ins_handle, bandwidth, port, network_interface)
        ins_handle.close()
