import server_utility

if __name__ == "__main__":
    config = server_utility.load_config("config.json")
    for instance in config["instances"]:
        ins_handle = server_utility.ssh_connect(instance["ip"], instance["user"], instance["ssh_key"])
        docker_run_command = (
            "sudo docker run -d --name {} ".format(config["container"])
            + " ".join(instance["parameters"])
            + " {}".format(config["image"])
        )       
        server_utility.run_cmd_in_ins(ins_handle, docker_run_command, True)
        ins_handle.close()
