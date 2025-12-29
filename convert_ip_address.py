import json

# 1. Define the new IP data
text_us = "100.29.185.69   100.29.191.229  44.223.77.102   3.238.32.124    18.207.183.195  34.234.223.178  3.236.188.128   44.200.133.0    98.82.25.229    13.219.209.18   44.200.72.59    44.200.206.120  3.239.219.146   44.195.67.43    44.195.32.28    44.223.74.15"
text_eu = "3.8.147.71      13.42.11.138    18.175.144.106  35.179.151.213  13.43.110.51    13.42.31.118    13.41.240.174   13.40.229.215   13.40.228.81    18.134.182.114  13.41.54.222    13.41.69.55     18.169.18.161   13.43.88.87     35.177.4.118    18.169.189.131"
text_ap = "52.196.66.8     13.231.37.124   18.183.169.96   18.177.136.228  54.168.242.62   57.180.60.75    54.178.90.193   13.231.161.64   18.183.107.200  3.112.68.214    54.250.106.15   3.112.172.6     3.112.246.230   3.112.214.40    54.64.178.183   57.181.28.212"
text_sa = "54.233.5.253    56.124.94.44    56.125.173.30   18.228.59.20    52.67.62.54     15.228.185.10   54.207.234.182  52.67.73.6      18.228.238.214  18.230.226.76   54.207.239.170  52.67.215.160   56.125.214.52   54.94.49.13     52.67.206.125   56.124.110.169"

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