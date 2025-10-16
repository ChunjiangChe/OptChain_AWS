import server_utility
import limit_bandwidth
import threading

def update_image(ip, user, ssh_key, image):
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    pull_docker_cmd = "sudo docker pull {}".format(image)
    server_utility.run_cmd_in_ins(ins_handle, pull_docker_cmd, True)
    ins_handle.close()

if __name__ == "__main__":
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    instances_config = server_utility.load_config("instances.json")
    user = instances_config["user"]
    tds = []
    for instance in instances_config["instances"]:
        region = instance["region"]
        ssh_key = instance["ssh_key"]
        for ip in instance["ips"]:
            t = threading.Thread(target=update_image, args=(ip, user, ssh_key, hyperparameters["image"]))
            t.start()
            tds.append(t)
    for td in tds:  
        td.join()
            
            
