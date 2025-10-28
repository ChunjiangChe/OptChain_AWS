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

def limit_download_only(ins, iface, port, bw_mbit, proto='tcp', r2q=200, quantum=3000):
    """
    只限制机器A的下行（ingress），不限制上行。
    - iface: 如 'ens5'
    - port:  如 6042
    - bw_mbit: 限速值（Mbps）
    - proto: 'tcp' 或 'udp'
    """
    script = f"""bash -lc '
set -euo pipefail

IFACE="{iface}"
PORT="{port}"
BW="{int(bw_mbit)}"
PROTO="{proto}"
R2Q="{int(r2q)}"
QUANTUM="{int(quantum)}"

# 0) 预检查
command -v tc >/dev/null 2>&1 || {{ echo "[!] tc not found. Install iproute2"; exit 1; }}

# 1) 清理旧规则（不删除真实网卡）
sudo tc qdisc del dev "$IFACE" ingress 2>/dev/null || true
sudo tc qdisc del dev ifb0 root 2>/dev/null || true
sudo tc qdisc del dev ifb0 ingress 2>/dev/null || true
sudo ip link set dev ifb0 down 2>/dev/null || true
sudo ip link delete ifb0 type ifb 2>/dev/null || true

# 2) 显式加载需要的模块（部分内核默认不自动加载）
sudo modprobe ifb numifbs=1
sudo modprobe sch_ingress 2>/dev/null || true
sudo modprobe act_mirred  2>/dev/null || true

# 3) 创建并启用 ifb0
sudo ip link add ifb0 type ifb 2>/dev/null || true
sudo ip link set ifb0 up

# 4) 在真实网卡上挂 ingress，重定向匹配端口的入站流量到 ifb0
sudo tc qdisc add dev "$IFACE" handle ffff: ingress 2>/dev/null || true

# 协议号：tcp=6, udp=17
if [ "$PROTO" = "tcp" ]; then PROTO_NUM=6; else PROTO_NUM=17; fi

# 普通下载（A做服务端）：入站 dport=PORT
sudo tc filter add dev "$IFACE" parent ffff: protocol ip prio 10 u32 \\
  match ip protocol ${{PROTO_NUM}} 0xff match ip dport ${{PORT}} 0xffff \\
  action mirred egress redirect dev ifb0 || true

# 反向测试(-R)（对端做服务端）：入站 sport=PORT
sudo tc filter add dev "$IFACE" parent ffff: protocol ip prio 11 u32 \\
  match ip protocol ${{PROTO_NUM}} 0xff match ip sport ${{PORT}} 0xffff \\
  action mirred egress redirect dev ifb0 || true

# 5) 在 ifb0 上做 HTB 限速
sudo tc qdisc add dev ifb0 root handle 2: htb default 3 r2q "$R2Q"
sudo tc class add dev ifb0 parent 2: classid 2:1 htb rate 200mbit ceil 200mbit quantum "$QUANTUM"
sudo tc class add dev ifb0 parent 2:1 classid 2:3 htb rate "${{BW}}mbit" ceil "${{BW}}mbit" quantum "$QUANTUM"

echo "[i] Applied: IFACE=$IFACE, PORT=$PORT/{proto}, DL_LIMIT=${{BW}}Mbit/s, r2q=$R2Q, quantum=$QUANTUM"

# 6) 打印状态便于核对
sudo tc qdisc show dev "$IFACE" || true
sudo tc filter show dev "$IFACE" parent ffff: || true
sudo tc qdisc show dev ifb0 || true
sudo tc class show dev ifb0 || true
'"""
    server_utility.run_cmd_in_ins(ins, script, True)


# def clear_download_only(ins, iface):
#     # 清理（不删除真实网卡）
#     script = f"""bash -lc '
# set -euo pipefail
# tc qdisc del dev {iface} ingress 2>/dev/null || true
# tc qdisc del dev ifb0 root 2>/dev/null || true
# tc qdisc del dev ifb0 ingress 2>/dev/null || true
# ip link set dev ifb0 down 2>/dev/null || true
# ip link delete ifb0 type ifb 2>/dev/null || true
# tc qdisc show dev {iface} || true
# ip link show ifb0 >/dev/null 2>&1 && tc qdisc show dev ifb0 || echo "(ifb0 not present)"
# '"""
#     server_utility.run_cmd_in_ins(ins, script, True)


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

def limit_bandwidth(ip, user, ssh_key, bandwidth, p2p_port, network_interface):
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    limit_download_only(ins_handle, network_interface, p2p_port, bandwidth)
    # clear_download_only(ins_handle, network_interface)



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
        print(instance["bandwidth"])
        t = threading.Thread(target=limit_bandwidth, args=(instance["ip"], instance["user"], instance["ssh_key"], instance["bandwidth"], instance["p2p_port"], network_interface))
        t.start()
        tds.append(t)
    for t in tds:
        t.join()
