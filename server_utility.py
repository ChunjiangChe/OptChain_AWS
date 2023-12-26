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

def write_config(file_path, dic):
    with open(file_path, "w") as file:
        return json.dump(dic, file)


def ssh_connect(hostname, username, key_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, key_filename=key_path)
    return client


def run_cmd_in_ins(ins, cmd, if_print):
    print("Running: {}".format(cmd))
    stdin, stdout, stderr = ins.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if if_print:
        print("Output: {}".format(output))
        print("Error: {}".format(error))
    return output, error


def get_docker_logs(ins, container_name, if_print):
    command = f"sudo docker logs {container_name}"
    output, error = run_cmd_in_ins(ins, command, if_print)
    return output, error
        


