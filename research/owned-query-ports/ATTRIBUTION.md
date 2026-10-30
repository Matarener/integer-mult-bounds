# Attribution and overlap

The exact Clifford compiler is retained, byte-pinned, at `research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py`. Recipe decoding and gate-by-gate conjugation in `verify.py` are adapted from the retained `research/kappa-function-composition/complex/prune_native.py`; its source is pinned as provenance. Existing notices are unchanged.

The graph snapshot builds on zxv's native/compiler work, Jacob Alan Sussman's mixed-target integer compiler, and Cinna Davis's padding, thinning, retiming and joint-boundary contributions. Relevant predecessors are [#4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359), [#4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416), [#4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440), [#4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441), [#4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447) and [#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470). #4470 is pinned at `b9a13c1673e0e9697de410de16e8bbf3207a7363`; canonical main for packaging is `2a13eb1827784206202db90e5dc8327cf8a250db`. These contributions are predecessors, not new work here.

The sufficient owned-copy/transform/ADD/erase identity is consistent with the inherited owned-query contract. Rank-one factorization and metric α-expansion are established concepts; no priority claim is made. The addition here is the explicit split-port cost model, complete local costs, primitive checks, portable discovery sources and scoped frozen evidence. It does not improve #4470's κ or independently accept its whole conditional construction.

Source-only discovery also consulted the shared MathProof DAG and `BinarySymplecticGroupOrder` and `Problem18CharTwoSymplecticBasis20260929` Lean sources. Those are retrieval precedents, not imported proof dependencies or fresh kernel audits. The authoritative DAG was not changed.

Prepared for Dugongue with substantial OpenAI assistance in mathematics, software, discovery and review. No independent human or proof-assistant acceptance is claimed. New work is Apache-2.0, with retained predecessor credit and notices.
