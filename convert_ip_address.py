text_us = "54.147.23.89    18.232.176.248  3.80.61.128     3.85.198.73     54.162.139.209  13.221.88.143   3.89.63.255     34.227.75.20    13.220.115.148  13.222.191.176  3.85.61.243     3.87.169.124    13.221.116.250  35.172.212.106  54.81.240.59    34.233.123.104"
text_eu = "13.40.65.49     13.40.96.117    18.134.151.37   18.135.98.57    3.10.209.113    35.176.108.198  35.178.16.203   18.130.58.71    13.40.151.93    13.40.151.228   18.171.173.196  52.56.136.98    18.132.207.89   3.9.180.168     18.134.249.111  18.171.207.173"
text_ap = "13.230.4.129    13.112.84.64    52.194.226.118  13.115.200.39   54.64.111.160   57.180.44.26    54.95.57.151    176.34.32.169   18.181.165.38   13.231.219.57   52.194.230.209  3.113.27.235    54.250.171.167  18.182.8.233    13.231.154.175  18.183.107.136"
text_sa = "56.125.77.68    15.228.175.76   15.229.215.127  54.233.40.242   18.230.222.231  56.125.103.194  15.228.195.141  54.207.137.211  15.229.25.143   15.229.153.67   15.229.207.220  15.229.159.51   15.229.21.210   56.124.12.253   56.125.234.61   56.125.171.67"
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