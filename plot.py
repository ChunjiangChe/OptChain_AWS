import matplotlib.pyplot as plt
import sys
import os
import server_utility
from datetime import datetime

if __name__ == "__main__":
    exper_id = sys.argv[1]
    iteration = sys.argv[2]

    folder_path = "./img/exper_{}/iter_{}/".format(exper_id, iteration)
    folder_exit = os.path.exists(folder_path)
    if not folder_exit:
        os.makedirs(folder_path)
        print("create img folder")
    else:
        print("exper folder already exits")

    config = server_utility.load_config("./expers/exper_{}/config.json".format(exper_id))
    shard_num = config["shard_num"]
    shard_size = config["shard_size"]

    times_of_nodes = []

    for i in range(shard_num):
        node_id = (i + 1) * shard_size - 1
        node_file_path = "./exper_log/exper_{}/iter_{}/node_{}.txt".format(exper_id, iteration, node_id) 
        f = open(node_file_path, "r")
        content = f.readlines()[0]
        content = content[18:-2]
        splited_content = content.split(",")
        content = [item[1:-1] for item in splited_content]
        forking_rate = content[-1]
        content = content[1:-1]
        times = [item[9:-1] for item in content]
        times_of_nodes.append(times)

    systimes_of_nodes = []
    base_time = datetime.strptime("2030-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    for times in times_of_nodes:
        systimes = [datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in times]
        begin_time = systimes[0]
        if begin_time < base_time:
            base_time = begin_time
        systimes_of_nodes.append(systimes)

    for i in range(len(systimes_of_nodes)):
        systimes = systimes_of_nodes[i]
        seconds = [(systime - base_time).seconds for systime in systimes]
        plt.plot(seconds, range(len(seconds)), label="shard {}".format(i))
    plt.legend()
    #plt.show()
    plt.savefig("./img/exper_{}/iter_{}/result.png".format(exper_id, iteration))
    for i in range(len(systimes_of_nodes)):
        print("Shard {} mines {} blocks".format(i, len(systimes_of_nodes[i])))
               



