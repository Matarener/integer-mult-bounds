# Validation

All scientific checks below pass on CPython 3.12.8, macOS arm64, 21 October
2026. Scientific code/receipts were committed at
`71c54ffcfee4c77d77164f9b02bdf763a8f267d0`; the final follow-up only records
validation and changes documentation/task status.

| Check | Result |
| --- | --- |
| Metadata and all source pins | PASS_PACKAGE_METADATA_AND_PINS |
| Registered full replay | PASS_REGISTERED_RESEARCH_PACKAGE |
| Both native orientations, two interpreters, 632 arbitrary persistent columns, arbitrary owned-center entry then legal erasure | PASS |
| Four new edge types, forward/conjugate Clifford decoding, exact rank and absolute phase | PASS |
| Complete p17 physical/Laurent word, changed full paid/productive invoice | PASS |
| Two interval engines, new root bracket, both paid strictification tails, both finite uniform ranks | PASS |
| Nine outer rows, 54 current predicates, four guards and 63 legacy predicates | PASS |
| Wrong contact, global-phase-only, short-product-bound and outer negative controls | REJECTED as intended |
| Committed-byte preflight, 59 exported files | PASS_RESEARCH_COMMIT_BYTES |
| Deterministic committed export and independent integrity check | PASS_RESEARCH_EXPORT |
| Isolated Git-free optimized replay (`-I -O -B`, explicit package import path) | PASS_CONDITIONAL_NEW_NATIVE_PROFILE_KAPPA |
| Changed pinned source comment in the Git-free export | Rejected by source authentication |
| Changed saved κ receipt in the Git-free export, full optimized replay | Rejected at exact RESULT.json comparison |
| Optional C++20 discovery | Reproduces exactly phase B contact 480 and the new span |

Commands:

```sh
python3.12 -B scripts/research_package.py --package research/native-lattice-retiming --check-only
python3.12 -B scripts/research_package.py --package research/native-lattice-retiming
python3.12 -B scripts/check_research_commit.py --package research/native-lattice-retiming
python3.12 -B scripts/export_research_package.py export --package research/native-lattice-retiming --ref 71c54ffcfee4c77d77164f9b02bdf763a8f267d0 --output /tmp/native-lattice-71c54ff.tar
python3.12 -B scripts/export_research_package.py check /tmp/native-lattice-71c54ff.tar
python3.12 -B research/native-lattice-retiming/discover.py --output /tmp/native-lattice-discovery-replay
```

The checked export was extracted without Git, then `verify.py` ran through
`runpy.run_path` under `python3.12 -I -O -B` with only the explicit package
folder inserted into `sys.path`. Its normal 43-input authentication, complete
native and arithmetic checks and receipt comparisons all ran. The two external
mutation controls used that export and restored the exact original bytes.
The optional compiler was Apple clang 21.0.0 with `-O3 -std=c++20`.

`--check-source-history` is **unavailable**: its explicit precondition rejects
this shallow checkout with “source-history check requires full Git history.”
No unshallow fetch was attempted. Exact pending heads and consumed bytes are
present, pinned and retained in local merge ancestry; the unavailable check
is not presented as scientific or provenance acceptance.

Source ancestry includes PR4440 head
`40e22a83ed660d3d6074c4f2dbf14bfb621eee51` and PR4441 head
`5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39`. SOURCES.json binds the 43
consumed source files. The final upstream checkpoint at 20:56 UTC found
canonical main still `2a13eb1827784206202db90e5dc8327cf8a250db`, unchanged
priority guidance, unchanged pending heads and selected κ=.0023.

No hosted CI, Lean, Docker, complete historical suite or independent
scientific review is claimed. Universal native/all-column, owned-query,
precision, physical tape, analytic and recovery contracts remain conditional
premises. At the initial validation checkpoint this package was unpublished.
The user subsequently approved submission after review.

## Publication preparation

The submission branch starts from public PR4441 head `5f9d871c` and carries
only this package beyond that dependency. The earlier unpublished p7 negative
screen remains on its local branch and is excluded. All 46 source/provenance
rows were checked byte-for-byte against this public base before updating the
base pin; no scientific program, patch or receipt changed. The original local
validation commit is retained locally, and its code/receipt bytes are identical
to this submission's scientific files.

The 21:36 UTC refresh found unchanged canonical main and guidance, plus
concurrent PR4447 at `322e0ec764aa7ef7801383feb1f656e460dd8bed`. Its same
contact/profile and higher declared endpoint are acknowledged in README.md
and the PR description. No unique-discovery or strongest-kappa claim is made.
