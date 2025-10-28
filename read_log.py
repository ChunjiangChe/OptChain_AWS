#!/usr/bin/env python3
import sys, re, ast, json

def parse_chain(text: str, label: str):
    """
    Extract the bytes-literal JSON array after `<label>:` and parse it.
    Returns (num_blocks, forking_rate).
    """
    # Grab the exact bytes literal: b'[...]'
    pat = re.compile(rf"{re.escape(label)}\s*:\s*(b'(?:\\'|[^'])*')", re.DOTALL)
    m = pat.search(text)
    if not m:
        raise ValueError(f"Could not find {label} bytes literal in input.")

    bytes_literal = m.group(1)                  # e.g., b'["...", "Proposer chain forking rate: 0.9"]'
    data_bytes = ast.literal_eval(bytes_literal)  # -> bytes
    json_text = data_bytes.decode("utf-8")        # -> '["...", "..."]'
    arr = json.loads(json_text)                   # -> list[str]

    # The last element contains the forking rate text; everything before it are blocks (incl. genesis)
    last = arr[-1]
    rm = re.search(r"forking rate:\s*([0-9]*\.?[0-9]+)", last, re.IGNORECASE)
    if not rm:
        raise ValueError(f"Could not parse forking rate for {label}. Got: {last}")

    rate = float(rm.group(1))
    num_blocks = len(arr) - 1  # exclude the trailing "… forking rate: X" entry
    return num_blocks, rate

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path-to-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    proposer_blocks, proposer_rate = parse_chain(text, "proposer chain")
    availability_blocks, availability_rate = parse_chain(text, "availability chain")

    print(f"Proposer blocks: {proposer_blocks}")
    print(f"Proposer forking rate: {proposer_rate}")
    print(f"Availability blocks: {availability_blocks}")
    print(f"Availability forking rate: {availability_rate}")

if __name__ == "__main__":
    main()