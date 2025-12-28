import json
import os
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIGURATION =================
INVENTORY_FILE = '../instances.json' 
# =================================================

# Commands to install Docker on Ubuntu
# 1. Update apt
# 2. Download official Docker install script
# 3. Run install script
# 4. Add 'ubuntu' user to docker group (so you can run docker without sudo)
INSTALL_COMMANDS = [
    "sudo apt-get update -y",
    "curl -fsSL https://get.docker.com -o get-docker.sh",
    "sudo sh get-docker.sh",
    "sudo usermod -aG docker ubuntu"
]

def load_inventory(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def install_docker_on_node(instance_info):
    ip, user, key_path, region = instance_info
    
    # Setup SSH connection
    key = paramiko.RSAKey.from_private_key_file(key_path)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"[{region}] Connecting to {ip}...")
    
    try:
        client.connect(hostname=ip, username=user, pkey=key, timeout=10)
        
        # Combine commands into one long shell string to ensure they run in order
        full_command = " && ".join(INSTALL_COMMANDS)
        
        # Execute
        stdin, stdout, stderr = client.exec_command(full_command)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            err = stderr.read().decode().strip()
            return (ip, False, f"Error: {err}")
            
        return (ip, True, "Docker Installed")

    except Exception as e:
        return (ip, False, str(e))
    finally:
        client.close()

def main():
    if not os.path.exists(INVENTORY_FILE):
        print(f"Error: {INVENTORY_FILE} not found.")
        return

    data = load_inventory(INVENTORY_FILE)
    global_user = data.get('user', 'ubuntu')
    
    targets = []
    for group in data['instances']:
        region = group['region']
        key_path = group['ssh_key']
        
        # Fix key permissions just in case
        if os.path.exists(key_path):
            os.chmod(key_path, 0o400)
            
        for ip in group['ips']:
            targets.append((ip, global_user, key_path, region))

    total = len(targets)
    print(f"Found {total} instances. Installing Docker (this may take 1-2 minutes per batch)...")
    
    # ThreadPool to install in parallel
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ip = {executor.submit(install_docker_on_node, t): t[0] for t in targets}
        
        for future in as_completed(future_to_ip):
            ip, success, msg = future.result()
            if success:
                print(f"✅ {ip}: Installed successfully")
            else:
                print(f"❌ {ip}: FAILED - {msg}")

    print("\nInstallation Complete. You may now run the deploy script.")

if __name__ == "__main__":
    main()