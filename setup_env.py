import server_utility
import limit_bandwidth
import threading

def configue_env(ins, image):
    apt_update_cmd = "sudo apt-get update -y"
    apt_install_docker_cmd = "sudo apt install -y docker.io"
    pull_docker_cmd = "sudo docker pull {}".format(image)
    server_utility.run_cmd_in_ins(ins, apt_update_cmd, True)
    server_utility.run_cmd_in_ins(ins, apt_install_docker_cmd, True)
    server_utility.run_cmd_in_ins(ins, pull_docker_cmd, True)

def allow_ufw(ins, ports):
    for port in ports:
        set_ufw = "sudo ufw allow {}/tcp".format(port)
        server_utility.run_cmd_in_ins(ins, set_ufw, True)

def ban_ip(ins):
    cmd = "sudo ufw deny from 94.102.61.44 to any"
    server_utility.run_cmd_in_ins(ins, cmd, True)

def install_limit_bandwidth_script(ins):
    sftp = ins.open_sftp()
    sftp.put("limit_AWS_bandwidth.sh", "./limit_AWS_bandwidth.sh")
    cmd = "sudo chmod +x limit_AWS_bandwidth.sh"
    server_utility.run_cmd_in_ins(ins, cmd, True)

def setup_node(ip, user, ssh_key, ports, image):
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    # configue_env(ins_handle, hyperparameters["image"])
    # allow_ufw(ins_handle, ports)

    # ban_ip(ins_handle)
    install_limit_bandwidth_script(ins_handle)
    ins_handle.close()



if __name__ == "__main__":
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    instances_config = server_utility.load_config("instances.json")
    user = instances_config["user"]
    p2p_ports = hyperparameters["p2p_ports"]
    api_ports = hyperparameters["api_ports"]
    ports = p2p_ports + api_ports
    image = hyperparameters["image"]
    tds = []
    for instance in instances_config["instances"]:
        region = instance["region"]
        ssh_key = instance["ssh_key"]
        for ip in instance["ips"]:
            t = threading.Thread(target=setup_node, args=(ip, user, ssh_key, ports, image))
            t.start()
            tds.append(t)
    for td in tds:
        td.join()
