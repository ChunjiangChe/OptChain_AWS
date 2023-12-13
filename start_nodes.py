import server_utility

if __name__ == "__main__":
    config = server_utility.load_config("config.json")
    for instance in config["instances"]:
        ins_handle = server_utility.ssh_connect(instance["ip"], instance["user"], instance["ssh_key"])
        docker_run_command = (
            "sudo docker run -d --name {} ".format(instance["container_name"])
            + " ".join(instance["docker_options"])
            + " yezzizzey/my-bitcoin-app"
        )       
        server_utility.run_cmd_in_ins(ins_handle, docker_run_command)
        ins_handle.close()
