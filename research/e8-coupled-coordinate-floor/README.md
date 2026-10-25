# Coupled E8 coordinate floors and a 28-neighbor partial-quotient theorem

Conditional on the retained written premises from pending same-author
PR3755, this package proves COPY≥72 for new two-sided families of exact full-E8
factorizations PQ^t=G/2, with any finite number of scalar-active terms.
The left encoder space lies in C+Kδ_v, where C is the eight-dimensional
root-evaluation code. The dense binary COPY table is fixed before scalar
reduction. Ordinary transpose is used.

The load-bearing PR3755 premises are its singleton classification,
rank-at-most-nine theorem and coordinate-pair classification. Source pins
and finite certificates preserve these dependencies; they do not independently
validate their written proofs. The low-budget partial-quotient argument also
uses PR3166 Theorem A, whose upstream ledger status is partially reviewed.
The two relative-cut implementations share the Weyl/parabolic reduction
for the complement-character branch; they do not independently validate
that written reduction.

The main new mechanism is an **actual-basis coupling lemma**: the only
unpaid singleton/hole state marks an equality-basis coordinate −1, while
the actual free-pivot cut forces that same coordinate to be zero. It uses
the given basis, rather than replacing it by a convenient minimum basis.

## Results and exact scope

| Right-space hypothesis | Field | Normalization | Result |
|---|---|---|---|
| Actual col(Q)=C+D_A, any coordinate set A⊂E8 | characteristic zero | Each exceptional P ray occurs at most once | COPY≥72 |
| col(Q)⊂C+span(δ_a,δ_b), any distinct a,b | every characteristic ≠2 | Raw ambient inclusion; arbitrary terms | COPY≥72 |
| col(Q)⊂C+D_A, A⊂H_v, card(A)≤28 | characteristic zero | Raw ambient inclusion; arbitrary partial quotient | COPY≥72 |
| col(Q)⊂C+D_A, card(A)≤13, u_v outside the binary label span of A | characteristic zero | Raw ambient inclusion; arbitrary partial quotient | COPY≥72 |
| Arbitrary actual col(Q)⊃C, dimension≥24 | characteristic zero | Each exceptional P ray occurs at most once | COPY≥72; inherited strict-floor corollary (PR2962 + coupling) |

Here D_A is the coordinate-unit space and H_v is the 56 nonself roots
nonorthogonal to v. All actual ranks/spaces discard zero-factor terms.
Pairwise nonproportional P columns suffice for the stated exceptional-ray
condition; Q columns may repeat. Full actual space cannot be inferred from
ambient inclusion after merging. The raw theorems explicitly handle that
rank drop and the resulting arbitrary coefficient subspace D'.

For normalized actual ranks (9,n), n≥10 in these families, the integer
COPY floor also gives the sharp bound

```
Σ_i ρ_i^q ≥ 1+8^q+7·9^q,        0<q≤1.
```

An eleven-term rank-(9,10) exact decoder attains it over every odd field.
The numerical expression and concavity argument are inherited from
adamgall's PR2062; the new assertion is its coupled-space coverage.

## What the additional research established

The 28-neighbor theorem allows noncoordinate partial quotients, not just
full coordinate extensions. Its proof combines three distinct facts:

- A nonroot corrected word needs **27 neighbor deletions** before it can
  have binary weight at most eight. This sharp relative bound is new and
  is checked by two complete reductions.
- A root corrected word needs **29 neighbor deletions** before it can
  have weight at most seven. This sharp boundary is checked both for every
  ordered root pair and by a separate fixed-pivot two-character exhaustion.
- If dim D'≥2 and its minimum basis bill is at most seven, its entire
  coordinate support has at most 21 sites. The weighted root-swap theorem
  then bounds all feasible normal directions. At larger coefficient bill,
  the ambient scalar rank-eight bound suffices.

The stronger assertion that every deficient mixed word is an eligible root
hole stops at 23: an explicit 24-neighbor word refutes it. The present
invoice proof works through 28 anyway, allowing nonroot weight-eight words
at 27. A normalized rank-(9,17) eighteen-term fixture has actual nonpivot basis
bill 73 but COPY 72: the one-unit rebate is sharp, and the corresponding
minimum-basis cut condition really fails at that higher basis floor.
A further sharp nonroot low-word bound is 55 neighbor deletions, checked
by a complete parabolic scan and a separate full-support-stratum algorithm.
Thus the next 29–54 boundary problem involves root normals only.
The 29-neighbor mixed-low example marks a boundary of this proof,
not a decoder counterexample.

## Proof map

- [PROOF.md](PROOF.md): generic coupling lemma, every actual equality basis
  for small full coordinate sets, all-A assembly, all-odd pair, concavity.
