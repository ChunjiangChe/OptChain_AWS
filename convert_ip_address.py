text_us = "54.89.167.143   34.226.196.238  54.91.115.243   54.91.175.10    54.227.109.69   52.23.172.41    98.94.91.136    54.147.180.79   52.23.184.189   54.221.188.120  98.89.3.72      54.84.65.122    54.242.69.187   52.207.225.63   54.84.233.73    98.84.100.23"
text_eu = "35.178.114.225  3.8.77.118      13.40.23.171    18.130.150.75   18.171.210.184  3.9.134.129     3.8.136.97      18.171.243.134  3.10.152.215    3.8.77.203      18.171.183.143  18.132.2.193    3.10.56.2       18.134.164.181  3.8.141.147     3.9.174.177"
text_ap = "3.112.230.62    54.95.23.202    57.180.248.202  54.178.91.163   54.199.124.56   13.112.50.10    52.68.73.193    13.112.162.32   54.250.214.217  52.198.222.112  18.183.184.22   52.192.73.94    52.198.191.174  43.206.231.18   57.180.244.75   57.181.29.218"
text_sa = "56.125.111.134  54.232.69.180   18.231.136.181  15.228.230.98   56.125.5.235    56.124.13.11    56.125.24.38    56.125.234.213  15.229.248.184  56.125.23.20    18.230.203.103  56.124.14.6     56.124.86.100   15.229.152.151  18.230.198.145  15.228.212.76"
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