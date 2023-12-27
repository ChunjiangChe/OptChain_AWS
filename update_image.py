import server_utility
import limit_bandwidth

def update_image(ins, image):
    pull_docker_cmd = "sudo docker pull {}".format(image)
    server_utility.run_cmd_in_ins(ins, pull_docker_cmd, True)

if __name__ == "__main__":
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    instances_config = server_utility.load_config("instances.json")
    user = instances_config["user"]
    for instance in instances_config["instances"]:
        region = instance["region"]
        ssh_key = instance["ssh_key"]
        for ip in instance["ips"]:
            ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
            update_image(ins_handle, hyperparameters["image"])
        #allow_ufw(ins_handle)
        #limit_bandwidth.limit_bandwidth(ins_handle, instance["bandwidth"], port, config["network_interface"])

            ins_handle.close()
