# ATC '26 paper #1160 — HotCRP comment thread (A1–A8)

Copied from https://atc26.hotcrp.com/u/1/paper/1160 on 2026-10-06. HotCRP showed
relative times for A4–A8; approximate absolute dates are added in brackets.

Key dates: revision plan due 2026-09-25 (posted, approved). Draft of the revised
paper to the shepherd by Friday 2026-10-09 (authors committed to this in A8, with
a summary of changes from the reviewed version). Final version due Friday
2026-10-16.

---

## @A1 — Reviewer E (meta comment), Aug 27

An issue that cuts across the reviews is BPF-Ext's effect on the eBPF trusted computing base.
In the author response to the reviews, please address this concern in particular. It would also be helpful to clarify aspects of Kinsn's Lean 4 proofs, e.g., the semantics on which they are based (cf. Review C) and the effort required to complete them (cf. Review D).
Please respond to other questions/issues raised in the reviews as space permits.

## Response — Yusheng Zheng (Author), Sep 3, 998 words (as submitted)

We thank the reviewers for their thoughtful and constructive comments. The main concern raised across the reviews is the effect of BPF-Ext on the trusted computing base of eBPF; we address it first and in detail, followed by the question on the Lean proofs and the questions on the evaluation. We will incorporate the suggestions on presentation in the revision.

1. Trusted computing base

Reviewers B, D, and E ask whether BPF-Ext enlarges the trusted computing base of eBPF. It does, but only by two of its four components, and both are bounded in size. The four components are the recognizer, the proof-sequence generator, the native emit, and the kernel core. The trusted computing base here means the code that can cause the verifier to accept a program that is unsafe at run time. Of the four components, the kernel core and the native emit are inside it; the recognizer and the proof-sequence generator are not.
The recognizer and the proof-sequence generator are outside the trusted computing base because everything they produce is bytecode, and the verifier checks all bytecode on every load. The recognizer marks where an operation applies; before verification, the kernel core replaces each mark with the proof sequence the generator produces; the unchanged verifier then checks the whole program. A wrong mark or a wrong proof sequence is rejected, or yields a safe program that computes something else. As kernel code, the generator must be free of ordinary kernel bugs, like any kernel module or kfunc; BPF-Ext does not change that.
The kernel core and the native emit are inside the trusted computing base, and both are small. The kernel core is 929 lines that substitute proof sequences before verification, restore the marks afterwards, check that each substituted region has a single entry and exit, and call the native emit at JIT time; it does no analysis and does not change when operations are added. The native emit of an operation is a function of a few dozen lines that writes one or two machine instructions; it is the only per-operation code whose output the verifier does not see. The almost 10K lines counted in the paper are the whole module tree, mostly tests, operations outside Kinsn, and proof-sequence generators; only the native emit functions affect the verifier's guarantee.
The native emit needs one property, and that property can be proved: the machine instructions it produces compute the same result as the proof sequence on every register and stack slot the program can read afterwards. Stated in terms of the JIT, the code the native emit produces must behave the same as the code the JIT produces when it compiles the proof sequence itself, which is what happens for an operation that has no native emit. The Lean proofs, described next, establish it. For rotate on ARM64 the property currently also relies on the recognizer choosing a temporary register that no later instruction reads; the revision moves that check into the kernel core, which already has the verifier's liveness information.

1. Lean proofs

Reviewer C asks which semantics the proofs rest on and whether a translation between them is trusted. Both sides are modeled in one Lean development with semantics we wrote ourselves, and the two sides meet in a shared specification through two proved lemmas; nothing is translated, and nothing is assumed beyond the semantics and Lean.
The proof checks the property of Section 1 directly, without any translation between the two instruction sets. The proof code, written in Lean 4, defines the semantics of the eBPF instructions that proof sequences use and of the native instructions that emit functions produce, over 64-bit registers; the ARM64 definitions follow LNSym, AWS's Lean model of ARM64. Each operation has a specification, a pure function on bit-vectors. One lemma shows that the proof sequence leaves the specification's value in its destination register, and a second lemma shows the same for the native instructions; equality of the two results follows from the two lemmas. What is trusted is therefore the two semantics and Lean itself; the specification need not be trusted, since the two lemmas give equality whatever it says. The next step is to connect the proof to the bytes that the emit function writes, and we will release the proof code with the artifact.

1. Other points

The remaining gap to native code lies in parts of the datapath that instruction selection cannot reach, so it is outside what Kinsn targets. On the microbenchmarks, which isolate instruction selection, Kinsn recovers 42% of the gap on x86-64; the rest is cross-instruction optimization such as register allocation. On Cilium the gain is 1.07x, or 1.11x with bulk copy disabled, because a real datapath spends most of its time in helper calls, map accesses, and tail calls. The revision adds a profile of the native run to confirm this attribution (Reviewer D).
Operation families are chosen by measurement, and the revision makes the selection rule explicit (Reviewers C, D, E). A family is the descriptors of one operation, and a policy is the set of families enabled for a workload. The conservative ARM64 policy enables rotate, bit extract, and conditional select; on Katran it gives 1.07x, while enabling every family applies three times as many sites and gives 0.995x, which is why the rule matters.
The microbenchmarks are derived from production programs and from synthetic kernels, and the revision cites each source (Reviewer E). Twelve of the 27 re-implement kernels from Katran, Cilium, BCC, bpftrace, Tetragon, Tracee, and the OpenTelemetry eBPF profiler; the other fifteen are synthetic kernels for packet parsing, hashing, and search. We will release them with the artifact.
We will restructure the design sections so that the design is presented once, end to end, before any implementation detail (Reviewer C). The revision merges Sections 4 and 5 into one section that follows a single operation from the recognizer to the proof, moves implementation detail to Section 6, and defines every term where it first appears.

