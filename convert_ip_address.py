import json

# 1. Define the new IP data
text_us = "18.215.189.60   35.171.203.150  44.200.197.12   54.147.89.91    98.80.202.203   44.203.205.216  34.234.207.126  100.48.191.222  3.235.51.165    44.223.7.90     100.48.212.154  3.219.234.162   13.220.129.254  3.215.174.130   3.236.188.63    98.92.136.16"
text_eu = "13.41.247.194   18.130.179.86   3.8.151.11      18.170.102.99   3.10.228.203    13.43.109.206   3.8.163.92      35.179.116.19   52.56.166.65    18.175.250.35   18.133.27.132   13.42.14.129    35.179.12.149   3.8.197.92      35.179.185.108  13.42.9.217"
text_ap = "54.199.250.14   13.112.161.107  52.197.73.99    18.183.217.104  52.193.99.38    54.248.46.168   57.180.247.226  35.72.5.83      54.250.159.132  18.177.137.52   18.183.75.132   43.207.3.46     13.114.61.185   54.238.130.153  54.238.213.110  54.238.241.114"
text_sa = "52.67.138.154   54.233.71.60    18.231.110.223  56.124.94.82    18.230.26.43    18.231.36.32    18.230.151.126  15.228.100.151  54.233.247.110  54.233.160.82   54.233.52.58    56.125.145.117  52.67.178.30    18.228.118.21   18.230.76.91    18.231.198.163"

# 2. Create a map linking JSON Region Names to the new text variables
# Note: Key names must match the "region" value in your JSON exactly
ip_updates = {
    "Virginia": text_us,
    "London": text_eu,
    "Tokyo": text_ap,
    "Saopaulo": text_sa
}

file_path = 'instances.json'

try:
    # 3. Read the existing JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # 4. Iterate through instances and update IPs if the region matches
    updated_count = 0
    for instance in data['instances']:
        region_name = instance.get('region')
        
        if region_name in ip_updates:
            # .split() handles tabs and multiple spaces automatically
            new_ips_list = ip_updates[region_name].split()
            instance['ips'] = new_ips_list
            updated_count += 1
            print(f"Updated IPs for region: {region_name}")

    # 5. Write the modified data back to the file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nSuccess! {updated_count} regions updated in {file_path}.")

except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
except json.JSONDecodeError:
    print(f"Error: Failed to decode {file_path}. Check if it is valid JSON.")

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