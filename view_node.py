import server_utility

if __name__ == "__main__":
    config = server_utility.load_config('config.json')
    for instance in config['instances']:
        ins_handle = server_utility.ssh_connect(instance['ip'], instance['user'], instance['ssh_key'])
        server_utility.get_docker_logs(ins_handle, config['container'], instance['ip'], False, True)
        ins_handle.close()