## @A2 — Shepherd, Sep 16: Discussion Summary

Members of the program committee discussed this submission and the authors' response online. The discussion was engaging but brief.
The authors' response was helpful and informative, and it allowed the reviewers to be comfortable in accepting this paper.
The reviewers noted the authors' promise to "restructure the design sections," and they agreed that this should be done. The reviewers also discussed the fact that the Lean proofs are missing from the submission, as well as the authors' pledge to include the proofs in the paper's artifact. Inclusion in the artifact is very good and should be done. The reviewers expressed hope that the planned paper restructuring will also make it possible for more information about the proofs to be placed in the paper itself. This will be a request from the paper shepherd to the authors.
Please see the individual reviews for additional suggestions for clarification and improvement.

## @A3 — Shepherd, Sep 22: Request for Revision Plan

tl;dr: Authors, please post your proposed revision plan here by Friday, September 25.
Hello, authors! Congratulations on having your paper accepted to the ATC '26 conference!
I am the shepherd for your paper. My job is to help you with the paper-revision process, leading to the final version of your paper for publication and presentation at the conference. The final version of your paper is due on Friday, October 16. A draft of your revised paper is due to me sometime before that.
The first step of the process is for you to come up with a revision plan, based on the reviewers' feedback and revision ideas that you previously proposed in your response to those reviews.
Can you (again) take a look at the review comments and discussion summary, write down a plan for addressing those comments, and post that plan here? It would perhaps be effective to copy the review comments into a file and insert your responses inline, so that it is clear how you propose to address the feedback point-by-point. You can share the file here by adding it as an attachment to a HotCRP comment.
If possible, I would like to receive your proposed revision plan not later than Friday, September 25. Do you think that you can post your plan here by that date?
Again, congratulations on your accepted ATC '26 paper! I very much look forward to working with you between now and the final paper deadline to help you polish your paper.

## @A4 — Zhengjie Ji (Author), [~2026-09-26]: Revision plan

Dear Reviewers and Shepherd,
Thank you for your suggestions. We will focus the revision on restructuring the design sections, adding proof details, and explaining the performance results.

1. Clarify the relationship between the extension mechanism and its operations

The paper mixes design and implementation details and does not clearly explain the overall pipeline, the relationship between BPF-Ext and KINSN, or what each experiment evaluates.
Shepherd @A2: The reviewers noted the authors' promise to "restructure the design sections," and they agreed that this should be done.
Reviewer C: The split between KINSN and BPF-EXT is confusing. I assume the point is to say that the "extended instructions" are a general idea, while KINSN is a particular set of idioms that you identify and support using the pipeline you introduce. [...] Furthermore, BPF-EXT appears to be the more interesting and generalizable idea or insight, given my reading of the current text, yet the evaluation questions focus on KINSN, other than RQ4, but then, looking at 7.4, the text actually discusses evaluating KINSN as an instantiation!
We will merge Sections 4 and 5, first introduce the BPF-Ext extension mechanism, and then follow one KINSN operation through recognition, verification, and native execution. Implementation details will move to Section 6. In Section 7, we will clarify what each research question evaluates: RQ1–RQ3 evaluate KINSN's hardware operations, while RQ4 evaluates the performance of whole-program native replacements loaded through BPF-Ext. We will also state the additional trust assumptions required by RQ4.

1. Explain safety from verification through native execution

The paper does not adequately explain how BPF-Ext ensures the safety of native extensions, particularly which components must be trusted and what the formal proofs cover.
Reviewer D: Introducing new, architecture-specific kernel modules enlarges the attack surface; a single bug in any of these hand-written native emits will bypass the verifier and compromise kernel safety. To make matters worse, these modules are not small (the paper mentions almost 10k LOC for the implementation of the modules alone).
Reviewer C: Your lemma that states the eBPF expansion and the native sequence for the same operation refine the same spec crosses over multiple semantics. [...] Do you have a translation of the eBPF semantics and the native instruction semantics to that shared specs? Do you have proofs that this translation is correct? is it part of the TCB?
Shepherd @A2: The reviewers also discussed the fact that the Lean proofs are missing from the submission, as well as the authors' pledge to include the proofs in the paper's artifact. Inclusion in the artifact is very good and should be done. The reviewers expressed hope that the planned paper restructuring will also make it possible for more information about the proofs to be placed in the paper itself.
In the design section, we will explain what the verifier checks, what additional checks and proofs native execution requires, and which components must be trusted. For ARM64 rotate, we will move the check for subsequent reads of the temporary register into the kernel core, so that this safety condition no longer depends on the userspace recognizer. Section 6 will report the size of the added trusted code by component and explain why re-verifying an eBPF program does not rule out implementation bugs in the kernel modules themselves. Using one operation as an example, we will show how the eBPF and native instruction sequences are each proved to satisfy the same specification, and how these proofs establish their equivalence. We will describe the instruction semantics, proof assumptions, and coverage, and address whether translation between the semantics is needed. We will also check the correspondence between the instruction models and the machine code generated by native emits, and state any gaps in coverage. Drawing on the development of this operation, we will explain the challenges of developing proofs for new operations or architectures, what can be reused, and the maintenance work required; the artifact will provide the Lean proofs and instructions for checking them.

