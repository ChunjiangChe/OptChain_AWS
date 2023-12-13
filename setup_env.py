import server_utility

def configue_env(ins):
    apt_update_cmd = "sudo apt-get update -y"
    apt_install_docker_cmd = "sudo apt install -y docker.io"
    pull_docker_cmd = "sudo docker pull yezzizzey/my-bitcoin-app"
    server_utility.run_cmd_in_ins(ins, apt_update_cmd)
    server_utility.run_cmd_in_ins(ins, apt_install_docker_cmd)
    server_utility.run_cmd_in_ins(ins, pull_docker_cmd)

def allow_ufw(ins):
    set_ufw_1 = "sudo ufw allow 6000:6100/tcp"
    set_ufw_2 = "sudo ufw allow 7000:7100/tcp"
    server_utility.run_cmd_in_ins(ins, set_ufw_1)
    server_utility.run_cmd_in_ins(ins, set_ufw_2)

def test_command(ins):
    test_cmd = "echo 'hello'"
    server_utility.run_cmd_in_ins(ins, test_cmd)

if __name__ == "__main__":
    config = server_utility.load_config("config.json")
    for instance in config["instances"]:
        ins_handle = server_utility.ssh_connect(instance["ip"], instance["user"], instance["ssh_key"])
        configue_env(ins_handle)
        #allow_ufw(ins_handle)

        #test_command(ins_handle)
        # docker_run_command = (
        #     "docker run -d --name {} ".format(server["container_name"])
        #     + " ".join(server["docker_options"])
        #     + " yezzizzey/my-bitcoin-app"
        # )

        ## 获取并保存容器日志，使用服务器 IP 作为文件名的一部分
        # get_docker_logs(client, server["container_name"], server["ip"])

        ins_handle.close()
