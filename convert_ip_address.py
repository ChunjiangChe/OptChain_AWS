import json

# 1. Define the new IP data
text_us = "98.81.31.176    13.217.128.36   98.84.29.208    44.192.70.182   3.236.170.210   18.207.250.160  44.220.182.237  44.223.46.51    3.231.217.194   100.48.60.1     3.210.181.128   3.236.101.202   18.207.224.110  44.221.42.144   18.232.54.176   100.48.78.207"
text_eu = "13.41.190.207   35.178.29.146   35.178.177.102  13.42.32.128    52.56.59.101    3.8.207.240     13.41.192.178   13.40.223.168   13.41.53.17     35.179.116.181  13.40.82.140    35.179.131.79   18.169.52.201   3.9.29.91       18.134.205.47   13.41.201.66"
text_ap = "54.168.237.53   13.114.20.229   54.199.229.245  35.78.211.38    43.207.182.155  52.195.160.214  3.112.51.82     18.181.208.204  43.207.177.226  13.115.56.119   52.195.81.32    43.206.122.244  54.199.154.208  35.78.249.61    35.78.189.25    13.114.88.14"
text_sa = "54.232.50.17    54.233.209.4    18.228.138.131  56.124.107.52   54.233.107.176  18.230.60.34    18.230.26.190   56.125.229.155  15.229.6.140    52.67.42.130    18.231.119.168  18.231.121.42   54.207.150.181  18.231.76.70    18.231.71.39    18.228.59.241"

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