1. Explain performance differences and policy selection

KINSN's application gains are modest and variable, and the paper does not adequately explain why, how optimization policies are chosen, or whether these gains justify the added complexity and security risks.
Reviewer C: [...] the policy (i.e., the choice of which sequences to replace with idioms?) is a double-edged sword. The paper, however, does not explain why, and does not help the reader or a practitioner develop an intuition for how they could select (or implement their own) families that would be a good fit for their loads. This is also true of the micro-benchmark, which shows a modest reduction in a small subset of operations -- which is okay -- but does not explain why, or whether it is indicative of an interesting pattern or insight.
Reviewer D: The authors' own "native-in-kernel upper bound" experiment shows that directly compiling the Cilium datapath to native code yields a 2.358x throughput improvement over stock eBPF. By comparison, KINSN's 1.074x throughput gain on Cilium recovers only a tiny fraction (5.4%) of that total available performance gap. This reveals that KINSN's improvements are too small compared to the total performance gap to warrant the added architectural complexity and security risks. Did you investigate what remains to be improved to recover most of the performance from native-in-kernel (Q2)?
Reviewer E: The differences between the full and conservative policies should be better described, or made more obvious (if I overlooked an existing discussion).
We will use the microbenchmarks and application experiments to explain the differences in performance gains. Section 7.1 will analyze representative speedups and regressions, relating instruction changes to results across architectures. Section 7.3 will include a table of the operation families enabled by each policy and use the Cilium and Katran results to explain how measurements guide policy selection, why more matched sites may not improve throughput, and the limitations of manual tuning. Section 7.4 will add a profile of the Cilium native run and compare it with baseline measurements to investigate the remaining performance gap. We will discuss whether the measured application gains justify the added code and trust requirements described in Section 6. In Sections 3 and 7, we will state the metric and baseline for each comparison, distinguishing microbenchmark execution time from application throughput.

1. Document benchmark sources and release the artifact

The microbenchmarks lack source citations and descriptions of how they were constructed, and the reviewers would like the benchmarks and system code to be released so that the results can be reproduced.
Reviewer E: Unless I overlooked it, the paper does not cite the sources from which the microbenchmarks were derived. The paper should obviously do so, and I think the paper should also describe the microbenchmarks in an appendix as well. I hope that if this paper is accepted, the authors will make the microbenchmarks publicly available (and BPF-Ext and Kinsn as well!).
We will correct Section 3.1 to state that 12 benchmarks are reimplemented from production programs and 15 are synthetic, and add an appendix describing each benchmark's source or purpose. The artifact will provide the microbenchmarks and the system implementations used in the paper, along with build and run instructions.
We will also make terminology and citations consistent and correct writing and formatting errors. We will send you a revised draft for review before the October 16 final deadline.
Please let us know if any further changes are needed. Thank you for your guidance.

## @A5 — Shepherd, [~2026-09-29]

Authors: I have read through your revision plan (@A4), and it is very good and on track. Thank you for being so responsive to the reviewers' feedback!
I particularly like the idea of using a single instruction as an example to show how the various parts of eBPF work.
Carry on!

## @A6 — Shepherd, [~2026-09-29]

Authors: I happened to notice the following paper, which was just published, and which may be related to your work. (This is just FYI.)
Farbod Shahinfar, Aurojit Panda, and Gianni Antichi. 2026. Fun Optimizations for eBPF Programs and How to Enable Them. In Proceedings of the 4th Workshop on eBPF and Kernel Extensions (eBPF'26). Association for Computing Machinery, New York, NY, USA, 41–49. https://doi.org/10.1145/3837779.3838161

## @A7 — Shepherd, [~2026-10-05]

Hi, authors! This is a quick reminder of what I wrote previously (@A3):
The final version of your paper is due on Friday, October 16. A draft of your revised paper is due to me sometime before that.
When can you provide me with an in-progress draft of your revised paper? The PC chairs have suggested that this be provided by Friday, October 9. A few days later would be OK with me, but I do need time to read and give you feedback, if necessary.
Thanks!

## @A8 — Zhengjie Ji (Author), [~2026-10-05]

Dear Shepherd,
We will send you a camera-ready draft by Friday, October 9. We will also include a summary of the changes from the reviewed version to make the revisions easier to follow.
Thank you for your time and guidance.
