# Validation

All commands ran from this owned directory with `python3 -B`; frozen inputs
were read only. No source directory outside this package was changed.

1. `python3 -B odd_certificate.py --write` — PASS, created the receipt.
2. `python3 -B odd_certificate.py` — PASS, exact saved-receipt readback.
3. `python3 -B -O odd_certificate.py` — PASS, identical optimized readback.

Final normal and optimized readbacks completed at 2026-10-19 14:57 UTC.
The script replays the deterministic bounded proposal search, exact graph
coverage, independent literal crossed traversal, signed tableaux, all-f
phase vectors, primitive exact Gaussian inverse checks, source native rank
bill, actual rank-one J, and parent ranks 11/15. No floating-point rank or
heuristic convergence is used to admit a certificate; floating arithmetic
is used only to propose pairing masks.

q2: 90 edges, 42 ADD vertices, four crossed vertices, six paths with ranks
12,11,10,11,11,11. q3: 132 edges, 62 ADD vertices, 17 crossed vertices,
eight paths each of rank15. Primitive exact inverse checks cover 35/46
distinct gates, respectively, in both inverse orders.

Negative controls reject omitted edges, omitted actual BANK_SWAP transport,
the weaker all-straight certificate, and a scalar-i inverse defect invisible
to the signed tableau. No large frame search or anneal ran. No active
process is left running. This package does not re-admit the frozen source's
complete selected-native recipe pool or full caller inverse metadata.
