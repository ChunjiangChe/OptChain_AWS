import numpy as np
import matplotlib.pyplot as plt
import numeric


if __name__ == "__main__":
    mu_min = 30
    mu_max = 50
    mu_step = 1
    sigma_min = 5
    sigma_max = 10
    sigma_step = 1
    tail_mu = 5
    tail_sigma = 1
    normal_weight = 0.9
    tail_weight = 0.1
    sample_num = 25
    iteration = 1000
    shard_num = 5
    shard_size = 5
    block_size = 547.14
    propagation_delay = 0.1


    if_plot = False
    scales_vary_sigma = []
    for sigma in range(sigma_min, sigma_max, sigma_step):
        average_scales = []
        for mu in range(mu_min, mu_max, mu_step):
            groups = []
            for i in range(iteration):
                # normal_samples = np.random.normal(mu, sigma, sample_num)
                # samples = normal_samples
                normal_samples = np.random.normal(mu, sigma, int(sample_num*normal_weight))
                tail_samples = np.random.normal(tail_mu, tail_sigma, sample_num - int(sample_num*normal_weight))
                samples = np.concatenate((normal_samples, tail_samples))
                samples.sort()
                groups.append(samples)
            average_samples = []
            for i in range(sample_num):
                vertical_samples = []
                for j in range(iteration):
                    vertical_samples.append(groups[j][i])
                average_samples.append(vertical_samples)
            average_samples = [np.mean(samples) for samples in average_samples]

            print(average_samples)
            # if not if_plot:
            #     plt.xlabel("node_id")
            #     plt.ylabel("bandwidth")
            #     plt.plot(range(len(average_samples)), average_samples)
            #     if_plot = True

            splited_bandwidths = np.array_split(average_samples, shard_num)
            base_bandwidth = splited_bandwidths[0][0]
            scales = []
            for i in range(shard_num):
                bandwidth = splited_bandwidths[i][0]
                scale = numeric.cal_scale(bandwidth, base_bandwidth, block_size, propagation_delay)
                scales.append(scale)
            #print(scales)
            average_scale = np.mean(scales)
            print("average improvement {} at sigma: {}".format(average_scale, sigma))
            average_scales.append(average_scale)
        scales_vary_sigma.append(average_scales)
    for i in range(len(scales_vary_sigma)):
        scales = scales_vary_sigma[i]
        sigma = range(sigma_min, sigma_max, sigma_step)[i]
        plt.plot(range(mu_min, mu_max, mu_step), scales, label="sigma: {}".format(sigma))
    plt.xlabel("mu")
    plt.ylabel("improvements")
    plt.legend()
    plt.show()
