# Independent audit of the paid-return/error/invoice bridge

**No gap found in PR5526 REPAIR.md Sections 2–4, conditional on the declared
initial-history, target-coset and pricing premises.** This audits the later
repair theorem expressly left outside DLamdata's [PR5547](https://github.com/CrocSwap/integer-mult-bounds/pull/5547).
It supplies an independent written derivation, exact rational fixtures and an
independent enclosure of the declared invoice. The theorem and bounds remain
Ali Romman's and the credited predecessors' work.

The [audit](AUDIT.md) checks why arbitrary linear feedback does not bypass
the quotient-dimension bound, why disjoint coefficient support does not mean
orthogonality, and why the orbit multiplicity and payload normalization occur
exactly once. Under the source premises, 104 extra field returns are necessary,
while the frozen reference-tariff margin permits at most 36. The resulting
width-84 squared operator-error floor remains 2125/3276. No new kappa,
native supplier, selected-frontier change or proof-kernel acceptance is claimed.

## Evidence and reproduction

Python 3.12 and the standard library suffice. From the repository root:

```sh
python -B scripts/research_package.py --package research/paid-return-bridge-audit
```

The registered commands run the following in normal and optimized modes:

```sh
python -I -W error -B research/paid-return-bridge-audit/verify.py
python -I -W error -B research/paid-return-bridge-audit/mutations.py
```

They print `PASS_PAID_RETURN_BRIDGE_AUDIT` and
`PASS_PAID_RETURN_BRIDGE_MUTATIONS controls=4`. The complete recomputed
receipt is available with `verify.py --emit`; normal replay compares
[RESULT.json](RESULT.json) without writing it. [VALIDATION.json](VALIDATION.json)
records the actual environment and completed checks.

- 175 exact prefix checks in two/three-input cyclic-unitary fixtures include
  120 new returns outside the initial-plus-target coefficient span. The
  fixture's relative Gram constant is exactly 8/9, with nonzero initial/target
  overlap; direct target returns attain its error bound.
- All 81 ternary one-return cases in a two-field Pauli fixture give the exact
  normalized error distribution: 64 at 1, 16 at 3/2, one at 2.
- Seven semantic controls expose changed premises and normalization mistakes.
  Four deliberately defective in-memory verifier copies fail their intended
  diagnostics in each Python mode. Frozen files are never modified.
- Literal AST extraction binds the invoice to its frozen source dictionaries.
  Direct sums check every integer hinge from 1 through 17. A separate rational
  log/exponential series gives margin
  `[36.037431499166, 36.037431503056]`, containing the source's finer enclosure
  and proving the 36-return budget without importing its calculator.

The finite cases corroborate the written general proof; they are not an
exhaustive search of arbitrary programs. The 8/9 fixture constant is not a
new constant for the actual caller. Eight live review inputs have exact Git
blob and SHA256 pins in [SOURCES.json](SOURCES.json). No predecessor executable
is imported or run. The source port list and grade receipts are consumed as
declarations, not relabelled as independently replayed native evidence.

## Scope and coordination

Base: canonical `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision 7.
PR5526's reviewed source head is `45f7de73b168721cdf7ec8c1769b1b594493716a`.
The selected-source orientation passed; it is metadata validation only.
[TASK.json](TASK.json) retains the exact task card and explains the scope
change from formalization to an independent informal proof audit. The picker
nonce was `0ae98c6c6a57ad53401268db8aa558d4`.

The [prospective claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236#discussioncomment-19182242)
followed handoff and live overlap checks. PR5547 covers the core Gram theorem;
PR5549 the one-qubit threshold; PR5531 a different endpoint application. Those
are separate from this conditional repair bridge. Targeted all-state PR
searches, the live canonical discussion and relevant local notes were checked.
Sparse local coverage, arbitrary historical diffs and unpublished work remain
outside the overlap claim; absence of a match is not a novelty certificate.

## Open next questions

Independently bind the complete actual initial history and its 104 target
columns to the literal PR4948/4978 caller, including both mandatory source
clarifications. Start with the pinned observation list and recompute one
affected input column through all nine cuts, then extend coverage explicitly.
The blocker is full caller/observation coverage, which this conditional bridge
and receipt parsing do not supply. That audit could change whether this theorem
applies, even though its abstract implication is sound.

Changed original paid inputs, free observations, target credits, ordinary
alphabets, capacities and multi-output suppliers require new contracts and
complete pricing. No additional fixed-invoice construction search is proposed.
See TASK.json for the structured handoff.

## Credit

Ali Romman supplies PR5526 and PR5449; Chris R / Clear1nsight supplies the
PR5425/5446 history arguments and PR4978 source audit; Dugongue supplies PR4948;
DLamdata supplies PR5547 and its explicit remaining scope. The existing
concave-order comparator, mightyOil and predecessors, zxv's interval engine,
and the full native/stabilizer lineage retain credit. Their source files and
notices are unchanged. Projection, rank, concave order and series bounds are
classical, not new general methods claimed here.

Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance; Apache-2.0. No subagents, independent human review or proof
assistant were used. Full native/physical replay, selected cold replay,
precision/stock/tape obligations and supplier admission were not performed.

## Credit

Prepared by josecarlosgonzalezroque-design. Retain predecessor attribution and source-specific notices.
New work is Apache-2.0. Disclose substantial AI assistance in TASK.json.
