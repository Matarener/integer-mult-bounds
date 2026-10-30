# Combined publication validation

2026-10-26; CPython 3.12.8, macOS arm64, standard library. Scientific assembly commit `5da9738d67542585920a6e7677ecc4d55f6d2744`; the later publication commit adds this record only. Canonical main was fetched immediately before submission and remains `de5ec2e7a6074068452f45b1a191b5c72832df4a`.

Passed:

- Registered metadata and exact source pins for `research/p104-boundary-reuse`.
- Registered normal and optimized replays: source-byte joins; both candidate-generator runs; constructive helper708 control; legal retiming and rejection controls; all six exact causal obstructions and favorable tensor relaxations; unchanged source invoice. The exact final obstruction receipt retains semantic SHA256 `50db363dbaca657f2e43f4f00edd6ef10d667769da9b92bbad30d24d414a955c`.
- Original file payloads remain semantically identical in temporary replay copies. Only documented diagnostic seconds and compressed-container metadata are excluded from the comparison.
- `scripts/check_research_commit.py --package research/p104-boundary-reuse`: exact 70-file committed-byte check.
- Official export and `export_research_package.py check --check-inputs`: all 70 payload files and 65 declared inputs verified.
- Optimized direct publication replay from that extracted Git-free export with empty PATH; all 71 files including its export manifest stayed byte-identical. The wrapper uses temporary copies, and needs no predecessor checkout or network.
- `git diff --check` on the contribution.

The optional `--check-source-history` preflight reports that full Git history is required; this checkout is shallow. It is not reported as passed. Every wrapper runtime dependency is nevertheless retained in the committed export and authenticated by its source hashes. Historical source pins and original notices are preserved. The final committed-byte preflight is repeated after adding this record.

The historical exhaustive three-/four-ADD searches were not rerun during assembly. Their frozen receipts are authenticated and their original full replay remains available; the main theorem is instead checked directly by the stronger exact three-meeting proof. No new native, caller, compiler, precision/tape, BIT, outer, Lean, Docker or selected-frontier replay was run. Hosted CI, independent human review and formal-kernel acceptance remain separate.

The original local-only session records are immutable historical evidence; this document and the publication overview describe their combined submission. No new κ or productive credit is claimed.
