# Independent audit of the reversible dirty-CNF reduction

PR #5369's Section 6 reduction and stated coNP-completeness result hold for
the declared unbounded five-role commuting-sign grammar. **No defect was
found in this scope.** [PROOF.md](PROOF.md) supplies an independent derivation
of the dirty controlled swap, chronological Boolean compiler, instruction
bounds, exact arithmetic bit bound and the required input-encoding choices.
This answers the separate review question explicitly left open by
[PR #5521](../native-cutoff-independent-audit/README.md).

The audit makes a distinction explicit: **at most 1200·max(1,m)² instructions
is not a quadratic serialized-byte bound**. The source emits dense generator
tables containing O(n³) bits. Renumbering used variables first gives
n≤max(1,3m), so the complete reduction remains polynomial. This preprocessing
is part of the audited reduction argument; the source compiler does not
automatically perform it. A certificate of inequality only needs signs for
referenced generators, avoiding a huge unused-axis assignment.

No new hardness theorem, tensor cutoff, physical supplier or κ is claimed.
Barrington's width-five construction and Ali Romman's native reduction retain
their credit. The current selected P104 κ=62009/20000000 and its five premises
remain unchanged.

## Independent evidence

The actual pinned `reversible_cnf.py` compiler generates the words under test.
A separately written [literal.py](literal.py) evaluates their full 5×5 rational
endpoints. It reads the serialized phase recipes and all tensor columns;
generator names are opaque. The source's evaluator, general verifier,
composition helpers and arithmetic are not used as the expected-result oracle.
The compiler imports its unchanged `exact.py` dependency for validation.

[RESULT.json](RESULT.json) records:

- All **14,400 pairs of five-role permutations**, with **28,800 complete dirty
  branch endpoints**, plus 120 constant endpoints. The maximum emitted branch
  length is 24 instructions. All 24 five-cycle targets also pass the conjugated
  AND check on all four assignments.
- **1,807 CNFs / 14,456 assignments** built from all 42 canonical clauses of
  up to three distinct signed literals on three variables. This checks the
  source group program against direct Boolean truth, including empty clauses,
  tautologies and contradictions.
- **820 literal tensor blocks** at widths 1,2,3 for seven complete emitted-CNF
  fixtures, with all five independent dirty input columns. This includes the
  complete three-axis tuple domain through width 3 and a sparse-label case.
  Separately, 120 local controlled-swap endpoints cover all 20 ordered role pairs.
- Actual clause lengths 0,1,9,25, plus 24 balanced-size fixtures through 65 clauses.
  A 201-bit variable-name fixture is compressed to three axes and checked on
  all eight assignments without constructing a huge dense axis table.
- **Eight semantic mutations**, each producing a recorded wrong matrix entry:
  missing inverse reversal, wrong relative-product order, reversed cycle swaps,
  wrong empty-conjunction semantics, query-sign error, missing final ADD,
  erased variable sign, and an extra constant phase. The last mutation passes
  the specified even-width control and fails at odd width. Seven invalid
  compiler inputs are also rejected.

The eight semantic failures are endpoint discrepancies, not hash failures.
Source-code mutations execute separate in-memory compiler copies; serialized
program/recipe mutations operate on deep copies. All original source bytes
remain unchanged. Finite controls corroborate the written proof; they do not
establish a complexity theorem by enumeration.

## Source and scope

Source: [PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369),
head `18354f41de4dc7bfda4692e814cf1d91a6d619ef`. Its proof, README, compiler and
arithmetic helper are unchanged at canonical main
`df0137efd35e11b4445734bf612bdd4c7ebc330c` and pinned in
[SOURCES.json](SOURCES.json). The PR #5521 review README and repository license
complete the six declared live inputs.

The scope is the five-role reversible reduction in Section 6. General native
composition, self-query semantics, the four-width cutoff theorem, source
event8814, physical cost/storage/precision and the full multiplication theorem
are outside this review. The predecessor's CLI has separate finite axis and
stored-term limits; the unbounded coNP statement is not attributed to a
fixed-axis implementation. No general-source or selected cold replay was run.

The picker ran once with seed `aa32479c3ec3e4781cbe692d0b861686`, selecting the
bit-mechanisms track. [TASK.json](TASK.json) explicitly records the handoff-first
override to the `formal-interface-lemma` card for this uncovered proof/source
implication. No formal proof-assistant build is claimed.

The initial overlap snapshot covered 7,676 local notes, 395 open PRs and 5,055
Discussion records with complete reported pagination and no warnings. Exact
Discussion #5354 and targeted all-status Barrington/coNP/CNF searches found the
source and complementary cutoff successors, with no competing Section 6 audit.
These searches do not cover unpublished work or every historical code diff.
[Canonical claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/5354#discussioncomment-19192650).

## Reproduce

Python 3.12 and its standard library; one registered command with a 120 s timeout.
The local scientific replay takes about four seconds.

```sh
python3.12 -B scripts/research_package.py --package research/reversible-cnf-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/reversible-cnf-independent-audit
python3.12 -I -O -B research/reversible-cnf-independent-audit/verify.py
```

The direct verifier checks all six pinned inputs before loading the source
compiler, executes the independent checks and compares the deterministic
receipt. It does not rewrite evidence or require Git/network access. An export
must retain the declared repository-relative source paths.
[VERIFICATION.md](VERIFICATION.md) records executed checks and their limits.

## Open next questions

A separate source-bound audit is still needed for the general native endpoint
compiler at a concrete physical caller, including generator composition,
inversion, self-query conventions, and every dirty input/return. This sign-only
reduction cannot supply that coverage. Another justified direction would name
a useful caller restriction and prove a tractable identity-test bound while
preserving the complete endpoint contract. No such restriction is supplied
here; the general hardness result is not a barrier for every subclass.
[TASK.json](TASK.json) gives the relevance, first steps and blockers.

## Credit

Ali Romman retains the source compiler and native dirty-register reduction.
Barrington retains the classical width-five branching-program construction;
classical CNF complexity theory is not new here. Mihir Srivastava retains
PR #5521's earlier cutoff audit and this review request. Jose Manuel and all
native/phase/compiler predecessors named in the source retain their attribution.
No predecessor file is changed and no predecessor executable is copied.

New proof, checks and prose prepared for Hiroki KUMAZAKI, with substantial
OpenAI Codex assistance. Delegated agents scoped overlap, independently derived
and reviewed the proof/encoding, implemented the literal interpreter and
reviewed the semantic controls. This is agent-assisted independent review,
not human acceptance or proof-kernel verification. Apache-2.0.
