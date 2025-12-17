import json

# 1. Define the new IP data
text_us = "3.239.9.180     34.236.170.4    98.92.71.206    3.209.10.78     3.236.246.13    98.82.128.192   18.207.241.78   3.235.148.157   98.92.118.135   98.93.88.195    44.200.188.107  44.211.83.13    3.238.250.100   98.92.32.114    44.220.249.20   35.170.64.218"
text_eu = "52.56.71.62     52.56.51.196    52.56.59.3      13.40.219.158   13.41.157.0     18.169.194.46   35.178.123.69   13.40.195.35    18.175.243.50   13.41.54.234    3.9.29.73       3.8.194.248     18.168.153.244  13.41.198.135   18.175.158.10   18.130.246.198"
text_ap = "54.95.97.121    54.168.59.48    43.207.40.178   103.4.11.132    54.95.132.251   54.238.85.124   13.230.247.132  18.183.34.93    13.230.234.228  13.230.154.3    18.183.7.146    52.68.168.149   54.178.61.234   54.249.138.65   13.158.51.63    54.178.89.232"
text_sa = "54.94.210.78    18.231.58.49    18.230.123.168  18.230.117.86   54.207.186.170  56.124.113.135  56.125.190.127  54.233.219.202  18.231.30.122   18.231.42.25    18.230.124.243  54.233.113.140  54.233.33.41    18.230.226.110  54.232.196.83   18.230.24.148"

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