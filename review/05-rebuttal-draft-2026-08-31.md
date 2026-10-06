We thank all reviewers for their careful reviews. Following Reviewer E's comment, we address the TCB first, then the Lean 4 proofs (semantics: C; effort: D-Q1), then performance (D-Q2), policy selection, and presentation.

[TCB] (B, D, E)

Reviewer D is concerned that the ~10k-line modules enlarge the TCB and the attack surface; Reviewer E notes that equivalence between a native emit and the verified bytecode cannot be checked at load time; Reviewer B asks why a recognizer bug cannot break safety.

Answer: BPF-Ext adds exactly two things to the TCB: the one-time 929-line kernel-core patch, and each operation's native emit (each emit produces one to a few machine instructions; [X] lines across all emits). No other new code needs to be trusted, because the unmodified verifier re-checks the entire program on every load.

To D: the ~10k figure counts the whole module tree. Test-only modules, shared headers, proof-sequence routines, and registration code are outside the TCB: proof-sequence output is re-checked by the verifier, and test and registration code produces no executed instructions. The trusted portion is the [X] lines of native emits. For comparison, the existing kfunc route trusts entire native function bodies.

To B: the sentence holds because of re-verification. On every load, the verifier lowers each extended instruction to its proof sequence and runs its unchanged, complete analysis on the lowered program. A wrongly rewritten program either fails verification, or has passed the complete analysis and is therefore safe. A recognizer bug has the same consequences as a userspace compiler bug: it can compute the wrong result; it cannot be unsafe.

To E (and D): we agree the gap named in Section 4.3 is real — emit/proof-sequence equivalence cannot be checked at load time. Closing that gap is exactly the obligation the Lean 4 proofs discharge; see the next item.

[Lean 4 proofs] (C; D-Q1)

Reviewer C asks which semantics the proofs rest on and whether the cross-ISA mediation is trusted; Reviewer D notes the proofs are not provided and asks (Q1) how hard the proofs are to build and maintain.

To C: the proofs live entirely in Lean and rest on three artifacts: a small-step eBPF semantics we formalize ourselves; one native semantics per architecture (ARM64 ported from LNSym; x86-64 from [source]); and one hardware-independent specification per operation. There is no semantic translation to trust: the specification is an independent third object, and we machine-check two refinement lemmas — the eBPF expansion refines the specification, and the native sequence refines the specification. The residual trust is the fidelity of the two semantic models to the real systems, plus Lean's kernel.

To D-Q1: one operation equals one specification plus two lemmas, about [X] Lean lines and [Y] person-days; a new architecture adds only one native-side lemma against the existing specification. The proofs will be released with the artifact.

[Performance and the remaining gap] (C, D; D-Q2)

Reviewers C and D find the ~1.07x end-to-end gains small; D asks (Q2) where the remaining gap to the 2.358x native-in-kernel ceiling lies.

To Q2: we did investigate; Sections 3 and 7.4 give the decomposition. The remaining gap has two parts. The first part is runtime mechanisms — helper calls, map accesses, and tail calls — where production datapaths spend most of their time; no code-generation improvement reaches this part. The second part is cross-instruction optimization such as register allocation and instruction scheduling; recovering the second part requires an optimizing compiler in the kernel or trust in whole-program replacements, and either costs far more TCB than per-operation emits. Kinsn deliberately takes only the share that a minimal, provable trust increment can take: 42% of the gap on pure-codegen microbenchmarks, diluted to ~1.07x end to end by the two parts above. We believe this gain is worthwhile: obtaining it requires no verifier change and its trust increment is covered by proofs; and the paper's contribution is the mechanism itself — Section 7.4 reaches the other end of the design space (2.358x) with the same mechanism, precisely to mark the cost of both ends.

[Policy selection] (C, D, E)

Reviewer C asks how a reader builds intuition for selecting families; Reviewer D notes the lack of an automated cost model and calls manual tuning brittle; Reviewer E notes the conservative policy is undefined.

Answer: a replacement pays off when the dynamic work it saves exceeds the replacement's overhead and the site lies on the throughput-dominating path. Matched-site count reflects neither condition, which is why the coverage-max policy regresses on Katran. The conservative policy means [definition]; the missing definition is our oversight, and the revision defines it at first use (E). We agree with D's direction that an automated cost model is right; the descriptor already carries the static instruction counts of both forms, and the recognizer has each site's context, so the inputs of the criterion are readily available.

[Presentation] (C, E)

We thank Reviewer C for the careful reading and agree that Sections 4 to 7 need restructuring. Section 4 will present only the design, namely the dual forms and the trust argument; descriptor layout, lowering, and restore move into the implementation section. Family-selection policy, bulk_memory, and the conservative policy will be defined at first use, and the introduction will state that BPF-Ext is the mechanism and Kinsn is the instantiation. Microbenchmarks will be individually cited and described in an appendix (E); the benchmarks, code, and all proofs will be released with the artifact.