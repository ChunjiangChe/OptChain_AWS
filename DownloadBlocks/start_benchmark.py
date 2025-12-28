import json
import os
import sys
import argparse
import paramiko

# ================= CONFIGURATION =================
INVENTORY_FILE = '../instances.json' 
PORT = 6042
# =================================================

def load_inventory(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    # 1. Parse Command Line Arguments
    parser = argparse.ArgumentParser(description='Start P2P Benchmark')
    parser.add_argument(
        '-n', '--receivers', 
        type=int, 
        help='Number of receiver nodes to target (default: all available)'
    )
    args = parser.parse_args()

    # 2. Load Inventory
    data = load_inventory(INVENTORY_FILE)
    global_user = data.get('user', 'ubuntu')
    
    all_nodes = []
    
    # Flatten the JSON structure
    for group in data['instances']:
        region = group['region']
        key_path = group['ssh_key']
        for ip in group['ips']:
            all_nodes.append({
                "ip": ip,
                "user": global_user,
                "key": key_path,
                "region": region
            })

    if len(all_nodes) < 2:
        print("Error: You need at least 2 instances (1 Sender + 1 Receiver) to run a benchmark.")
        sys.exit(1)

    # 3. Assign Roles
    # The first node is ALWAYS the Sender
    sender = all_nodes[0]
    
    # The rest are potential Receivers
    potential_receivers = all_nodes[1:]
    max_receivers = len(potential_receivers)

    # Determine actual count based on user input
    target_count = args.receivers if args.receivers else max_receivers

    if target_count > max_receivers:
        print(f"Warning: You asked for {target_count} receivers, but only {max_receivers} are available.")
        target_count = max_receivers

    # Slice the list to get exact number of targets
    targets = potential_receivers[:target_count]

    print(f"--- Benchmark Configuration ---")
    print(f"Sender:     {sender['ip']} ({sender['region']})")
    print(f"Receivers:  {len(targets)} node(s)")
    print(f"Port:       {PORT}")
    print(f"-------------------------------")

    # 4. Construct Command
    # Create the list of target IP:PORT
    target_args = " ".join([f"{t['ip']}:{PORT}" for t in targets])
    
    # Docker command
    docker_cmd = f"sudo docker run --rm --network host p2p-bench client {target_args}"

    print(f"Connecting to Sender ({sender['ip']}) to start test...")

    # 5. SSH and Execute
    key = paramiko.RSAKey.from_private_key_file(sender['key'])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=sender['ip'], username=sender['user'], pkey=key)
        
        # Execute with real-time output
        stdin, stdout, stderr = client.exec_command(docker_cmd, get_pty=True)

        print("\n=== BENCHMARK OUTPUT START ===\n")
        for line in iter(stdout.readline, ""):
            print(line, end="")
        print("\n=== BENCHMARK OUTPUT END ===")
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("\n✅ Benchmark completed successfully.")
        else:
            print(f"\n❌ Benchmark failed with exit code {exit_status}.")
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()