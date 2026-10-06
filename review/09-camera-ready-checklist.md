# Camera-ready checklist — A4 revision plan → original draft

Scope-control doc for the ATC '26 #1160 camera-ready. Derived from the approved
revision plan (`00-hotcrp-comment-thread.md` @A4), the reviews (`01-atc26-reviews.txt`),
and the group-chat decision (2026-10-06).

## Governing principle: data freeze

**Base = the submitted/arXiv-v1 text (this repo's `sections/`). We restructure and
re-explain; we do NOT re-measure.**

- Every number in the camera-ready is the **reviewed value**. No experiment is re-run.
- The `revision/` folder's 2-vCPU cloud re-runs are **not used** — no evidence value
  (high variance, testbed bottlenecked off the application), and the originals were
  never retested on their own (8-vCPU desktop / t4g) config, so they are not "wrong."
- Consequence: the shepherd "summary of changes" can state *"results unchanged from
  the reviewed version; paper restructured per the approved plan."* Nothing to disclose.
- Any analysis that needs a measurement the reviewed paper did not already contain is
  itself a **new experiment** → in-scope only if A4 named it, and even then it must be
  produced on the **original testbed**, never the 2-vCPU platform.

## Frozen numbers (use these verbatim; `sections/` already contains them)

| Result | Reviewed value | Source file |
|---|---|---|
| Microbenchmark geomean | x86-64 **1.242×** (−19.47%), ARM64 **1.222×** | `sections/7-evaluation.tex` |
| Micro headline framing | up to **24%** (x86) / **22%** (ARM) | `sections/0-abstract`, `1-introduction` |
| Gap to native recovered (micro) | up to **42%** | `1-introduction`, `7-evaluation` |
| Native code size reduction | **22.8% / 12.1%** | `sections/3`, `7` |
| Cilium throughput (KINSN) | **1.074×** (1.11× with bulk-memory disabled) | `7-evaluation` |
| Katran policy contrast | conservative **1.07×** vs full-coverage **0.995×** | @A1/@A4 |
| App headline framing | up to **12%** | `0-abstract`, `1-introduction` |
| Cilium native "upper bound" (RQ4) | **2.358×**; BPF cost 488.7→262.3 ns (1.86×); KINSN recovers 5.4% of gap | `7-evaluation` |
| TCB sizes | core **929 LOC**; native emit a few dozen LOC/op; ~10K = whole module tree | @A1 |

## A4 commitments → where in `sections/` → action → data source

### Group 1 — Clarify mechanism vs. operations (the one big rewrite)
Reviewer C; Shepherd @A2. **This is the only section that gets a ground-up reorg.**

- [ ] Merge `4-bpfext.tex` + `5-kinsn.tex` into **one design section**: introduce the
      BPF-Ext mechanism first, then follow **one KINSN operation** end-to-end
      (recognition → verification → native execution). *Port structure from
      `revision/sections/4-design.tex`; keep the original's story/terms.* — **no data**
- [ ] Move implementation detail out of design into the implementation section
      (`6-implementation.tex`). — **no data**
- [ ] In `7-evaluation.tex`, state explicitly: **RQ1–RQ3 evaluate KINSN** hardware ops;
      **RQ4 evaluates whole-program native replacement** loaded via BPF-Ext, and name
      RQ4's **extra trust assumptions**. — **no data (reuses 2.358× as-is)**

### Group 2 — Safety from verification through native execution
Reviewer D (attack surface / 10K LOC), Reviewer C (proof semantics), Shepherd @A2.

- [ ] In the design section: what the verifier checks, what native execution adds, which
      of the 4 components are in the TCB (core + native emit) and which are not
      (recognizer + proof-seq generator). — **no data**
- [ ] Describe moving the ARM64-rotate temp-register-read check **into the kernel core**
      (no longer trusts the userspace recognizer). *Artifact code must match.* — **no data**
- [ ] In `6-implementation.tex`: report **added trusted code size by component** (929 /
      few-dozen / ~10K breakdown) and explain why re-verifying the eBPF program does not
      rule out bugs in the kernel modules. — **data = @A1 LOC counts, no re-measure**
- [ ] Walk one operation's **proof**: eBPF proof-sequence and native emit each satisfy the
      same bit-vector spec (two lemmas); state semantics (ARM64 follows **LNSym**),
      assumptions, coverage, and that **no cross-semantics translation** is trusted; note
      the model↔emitted-machine-code gap. — **no data**
- [ ] Artifact ships the **Lean proofs** + checking instructions. — **no data**

### Group 3 — Performance differences & policy selection
Reviewer C (why / intuition), Reviewer D (2.358× vs 1.074× worth it?), Reviewer E (policies).

- [ ] `7.1`: analyze **representative speedups AND regressions**, relating instruction
      changes to results per architecture. — **data = reviewed micro results only.**
      ⚠ A recompilation-vs-rewriting split or rotation ablation (as in `revision/`) is
      allowed ONLY if reproducible on the **original testbed**; otherwise drop or state
      qualitatively. Do not import 2-vCPU-derived ablation numbers.
- [ ] `7.3`: add **policy × operation-families table**; use Cilium/Katran to explain how
      measurement guides policy and **why more matched sites need not raise throughput**
      (Katran 1.07× conservative vs 0.995× full), plus limits of manual tuning.
      — **data = reviewed values**
- [ ] `7.4`: add a **profile of the Cilium native run** vs baseline to explain the
      remaining gap; discuss whether the gains justify the added code/trust. — **profile
      must come from the ORIGINAL Cilium setup, not 2 vCPU.** If that profile data does
      not exist yet, this is the one item that may need a run — on the original config.
- [ ] `sections/3` + `7`: state **metric and baseline** for every comparison; keep
      microbenchmark **execution time** distinct from application **throughput**. — no data

### Group 4 — Benchmark sources & artifact
Reviewer E.

- [ ] `3-characterization.tex` §3.1: state **12 reimplemented from production** (Katran,
      Cilium, BCC, bpftrace, Tetragon, Tracee, OTel eBPF profiler) + **15 synthetic**
      (packet parsing, hashing, search). — **no data**
- [ ] `10-appendix.tex`: describe each benchmark's source/purpose. — **no data**
- [ ] Artifact: microbenchmarks + system implementations + build/run instructions. — no data

### Cross-cutting
- [ ] Add citation to **Shahinfar et al., eBPF'26** (shepherd FYI @A6; contrast as
      post-verification userspace native optimization that must trust the optimizer).
