import server_utility
import remove_limitation
import threading
import sys

def limit_bandwidth_old(ins, bandwidth, port, network_interface):
    cmd1 = "sudo tc qdisc add dev {} root handle 1: htb default 2".format(network_interface)
    cmd2 = "sudo tc class add dev {} parent 1: classid 1:1 htb rate 200mbit".format(network_interface)
    cmd3 = "sudo tc class add dev {} parent 1:1 classid 1:2 htb rate 200mbit".format(network_interface)
    cmd4 = "sudo tc class add dev {} parent 1:1 classid 1:3 htb rate {}mbit".format(network_interface, bandwidth)
    cmd5 = "sudo tc filter add dev {} parent 1:0 prio 1 u32 match ip dport {} 0xffff flowid 1:3".format(network_interface, port)
    server_utility.run_cmd_in_ins(ins, cmd1, True)
    server_utility.run_cmd_in_ins(ins, cmd2, True)
    server_utility.run_cmd_in_ins(ins, cmd3, True)
    server_utility.run_cmd_in_ins(ins, cmd4, True)
    server_utility.run_cmd_in_ins(ins, cmd5, True)

def limit_download_only(ins, iface, port, bw_mbit):
    cmd1 = "echo 'limit bandwidth'"
    server_utility.run_cmd_in_ins(ins, cmd1, True)
    cmd2 = "sudo ./limit_AWS_bandwidth.sh apply --port {} --rate {}mbit".format(port, bw_mbit)
    server_utility.run_cmd_in_ins(ins, cmd2, True)


def limit_bandwidth(ip, user, ssh_key, bandwidth, p2p_port, network_interface):
    print(bandwidth)
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    print("connected to {}".format(ip))
    limit_download_only(ins_handle, network_interface, p2p_port, bandwidth)



    # limit_bandwidth_old(ins_handle, bandwidth, p2p_port, network_interface)
    # remove_limitation.remove_limitation(ins_handle, network_interface)
    ins_handle.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python limit_bandwidth.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    config = server_utility.load_config("./expers/{}/exper_{}/nodes.json".format(protocol, exper_id))
    
    network_interface = config["network_interface"]
    tds = []
    for instance in config["instances"]:
        t = threading.Thread(target=limit_bandwidth, args=(instance["ip"], instance["user"], instance["ssh_key"], instance["bandwidth"], instance["p2p_port"], network_interface))
        t.start()
        tds.append(t)
    for t in tds:
        t.join()
