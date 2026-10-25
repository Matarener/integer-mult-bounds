# PR4100 arbitrary-source compact caller and explicit repair inverse

The arbitrary-source substitution in Cinna Davis's
[PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100)
has the required address-algebra property: when each Boolean control omits
**every** active target and the borrowed controls, the literal compact word
agrees with the ideal switches on its stated good set. Its reverse word
computes the inverse on the entire dirty address rectangle. Applying the
existing exceptional-repair theorem then restores every payload exactly.

[PROOF.md](PROOF.md) gives the argument for arbitrary admissible field widths,
target count and source functions. It treats guard-dependent functions,
loaded control digits equal to `B-1`, inactive high control digits and
evaluation at current inverse states. These details matter at the actual
balanced-CRT/Beneš caller in `research/unconditional-batched-crt/CRT.md`.
This is one scoped implication of the proposed construction; it does not
validate the full multiplication theorem or its machine costs.

The generic carry and repair lemmas were already established in
John-Michael Smith / @jp3isme's [PR763](https://github.com/CrocSwap/integer-mult-bounds/pull/763).
The contribution here is their caller-specific arbitrary-function application,
an explicit inverse evaluator for exceptional states, and its comparison with
the literal PR4100 caller. PR4100's previous complete caller fixture obtains
inverse addresses from an exhaustively constructed table; this audit's
repair keys use the reverse word directly.

## Evidence and reproduction

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/crt-arbitrary-source-repair --check-only
python3.12 -B scripts/research_package.py --package research/crt-arbitrary-source-repair
```

Both normal and optimized registered commands must return
`PASS_CRT_ARBITRARY_SOURCE_REPAIR` and reproduce [RESULT.json](RESULT.json).
Checks use explicit exceptions, not removable assertions. The default verifier
does not write artifacts. `--write /tmp/result.json` explicitly regenerates
the receipt for comparison.

Registered normal and optimized replays passed with CPython 3.12.13.

| Check | Exact coverage |
| --- | --- |
| Complete one-target domains | Three source functions, 4,096 addresses each; all three-bit `u,t`, six-bit `y`, radix 4 |
| Complete two-target domain | 65,536 addresses; all three-bit `u,t`, ten-bit `y`, radix 2; both functions depend on guard bits |
| Inverses and source comparison | Both inverse compositions, literal predecessor forward map and good predicate on all 77,824 states |
| Sparse repair | Full destination keys, every marked hole, and unique payload correspondence in all four domains |
| Larger parameters | 1,024 deterministic sampled states across four tuples, including 2–4 targets and radix up to 16; 64 good states |
| Actual CRT caller | All 4,096 addresses through five forward and five reverse layers; 29,440 exception visits; direct padded rotation oracle |
| Rejection controls | Five explicit weakened-contract or wrong-key cases |

The two-target exhaustive domain includes 6,496 raw executions that change an
inactive high compact-control digit. Those digits are retained in inverse
evaluation and repair keys. The complete fixtures and seeded comparisons use
ordered target positions; the written disjoint-interval proof also permits a
different target-to-digit order.

The new interpreter is separately specified as ten modular shears. It does
not import the predecessor primitive, predicate or inverse into its evaluator.
The authenticated predecessor code is executed only for comparisons and for
its actual Beneš network/caller. The latter still uses its table inverse,
providing a separate comparison against the new direct key calculation.
Both results are checked against the simple padded modular-rotation formula.
The finite repair simulator uses in-memory arrays; it is not a fixed-tape
implementation or a timing certificate.

## What the failure controls distinguish

With radix 4, targets `(0,6)`, and input `(u,t,y)=(4,0,1040)`, take
`f_0(y)=bit_6(y), f_1(y)=0`. The input satisfies every stated guard and
each function omits its own target. The raw word returns `(5,0,1041)`,
while the intended result is `(4,0,1040)`: omitting only one's own target
is insufficient. PR4100's actual caller satisfies the stronger all-target
condition, so this is not a source defect.

The other controls reject reusing stale function values during reversal,
using the guarded identity as an inverse on bad states, and dropping a high
key bit. They also confirm PR763's warning that incorrect keys `T(q)` can
fill every hole while delivering the wrong payload. Hole coverage alone
does not verify repair.

## Sources, coordination and limits

Base: current canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7.
The four audited PR4100 files equal their bytes at head
`337d04939571a637aeab54a0f58f54fde811663a`.
[SOURCES.json](SOURCES.json) authenticates six live inputs and retains
the original task catalogue and selected record as historical provenance.
[TASK.json](TASK.json) records the refined assignment and overlap coverage.
The [canonical Discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/4168)
tracks the claim and final handoff.

The baseline binding check passed; it is not a supplier replay. The selected
conditional `κ=0.001672660197076918` is unchanged. The audit does not prove
reservoir availability, the separate last-K-position branch, ordinary-callee
correctness, the control-generation tariff, sorting/head-travel costs,
precision, or the remaining complex/Gaussian interfaces. It is a written
mathematical audit with finite implementation evidence, not a formal proof
assistant result or independent human peer review.

## Open next questions

1. Audit one actual reservoir placement and its charged full-field shuttles
   from CRT.md sections 3–4, preserving the exact source dependency set.
   This addresses the physical premise left outside the address identity.
2. Implement one explicit inverse-key computation on sequential encoded
   controls and account for current-state reevaluation, complete high digits,
   head return and erasure. A concrete implementation is needed before its
   runtime can validate the claimed `E(p,ell)` allowance.

These are separate scoped obligations; the structured handoffs are in TASK.json.

## Credit

Cinna Davis supplies the audited PR4100 construction and caller. Douglas
Colkitt supplies the compact-control and sparse-repair construction.
John-Michael Smith / @jp3isme supplies PR763's explicit carry/repair audit.
OpenAI and the upstream contributors retain their surrounding source credit.

This contribution is by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI
Codex assistance in research, derivation, implementation, writing and scoped
agent review. New material is Apache-2.0.
