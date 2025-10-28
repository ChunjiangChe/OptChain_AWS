text_us = "3.95.58.7       18.209.70.30    54.163.18.36    54.234.52.93    13.221.128.252  100.27.198.162  13.222.174.149  54.198.237.35   54.90.181.24    98.93.228.239   13.221.84.48    54.82.38.99     54.90.234.249   54.209.189.236  98.93.227.120   44.223.65.34"
text_eu = "13.40.43.80     18.171.186.113  35.176.146.33   18.171.153.214  3.9.146.179     18.135.16.66    18.130.24.143   18.130.247.225  13.40.18.23     18.171.56.101   3.9.10.241      3.10.203.207    18.171.159.252  18.130.247.115  13.40.97.220    18.175.136.172"
text_ap = "52.194.187.123  54.199.184.58   52.199.119.201  3.112.5.237     13.113.104.35   35.72.14.168    18.181.212.17   18.183.213.233  52.192.105.149  57.180.60.23    54.250.244.129  13.231.232.30   52.195.174.6    13.114.45.216   43.207.75.100   54.199.75.13"
text_sa = "15.228.83.14    15.228.208.92   15.229.148.48   56.124.16.226   54.207.161.178  18.230.193.45   56.125.23.204   15.229.215.224  15.228.80.236   18.231.134.169  177.71.237.137  18.230.189.140  15.229.146.137  54.233.252.77   18.231.169.17   56.125.27.208"
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