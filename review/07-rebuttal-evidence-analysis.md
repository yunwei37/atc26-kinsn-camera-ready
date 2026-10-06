# BPF-Ext #1160：rebuttal 分析

## 工作边界与来源

2026-08-31；ATC 2026；HotCRP single-document response；硬上限 1000 words；截止 2026-09-03 04:59:59 America/Los_Angeles (=11:59:59 UTC)。初轮只起草；本轮追加授权仅为 Git 提交，不保存或提交 HotCRP response，不修改论文或代码。

使用 lab:/home/yunwei37/workspace/my-paper-work/academic-writing-skills/domain-skills/rebuttal/SKILL.md 及 references/workflow.md。输出只有本分析及 rebuttal.md；问题、证据、承诺、审计都在本文件。评审先于论文进入上下文，因此不声称完成 blind review；不执行 iter-review-critique 的盲审循环。

2026-08-31，作者明确授权将本文件与 rebuttal.md commit/push 到此私有论文仓库。完整评审原文仍只保留在本地私有记录。精确投稿 PDF 由已登录 Chrome 下载并核对 HotCRP checksum。读远端源码只作证据，不重跑实验、不启动服务、不编译代码。


投稿: https://atc26.hotcrp.com/u/1/paper/1160
PDF: HotCRP 精确投稿版本（文件名 atc26-paper1160.pdf，使用下述 SHA256 标识；PDF 不随本次提交）。
SHA256: 0149a511ba5c676ce31bf5550802cf3881dcef32bf93c7c63a789a749ab45f73
lab论文/研究仓库: /home/yunwei37/workspace/bpf-benchmark/docs/paper/；当前main.pdf SHA256 02dc0f21ba7851234e687840db11bfed6c4c0a1514fba3c2c79b1f43fc396901，与投稿不同。现仓库正在做speculative optimizer，不能用新结果回答旧BPF-Ext投稿。

## 评审格局与策略

| Reviewer | 分数 | Expertise | 立场/目标 |
| --- | --- | --- | --- |
| A | R1 4 Accept | 未单列 | 支持；无显式问题 |
| B | R1 4 Accept | 未单列 | 支持但质疑recognizer safety，必须回答 |
| C | Overall1 Reject | 2 Low | blocker；设计/证明解释与收益意义 |
| D | Overall2 Weak reject | 3 Mild | pivotal；TCB大小、proof effort、性能gap |
| E | Overall4 Accept | 3 Mild | 主要champion，评论深入并写汇总；严肃对待安全和可复现问题 |

粗略主观判断55%-70%，非统计概率；三支持不等于稳收。优先防止TCB或证明过度主张让E转负，争取D看到条件化安全论证，向C解释mechanism与instance不必扩大性能结果。

## Concern board

| issue_id / reviewer | concern / type | severity | stance / priority | mode / evidence | draft / status |
| --- | --- | --- | --- | --- | --- |
| D-C1; E-C1; META1 | 内核模块扩大TCB、native emit绕过verifier、实际部署信任 | critical | all/pivotal | assumption-hierarchy; §4.3; code audit | Q1 / answered conditionally |
| D-C2 | 9765LOC是否真的minimal | major | negative/pivotal | §6.3包括test/helpers/其它ops；不等于zeroTCB | Q2 / answered |
| B-C1 | recognizer bug为何不使内核unsafe | critical | positive/pivotal | §4.3 safety vs original semantics | Q3 / answered |
| C-C5a; META2 | BPF/native语义出处，是否自定义BPF模型 | critical | negative/pivotal | §5; bounded search found no Lean package | Q4 / needs-user-input |
| C-C5b | shared spec、refinement、translation correctness与TCB | critical | negative/pivotal | §5; implementation/proof correspondence unverified | Q4 / needs-user-input |
| D-Q1; META3 | proof effort/maintenance、新ISA有多难 | major | negative/pivotal | no person-time or proof logs found | Q5 / needs-user-input |
| D-C3 | proofs缺失artifact；如何review | critical | negative/pivotal | no verified proof location; no release promise | Q5 / needs-user-input |
| E-C2 | admin是否检查proof、一般extension安全 | major | positive/pivotal | §8 offline proof，不是runtime proof checker | Q1 / answered |
| E-C3 | benchmark来源及公开、附录 | major | positive/pivotal | §3.1不足，查source manifest | Q6 / open |
| E-C4; C-C3 | conservative vs full具体families / bulk_memory | major | positive/pivotal | Fig6 + historical report/plan located | Q7 / answered |
| C-C4; D-C4 | policy brittle/cost-model/负收益解释 | major | negative/pivotal | §7.3 concrete tradeoff; no automated model claim | Q8 / answered |
| D-C5 | end-to-end收益小是否值得复杂度 | major | negative/pivotal | bounded trust tradeoff + exact 1.074/1.073/1.114 | Q9 / answered |
| D-Q2 | 2.358上限相比5.4%gap，余下改进在哪里 | major | negative/pivotal | §3.4/7.4; no measured causal breakdown | Q9 / answered with limit |
| C-C4b | micro结果及architecture insight | major | negative/pivotal | §7.1 geomean vs individual/regression | Q10 / answered |
| C-C1 | design vs incidental details, flow confused | major | negative/pivotal | §4 recognition→lower→verify→restore→emit | Q11 / answered |
| C-C2 | BPF-Ext vs Kinsn, RQ4是否whole program | major | negative/pivotal | §7.4 exact design-space boundary | Q11 / answered |

