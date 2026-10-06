# #1160 English rebuttal working draft

工作稿，未提交。保留评审原话以便作者逐项修改。英文 Response 段共 713 whitespace words。问题、引文、表格和作者提示不是提交正文，不可整份粘贴；最终需合并并用 HotCRP 计数，硬上限 1000 words。证据/待核验/承诺见 analysis.md。

| Rev | Overall | Confidence/Notes | Key concerns | Rebuttal goal |
| --- | --- | --- | --- | --- |
| A | R1 4 accept | 未单列expertise | 无显式问题 | 保留支持 |
| B | R1 4 accept | 未单列expertise | recognizer safety | 清晰说明条件 |
| C | 1 reject | expertise2 | 写法/证明/收益 | 化解技术误读 |
| D | 2 weak reject | expertise3 | TCB/proof effort/gap | pivotal blocker |
| E | 4 accept | expertise3 | TCB/provenance/policy | 主要champion |

## Q1. What does BPF-Ext add to the TCB, and who must trust it? (D, E)

**D:** "the added KINSN modules inherently increase the TCB by introducing new native emits that the CPU executes directly."

**E:** "would a systems administrator actually "check the proofs" before deploying an extension?"

**Response:** BPF-Ext enlarges the trusted kernel surface: §4.3 identifies the generic lowering/restore/validation/dispatch path and operation-specific native emits in addition to the existing verifier/JIT. The verifier checks expanded eBPF, not the native emit's equivalence, so an incorrect emit can invalidate safety despite acceptance. The offline proof argument is not a load-time checker or a guarantee for arbitrary third-party modules. Administrators must still trust the privileged implementation and its supplier's assurance process; an abstract theorem does not automatically certify the deployed module.

## Q2. Is the module implementation really small enough to justify the trust claim? (D)

**D:** "To make matters worse, these modules are not small (the paper mentions almost 10k LOC for the implementation of the modules alone)."

**Response:** Table 4's 929 lines count the generic kernel-core addition, not the total new privileged code. Section 6.3's 9,765-line module tree includes shared headers, test-only modules, and operations beyond Kinsn's seven. This distinction explains the counts but does not remove module code from the attack surface or establish a complete emitter-only TCB audit.

## Q3. Why can a recognizer bug preserve kernel safety while producing a wrong rewrite? (B)

**B:** "a bug in the compile-time recognizer that rewrites programs to use the new operations therefore cannot make a verified program unsafe"

**Response:** The claim concerns verifier safety, not preservation of the source program's intended result. Each rewritten program is lowered and checked anew, with proof regions validated as single-entry/single-exit and without forbidden control flow (§4.3). A mistaken recognizer can change application behavior and still produce a verifier-safe program; safety then carries to execution only under the trusted core and native/proof-equivalence assumptions.

## Q4. Which semantics are proved, and how does the shared specification connect eBPF and native code? (C)

**C:** "Do you have proofs that this translation is correct? is it part of the TCB?"

**Response:** Section 5 describes small-step register-transfer models, with each eBPF expansion and native sequence refining a shared architectural specification. Register-only cases compare destination results, memory operations require relevant register/memory projections and unchanged other visible memory, and prefetch excludes cache effects. The cited LNSym work concerns ARM semantics, not an established source for the eBPF and x86 models. This ISA-local argument does not mechanically verify the complete C emitter, encoding, and loader; the eBPF/x86 model provenance and implementation correspondence remain to be substantiated.

## Q5. How difficult are the Lean proofs to construct and maintain, and are they available for inspection? (D)

**D:** "how hard is it to actually create and maintain these proofs for new operations or architectures (Q1)?"

**Response:** The submission gives the proof decomposition but no measured person-time or maintenance study, so a claim that new proofs are inexpensive would be unsupported. A new descriptor requires both ISA-local refinements and agreement with the implementation's operand, width, and memory behavior. The paper also does not expose a reviewer-accessible proof package, which limits independent inspection of the claimed coverage.

## Q6. Where do the microbenchmarks come from? (E)

**E:** "The paper does not cite the sources from which the microbenchmarks are extracted (S3.1)."

