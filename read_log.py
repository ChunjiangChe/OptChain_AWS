import json
import re
import sys
from datetime import datetime
import server_utility
import ast

def calculate_mining_rate(chain_list):
    """
    Calculates blocks/second.
    Ignores the first block (index 0) unconditionally.
    Finds the first and last valid timestamps in the remaining list to calculate duration.
    Mining Rate = (Index_Last - Index_First) / (Time_Last - Time_First)
    """
    if not chain_list or len(chain_list) < 2:
        return 0.0

    # Ignore the first block as requested
    working_list = chain_list[1:]

    # Updated Regex: (?:\.\d+)? makes the milliseconds part optional
    ts_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)"
    
    first_time = None
    last_time = None
    first_idx = -1
    last_idx = -1

    for i, block in enumerate(working_list):
        # Ensure block is a string before regex search
        if isinstance(block, str):
            match = re.search(ts_pattern, block)
            if match:
                dt_str = match.group(1)
                try:
                    # Try parsing with milliseconds first
                    if "." in dt_str:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
                    else:
                        # Fallback for timestamps without milliseconds
                        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

                    if first_time is None:
                        first_time = dt
                        first_idx = i
                    last_time = dt
                    last_idx = i
                except ValueError:
                    continue

    if first_time and last_time and last_time > first_time:
        duration = (last_time - first_time).total_seconds()
        # Count is the number of blocks generated between start and end
        count = last_idx - first_idx
        return count / duration

    return 0.0

def analyze_manifoldchain(file_path):
    with open(file_path, 'r') as f:
        content = f.read().strip()

    match = re.search(r"b'(\[.*\])'", content)
    if not match:
        print(f"[Error] No valid chain list found in {file_path}")
        return

    chain_str = match.group(1).replace('\\"', '"').replace("\\'", "'")

    try:
        chain_list = ast.literal_eval(chain_str)
    except Exception as e:
        print(f"[Error] Failed to parse chain list in {file_path}: {e}")
        return

    forking_rate = None
    if chain_list and isinstance(chain_list[-1], str) and "forking_rate" in chain_list[-1]:
        try:
            forking_rate = float(chain_list[-1].split(":")[1].strip())
            chain_list = chain_list[:-1]
        except Exception:
            pass

    mining_rate = calculate_mining_rate(chain_list)

    chain_list = [b for b in chain_list if "1970-01-01" not in b]
    num_blocks = len(chain_list)

    print(f"{file_path}")
    print(f"Number of blocks (excluding genesis): {num_blocks}")
    print(f"Forking rate: {forking_rate if forking_rate is not None else 'N/A'}")
    print(f"Mining rate: {mining_rate:.4f} blocks/s")