- [EXTENSIONS.md](EXTENSIONS.md): arbitrary partial quotient after merging,
  actual-basis deficit count, neighbor-28 and cut-excluded-13 consumers.
- [RELATIVE.md](RELATIVE.md): sharp relative 27 and root-low 29 certificates,
  characteristic-zero completeness and the explicit 24/29 boundaries.
- [FINITE.md](FINITE.md): root/parabolic and Fourier capacity arguments,
  plus PR2962's strict one-sided dimension-24 relaxation.
- [SHARPNESS.md](SHARPNESS.md): exact normalized and noncoordinate equality
  fixtures, raw-rank padding and proper-cut examples.
- [FORMAL.md](FORMAL.md): five partial Init-only Lean declarations and the
  unformalized geometric/consumer bridges.

## Reproduce

From the repository root, under CPython 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/e8-coupled-coordinate-floor --check-only
python3 -B scripts/research_package.py --package research/e8-coupled-coordinate-floor
```

`verify.py` compares the exact semantic receipt in RESULT.json and all
package source hashes. `--emit` explicitly regenerates the receipt after
an intentional source change. Live input SHA256 pins are checked before
scientific imports. Direct and Git-free invocations use a fresh private
bytecode namespace, so adjacent stale .pyc files do not replace the
source-authenticated modules. Package-local vendor namespaces are explicit.

The replay checks 109 power-of-two minors; all 256 proper/full simple-root
subsets; 256 Fourier values and capacity attainers; 61,320 root/character
pairs; 49 strict-dimension cases by two DPs; 15,575,280 relative parabolic
comparisons and a separate exact-kernel algorithm; all 14,400 root-pivot
pairs plus a fixed-pivot 10,851-plane exhaustion; 32 exact full-coordinate
fixtures in two models; two noncoordinate fixtures and the rank-(9,17) strict-slack fixture per
field over Q/F3/F5/F7; and 60 actual equality bases across 7,200 cuts.

Product/compensation faults, actual-space and normalization controls,
a false general minimum-basis cut assertion, and the classification
boundaries are tested separately. Finite fixtures and internal cross-checks
support the written proof; they are not a census of arbitrary scalar
factorizations or independent human review. Lean is a separate explicit
check, not part of the Python replay.

Pending PR3755's exact geometry, unit certificate and written premises
are retained under vendor/pr3755 with original hashes in REFERENCES.json.
No pending Git object or network fetch is needed for replay. These retained
premises are reused explicitly, not described as an independent model.
The second root/factor implementation constructs its own standard inventory
and exact arithmetic; it is an internal cross-check by the same AI-assisted
contribution, not independent human certification.

## Task, overlap and limitations

Base 20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision 6.
TASK.json records the handoff-driven change from complex-rank-shape-decoder.
PR3154's C′ / RL-s1 compensation questions and PR3755's higher-rank residual
motivate this scoped lower-bound contribution. It does not close general
C′ or G1-MFREE. In particular arbitrary partial right spaces of dimensions
10–23 without these support restrictions remain open.

The read-only 01:26 UTC October 19 refresh inspected all five PR updates
since 00:56 UTC and fully paginated 887 comments plus 124 replies across
Discussions 3156, 1587, 1166 and 1167. Main and the PR3154/3755 heads were
unchanged; no matching E8 completion appeared in that delta. Earlier scout
coverage is broader but historical. This is bounded overlap evidence, not
a guarantee about all PR diffs, unpublished work or future updates. The
work remains local under the contributor's publication restriction.

No selected frontier, shared infrastructure, predecessor source or κ is
changed. The written root-system and weighted root-swap inputs remain
substantive dependencies. Full E8 instantiation, field transfer and theorem
assembly are not formalized; no hosted CI or repository-wide build is claimed.

## Open next questions

1. Extend the coupled floor to arbitrary partial right quotients in dimensions
   10–23. Start by testing the actual equality-basis functional cut, which is
   false for unrestricted minimum bases; a new structural premise is needed.
2. Cross the 29-neighbor mixed-low boundary. Classify how corrected root
   weight-seven words enter an actual bill-72 basis; the eligible-root-only
   shortcut already fails at 24 and cannot be restored by assertion.
3. Formalize the E8/linear-functional bridge and actual-basis assembly.
   The five small Lean declarations expose the missing geometric hypotheses.

## Credit

See [NOTICE.md](NOTICE.md) for the complete source roles and assistance
record. The coupled compensation and new relative-cut results are by
conorholds, with substantial OpenAI Codex assistance and GPT-6.1 SOL agents
at xHigh reasoning. Apache-2.0. No independent human review is claimed.
