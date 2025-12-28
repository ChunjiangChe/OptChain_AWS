import json
import os
import subprocess
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIGURATION =================
INVENTORY_FILE = '../instances.json' 
REMOTE_DIR = '/home/ubuntu/p2p_project'
SERVER_PORT = 6042

# Exclude these to speed up the upload significantly
RSYNC_EXCLUDES = [
    "--exclude 'target'",
    "--exclude '.git'",
    "--exclude '.idea'",
    "--exclude '__pycache__'",
    "--exclude '*.pem'"
]
# =================================================

def load_inventory(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def update_node(instance_info):
    ip, user, key_path, region = instance_info
    
    print(f"[{region}] Updating {ip}...")

    # 1. SYNC FILES (Rsync)
    # We use subprocess to call system rsync because it's faster/more robust than Python libs
    ssh_opts = f"ssh -i {key_path} -o StrictHostKeyChecking=no -o ConnectTimeout=10"
    exclude_str = " ".join(RSYNC_EXCLUDES)
    
    # Ensures the remote directory exists before syncing
    mkdir_cmd = f"{ssh_opts} {user}@{ip} 'mkdir -p {REMOTE_DIR}'"
    subprocess.run(mkdir_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Sync local folder to remote folder
    rsync_cmd = f"rsync -avz -e '{ssh_opts}' {exclude_str} ./ {user}@{ip}:{REMOTE_DIR}"
    
    res = subprocess.run(rsync_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        return (ip, False, f"Rsync failed: {res.stderr.decode().strip()}")

    # 2. BUILD & RESTART (SSH)
    # We chain commands to ensure they run in the correct environment
    commands = [
        f"cd {REMOTE_DIR}",
        # Build image using the Dockerfile in the subdirectory, context is root (.)
        "sudo docker build -t p2p-bench -f Docker/Dockerfile .",
        # Stop and remove old container
        "sudo docker stop p2p-node || true",
        "sudo docker rm p2p-node || true",
        # Start new container in Server mode
        f"sudo docker run -d --network host --name p2p-node --restart unless-stopped p2p-bench server --port {SERVER_PORT}"
    ]
    
    full_command = " && ".join(commands)

    # Paramiko SSH Connection
    key = paramiko.RSAKey.from_private_key_file(key_path)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=ip, username=user, pkey=key, timeout=15)
        stdin, stdout, stderr = client.exec_command(full_command)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            err = stderr.read().decode().strip()
            # Sometimes docker build warnings print to stderr but exit 0. 
            # If exit is non-zero, it's a real error.
            return (ip, False, f"Build/Run failed: {err}")
            
        return (ip, True, "Updated & Restarted")

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
    # Flatten inventory
    for group in data['instances']:
        region = group['region']
        key_path = group['ssh_key']
        
        # Ensure key security
        if os.path.exists(key_path):
            os.chmod(key_path, 0o400)
            
        for ip in group['ips']:
            targets.append((ip, global_user, key_path, region))

    total = len(targets)
    print(f"Starting update for {total} instances with 16 parallel threads...")
    print("---------------------------------------------------------------")

    successful = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_ip = {executor.submit(update_node, t): t[0] for t in targets}
        
        for future in as_completed(future_to_ip):
            ip, success, msg = future.result()
            if success:
                print(f"✅ {ip}: {msg}")
                successful += 1
            else:
                print(f"❌ {ip}: {msg}")
                failed += 1

    print("---------------------------------------------------------------")
    print(f"Update Complete. Success: {successful} | Failed: {failed}")
    if successful > 0:
        print("All updated nodes are now running in SERVER mode.")
        print("You can now run 'python3 start_benchmark.py'.")

if __name__ == "__main__":
    main()