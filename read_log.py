import json
import re
import sys
from datetime import datetime
import server_utility

def analyze_chain_log(file_path: str):
    """Parse proposer/availability chains from a log file and print metrics."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- Helper functions ---
    def extract_list_from_log(raw_line: str) -> list[str]:
        start = raw_line.find('[')
        end = raw_line.rfind(']')
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Malformed log section")
        return json.loads(raw_line[start:end+1])

    def parse_ts(ts: str) -> datetime:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

    def extract_forking_rate(entries: list[str]) -> float | None:
        if entries and "forking rate" in entries[-1]:
            m = re.search(r"forking rate:\s*([0-9]*\.?[0-9]+)", entries[-1])
            return float(m.group(1)) if m else None
        return None

    def parse_proposer_items(items):
        pairs = []
        for s in items:
            if "forking rate" in s:
                continue
            blk, ts = s.split(":", 1)
            pairs.append((blk, parse_ts(ts)))
        return pairs

    def parse_availability_items(items):
        triples = []
        for s in items:
            if "forking rate" in s:
                continue
            blk, rest = s.split(":", 1)
            m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\((Inclusive|Exclusive)\)", rest)
            if m:
                triples.append((blk, parse_ts(m.group(1)), m.group(2)))
        return triples

    def ignore_genesis(seq):
        return seq[1:] if seq else []

    def rate_per_second(timestamps, count):
        if not timestamps or count <= 0:
            return 0.0
        start, end = min(timestamps), max(timestamps)
        span = (end - start).total_seconds()
        return count / span if span > 0 else float("inf")

    # --- Split into proposer and availability sections ---
    proposer_match = re.search(r"proposer chain: b'(\[.*?\])", content, flags=re.DOTALL)
    availability_match = re.search(r"availability chain: b'(\[.*?\])", content, flags=re.DOTALL)
    if not proposer_match or not availability_match:
        raise ValueError("Missing proposer or availability chain sections in log")

    proposer_raw = "b'" + proposer_match.group(1) + "'"
    availability_raw = "b'" + availability_match.group(1) + "'"

    proposer_entries = extract_list_from_log(proposer_raw)
    availability_entries = extract_list_from_log(availability_raw)

    proposer_fork = extract_forking_rate(proposer_entries)
    avail_fork = extract_forking_rate(availability_entries)

    proposer_list = parse_proposer_items(proposer_entries)
    availability_list = parse_availability_items(availability_entries)

    proposer_no_gen = ignore_genesis(proposer_list)
    availability_no_gen = ignore_genesis(availability_list)

    prop_cnt = len(proposer_no_gen)
    avail_cnt = len(availability_no_gen)
    incl_cnt = sum(1 for _,_,t in availability_no_gen if t == "Inclusive")
    excl_cnt = sum(1 for _,_,t in availability_no_gen if t == "Exclusive")

    prop_ts = [ts for _, ts in proposer_no_gen]
    avail_ts = [ts for _, ts, _ in availability_no_gen]
    incl_ts = [ts for _, ts, t in availability_no_gen if t == "Inclusive"]
    excl_ts = [ts for _, ts, t in availability_no_gen if t == "Exclusive"]

    prop_rps = rate_per_second(prop_ts, prop_cnt/proposer_fork)
    avail_rps = rate_per_second(avail_ts, avail_cnt/avail_fork)
    incl_rps = rate_per_second(incl_ts, incl_cnt)
    excl_rps = rate_per_second(excl_ts, excl_cnt)

    print("=== Chain Analysis ===")
    print(f"1) Proposer blocks (non-genesis): {prop_cnt}")
    print(f"2) Availability blocks (non-genesis): {avail_cnt}")
    print(f"3) Availability breakdown -> Inclusive: {incl_cnt}, Exclusive: {excl_cnt}")
    print(f"4) Proposer blocks per second: {prop_rps:.6f}")
    print(f"5) Availability blocks per second: {avail_rps:.6f}")
    print(f"6) Availability per second -> Inclusive: {incl_rps:.6f}, Exclusive: {excl_rps:.6f}")
    print(f"7) Forking rates -> Proposer: {proposer_fork}, Availability: {avail_fork}")

# Example usage:
# analyze_chain_log("chain_log.txt")
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

    for i in range(shard_num):
        node_id = i * shard_size
        analyze_chain_log("./exper_log/{}/exper_{}/iter_{}/node_{}.txt".format(protocol, exper_id, exper_iter, node_id))