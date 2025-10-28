import server_utility
import sys
import threading

def remove_limitation(ip, user, ssh_key, network_interface):
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    clear_download_only(ins_handle, network_interface)

def clear_download_only(ins, network_interface):
    """
    清理仅限下行的规则；不删除真实网卡，只删除 qdisc 和 ifb0。
    """
    iface = network_interface
    cmds = [
        f"sudo tc qdisc del dev {iface} ingress 2>/dev/null || true",
        "sudo tc qdisc del dev ifb0 root 2>/dev/null || true",
        "sudo tc qdisc del dev ifb0 ingress 2>/dev/null || true",
        "sudo ip link set dev ifb0 down 2>/dev/null || true",
        "sudo ip link delete ifb0 type ifb 2>/dev/null || true",
        f"sudo tc qdisc show dev {iface} || true",
        "sudo tc qdisc show dev ifb0 || true",
    ]
    for c in cmds:
        server_utility.run_cmd_in_ins(ins, c, True)

if __name__=="__main__":

    if len(sys.argv) < 3:
        print("Usage: python remove_limitation.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    hyperparameters = server_utility.load_config("./hyperparameter.json")
    config = server_utility.load_config("./expers/{}/exper_{}/nodes.json".format(protocol, exper_id))

    network_interface = config["network_interface"]
    tds = []
    for instance in config["instances"]:
        print(instance["bandwidth"])
        t = threading.Thread(target=remove_limitation, args=(instance["ip"], instance["user"], instance["ssh_key"], network_interface))
        t.start()
        tds.append(t)
    for t in tds:
        t.join()
