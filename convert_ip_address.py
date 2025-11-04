text_us = "23.22.131.186   34.227.191.189  18.212.225.61   98.93.222.172   54.234.129.78   54.163.9.38     52.91.138.108   54.198.194.181  3.88.42.252     54.163.56.59    54.196.208.218  54.242.109.228  54.221.185.11   54.227.97.81    54.160.170.222  107.22.98.49"
text_eu = "18.171.209.200  3.8.8.179       3.9.10.198      3.9.169.189     18.175.137.37   18.134.228.234  18.171.157.231  35.178.200.253  18.175.217.184  35.178.201.15   18.171.162.52   13.40.129.47    18.133.157.171  13.40.61.28     18.171.244.123  18.130.247.8"
text_ap = "13.114.103.78   54.250.102.89   13.113.67.138   13.158.141.174  43.207.109.223  18.183.126.148  54.95.197.66    54.238.237.192  57.181.35.160   3.113.17.80     54.249.61.58    35.72.5.153     52.192.21.125   18.183.85.76    52.195.211.125  18.177.138.92"
text_sa = "15.228.124.68   15.228.80.153   18.230.119.158  15.229.154.207  56.124.18.100   15.229.17.187   18.231.169.4    56.125.183.247  56.124.13.54    56.125.63.149   15.228.80.21    56.125.88.54    54.207.237.163  18.230.198.3    18.231.130.220  54.232.28.37"
# Split by whitespace
texts = [text_us, text_eu, text_ap, text_sa]
regions = ["virginia", "london", "japan", "saopaulo"]

for i in range(len(texts)):
    text = texts[i]
    region = regions[i]
    ips = text.split()
    # Format as JSON-like structure
    formatted = '"ips": [\n'
    formatted += ',\n'.join([f'    "{ip}"' for ip in ips])
    formatted += '\n]'
    print("Regions:", region)
    print(formatted)

"""
aws ec2 describe-instances --region us-east-1 --query "Reservations[*].Instances[*].PublicIpAddress" --output text
echo
aws ec2 describe-instances --region eu-west-2 --query "Reservations[*].Instances[*].PublicIpAddress" --output text
echo
aws ec2 describe-instances --region ap-northeast-1 --query "Reservations[*].Instances[*].PublicIpAddress" --output text 
echo
aws ec2 describe-instances --region sa-east-1 --query "Reservations[*].Instances[*].PublicIpAddress" --output text 
echo
"""