def analyze_chain_log(file_path: str):
    """
    Parse proposer, availability, and ordering chains from a log file.
    Calculates metrics including the total cmts included by the ordering chain.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return 0, 0

    # --- Helper: Extract JSON list from b'...' string ---
    def load_chain_list(chain_name, raw_content):
        # Relaxes regex to capture potentially complex nested content inside the list
        pattern = f"{chain_name}: b'(\\[.*?\\])'"
        match = re.search(pattern, raw_content, flags=re.DOTALL)
        if not match:
            return []
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON for {chain_name}")
            return []

    # --- Helper: Parse specific chain metrics ---
    def process_chain_data(chain_entries, chain_type):
        """Returns: (block_count, forking_rate, total_items_count)"""
        if not chain_entries:
            return 0, 0.0, 0

        # Extract Forking Rate if present
        forking_rate = 0.0
        if isinstance(chain_entries[-1], str) and "forking rate" in chain_entries[-1].lower():
            try:
                fr_match = re.search(r"forking rate:\s*([0-9]*\.?[0-9]+)", chain_entries[-1], re.IGNORECASE)
                if fr_match:
                    forking_rate = float(fr_match.group(1))
            except:
                pass
            chain_entries = chain_entries[:-1]

        valid_blocks = 0
        total_items = 0

        for entry in chain_entries:
            if "1970-01-01" in entry:
                continue
            
            valid_blocks += 1
            # Extract content in the last brackets [...]
            content_match = re.search(r"\[(.*?)\]$", entry)
            
            if content_match:
                inner_content = content_match.group(1).strip()
                if not inner_content:
                    count = 0
                elif chain_type == "ordering":
                    # Ordering content format: [(hash, shard), (hash, shard)]
                    count = inner_content.count('(')
                else:
                    # Proposer/Availability content format: [hash, hash, hash]
                    count = inner_content.count(',') + 1
                total_items += count

        return valid_blocks, forking_rate, total_items

    # 1. Load raw lists
    prop_raw = load_chain_list("proposer chain", content)
    avail_raw = load_chain_list("availability chain", content)
    order_raw = load_chain_list("ordering chain", content)

    # 2. Process basic metrics
    prop_cnt, prop_fork, prop_cmts = process_chain_data(prop_raw, "proposer")
    avail_cnt, avail_fork, avail_cmts = process_chain_data(avail_raw, "availability")
    order_cnt, order_fork, order_hashes = process_chain_data(order_raw, "ordering")

    # 3. Calculate Mining Rates
    prop_rate = calculate_mining_rate(prop_raw)
    avail_rate = calculate_mining_rate(avail_raw)
    order_rate = calculate_mining_rate(order_raw)

    # 4. Calculate "Total cmts of availability blocks included by ordering blocks"
    
    # Step A: Build a map for Availability Blocks -> Number of Cmts
    avail_block_cmts = {}
    
    for entry in avail_raw:
        if "forking rate" in entry.lower() or "1970-01-01" in entry:
            continue
        
        # Extract Block Hash (everything before the first colon)
        parts = entry.split(':', 1)
        if not parts: continue
        blk_hash = parts[0].strip()
        
        # Calculate number of cmts inside this block
        cmt_count = 0
        content_match = re.search(r"\[(.*?)\]$", entry)
        if content_match:
            inner = content_match.group(1).strip()
            if inner:
                cmt_count = inner.count(',') + 1
        
        avail_block_cmts[blk_hash] = cmt_count

    # Step B: Iterate Ordering Blocks and accumulate sum
    total_included_cmts = 0
    
    for entry in order_raw:
        if "forking rate" in entry.lower() or "1970-01-01" in entry:
            continue
        
        content_match = re.search(r"\[(.*?)\]$", entry)
        if content_match:
            inner = content_match.group(1).strip()
            # Extract hashes from tuples like (0000..aaf6, 0)
            refs = re.findall(r"\(([^,]+),", inner)
            
            for raw_ref_hash in refs:
                raw_ref_hash = raw_ref_hash.strip()
                
                # --- HASH CONVERSION LOGIC ---
                if ".." in raw_ref_hash:
                    prefix, suffix = raw_ref_hash.split("..", 1)
                    new_prefix = prefix[:3]
                    new_suffix = suffix[-3:]
                    converted_hash = f"{new_prefix}..{new_suffix}"
                else:
                    converted_hash = raw_ref_hash

                if converted_hash in avail_block_cmts:
                    total_included_cmts += avail_block_cmts[converted_hash]

    # 5. Print Results
    print(f"--- Analysis for {file_path} ---")
    print("1. Number of blocks (excluding genesis):")
    print(f"   - Proposer:     {prop_cnt}")
    print(f"   - Availability: {avail_cnt}")
    print(f"   - Ordering:     {order_cnt}")
    
    print("\n2. Forking Rates:")
    print(f"   - Proposer:     {prop_fork}")
    print(f"   - Availability: {avail_fork}")
    print(f"   - Ordering:     {order_fork}")

    print("\n3. Mining Rates (blocks/s):")
    print(f"   - Proposer:     {prop_rate:.4f}")
    print(f"   - Availability: {avail_rate:.4f}")
    print(f"   - Ordering:     {order_rate:.4f}")

    print("\n4. Number of cmts (transactions):")
    print(f"   - Proposer Chain:         {prop_cmts}")
    print(f"   - Availability Chain:     {avail_cmts}")
    print(f"   - Included by Ordering:   {total_included_cmts}")

    print("\n5. Number of hashes (availability refs):")
    print(f"   - Ordering Chain:         {order_hashes}")
    print("-" * 30)

    # Calculate inclusive/exclusive counts for return values
    incl_cnt = 0
    excl_cnt = 0
    for entry in avail_raw:
        if "1970-01-01" in entry or "forking rate" in entry.lower(): continue
        if "(Inclusive)" in entry: incl_cnt += 1
        elif "(Exclusive)" in entry: excl_cnt += 1

    return excl_cnt, incl_cnt

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_nodes.py <protocol> <exper_id> <exper_iter>")
        sys.exit(1)
    protocol = str(sys.argv[1])
    exper_id = sys.argv[2]
    exper_iter = sys.argv[3]

    nodes_config = server_utility.load_config("./expers/{}/exper_{}/config.json".format(protocol, exper_id))
    shard_num = nodes_config["shard_num"]
    shard_size = nodes_config["shard_size"]

    if protocol == "optchain":
        avai_size = nodes_config["avai_size"]

        throughput = 0
        for i in range(shard_num):
            node_id = i * shard_size
            excl_cnt, incl_cnt = analyze_chain_log("./exper_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id))
            throughput += (excl_cnt + (incl_cnt / shard_num)) * avai_size
        print(f"throughput: {throughput}")
    elif protocol == "manifoldchain":
        total_blocks = 0
        for i in range(shard_num):
            node_id = i * shard_size
            analyze_manifoldchain("./exper_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id))