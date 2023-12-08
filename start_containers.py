import json
import logging

import paramiko

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("docker_operations.log", mode="a"),
        logging.StreamHandler(),
    ],
)


def load_config(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def ssh_connect(hostname, username, key_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, key_filename=key_path)
    return client


def run_cmd_in_ins(ins, cmd):
    stdin, stdout, stderr = ins.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print("Output: {}".format(output))
    print("Error: {}".format(error))
    return output, error


def get_docker_logs(client, container_name, server_ip):
    command = f"docker logs {container_name}"
    logs = docker_command(client, command)
    # 使用服务器 IP 来命名日志文件
    log_file_path = f"./log/{server_ip}_{container_name}_logs.txt"
    with open(log_file_path, "w") as log_file:
        log_file.write(logs)
    print(f"Logs for {container_name} on server {server_ip} saved to {log_file_path}")


def ConfigueEnv(ins):
    apt_update_cmd = "sudo apt-get update -y"
    apt_install_docker_cmd = "sudo apt install -y docker.io"
    pull_docker_cmd = "sudo docker pull yezzizzey/my-bitcoin-app"
    run_cmd_in_ins(ins, apt_update_cmd)
    run_cmd_in_ins(ins, apt_install_docker_cmd)
    run_cmd_in_ins(ins, pull_docker_cmd)


def main():
    config = load_config("config.json")
    for instance in config["instances"]:
        ins_handle = ssh_connect(instance["ip"], instance["user"], instance["ssh_key"])
        ConfigueEnv(ins_handle)

        # docker_run_command = (
        #     "docker run -d --name {} ".format(server["container_name"])
        #     + " ".join(server["docker_options"])
        #     + " yezzizzey/my-bitcoin-app"
        # )

        ## 获取并保存容器日志，使用服务器 IP 作为文件名的一部分
        # get_docker_logs(client, server["container_name"], server["ip"])

        ins_handle.close()


if __name__ == "__main__":
    main()
