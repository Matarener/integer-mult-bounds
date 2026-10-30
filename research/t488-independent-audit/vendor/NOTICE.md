# Vendored files

Every file below is an earlier checker by the author of this package (Sagar Thakrar / thakrarsagar), Apache-2.0,
prepared with substantial AI assistance (Claude Code, Anthropic). Each is a byte-for-byte copy of the file of the same name
on main at `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (paths below). `verify.py` checks each copy's git blob id and SHA-256
and executes exactly the verified bytes as the module, so no cached `.pyc` can stand in. No code of PR #3633, #3630, #3605,
#3624, #3626 or #3653 is vendored, imported or executed by `verify.py`.

| File | Module | Git blob | SHA-256 | Copied from (main) | Origin |
| --- | --- | --- | --- | --- | --- |
| `vendor/pr3053/audit_common.py` | `audit_common` | `17c4064f01b110012b54c05e64bdee8ae498e0b2` | `7ced740252ac8d8a8c66ef3cc825008e0aacf080494d0e983fb322d7dcddbf42` | `research/t74-3015-restore-edit-audit/vendor/pr2804/audit_common.py` | PR #2804 (merged): shared rule/attempt bookkeeping, pinned git inputs |
| `vendor/pr3053/words_check.py` | `words_check` | `0b646b9d5583c75a78e0c2dd7e9cfffa02055058` | `b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6` | `research/t74-3015-restore-edit-audit/vendor/pr2315/words_check.py` | PR #2315 (merged): free-operator word parser, warp algebra and forward/dual replay |
| `vendor/pr3053/fill_check80.py` | `fill_check80` | `557e0732bfe4c030436a11f5433143c10fa07821` | `1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06` | `research/t74-3015-restore-edit-audit/vendor/pr2387/fill_check80.py` | PR #2387 (merged): T74 owner-row rules (imported by audit_lib/check_accounting; not used directly here) |
| `vendor/pr3053/check_words.py` | `check_words` | `451dbb82f147ef446a1819b1ed595b4bf5547583` | `5996e804fa006906abff63a982c272588a44c35dfc932fdf687ef98dd3e0905f` | `research/t74-3015-restore-edit-audit/vendor/pr2804/check_words.py` | PR #2804: extended parser, literal frame recount, replays, cleanup re-derivation |
| `vendor/pr3053/audit_lib.py` | `audit_lib` | `e8e847cc89dae6bb4e90e2c3dbebc30f615b698f` | `e0cf84dd959d39e3f299c1e171753c29465fd5b4457561f4ab9ec0675d8e9dc1` | `research/t74-3015-restore-edit-audit/vendor/pr2865/audit_lib.py` | PR #2865 (merged): parse with initial corrections, own exact tracker, negative-control harness expect() |
| `vendor/pr3053/audit_kappa.py` | `audit_kappa` | `6e935547c98188a5fd2ba952641bf474d9323d9b` | `8dd12fac27ba3ee7decf99a7a1e410e138ec0fc34805bb28b93fa5cc843ab0ee` | `research/t74-3015-restore-edit-audit/audit_kappa.py` | PR #3053 (merged): rational interval moment enclosure (atanh/Taylor series with explicit tails) |
| `vendor/pr3053/audit_words.py` | `audit_words` | `6368333e16c4f50e6eb8b5f2f4c178a2de8cbbb9` | `ff831ad648dbecfd1c80f63245a84b762fdc70eb9fc3aa94dba23cd364857d18` | `research/t74-3015-restore-edit-audit/audit_words.py` | PR #3053: the word pipeline (counts, replays, tracker, cleanup, buffers) |
| `vendor/pr3053/check_accounting.py` | `check_accounting` | `e749057dd838b715d0630de618f32d66a38da931` | `fb6aef50da586f15cd60762edc074c20e300d65f1378a80160b3d4b840762548` | `research/t74-3015-restore-edit-audit/vendor/pr2804/check_accounting.py` | PR #2804: 640-bit fixed-point moment enclosure (second engine) |

## Predecessor credits

Carried over from the files' docstrings and from `research/t74-3015-restore-edit-audit/vendor/NOTICE.md` on main:

- `words_check.py`: PR2269 (Jeremy Kothe, jeremykothe2): the borrow43 package and words; PR2226 (Cinna Davis /
  1337isnot1337, with OpenAI Codex): anticipatory dirty borrowing, the alias rule and the free-operator replay idea;
  PR2260 (Dugongue); the T74 lineage PR1319/PR1297 (Rohan Arun) and PR1625 (mdumitrean); **icekylinx and Zhihao Chen
  (jacklightChen)** (two contributors): Clifford-frame normal forms and the local-word checker lineage. The pinned bytes of
  `words_check.py` and `fill_check80.py` carry the conflated form "icekylinx (Zhihao Chen)" in their docstrings, which the
  maintainer corrected on main when integrating PR #2315; the correct attribution is the one here.
- `fill_check80.py`: PR2269 (Jeremy Kothe): the T74 template, windows, dispatch and owner-row format; PR2322 (Vlado
  Vojdanovski); PR2226 (Cinna Davis); the PR858 / complex-double-replica-owners hosting rules (Hao Yan); the T16 owner audit
  (Josie Elliston; icekylinx and Zhihao Chen (jacklightChen) checker lineage).
- `check_accounting.py`, `check_words.py`, `audit_common.py` (PR #2804), `audit_lib.py` (PR #2865), `audit_kappa.py` and
  `audit_words.py` (PR #3053): this contributor's own, built on the above.
