# Local validation and handoff

Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Environment: macOS 26.5.2, arm64, CPython 3.12.7; standard library only.
Run date: 2026-10-19 Asia/Hong_Kong (2026-10-18 UTC).

The registered command passed all three declared checks:

```
python3.12 -I -B scripts/research_package.py --package research/connector-overlapping-windows
PASS_CONNECTOR_OVERLAPPING_WINDOWS cases=5336 matrices=4096 controls=7 XORs=126/84->70 kappa=unchanged
PASS_INDEPENDENT_WINDOW_QUERIES cases=5336 settled=618645 dirty_inputs=1024 cost_digest=8e7011ae6f8a29988302333111b031039636b1e9e40c1060f0f31ca1c222f28d
PASS_WINDOW_PACKAGE_CONTROLS optimized_git_free=1 readonly=1 corruption_rejections=4 exclusive_write=1
PASS_REGISTERED_RESEARCH_PACKAGE research/connector-overlapping-windows outcome=completed
```

The primary checker also passed directly under `-I -O -B`. The package control
creates a Git-free copy with exactly the three declared input files; optimized
replay leaves every byte unchanged. It independently rejects a changed source,
a changed receipt, removal of restoration parity, and removal of deadline
validation. Exclusive receipt creation refuses an existing file and preserves
it. The primary seven semantic controls remain active under optimization.

The unchanged PR1442 predecessor verifier was run once: 954 exact quotient
price cases, 110,850 visited states, all four chronology/restoration controls,
and its credited 142/222/74 query comparisons passed. That replay is orientation
and regression evidence, not new work. No expensive selected cold replay or
historical repository-wide suite was required for this isolated package.

The selected ASSEMBLY.json SHA256 matches the selected pointer. The current
review and actual retained PR1094 construction were inspected. Fetching canonical
main before submission returned the same base and priority revision 6. Final
PR/Discussion overlap metadata is in TASK.json. The publication link is recorded
in the local sprint handoff after submission.

The final phase was reserved for verification, scope review and handoff. No
subagent was used. Mathematical review was by the same AI-assisted author;
independent human review and formal proof-kernel acceptance are not claimed.

Handoff: review PROOF.md's exact write-permission contract, lower bound and
attainment, then replay the registered command. The finite certificate concerns
only that interface. The open adoption question is a source-pinned physical
caller with compatible output windows and a fully paid favorable lifetime bill.
No new kappa, selected-frontier change, supplier admission, merge or hosted CI
success is implied by these local passes.

Committed-byte check: `python3.12 -B scripts/check_research_commit.py --package research/connector-overlapping-windows` passed for all 13 package/input files. The optional `--check-source-history` audit requires full Git history and could not run in this shallow checkout. The registered metadata checker did authenticate the pinned reachable base blobs and live source bytes. The commit checker must be run without `-I`, since it imports its sibling research_package module.
