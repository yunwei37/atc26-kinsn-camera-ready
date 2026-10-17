"""Plot Figures 2 and 5: the characterization and Kinsn microbenchmark speedups.

Data come from the ATC'26 bundle in bpf-benchmark (kinsn/paper/atc26), whose
plots.py rebuilds the published bars from data/ and checks them against the
published PDFs. This script keeps the published page size, axes, bars and
typography, and differs only in its labels: multiplication signs instead of
the letter x, the baseline named as in the captions, value labels of bars
below 1x inside the bar instead of across the 1x line, and the ARM64 geomean
label placed where it covers no bar.

Usage: python figures/scripts/plot_micro_figures.py <bpf-benchmark>/kinsn/paper/atc26
Output: figures/sec-3-4config-percase.pdf,
        figures/sec-6-{x86-kinsn-micro-best-raw,arm64-kinsn-micro-rejit}-27-20260608.pdf
"""
import os
import sys
from pathlib import Path

BUNDLE = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUNDLE / 'scripts'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

import metrics
from plots import COLORS, SHORT_NAMES, gm

# ORIG=1 draws the published labels, to compare the geometry with the published PDFs.
ORIG = bool(os.environ.get('ORIG'))
TIMES = 'x' if ORIG else '×'
EDGE = '#333333'
plt.rcParams.update({'pdf.fonttype': 42, 'font.family': 'DejaVu Sans',
                     'grid.color': '#eeeeee', 'grid.linewidth': .9})
# Font sizes in pt: Figure 2 x ticks, y ticks, legend, panel name; Figure 5
# x ticks, y ticks, y label, value labels, geomean label.
FS = dict(f2_xt=16, f2_yt=18, f2_lg=18, f2_name=22,
          f5_xt=21, f5_yt=22, f5_yl=22, f5_val=18, f5_gm=20)
FS.update({k: float(v) for k, v in (kv.split('=') for kv in os.environ.get('FS', '').split(',') if kv)})


def ratio(v, _=None):
    return f'{v:g}{TIMES}'


def fig2(chars):
    """Figure 2: two panels, three non-baseline paths per benchmark."""
    width_pt, height_pt = 1234.46, 709.7
    panels = [(49.2, 276.2), (389.8, 616.9)]  # top and bottom of each axes, in pt
    with plt.rc_context({'font.size': 18}):
        fig = plt.figure(figsize=(width_pt / 72, height_pt / 72))
        for (top, bottom), arch, label in zip(panels, ['x86', 'arm'], ['x86-64', 'ARM64']):
            ax = fig.add_axes([95.1 / width_pt, 1 - bottom / height_pt,
                               (1227.3 - 95.1) / width_pt, (bottom - top) / height_pt])
            names = sorted(chars[arch, 'native_kernel'], key=lambda n: list(SHORT_NAMES).index(n))
            x = np.arange(len(names))
            w = .8 / 3
            for i, (runtime, legend) in enumerate([('native_kernel', 'In-kernel native'),
                                                  ('native', 'Userspace native'),
                                                  ('llvmbpf', 'Userspace LLVM-BPF')]):
                values = [chars[arch, runtime][n] for n in names]
                ax.bar(x + (i - 1) * w, values, width=w, color=COLORS[i], edgecolor=EDGE,
                       linewidth=.5, label=f'{legend} ({gm(values):.2f}{TIMES})')
            ax.axhline(1, color=EDGE, linestyle='--', linewidth=1.4)
            ax.set_xticks(x, [SHORT_NAMES[n] for n in names], rotation=50, ha='right', fontsize=FS['f2_xt'])
            ax.tick_params(axis='y', labelsize=FS['f2_yt'])
            ax.set_xlim(-.6, len(names) - .4)
            ax.set_ylim(0, 4.25)
            ax.set_yticks(np.arange(0, 4.5, .5))
            ax.yaxis.set_major_formatter(FuncFormatter(ratio))
            ax.set_ylabel('Speedup over\nkernel eBPF JIT')
            ax.text(.005, .96, label, transform=ax.transAxes, va='top', weight='bold', fontsize=FS['f2_name'])
            ax.grid(axis='y')
            ax.legend(loc='lower center', bbox_to_anchor=(.5, 1.02), ncol=3, frameon=False, fontsize=FS['f2_lg'])
        fig.savefig(OUT / 'sec-3-4config-percase.pdf')
        plt.close(fig)


