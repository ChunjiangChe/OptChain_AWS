import json
import paramiko
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler('docker_operations.log', mode='a'),
                              logging.StreamHandler()])

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def ssh_connect(hostname, key_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='root', key_filename=key_path)
    return client

def docker_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    logging.info(output)

def main():
    config = load_config('config.json')
    for server in config['servers']:
        client = ssh_connect(server['ip'], server['ssh_key'])
        docker_stop_command = "docker stop {}".format(server['container_name'])
        docker_remove_command = "docker rm {}".format(server['container_name'])
        docker_command(client, docker_stop_command)
        docker_command(client, docker_remove_command)
        client.close()

if __name__ == "__main__":
    main()
