# plot_eth_bw_pdf.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

INPUT_CSV = "ethereum_node_bandwidth_synthetic_samples.csv"
OUTPUT_PNG = "ethereum_node_bandwidth_pdf_synthetic.png"
OUTPUT_CSV = "ethereum_node_bandwidth_pdf_points.csv"

def main():
    df = pd.read_csv(INPUT_CSV)

    regions = [
        "aws-region=us-east-2",
        "aws-region=eu-central-1",
        "aws-region=ap-southeast-2",
        "aws-region=us-west-1",
    ]

    # Shared x-grid (in Mbps)
    x_min = max(0.0, df["mbps"].min() - 2.0)
    x_max = df["mbps"].max() + 2.0
    x = np.linspace(x_min, x_max, 2000)

    plt.figure(figsize=(10, 6))
    pdf_frames = []

    for r in regions:
        vals = df.loc[df["region"] == r, "mbps"].to_numpy()
        if len(vals) == 0:
            continue

        # Smooth PDF using Gaussian KDE (Scott's rule)
        kde = gaussian_kde(vals)
        pdf = kde(x)

        plt.plot(x, pdf, linewidth=2, label=r)

        pdf_frames.append(pd.DataFrame({"x_mbps": x, "pdf": pdf, "region": r}))

    # Export the sampled PDF points (for reproducibility)
    if pdf_frames:
        pd.concat(pdf_frames, ignore_index=True).to_csv(OUTPUT_CSV, index=False)

    plt.title("PDF of Node Bandwidth (Synthetic)")
    plt.xlabel("Mean Mbps per node (synthetic)")
    plt.ylabel("Probability Density")
    plt.grid(True, alpha=0.3)
    plt.legend(title="tag")
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=160, bbox_inches="tight")

if __name__ == "__main__":
    main()