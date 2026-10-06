# BPF-Ext: Safely Extending the eBPF Compilation Pipeline with Native Operations

Camera-ready source for the ATC '26 paper. Overleaf syncs this repository;
`main.tex` is the root document.

## Layout

| Path | Content |
|---|---|
| `main.tex` | Root document: title, authors, ACM metadata, section list |
| `sections/`, `tables/`, `figures/` | Paper body, restored on 2026-10-06 from the arXiv version ([2606.24213v1](https://arxiv.org/abs/2606.24213)) |
| `helpers/commands.tex` | Macros; `\tool` renders BPF-Ext and `\lang` renders Kinsn, the names used in the submission |
| `helpers/packages.tex`, `reference.bib`, `resources/` | Packages, bibliography, ACM template files |
| `revision/` | The camera-ready draft as it was before the restore (its own `main.tex`, sections, tables, figures, helpers and bibliography) |

The arXiv text calls the system Kops and the operations EInsn; here the
macros give BPF-Ext and Kinsn, and the descriptor struct is `bpf_kinsn`.

## Schedule

- Draft of the revised paper to the shepherd: Friday 2026-10-09, with a
  summary of changes from the reviewed version.
- Final version: Friday 2026-10-16.

The reviews, author response, shepherd comments, revision plan and the
submitted PDF are in `review/` (see `review/README.md`).

## Related

- Artifact, benchmarks and Lean proofs of the Kinsn operations
  (`kinsn/lean/`): https://github.com/eunomia-bpf/bpf-benchmark

## Build

```sh
latexmk -pdf main.tex
```
