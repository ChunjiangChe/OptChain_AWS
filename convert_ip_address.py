import json

# 1. Define the new IP data
text_us = "35.170.51.132   100.48.90.58    44.195.59.83    34.232.46.25    44.201.37.200   98.80.209.107   98.92.216.18    44.213.107.104  3.234.143.202   3.239.171.65    3.237.180.206   98.92.143.68    35.170.33.133   44.195.82.151   3.238.91.231    98.92.37.160"
text_eu = "18.170.229.161  18.175.159.43   18.134.181.54   18.130.145.71   18.175.150.1    18.175.229.163  35.179.90.2     13.41.65.3      13.41.198.126   13.41.188.7     18.175.159.41   18.175.156.181  13.40.191.158   35.177.243.90   18.130.30.208   3.8.159.117"
text_ap = "52.195.10.130   3.112.34.163    52.194.247.229  18.179.136.166  52.192.156.110  54.178.86.91    13.231.242.81   52.68.184.47    43.206.218.200  13.158.129.46   13.114.251.203  57.180.9.14     3.112.208.183   54.168.136.228  54.250.162.22   52.197.143.185"
text_sa = "15.228.242.24   15.228.231.170  18.228.195.5    18.228.241.5    56.125.220.94   56.124.79.88    15.228.232.52   56.125.173.235  18.230.56.142   56.124.75.34    54.207.105.83   18.231.190.14   18.230.65.54    56.124.98.161   56.125.9.184    18.230.76.232"

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