- [ ] Terminology/citation consistency; fix writing & formatting.
- [ ] Keep abstract/intro = **targeted clarity edits only**; preserve the original story
      and the **TCB-minimization insight** (the cross-cutting reviewer concern, @A1).
- [ ] Draft to shepherd **by Fri 2026-10-09** with a **summary of changes** (@A8); final
      **2026-10-16**.

## Port from `revision/` vs. drop

**Port** (plan-required, data-safe):
- Restructured design (`4-design.tex`) — adopt the organization, re-attach original story/numbers.
- Policy × families table; metric/baseline statements; RQ1–3 / RQ4 split.
- Discussion of KINSN/optimization selection — *optional*, keep only if space; it partly
  discharges the §7.3 duty (Reviewer C's "intuition for policy selection").

**Drop** (out of scope / unsupported):
- The rewritten abstract & introduction narrative (flattens the TCB insight).
- All **2-vCPU re-run numbers** (micro 1.17×, Cilium 0.970, Katran 1.006, native ~1.005×,
  35.6/34.2 ms prep cost, 15.1/12.9% size).
- Wholesale rewrites of background / motivation / related work beyond the edits above.

## Explicitly NOT doing
- Re-running any experiment on the 2-vCPU cloud platform.
- Changing any headline number from the reviewed version.
- Adding experiments/content the reviewers did not ask for and A4 did not promise.
