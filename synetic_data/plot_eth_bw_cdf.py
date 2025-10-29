# plot_eth_bw_cdf.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_CSV = "ethereum_node_bandwidth_synthetic_samples.csv"
OUTPUT_PNG = "ethereum_node_bandwidth_cdf_synthetic.png"

def ecdf(values: np.ndarray):
    """Return x (sorted values) and y (empirical CDF) for an array."""
    x = np.sort(values)
    n = x.size
    y = np.arange(1, n + 1) / n
    return x, y

def main():
    # Load data: expect columns ["region", "mbps"]
    df = pd.read_csv(INPUT_CSV)

    # Order regions for consistent legend (optional)
    region_order = [
        "aws-region=us-east-2",
        "aws-region=eu-central-1",
        "aws-region=ap-southeast-2",
        "aws-region=us-west-1",
    ]
    # Fallback to whatever is present if any are missing
    regions = [r for r in region_order if r in df["region"].unique()]
    for r in df["region"].unique():
        if r not in regions:
            regions.append(r)

    # Plot ECDFs
    plt.figure(figsize=(10, 6))
    for region in regions:
        mbps = df.loc[df["region"] == region, "mbps"].to_numpy(dtype=float)
        x, y = ecdf(mbps)
        plt.plot(x, y, linewidth=2, label=region)

    # Styling to match the previous figure
    plt.title("CDF of BW in Ethereum (Synthetic, fitted to example)")
    plt.xlabel("Mean Mbps per node (synthetic)")
    plt.ylabel("CDF of nodes")
    plt.grid(True, alpha=0.3)
    plt.legend(title="tag")
    plt.tight_layout()

    # Save and show
    plt.savefig(OUTPUT_PNG, dpi=160, bbox_inches="tight")
    plt.show()  # uncomment if you want an interactive window

if __name__ == "__main__":
    main()