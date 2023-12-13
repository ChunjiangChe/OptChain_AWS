import json
import logging
import paramiko

# set the log
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
    print("Running: {}".format(cmd))
    stdin, stdout, stderr = ins.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print("Output: {}".format(output))
    print("Error: {}".format(error))
    return output, error


def get_docker_logs(ins, container_name, ip, store_or_not):
    command = f"sudo docker logs {container_name}"
    output, error = run_cmd_in_ins(ins, command)
    if store_or_not:
        log_file_path = f"./exec_log/{ip}_{container_name}_logs.txt"
        with open(log_file_path, "w") as log_file:
            log_file.write("output: {}".format(output))
            log_file.write("err: {}".format(error))
        print(f"Logs for {container_name} on server {ip} saved to {log_file_path}")



