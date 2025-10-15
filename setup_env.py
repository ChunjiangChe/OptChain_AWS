import server_utility
import limit_bandwidth

def configue_env(ins, image):
    apt_update_cmd = "sudo apt-get update -y"
    apt_install_docker_cmd = "sudo apt install -y docker.io"
    pull_docker_cmd = "sudo docker pull {}".format(image)
    server_utility.run_cmd_in_ins(ins, apt_update_cmd, True)
    server_utility.run_cmd_in_ins(ins, apt_install_docker_cmd, True)
    server_utility.run_cmd_in_ins(ins, pull_docker_cmd, True)

def allow_ufw(ins):
    set_ufw_1 = "sudo ufw allow 6000:6100/tcp"
    set_ufw_2 = "sudo ufw allow 7000:7100/tcp"
    server_utility.run_cmd_in_ins(ins, set_ufw_1, True)
    server_utility.run_cmd_in_ins(ins, set_ufw_2, True)

def ban_ip(ins):
    cmd = "sudo ufw deny from 94.102.61.44 to any"
    server_utility.run_cmd_in_ins(ins, cmd, True)



if __name__ == "__main__":
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    instances_config = server_utility.load_config("instances.json")
    user = instances_config["user"]
    for instance in instances_config["instances"]:
        region = instance["region"]
        ssh_key = instance["ssh_key"]
        for ip in instance["ips"]:
            ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
            configue_env(ins_handle, hyperparameters["image"])
        #allow_ufw(ins_handle)
        #limit_bandwidth.limit_bandwidth(ins_handle, instance["bandwidth"], port, config["network_interface"])
            # ban_ip(ins_handle)
            ins_handle.close()
