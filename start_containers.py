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

def ssh_connect(hostname, username, key_path, passwd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=passwd)
    return client

def run_command_in_server(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    logging.info(output)
    return output

def docker_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    logging.info(output)
    return output

def get_docker_logs(client, container_name, server_ip):
    command = f"docker logs {container_name}"
    logs = docker_command(client, command)
    # 使用服务器 IP 来命名日志文件
    log_file_path = f"{server_ip}_{container_name}_logs.txt"
    with open(log_file_path, 'w') as log_file:
        log_file.write(logs)
    print(f"Logs for {container_name} on server {server_ip} saved to {log_file_path}")

def main():
    config = load_config('config.json')
    for server in config['servers']:
        client = ssh_connect(server['ip'], server['user'], server['ssh_key'], server['passwd'])
        test_command = "touch test.txt"
        run_command_in_server(client, test_command)
        #docker_run_command = "docker run -d --name {} ".format(server['container_name']) + " ".join(server['docker_options']) + " yezzizzey/my-bitcoin-app"
        #docker_command(client, docker_run_command)
        #
        ## 获取并保存容器日志，使用服务器 IP 作为文件名的一部分
        get_docker_logs(client, server['container_name'], server['ip'])

        client.close()

if __name__ == "__main__":
    main()
