import server_utility



if __name__ == "__main__":
    instances_config = server_utility.load_config("instances.json")
    user = instances_config["user"]
    for instance in instances_config["instances"]:
        region = instance["region"]
        ssh_key = instance["ssh_key"]
        print(region)
        for ip in instance["ips"]:
            ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
            #configue_env(ins_handle, hyperparameters["image"])
        #allow_ufw(ins_handle)
        #limit_bandwidth.limit_bandwidth(ins_handle, instance["bandwidth"], port, config["network_interface"])
            server_utility.run_cmd_in_ins(ins_handle, "echo 'Faker'", True)
            ins_handle.close()
