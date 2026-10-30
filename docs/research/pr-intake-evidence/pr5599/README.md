# P104 helper-split maintainer review

Under review: PR5599 at `09dd0965711ca7eeb169057a420abab1c9052137`, claiming conditional κ = 0.00310045. This package is already preserved as an archive; that publication is not selected-frontier admission. The current selected result is resolved by `certificates/selected-result.json`.

The audit checks the independent helper split, the complete caller's fresh-input ownership and normalizers, the full paid/target invoice, exact strictification and compiler parameters, and inherited precision/implementation boundaries. Primary replay runs in a closed source export, serially under a sampled 1 GiB descendant RSS limit and a 600-second timeout. No Lean or Docker is involved.

Chris R / Clear1nsight's PR5550 independent caller checker is parameterized for the new public inventory. Its original source is unchanged on main; the precise adapter is retained here. It must first reproduce its original positive control, then check the new caller. Source hashes, immutable exports, execution receipts and scope decisions are retained separately.

Credit: Ali Romman (13 helper-subspace splits and complete assembly); Pierre-Loic Doulcet / hexapode (PR5565 commuting contacts); GamingPuzzled (PR5569 handoff); DreamingOfClouds (PR5561 endpoint retiming); thu-nmrc (PR5551 contact improvements); Chris R / Clear1nsight and Matarener (independent caller, native and endpoint audits). Retain David Arias, Cinna Davis, Gareth Davidson, Cao Yifan, zxv, Jacob Alan Sussman and the full credited P104, BIT, compiler and analytic lineage in the source packages.

Maintainer review prepared by Douglas Colkitt with OpenAI Codex assistance. Apache-2.0. No independent human or proof-kernel verification is claimed.

## Current execution status and continuation

The primary replay reached its 600-second wall limit after the complete endpoint checkpoint; peak sampled descendant RSS was 65,424 KiB. This is a partial check, not a failed theorem and not a promotion. [VALIDATION.json](VALIDATION.json) enumerates the remaining work. [PROOF-REVIEW.md](PROOF-REVIEW.md) records the mechanism assessment and interface questions.

`prepare.py --work /absolute/fresh/path` authenticates and exports the exact source and caller adapter. It runs no scientific checks. From that exported directory, the serial commands are `python3.12 -I -B run_bounded.py primary 600 -I source/research/p104-helper-subspace-splits/verify.py`, then separately bounded `run_caller.py control` and `run_caller.py candidate`. The 600-second primary limit was insufficient on this host; do not blindly repeat it. Plan a suitable resource window or divide the source-bound checks into stages first. The independent adapter must reproduce PR5550's original output exactly before its candidate result is trusted. No automatic heavy replay is registered.
