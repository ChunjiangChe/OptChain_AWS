import server_utility

if __name__ == "__main__":
    config = server_utility.load_config('config.json')
    for instance in config['instances']:
        ins_handle = server_utility.ssh_connect(instance['ip'], instance['user'], instance['ssh_key'])
        docker_stop_command = "sudo docker stop {}".format(instance['container_name'])
        docker_remove_command = "sudo docker rm {}".format(instance['container_name'])
        server_utility.get_docker_logs(ins_handle, instance['container_name'], instance['ip'], True)
        server_utility.run_cmd_in_ins(ins_handle, docker_stop_command)
        server_utility.run_cmd_in_ins(ins_handle, docker_remove_command)
        ins_handle.close()