## 证据与防反噬

- §4.3 generic core新增929LOC(Table4)，包括lower/restore/validation487、BTF139、ARMJIT121、x86JIT97、headers85。不得说totalTCB929或verifier文件零改动；是分析transfer functions复用。
- §6.3模块树9765LOC包含14x86/11ARM modules、shared headers、test-only、七族以外ops。不能因为不是全部native emitter就把privileged C实现排除TCB。
- Runtime verifier只验证proof expansion，不检查native emit等价；proof offline不在kernel检查。安全依赖native emit忠实实现对应proof，并依赖generic core、existing verifier/JIT、proof model fidelity。错误recognizer可改变application semantics而仍kernel-safe。
- §5 partial semantics: register-only destination、memory operations relevant registers/memory+untouched rest、prefetch architectural no-op，cache/timing不在模型。必须核实real emitted byte encodings与Lean模型链接，不能声称形式验证整个模块加载器。
- 外部source已核实 https://github.com/leanprover/LNSym ：它是Armv8 symbolic simulator，不是eBPF/x86完整语义来源。当前README不能证明本项目复用了哪些definition。
- https://docs.kernel.org/bpf/kfuncs.html 支持kernel functions/BTF annotations背景，不能用它证明本项目equivalence。
- §7.1 1.242/1.222是27case geomean，execution-time reductions19.47%/18.17%，不能说“每个case最多24%”或所有workload都受益。ARM的0.862和0.966 regression不隐藏。
- Fig6 Cilium是单调family ladder：coverage-max 4697 sites=1.114/0.776；no-prefetch 4086=1.055/0.871；no-bulk 4136=1.037/0.918；no-bulk+no-prefetch 3512=0.999/0.991。site越少吞吐越低、cost越高，故Cilium上coverage-maxization成立。Katran相反（见下），不得再用“Cilium full→no-bulk”配对叙述。
- Katran conservative21sites1.073/BPFcost0.941；full62sites0.995/BPFcost1.006。已找回exact selected family list，见下述原始report/plan；metadata与stats-disabled叙述差异仍需作者对齐。
- §7.4 upper bound是同样Cilium setup但全native replacement，113替換/22pass-through，源码相同但equivalence未证明，更大TCB。5.4%gap recovery用(1.074-1)/(2.358-1)，与micro42%分母不同。helpers/maps/tailcall+regallocation/scheduling是剩余方向，不是本次测得的百分比分解。
- 当前bpf-benchmark发展到新stock-kernel optimizer。只读检查旧paper证据；不运行make或维护脚本，不混入后续结果，不公开评审。

## 结构与预算

11Q：TCB、LOC、recognizer、安全语义证明、proof effort/artifact、benchmark来源、exact policy、profitability、意义与ceiling、micro、pipeline。约950词回应正文，quotes和summary非提交内容。proof effort没有日志则诚实不量化，禁止编造几天/多少LOC就代表person-hours。

