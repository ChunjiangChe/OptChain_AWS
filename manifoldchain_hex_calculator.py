import numpy as np
import math

def cal_binary(binary_num):
    num = int(binary_num, 16)
    print("%x\n"%num)

    mult_result = num * 2
    print("%x\n"%mult_result)
    
    div_result = mult_result // 2
    print("%x\n"%div_result)

def cal_target(bandwidth, base_bandwidth, base_target, block_size, propagation_delay):
    base_target = int(base_target, 16)
    base_delay = (block_size*1024*8)/(base_bandwidth*1000000) + propagation_delay

    delay = (block_size*1024*8)/(bandwidth*1000000) + propagation_delay
    print("scale:{}".format(base_delay / delay))
    scale = int(base_delay * 100 / delay)
    print("scale:{}".format(scale))
    target = base_target * scale // 100
    return target


def cal_err_probability():
    lambda_s = 0.00244941
    #lambda_i = 0.0016667
    gamma = 0
    lambda_i = lambda_s * gamma
    rho_i = 0
    rho = 0.9
    m = 1000000000
    k = 14
    block_size = 547.14 #KB
    bandwidth_i = 20 #Mbps
    propagation_delay = 0.1 #s 100ms
    transmission_delay = (block_size*1024*8)/(20*1000000)
    delay = propagation_delay + transmission_delay
    
    p_i = (lambda_i*rho_i + m*lambda_s*rho) / (lambda_i + m*lambda_s) * math.exp(-(lambda_i+lambda_s)*delay)
    print("p_i: {}".format(p_i))
    err_pro = (2 + 2*math.sqrt(p_i/(1-p_i)))*pow(4*p_i*(1-p_i), k)
    #print(2 + 2*math.sqrt(p_i/(1-p_i)))
    #print(4*p_i*(1-p_i))
    print("Error probability: {}".format(err_pro))

    delay = delay / 2
    gamma = 1
    lambda_i = lambda_s * gamma
    p_i = (lambda_i*rho_i + m*lambda_s*rho) / (lambda_i + m*lambda_s) * math.exp(-(lambda_i+lambda_s)*delay)
    print("p_i: {}".format(p_i))
    err_pro = (2 + 2*math.sqrt(p_i/(1-p_i)))*pow(4*p_i*(1-p_i), k)
    #print(2 + 2*math.sqrt(p_i/(1-p_i)))
    #print(4*p_i*(1-p_i))
    print("Error probability: {}".format(err_pro))

def cal_targets():
    block_size = 24540 #KB
    propagation_delay = 0.1
    base_bandwidth = 14
    base_diff = "0000000450ed6300450ed6300450ed6300450ed6300450ed6300450ed6300450"
    bandwidths = [14, 22, 34, 135]
    for i in range(len(bandwidths)):
        target = cal_target(bandwidths[i], base_bandwidth, base_diff, block_size, propagation_delay)
        target_hex = f"{target:0{len(base_diff)}x}"
        print("Bandwidth: {} Mbps, Target diff: {}".format(bandwidths[i], target_hex))


if __name__ == "__main__":
    #cal_err_probability()
    cal_targets()