**Response:** Section 3.1 presents 27 computation kernels from networking, tracing, and security, but does not provide a per-benchmark source/revision mapping. The retained SipHash-like mixer's source describes deliberate construction of a rotate pattern, so naming an application family does not establish verbatim extraction from that application. Measurements are scoped to pure-bytecode benchmark kernels, excluding helper and map accesses, and the complete upstream provenance remains unverified.

## Q7. What distinguishes the conservative policy from full coverage? (E)

**E:** "The differences between the full and conservative policies should be better described, or made more obvious (if I overlooked an existing discussion)."

**Response:** The conservative ARM64 configuration disables bulk-memory, endian-fusion, and prefetch recovery while retaining rotate, extract, conditional-select, and bit-operations recovery. In Katran, only rotate and extract match, producing 20 and 1 sites. The coverage-max run executes rotate, extract, endian-fusion, bulk-memory, prefetch, conditional-select, and conditional-compare passes; the first five contribute 20, 1, 9, 26, and 6 sites, totaling 62. Figure 6 shows that this increased coverage lowers throughput from 1.073× to 0.995×.

## Q8. How should practitioners interpret regressions without an automated cost model? (D)

**D:** "Without a reliable, automated cost model to guide the recognizer, the system relies on manual policy tuning, making it brittle in production environments."

**Response:** Profitability is distinct from recognition and safety: more matched sites need not improve the critical path (§7.3). The two applications probe the policy surface in opposite directions. On Cilium, disabling descriptor families monotonically lowers throughput and raises BPF cost, so the coverage-max policy (4697 sites, 1.114×, 0.776× cost) beats the two-family-removed policy (3512 sites, 0.999×, 0.991× cost); coverage maximization pays here. On Katran it does not: the coverage-max policy applies more sites (62 vs 21) yet drops throughput from 1.073× to 0.995× and raises BPF cost from 0.941× to 1.006×. These paired probes reject a single global site-count objective, but do not establish an automated cost model, a universal family recommendation, or a causal explanation of every regression.

## Q9. Why are application gains much smaller than the native upper bound, and what remains? (D)

**D:** "Did you investigate what remains to be improved to recover most of the performance from native-in-kernel (Q2)?"

**Response:** Section 7.4 explicitly reports that the 1.074× Cilium gain recovers 5.4% of the 2.358× native-replacement gap, not the microbenchmarks' 42%. The native experiment uses whole-program replacements with unproved equivalence and a larger trusted surface, while Kinsn targets bounded idioms. Section 3.4 identifies register allocation and instruction scheduling as remaining code-generation opportunities, and real datapaths include helpers, maps, and tail calls; the paper does not measure a complete causal breakdown of the remaining gap.

## Q10. What do the microbenchmarks show beyond modest improvements? (C)

**C:** "This is also true of the micro-benchmark, which shows a modest reduction in a small subset of operations -- which is okay -- but does not explain why, or whether it is indicative of an interesting pattern or insight."

**Response:** Section 7.1 reports geometric-mean speedups of 1.242× on x86-64 and 1.222× on ARM64, not uniform per-program gains. Its architectural distinction is that x86 benefits track code-size reduction more closely, whereas ARM gains depend on target-specific idioms and critical-path placement. Regressions such as ARM64 FNV hashing at 0.862× are part of the result, supporting selective profitability rather than universal improvement.

## Q11. How do BPF-Ext, Kinsn, and the evaluation fit into one pipeline? (C)

**C:** "The split between KINSN and BPF-EXT is confusing."

**Response:** BPF-Ext is the extension mechanism: recognize an operation, expand it for verification, restore the accepted operation, and dispatch its native emit. Kinsn supplies seven hardware-idiom families to that mechanism; RQ1–RQ3 evaluate those families and their selection policies. RQ4 instead uses BPF-Ext for whole-program native replacement, illustrating the larger-trust performance ceiling rather than another Kinsn result.

## 作者核对提示（不属于回复正文）

此稿未承诺任何新实验、论文修改或公开材料。提交前需作者补齐 Lean 证明包位置、eBPF/x86 语义出处及 emitter 对应关系、proof effort 和 benchmark provenance；同时解释 Katran 原始 metadata 的 bpf_stats=true 与投稿 §7.2 的差异。Q7 仅使用已保留历史记录，不是本次新跑结果。引用为所示评审的逐字摘句，完整评审保留在本地私有记录，未随本次 Git 提交。