## Verification checklist

- [x] 投稿13页全部读完；Fig5/6可视确认。
- [x] 对比提交/remote PDF发现版本不一致。
- [x] 对相关目录及可达历史做有界 Lean 搜索，未找到；这不证明其他位置不存在。
- [ ] sorry/axioms、model provenance、proof-to-emitter correspondence：无证明包，无法核验。
- [x] 历史conservative/full policy已核验。
- [ ] 27micro逐项upstream provenance未完成；发现人为构造pattern的源码证据。
- [x] 独立对抗评审与三轮精修；实证缺口保留。

## Commitment ledger

already-done: 当前草稿，不是新增proof或实验。
approved-for-rebuttal: 无。
future-work-only: cost model、full native equivalence、更多ops，不承诺。
needs-user-input: proof/benchmark artifact发布许可及proof effort来源；最终作者response提交。

## Adversarial review 与三轮记录

2026-08-31 独立子代理 audit_bpfext 完成投稿、评审、工作稿及有界远端证据审查；结论 needs revision / not paste-ready。已修正可据证据关闭的部分，不把未找到证明包当作已完成形式化验证。

历史记录，均相对 lab:/home/yunwei37/workspace/bpf-benchmark：

- docs/tmp/kop_ablation_20260605_summary.md:45-61 对应 conservative=corpus/results/aws_arm64_corpus_20260605_080836_924256（21sites,1.073 throughput,0.941 BPFcost）、full=corpus/results/aws_arm64_corpus_20260605_094729_221231（62,0.995,1.006）。
- conservative 目录 details/loadtime-reports/katran.jsonl:6：bitops/cond_select/extract/rotate 启用；bulk_memory/endian_fusion/prefetch 禁用；LLVM all=disable。实际仅rotate20+extract1命中，不是仅启用两族。
- full 目录 details/loadtime-plans/katran.json:3-37 顺序 rotate,extract,endian_fusion,bulk_memory,prefetch,cond_select,ccmp；report:36-40 对应命中20+1+9+26+6=62，后两族0。Q7是旧记录解释，不是本轮新实验。
- conservative 目录 metadata.json:2 为 bpf_stats=true；投稿§7.2称throughput测量关闭stats。两者关系未解释，需作者核对；不能自行断言结果失效，也不能强化“已排除stats开销”。
- 快照 f5aed4c46 的 micro/programs/siphash_rotate64_mixer.bpf.c:3-17 明确构造 rotate-pattern；docs/tmp/micro-bench-status-20260520-archive.md:116-128 称workload-pattern/cilium-shaped等。发现27case源码及manifest不等于完成27条真实upstream抽取证明。
- 快照 f5aed4c46 的 module/x86/bpf_x86_rotate.c:129-181,372-438,472-494 可核对eBPF expansion/native emitter/descriptor配对；module/include/kinsn_common.h:185-202 是BTF registration，不是proof checking。这只能证实两条实现路径存在。
- 未在当前bpf-benchmark（含相关hidden/ignored目录）、该仓库及docs/paper全部可达Git历史、邻近ebpf-correctness-verifier、有界相关workspace目录找到对应Lean包；后者是C++/SMT项目，不能替代。不能确认无sorry/axioms、全variant覆盖、模型来源、编码一致性或proof effort。

Round 1（覆盖与事实）：11问覆盖concern board；Q1补E管理员部署问题的精确引文；Q7以原始report实答；Q6取消“全部直接extract真实代码”的更强断言；逐字匹配12条引文。

Round 2（过度声称与承诺）：Q1保留整个privileged implementation的信任义务，Q4区分ARM LNSym与未核验的eBPF/x86语义；Q5不虚构proof effort或artifact存在；保留micro geomean、application gap和whole-native不同TCB边界；无新增实验或公开承诺。

Round 3（写作与词数）：每项Response为3-4句，共713 whitespace words；删除跨论文作者提示。最终 draft-ready / needs-user-input；proof artifact、benchmark provenance和stats记录差异未关闭，不能标为可直接提交。

## Follow-up log

仅@A1 Reviewer E汇总，没有作者response。
