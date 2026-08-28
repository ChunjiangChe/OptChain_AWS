import json

# 1. Define the new IP data
text_us = "13.222.213.118  52.70.208.133   18.208.164.225  35.173.230.56   52.55.239.189   44.203.86.203   44.212.56.18    3.82.99.220     34.238.80.123       34.201.113.164  34.227.112.78   52.23.183.203   34.205.73.247   100.62.119.69   34.230.42.17    184.192.225.96"
text_eu = "18.133.122.74   51.24.113.145   3.8.86.89       13.40.10.113    18.132.202.98   13.40.52.35     18.134.10.158   13.40.169.62    13.135.95.7         35.178.178.184  35.177.152.189  16.61.15.198    18.134.129.224  18.175.214.90   18.132.3.65     3.8.95.125"
text_ap = "3.113.243.233   35.72.183.205   35.77.32.8      57.183.36.81    35.75.17.203    13.196.24.231   18.181.235.62   13.196.180.141  35.73.128.213       13.196.187.251  35.79.15.209    3.115.214.176   18.179.55.228   13.158.67.111   13.196.194.179  18.183.128.35"
text_sa = "54.20.126.231   56.125.170.249  18.231.139.193  15.228.169.241  56.124.90.28    15.228.85.198   15.229.21.108   56.125.88.53    54.233.9.61         54.207.218.14   56.125.133.255  56.124.24.61    15.229.208.191  56.125.24.241   56.124.12.149   18.231.182.62"

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