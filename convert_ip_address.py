import json

# 1. Define the new IP data
text_us = "3.222.189.162   18.207.98.4     3.234.250.53    44.201.53.43    34.205.26.16    44.193.25.38    13.219.252.90   44.211.120.223  35.170.59.12    3.238.15.142    98.84.161.37    44.198.189.171  98.92.46.97     44.195.89.98    3.219.167.15    98.84.42.150"
text_eu = "13.42.103.74    3.8.155.45      13.42.15.174    13.40.225.16    35.177.109.168  3.8.155.11      13.42.49.207    3.8.92.232      18.134.180.20   13.42.44.143    18.170.215.206  35.178.177.98   35.179.185.210  13.41.81.6      35.179.91.126   13.42.50.183"
text_ap = "52.192.81.119   3.112.205.165   3.112.234.121   57.180.248.247  13.113.50.179   57.180.9.150    57.180.23.77    13.115.4.228    3.112.132.35    13.158.133.245  43.207.120.116  52.195.174.39   3.112.15.218    18.183.188.2    54.150.203.3    18.183.165.82"
text_sa = "18.231.10.45    15.228.220.122  54.232.35.145   18.231.88.32    56.124.78.148   56.124.52.133   15.228.228.169  18.228.6.253    18.228.153.127  54.233.34.94    56.124.110.174  18.229.137.203  54.233.49.171   54.232.199.189  56.125.229.180  52.67.239.19"

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