import json
import os
import subprocess
import sys
import time
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIGURATION =================
# The file containing your instance list
INVENTORY_FILE = '../instances.json' 

# Project directory on the remote server
REMOTE_DIR = '/home/ubuntu/p2p_project'

# Deployment Commands
# 1. Build the image (using the Docker/Dockerfile structure)
# 2. Stop/Remove old container
# 3. Run new container in SERVER mode
REMOTE_COMMANDS = [
    # 1. Force start the Docker Daemon (fixes "Cannot connect" error)
    "sudo systemctl start docker",
    
    # 2. Force enable it so it restarts on reboot
    "sudo systemctl enable docker",

    # 3. Open permissions on the Docker Socket. 
    # This fixes the permission error instantly without needing to log out/in.
    "sudo chmod 666 /var/run/docker.sock",

    # 4. Now run the actual build and deploy (standard commands now work)
    f"cd {REMOTE_DIR} && docker build -t p2p-bench -f Docker/Dockerfile .",
    "docker stop p2p-node || true",
    "docker rm p2p-node || true",
    "docker run -d --network host --name p2p-node --restart unless-stopped p2p-bench server --port 6042"
]
# =================================================

def load_inventory(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def sync_files(ip, user, key_path):
    """
    Uses local rsync to copy files. faster and more robust than python-based sftp.
    """
    # Exclude heavy artifacts to speed up transfer
    exclude_flags = "--exclude target --exclude .git --exclude .idea --exclude __pycache__"
    
    # Construct rsync command
    # -o StrictHostKeyChecking=no prevents the "yes/no" prompt for new IPs
    ssh_cmd = f"ssh -i {key_path} -o StrictHostKeyChecking=no"
    cmd = f"rsync -avz -e '{ssh_cmd}' {exclude_flags} ./ {user}@{ip}:{REMOTE_DIR}"
    
    # Suppress output unless error
    result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Rsync failed: {result.stderr.decode().strip()}")

def run_remote_commands(ip, user, key_path):
    """
    Connects via SSH and runs the build/run commands.
    """
    key = paramiko.RSAKey.from_private_key_file(key_path)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=ip, username=user, pkey=key, timeout=10)
        
        for cmd in REMOTE_COMMANDS:
            stdin, stdout, stderr = client.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status != 0:
                error_msg = stderr.read().decode().strip()
                raise Exception(f"Command failed: {cmd}\nError: {error_msg}")
                
    finally:
        client.close()

def deploy_to_instance(instance_info):
    """
    The worker function for a single instance.
    """
    ip, user, key_path, region = instance_info
    
    print(f"[{region}] Starting deployment to {ip}...")
    
    try:
        # 1. Sync Code
        sync_files(ip, user, key_path)
        
        # 2. Build and Run
        run_remote_commands(ip, user, key_path)
        
        return (ip, True, "Success")
    except Exception as e:
        return (ip, False, str(e))

def main():
    if not os.path.exists(INVENTORY_FILE):
        print(f"Error: {INVENTORY_FILE} not found.")
        return

    data = load_inventory(INVENTORY_FILE)
    global_user = data.get('user', 'ubuntu')
    
    # Flatten the list of all targets
    targets = []
    for group in data['instances']:
        region = group['region']
        key_path = group['ssh_key']
        
        # Ensure key permissions are correct (SSH requires 400)
        if os.path.exists(key_path):
            os.chmod(key_path, 0o400)
        else:
            print(f"Warning: Key file {key_path} not found!")
        
        for ip in group['ips']:
            targets.append((ip, global_user, key_path, region))

    total = len(targets)
    print(f"Found {total} instances. Starting parallel deployment...")
    
    successful_ips = []
    failed_ips = []

    # Use ThreadPool to run 16 deployments at a time
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_ip = {executor.submit(deploy_to_instance, t): t[0] for t in targets}
        
        for future in as_completed(future_to_ip):
            ip, success, msg = future.result()
            if success:
                print(f"✅ {ip}: Deployed successfully")
                successful_ips.append(ip)
            else:
                print(f"❌ {ip}: FAILED - {msg}")
                failed_ips.append(ip)

    print("\n" + "="*50)
    print(f"Deployment Complete.")
    print(f"Success: {len(successful_ips)}/{total}")
    print(f"Failed:  {len(failed_ips)}/{total}")
    print("="*50)

    if successful_ips:
        print("\nTo start the BENCHMARK, login to one node and run this Client command:")
        
        # Generate the client command string excluding the sender's own IP (just pick the first one)
        sender = successful_ips[0]
        receivers = successful_ips[1:]
        
        # Format IP:PORT list
        target_args = " ".join([f"{ip}:6042" for ip in receivers])
        
        print(f"\nSSH into Sender: ssh -i <KEY> ubuntu@{sender}")
        print(f"Run Command:     docker run --rm --network host p2p-bench client {target_args}")

if __name__ == "__main__":
    main()