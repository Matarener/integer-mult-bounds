# Independent review of the native equality-cut tariff

The signed Clifford tariff and caller implications in **PR #5588 PROOF.md
§§3–5 hold under their stated hypotheses**. No mathematical defect was found
in this scope. [PROOF.md](PROOF.md) independently derives the intersection
by a trace calculation and proves the complete-word, cached-history and
approximation statements. This takes the
[explicit independent-review request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19183713).

For `a_k = 2^(n(f-k))`, a Fourier-rank-r Clifford call has crossing rank
`a_k (1-2^(-kr))` across the cut equating k disjoint pairs of columns.
Rectangular rank subadditivity then bounds any chronological linear word,
including changed paid inputs, feedback, COPY, CLEAR and independent dirty
helpers. A cached boundary contributes **one joint crossing rank of its
complete availability map J**. The exact rank bound permits invertible
ordinary endpoint codes; the stated unit error floor needs unitary,
cut-preserving endpoint frames.

This validates one proposed supplier-screening theorem. It does not produce
a supplier, extract J from P104, or discharge any selected implementation
premise. No κ change or native admission is claimed.

## What the independent checks add

The checkers import no implementation from PR #5588. They use standard-library
rational and Gaussian-integer arithmetic and independently check:

- All **366 signed ordered commuting Pauli image frames** for one/two axes,
  covering 18 image subgroups. The 54 literal projector checks verify
  symmetry, idempotence, trace and rational rank. These are image-frame
  enumerations, not an enumeration of all Clifford unitaries. Separate
  two-pair checks give crossing ranks 3 and 6 at widths 4 and 5.
- A complex Clifford with `C Z C* = -Y`. Its same-factor tensor has a
  Bell-minus intersection; conjugating the second factor changes it to
  Bell-plus without changing its rank. This catches a sign/orientation
  distinction that rank-only tests miss.
- One **18-operation complete word**, with four paid overwrites, feedback
  into the third query, an arbitrary dirty field, and a zero temporary.
  All 19 prefixes obey the cut bound; the complete endpoint is
  `(2x + Ty, Tx + y, d, 0)`. Omitting dirty subtraction, the final CLEAR,
  or the first crossing charge is detected. Five two-bank paid updates
  and five self updates also cover zero, negative and fractional coefficients,
  including singular self updates.
- `J = [I; T; T]`: joint crossing rank 1, while summing separate cache ranks
  gives 2. Selecting a cached response realizes T with no additional call,
  demonstrating why omitting J gives a false obstruction.
- Invertible ordinary codes preserve rank. Scaling a unitary target by 1/8
  preserves positive crossing rank but lowers its zero-program operator
  error to 1/8. A non-columnwise unitary monomial endpoint instead gives
  cut Gram `I/2`, invalidating the partial-isometry step. Both distinguish
  restrictions already present in the source contract.

[RESULT.json](RESULT.json) is a deterministic receipt. Finite controls support
the written all-size argument; they do not replace it. This is an agent-assisted
independent derivation and implementation, not human or proof-kernel acceptance.

## Source and scope

Reviewed source: [Ali Romman's PR #5588](https://github.com/CrocSwap/integer-mult-bounds/pull/5588),
head `97db3fb45cd93a350e300781d75440d14e6a1f73`.
The unchanged proof and README are pinned in [SOURCES.json](SOURCES.json)
at canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`.
The selected baseline at this checkpoint is P104 PR #5599,
κ=`62009/20000000`; its five inherited premises remain.

Excluded: source §6's profile algorithm, §7's semisimple output-packing
question, extraction of an actual retained-observation ledger, full supplier
replay, compiler/precision/storage/routing costs, and the complete rounded
multiplication theorem. The source verifier and selected cold replay were not
run. The common factor assumes equal field capacities. Free maps must preserve
the cut and its complement; arbitrary inter-column maps are not included.

The picker ran once with seed `81093d593dbc22d5b1e5cb3cc7d46405`.
[TASK.json](TASK.json) retains the `uniform-transfer-audit` card and records
the handoff-first scope change from its historical #4100 target to this explicit
current native-lift review. The first overlap snapshot covered 7,676 local
notes, 370 open PRs and 4,998 Discussion records with complete reported
pagination and no warnings. Exact-thread and targeted all-status searches
found no competing audit; PR #5617's stronger stage cuts are distinct.
Searches do not cover unpublished work or every historical code file.
The canonical claim is in
[Discussion #5582](https://github.com/CrocSwap/integer-mult-bounds/discussions/5582#discussioncomment-19188980).

## Reproduce

Python 3.12, standard library only; the registered replay is bounded at 120 s.

```sh
python3.12 -B scripts/research_package.py --package research/native-equality-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/native-equality-independent-audit
python3.12 -I -O -B research/native-equality-independent-audit/verify.py
```

[VERIFICATION.md](VERIFICATION.md) records executed commands and transport
checks. Direct replay needs only the package and its three declared input
files; Git and network are unnecessary. It reads exact pinned source bytes
and compares the recomputed receipt. Normal execution never regenerates it.

## Open next questions

At one unclaimed physical caller boundary, extract the complete actual J,
including row versions and independent dirty inputs, and certify its joint
cut rank. The blocker is a source-bound availability ledger, not this rank
inequality. For a concrete caller with inter-column operations or unequal
field sizes, first specify typed projectors and charge every crossing map;
the present normalized tariff cannot be imported unchanged. See the
structured relevance, first steps and blockers in [TASK.json](TASK.json).

## Credit

Ali Romman retains credit for the equality-cut invariant, Clifford tariff,
complete-word theorem and explicit boundary/approximation limitations in
PR #5588. Its fused-block and dirty-host predecessors, an664 and reviewers,
Adam Gall, Ross Richardson, Chris R/Clear1nsight, and the P104/native/helper/
compiler lineage retain their credit. Pauli/stabilizer theory, trace
orthogonality and product-rank inequalities are classical.

New derivation, code and review prepared for Hiroki KUMAZAKI, with substantial
OpenAI Codex assistance. Delegated agents separately scoped overlap,
reviewed the proof and signs, and implemented chronological/cache controls.
No predecessor code is copied or imported. Apache-2.0.
