"""Plot Figure 6 (RQ3): application throughput and BPF cost under Kinsn policies.

Values are the medians reported in Section 6.3. The style follows the original
figure, but the canvas is sized for one column of the ACM sigplan layout so
that its text is not scaled down in the paper.

Usage: python figures/scripts/plot_rq3_cilium_katran.py
Output: figures/sec-6-rq3-cilium-katran.pdf
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (label, throughput ratio, BPF cost ratio)
CASES = [
    ("Cilium\nFull\n4086 sites", 1.074, 1.010),
    ("Cilium\nNo Bulk\n3512 sites", 1.119, 1.062),
    ("Katran\nFull\n62 sites", 0.984, 1.006),
    ("Katran\nConservative\n21 sites", 1.065, 0.941),
]

COLUMN_WIDTH_IN = 241.14 / 72.27  # \columnwidth of acmart sigplan
HEIGHT_IN = 1.55
THROUGHPUT_COLOR = "#4C78A8"
COST_COLOR = "#D18F32"
EDGE_COLOR = "#3a3a3a"
Y_MIN, Y_MAX = 0.915, 1.19

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.5,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "sec-6-rq3-cilium-katran.pdf"

    # Two bars per case, side by side, with a wider gap between Cilium and Katran.
    centers = [0.0, 1.0, 2.6, 3.6]
    width = 0.44

    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN, HEIGHT_IN))
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.5, zorder=0)
    for x, (_, thr, cost) in zip(centers, CASES):
        for dx, value, color in ((-width / 2, thr, THROUGHPUT_COLOR), (width / 2, cost, COST_COLOR)):
            ax.bar(x + dx, value - Y_MIN, width, bottom=Y_MIN, color=color,
                   edgecolor=EDGE_COLOR, linewidth=0.35, zorder=2)
            ax.text(x + dx, value + 0.003, f"{value:.3f}x", ha="center", va="bottom",
                    fontsize=5.0, zorder=4,
                    bbox=dict(boxstyle="square,pad=0.05", facecolor="white", edgecolor="none"))

    ax.axhline(1.0, color="#555555", linestyle="--", linewidth=0.6, zorder=3)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_yticks([1.0, 1.1])
    ax.set_ylabel("Ratio to original eBPF")
    ax.set_xticks(centers)
    ax.set_xticklabels([c[0] for c in CASES], linespacing=1.15)
    ax.set_xlim(-0.55, 4.15)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=THROUGHPUT_COLOR, edgecolor=EDGE_COLOR, linewidth=0.35),
        plt.Rectangle((0, 0), 1, 1, facecolor=COST_COLOR, edgecolor=EDGE_COLOR, linewidth=0.35),
    ]
    ax.legend(handles, ["Workload throughput ↑", "BPF cost ↓"], loc="upper center",
              ncol=2, frameon=False, fontsize=5.8, handlelength=1.8, handleheight=0.7,
              columnspacing=2.0, borderaxespad=0.3)

    fig.tight_layout(pad=0.2)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.01)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