def fig5(x86, arm64):
    """Figure 5: Kinsn speedup per benchmark, in x86-64 order in both panels."""
    names = sorted(x86, key=x86.__getitem__, reverse=True)
    for arch, values, filename in [
            ('x86', x86, 'sec-6-x86-kinsn-micro-best-raw-27-20260608.pdf'),
            ('arm64', arm64, 'sec-6-arm64-kinsn-micro-rejit-27-20260608.pdf')]:
        ys = [values[n] for n in names]
        threshold = 1.35 if arch == 'x86' else 1.30
        with plt.rc_context({'font.size': 22}):
            fig = plt.figure(figsize=(24, 4.8))
            # The two-line y label of the revision needs a slightly wider left margin.
            left = .055 if ORIG else .064
            ax = fig.add_axes([left, .34, .995 - left, .60])
            bars = ax.bar(range(len(names)), ys, width=.82,
                          color=[(COLORS[0] if arch == 'x86' else COLORS[1]) if v >= 1 else COLORS[2] for v in ys],
                          edgecolor=EDGE, linewidth=.45)
            ax.axhline(1, color=EDGE, linestyle='--', linewidth=1.35)
            g = gm(ys)
            ax.axhline(g, color='#7f7f7f', linestyle='-.', linewidth=1.65)
            if ORIG or arch == 'x86':
                ax.text(.995, g, f'geomean {g:.2f}{TIMES}', transform=ax.get_yaxis_transform(),
                        ha='right', va='bottom', color='#555555', fontsize=FS['f5_gm'])
            else:
                # Right-align the label before the cgroup bar, over three bars below the geomean.
                ax.text(names.index('cgroup_skb_hash_chain') - .55, g, f'geomean {g:.2f}{TIMES}',
                        ha='right', va='bottom', color='#555555', fontsize=FS['f5_gm'])
            for bar, v in zip(bars, ys):
                x = bar.get_x() + bar.get_width() / 2
                if v >= threshold or (ORIG and v < .9):
                    ax.text(x, v + .078, f'{v:.2f}{TIMES}', ha='center', fontsize=FS['f5_val'])
                elif v < .9:
                    ax.text(x, v - .05, f'{v:.2f}{TIMES}', ha='center', va='top', fontsize=FS['f5_val'] - 2, color='white')
            if ORIG:
                ax.set_ylabel('Speedup over stock', fontsize=FS['f5_yl'])
            else:
                ax.set_ylabel('Speedup over\noriginal eBPF JIT', fontsize=20, linespacing=1.0, labelpad=4)
            ax.set_xticks(range(len(names)), [SHORT_NAMES[n] for n in names], rotation=50, ha='right', fontsize=FS['f5_xt'])
            ax.tick_params(axis='y', labelsize=FS['f5_yt'])
            ax.set_xlim(-.70, len(names) - .449)
            top = max(x86.values()) * 1.17
            ax.set_ylim(0, top)
            ax.set_yticks(np.arange(0, top, .5))
            ax.yaxis.set_major_formatter(FuncFormatter(ratio))
            ax.grid(axis='y')
            fig.savefig(OUT / filename)
            plt.close(fig)
            print(f'{arch}: top={top:.3f} geomean={g:.4f} labeled={[round(v, 3) for v in ys if v >= threshold or v < .9]}')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    chars, x86, arm, _ = metrics.main_claims()
    fig2(chars)
    fig5(x86, arm)
