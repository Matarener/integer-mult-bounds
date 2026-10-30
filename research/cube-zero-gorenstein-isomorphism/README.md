# Isomorphism of cube-zero local multiplication tensors

This contribution was produced by Nick Petalas. Apache-2.0.

For an odd finite field K, consider commutative unital local K-algebras A with
residue field K and radical J satisfying

```text
J^3 = 0,  dim_K J^2 = 1,  Ann_A(J) = J^2.
```

Put r=dim_K(J/J^2), which is positive. There is exactly **one isomorphism
class for each odd r**, and **two for each even r**. Recover the symmetric
multiplication matrix B on J/J^2 using any generator of J^2. When r is even,
the two classes are distinguished by whether det(B) is a square. When r is
odd, rescaling the socle removes that distinction. The same classification
holds for isotopy of their multiplication tensors.

This is a scoped written algebraic proof with exact finite corroboration.
It answers one restricted part of the recovered-algebra isomorphism question
in Ali Romman's [PR #5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540).
That reconstruction theorem is a cited premise, not a result rechecked here.
The new package supplies the specialization, explicit maps and bounded
implementation. Symmetric-form classification and its elementary methods
are classical; no general literature-priority claim is made. No new kappa.

[PROOF.md](PROOF.md) gives the reduction, classification, constructive
congruence algorithm and tensor implication. `algebra.py` accepts supplied
tables in arbitrary bases over odd primes 3 through 31, in dimensions 3
through 10. It checks the algebra laws and class hypotheses, computes a
canonical signature and chart, and returns a literal isomorphism between
accepted tables with the same signature. Different signatures return `None`;
invalid or out-of-class inputs raise `ValueError`.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/cube-zero-gorenstein-isomorphism/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/cube-zero-gorenstein-isomorphism/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cube-zero-gorenstein-isomorphism
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cube-zero-gorenstein-isomorphism --check-source-history
```

Other machines may substitute their CPython 3.12 interpreter path. The direct
checker prints `PASS_CUBE_ZERO_GORENSTEIN_ISOMORPHISM` in a JSON report with
enumerated coverage and SHA256 hashes of every package source/document file.
The default replay writes no files. No receipt is handwritten.

The finite corroboration checks **51,200 nonsingular forms**. Independent
full GL/similarity orbit generation covers 18, 100 and 294 forms in dimension
two over F3, F5 and F7, and all 468 forms in dimension three over F3. It
enumerates respectively 48, 480, 2,016 and 11,232 invertible matrices.
The new 96 arbitrary-basis algebra presentations check 4,128 transported
basis products. All 96 unit-image transporter mutations and 12 input/class
rejection controls pass. These are new fixtures, not predecessor inventories
or scientific replays. The proof supplies the universal quantifiers.

## Scope and research decision

The original `formal-interface-lemma` card is explicitly changed to this
written algebraic side result. The current selected source-binding command
passed; it is metadata orientation only. The actual caller is the recovered
table interface of #5540. The contribution closes isomorphism for this
specified class, without claiming the card's proof-assistant acceptance gate.
Stop after the classification. Physical maps, costs and supplier admission
remain unpriced and provide no basis for a construction expansion.

The live overlap check included open PRs, this account's recent PRs, handoff
comments, active Discussions, main-tree README searches and merged searches
for the class and its invariants. The cached helper searched only a sparse
subset of local notes; Git-object searches supplemented it. Absence of a
match is not a global novelty certificate. The advance claim is
[Discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19220065).

The proof covers all odd finite fields and all positive r. The executable
supports the bounded prime-field interface above. Characteristic two,
nonsplit residue fields, larger socles, higher nilpotency, arbitrary algebra
isomorphism, native/frame/ownership/restoration costs, precision, movement,
complete recursive invoices and the multiplication theorem are outside scope.
No selected cold replay, predecessor scientific suite, Lean or Docker build
was run. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Extend this particular isomorphism interface to characteristic two. Start
   with the alternating versus nonalternating multiplication form; the odd
   pivot and square-class algorithm here does not apply. A separate proof
   and field contract are needed.
2. Price the returned maps for one concrete native caller. First identify
   its legal coefficients, dirty state and required restoration, then charge
   every conversion. The current algebraic maps have no physical tariff.

## Credit

Credit Ali Romman #5540, exact head
`831b41da0fc09e3e4cb983c03662da5df7970f68`, for the recovered-table interface
and explicit isomorphism question. Credit apoursh #5502 for the supplied-table
recognition lineage, Ali Romman #5525 for the nucleus reconstruction lineage,
and Nick Petalas #5252, David Ganz and the retained tensor/algebra sources.
Their files and credit lines are unchanged. `SOURCES.json` records historical
provenance at canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`,
priority revision 8. No predecessor code is copied or executed.

## Implementation constraints

All checks use explicit exceptions and remain enabled under optimized Python.
There is no recursion, dynamic code execution or file-writing path. Loops
are bounded by the validated dimensions and prime, or by the verifier's
literal finite domains. The largest form enumeration has 3^10 candidates;
the largest GL enumeration has 3^9 candidates. Functions stay below 60 lines.
Python's managed allocation is a Power of Ten deviation: the table API caps
dimension at 10 and prime at 31, and each exhaustive loop discards its current
candidate. The finite orbit dictionary is bounded by its enumerated symmetric
form space. No fixed-memory or general runtime-speed claim is made.
