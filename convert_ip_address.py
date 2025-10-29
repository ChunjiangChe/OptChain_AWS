text_us = "13.220.116.72   34.204.44.184   13.220.60.28    3.80.41.51      54.227.120.209  98.89.4.20      54.166.200.210  54.147.22.61    52.90.2.4       52.90.222.210   98.94.13.188    98.93.70.47     34.228.81.94    18.212.99.103   18.208.224.195  54.87.47.49"
text_eu = "18.169.170.51   35.177.144.17   18.175.139.33   35.178.176.123  13.40.42.204    18.134.151.12   3.10.116.218    35.176.167.198  18.171.153.211  13.40.130.27    3.8.3.29        13.40.23.34     18.130.241.211  3.9.114.233     18.170.97.220   18.171.157.152"
text_ap = "18.179.119.138  18.183.221.242  52.199.241.3    13.231.202.86   13.230.181.137  54.199.229.177  18.183.169.15   57.180.56.188   13.112.176.203  52.194.189.120  52.198.24.82    3.113.17.174    54.178.123.157  54.178.49.95    43.207.109.152  35.77.94.216"
text_sa = "56.125.23.161   56.125.2.102    56.125.102.194  56.125.22.244   56.124.73.45    54.94.3.187     15.228.169.123  56.125.77.146   56.125.4.20     54.94.96.176    15.228.176.236  15.228.37.21    15.228.80.205   56.125.233.132  56.125.81.232   15.228.169.243"
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