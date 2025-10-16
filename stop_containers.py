import server_utility
import sys
import threading

def rm_all_containers(ip, user, ssh_key):
    ins_handle = server_utility.ssh_connect(ip, user, ssh_key)
    # docker_stop_command = "sudo docker stop {}{}".format(container, node_id)
    # docker_remove_command = "sudo docker rm {}{}".format(container, node_id)
    docker_stop_command = "sudo docker stop $(sudo docker ps -aq)"
    docker_remove_command = "sudo docker rm $(sudo docker ps -aq)"

    #output, error = server_utility.get_docker_logs(ins_handle, container, False)
    #log_file_path = "./exec_log/exper_{}/iter_{}/node_{}.txt".format(exper_id, iteration, node_id)
    #with open(log_file_path, "w") as log_file:
    #    log_file.write("output: {}".format(output))
    #    log_file.write("err: {}".format(error))
    #print("Logs for {} on node {} saved to {}".format(container, node_id, log_file_path))

    server_utility.run_cmd_in_ins(ins_handle, docker_stop_command, True)
    server_utility.run_cmd_in_ins(ins_handle, docker_remove_command, True)
    ins_handle.close()

if __name__ == "__main__":
    hyperparameters = server_utility.load_config("./hyperparameter.json")
    instances_config = server_utility.load_config("instances.json")
    user = instances_config["user"]

    tds = []

    for instance in instances_config['instances']:
        ssh_key = instance["ssh_key"]
        for ip in instance["ips"]:
            t = threading.Thread(target=rm_all_containers, args=(ip, user, ssh_key))
            t.start()
            tds.append(t)
        
    for td in tds:
        td.join()

        


