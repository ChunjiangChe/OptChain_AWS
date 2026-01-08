import json
import os
import sys
import paramiko
import re
import time
import random
from statistics import mean

# ================= CONFIGURATION =================
# Path to your nodes.json file
INVENTORY_FILE = '../expers/optchain/exper_53/nodes.json' 

# Port used for the benchmark
PORT = 6042

# ----------------- BENCHMARK SETTINGS -----------------
# Number of receiver nodes to target (Set to 0 or None to use ALL available nodes)
NUM_RECEIVERS = 63 

# Number of times to run the benchmark
NUM_ITERATIONS = 10

# File path to save the results (e.g., 'results.txt'). Set to None to disable file saving.
OUTPUT_FILE = './optimal_tps_img/optchain_53.txt'
# ======================================================

def load_inventory(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    # 1. Load Inventory
    print(f"Loading inventory from: {INVENTORY_FILE}")
    data = load_inventory(INVENTORY_FILE)
    global_user = data.get('user', 'ubuntu')
    
    all_nodes = []
    ip_to_id = {} 
    ip_to_bw = {} 

    if 'instances' in data:
        for inst in data['instances']:
            ip = inst.get('ip')
            region = inst.get('region')
            key_path = inst.get('ssh_key') 
            user = inst.get('user', global_user)
            node_id = inst.get('node_id', -1)
            bandwidth = inst.get('bandwidth', 'N/A')

            if ip and key_path:
                node_entry = {
                    "ip": ip,
                    "user": user,
                    "key": key_path,
                    "region": region,
                    "node_id": node_id
                }
                all_nodes.append(node_entry)
                ip_to_id[ip] = node_id
                ip_to_bw[ip] = bandwidth

    if len(all_nodes) < 2:
        print("Error: You need at least 2 instances.")
        sys.exit(1)

    # Prepare data structure for results
    aggregated_results = {node['ip']: {"blocks": [], "rates": []} for node in all_nodes}

    print(f"--- Benchmark Configuration ---")
    print(f"Total Nodes: {len(all_nodes)}")
    print(f"Iterations:  {NUM_ITERATIONS}")
    print(f"Port:        {PORT}")
    if OUTPUT_FILE:
        print(f"Output File: {OUTPUT_FILE}")
    print(f"-------------------------------")

    # 2. Benchmark Loop
    for i in range(1, NUM_ITERATIONS + 1):
        # Shuffle Nodes
        current_shuffle = all_nodes[:]
        random.shuffle(current_shuffle)

        sender = current_shuffle[0]
        potential_receivers = current_shuffle[1:]
        
        max_receivers = len(potential_receivers)
        
        # Use hardcoded parameter logic
        if NUM_RECEIVERS and NUM_RECEIVERS > 0 and NUM_RECEIVERS < max_receivers:
            target_count = NUM_RECEIVERS
        else:
            target_count = max_receivers
            
        targets = potential_receivers[:target_count]

        print(f"\n[Iteration {i}/{NUM_ITERATIONS}]")
        print(f"  Sender:    {sender['ip']} (ID: {sender['node_id']})")
        print(f"  Receivers: {len(targets)} nodes")

        target_args = " ".join([f"{t['ip']}:{PORT}" for t in targets])
        docker_cmd = f"sudo docker run --rm --network host p2p-bench client {target_args}"

        key = paramiko.RSAKey.from_private_key_file(sender['key'])
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(hostname=sender['ip'], username=sender['user'], pkey=key, timeout=10)
            stdin, stdout, stderr = client.exec_command(docker_cmd, get_pty=True)
            
            run_output = []
            for line in iter(stdout.readline, ""):
                run_output.append(line)
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"  ❌ Iteration {i} failed with code {exit_status}")
            else:
                parse_and_store_run(run_output, aggregated_results)
                print("  ✅ Complete")

        except Exception as e:
            print(f"  ❌ Connection to sender failed: {e}")
        finally:
            client.close()
        
        if i < NUM_ITERATIONS:
            time.sleep(2)

    # 3. Generate and Save Report
    generate_and_save_report(aggregated_results, ip_to_id, ip_to_bw, OUTPUT_FILE)


def parse_and_store_run(output_lines, aggregator):
    row_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\|\s+(\d+)\s+\|\s+(\d+\.\d+)")

    for line in output_lines:
        match = row_pattern.search(line)
        if match:
            ip = match.group(1)
            blocks = int(match.group(2))
            rate = float(match.group(3))

            if ip in aggregator:
                aggregator[ip]["blocks"].append(blocks)
                aggregator[ip]["rates"].append(rate)

def generate_and_save_report(results, ip_to_id, ip_to_bw, output_path):
    # 1. Prepare Data
    final_data = []

    for ip, data in results.items():
        runs = len(data["rates"])
        avg_blocks = mean(data["blocks"]) if runs > 0 else 0.0
        avg_rate = mean(data["rates"]) if runs > 0 else 0.0
        
        node_id = ip_to_id.get(ip, 9999)
        bw = ip_to_bw.get(ip, "N/A")

        final_data.append({
            "id": node_id,
            "ip": ip,
            "bw": bw,
            "runs": runs,
            "blocks": avg_blocks,
            "rate": avg_rate
        })

    # 2. Sort by Node ID
    final_data.sort(key=lambda x: x["id"])

    # 3. Construct the Output String
    lines = []
    
    # Python List Section
    rates_only = [x["rate"] for x in final_data]
    formatted_list_str = ", ".join([f"{val:.2f}" for val in rates_only])

    lines.append("\n" + "="*80)
    lines.append(" PYTHON LIST FORMAT")
    lines.append("="*80)
    lines.append(f"download_blocks = [\n    {formatted_list_str}\n]")
    
    # Readable Table Section
    lines.append("\n" + "="*100)
    lines.append(f" READABLE SUMMARY TABLE (Sorted by Node ID)")
    lines.append("="*100)
    lines.append(f"{'ID':<5} | {'Node IP':<16} | {'Bandwidth':<10} | {'Runs (Rx)':<10} | {'Avg Blocks':<12} | {'Avg T-put (A/s)':<15}")
    lines.append("-" * 100)

    for node in final_data:
        lines.append(f"{node['id']:<5} | {node['ip']:<16} | {str(node['bw']):<10} | {node['runs']:<10} | {node['blocks']:<12.1f} | {node['rate']:<15.2f}")

    lines.append("-" * 100)

    # Join everything into one big string
    final_report = "\n".join(lines)

    # 4. Print to Console
    print(final_report)

    # 5. Save to File (if path provided)
    if output_path:
        try:
            with open(output_path, 'w') as f:
                f.write(final_report)
            print(f"\n✅ Results successfully saved to: {output_path}")
        except Exception as e:
            print(f"\n❌ Failed to save results to file: {e}")

if __name__ == "__main__":
    main()