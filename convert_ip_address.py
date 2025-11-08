text_us = "98.88.77.65     52.91.51.244    18.234.50.224   3.83.229.255    3.80.74.65      54.221.114.222  3.84.226.244    54.167.45.44    54.144.47.93    54.227.226.166  54.90.205.62    50.17.31.142    204.236.212.14  18.208.224.17   54.227.52.215   54.161.39.105"
text_eu = "35.178.198.216  18.171.187.232  3.10.233.250    52.56.137.11    52.56.44.147    3.10.169.55     18.130.227.55   3.8.40.189      18.170.34.73    52.56.216.128   3.8.238.213     3.10.143.111    35.178.198.90   35.177.45.150   35.176.179.189  18.130.2.2"
text_ap = "43.207.119.28   18.181.167.9    3.112.151.78    57.181.31.27    52.199.192.24   13.230.189.90   35.72.14.91     18.183.102.158  3.112.226.196   18.183.233.59   18.181.174.227  54.249.155.117  18.183.76.101   43.206.194.21   3.112.213.154   54.95.116.238"
text_sa = "15.228.122.73   15.229.255.61   15.228.90.202   56.125.175.133  56.124.20.175   18.231.7.16     18.230.213.20   15.228.214.203  15.228.219.212  56.125.88.114   15.228.173.137  56.125.186.33   15.228.63.234   54.94.94.160    18.230.198.63   15.228.69.246"
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