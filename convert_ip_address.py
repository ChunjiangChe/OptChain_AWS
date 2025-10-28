text_us = "98.93.33.75     3.91.33.187     54.226.16.157   54.234.72.52    35.175.221.157  54.234.35.233   3.88.229.97     13.218.34.194   54.227.78.237   13.218.91.115   54.234.21.161   18.234.220.212  98.88.249.47    54.83.155.45    54.221.130.124  54.226.116.82"
text_eu = "18.130.255.76   35.179.152.195  18.132.114.211  35.179.132.53   35.178.167.112  35.179.145.121  18.171.52.24    18.133.239.101  35.179.134.28   35.178.250.247  18.132.196.254  18.130.182.250  35.178.212.31   18.134.229.96   3.10.169.93     18.170.77.188"
text_ap = "13.230.237.39   52.194.229.143  52.195.229.151  54.178.12.176   54.199.125.19   52.68.49.41     54.178.186.44   54.248.28.234   18.183.141.244  54.199.31.27    54.199.145.53   52.198.113.59   43.207.1.123    13.115.229.152  54.199.116.76   13.230.168.150"
text_sa = "56.125.174.42   15.228.81.239   18.230.223.236  18.228.17.89    15.228.173.162  18.231.134.9    18.230.223.76   56.125.79.140   18.230.215.34   56.124.117.224  15.228.179.1    15.228.122.68   56.125.94.148   56.125.24.81    18.231.127.181  56.125.133.210"
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