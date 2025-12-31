import json

# 1. Define the new IP data
text_us = "100.31.185.113  44.203.221.36   44.223.93.102   44.193.197.219  44.203.32.101   44.200.203.230  13.223.227.68   3.215.134.231   44.205.19.119   100.31.142.165  3.235.53.64     100.27.34.71    98.92.61.167    44.201.47.179   54.83.238.75    44.204.202.190"
text_eu = "13.43.54.211    13.42.45.225    13.40.195.216   52.56.58.224    35.177.97.115   13.41.79.142    3.8.165.188     13.41.196.203   13.40.236.157   18.130.72.212   52.56.57.79     13.42.105.253   18.133.234.246  13.42.20.252    3.8.188.44      35.178.115.31"
text_ap = "18.181.168.173  54.238.209.16   3.112.248.25    13.230.241.240  3.113.3.24      52.69.192.48    57.180.253.222  52.197.79.101   52.193.178.206  13.230.4.35     18.181.211.57   3.112.212.26    18.183.227.84   13.231.193.190  54.199.167.25   54.249.13.187"
text_sa = "18.231.2.55     18.228.154.73   52.67.155.205   15.228.194.158  18.229.161.38   56.124.103.255  18.228.24.81    18.229.125.6    54.233.16.25    56.124.96.15    54.232.70.32    18.231.115.100  18.231.113.48   56.124.121.193  18.228.14.192   18.230.25.33"

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