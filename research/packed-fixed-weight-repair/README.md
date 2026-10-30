# Exact fixed-weight packed-bit repair counts

This scoped proof gives the exact mean repair density of the original
eight-rotation packed-bit gadget when its `m` used source bits are uniform
among the `binom(m,w)` patterns of weight `w`. Both dirty fields must remain
complete and independent of that source choice. No new kappa is claimed.

Let `A[m,w]` be the sum of the agreement fractions over those source patterns.
The new bivariate generating function is

```text
sum A[m,w] z^m u^w
    = (B + (2u-1)z) / (B - (B+1+(B-2)u)z + (1-u)z^2).
```

Consequently the exact slice failure density is
`1 - A[m,w]/binom(m,w)`. The initial polynomials are `A[0](u)=1` and
`A[1](u)=1+u`. For `m>=2`, with out-of-range indices interpreted as zero,

```text
B A[m,w] = (B+1) A[m-1,w] + (B-2) A[m-1,w-1]
           - A[m-2,w] + A[m-2,w-1].
```

At `B=64,m=3,w=2`, the three patterns give mean failure `43/2048`.
The predecessor's fixed-weight worst case is `1/32`, and its unrestricted
source average is `255/16384`. Neither equals this slice mean. At
`B=64,m=10,w=2`, the exact mean is `57087705027109/9007199254740992`.
These are address fractions, not measured runtime improvements.

[PROOF.md](PROOF.md) derives the rational function by summing the cited
gap product over leading zeros, trailing zeros and consecutive-one gaps.
The algebraic identity holds for real `B>=4`; the inherited binary gadget
uses `B=2^K`, `K>=6`, `m=f-1` and its allowed offset. The proof handles
`m=w=0` and weights zero and one.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/packed-fixed-weight-repair
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/packed-fixed-weight-repair --check-source-history
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-fixed-weight-repair/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/packed-fixed-weight-repair/verify.py
```

Expected markers are `PASS_PACKED_FIXED_WEIGHT_REPAIR` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The standalone verifier enumerates
every source pattern through length 14 at `B=4,6,64,128`, and compares each
weight total with the new recurrence. It checks the boundary rows through
length 128 and three wrong aggregation shortcuts. Seven invalid inputs
must also reject. The nonbinary radices are algebraic controls, not new
binary gadget parameters. [RESULT.json](RESULT.json) is a generated
receipt bound to the proof, code and metadata hashes. Default replay writes
nothing and works without Git or any predecessor package.

The universal claim rests on the written combinatorial proof, conditional
on the cited predecessor theorem. The finite enumeration checks the new
aggregation, not the predecessor's digit program, transition table or
mathematical correctness. No predecessor verifier is run or imported.

## Scope and sources

Canonical base `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The `uniform-transfer-audit` card changes scope to this exact source-mixture
side result. It does not discharge one of the selected five assumptions.
The selected baseline source-binding check passed after materializing its
omitted inputs. No selected supplier cold replay was run.

Hanson Sun / bbMisk's [PR #1245](https://github.com/CrocSwap/integer-mult-bounds/pull/1245)
already proves each source's gap-product law, the fixed-weight extrema and
the unrestricted average. Those are cited premises. This package adds the
exact fixed-weight mean and its coefficient recurrence. Precious / Kyu's
[#773](https://github.com/CrocSwap/integer-mult-bounds/pull/773) supplies the
matching-prefix approach and complete-rectangle count; Aryan Sudhir's
[#735](https://github.com/CrocSwap/integer-mult-bounds/pull/735) supplies the
earlier sufficient guard envelope. Their retained manuscript and primitive
lineage stay credited. [SOURCES.json](SOURCES.json) binds the cited README
as historical provenance, with no live executable dependency.

This supplies a count for a proposed source-restricted caller, not that
caller. Restricted dirty fields, nonuniform sampling within a weight slice,
or source-dependent dirty layouts do not meet the count's hypotheses.
Source access, layout admission, all scans, correction sorting, reinsertion,
restoration, precision and the complete physical bill remain obligations.
No finite certificate or scoped proof here establishes a complete
multiplication theorem or changes the selected frontier.

Live claims, open PRs, merged PRs and main README searches were checked
before reservation and publication. The overlap helper also reports its
sparse local-note coverage; no-match searches are not novelty certificates.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228368)
states this scope. The first verified identity ended the research.

## Open next questions

1. Can an actual paid caller preserve complete dirty fields while supplying
   uniform fixed-weight source slices? Trace one invocation and include the
   source partition, address descriptors and all movement costs. No such
   physical layout is supplied here; its cost can outweigh the repair saving.
2. What is the sparse-weight asymptotic of this exact count? Start with the
   coefficient formula at fixed `w` and increasing `m`. This could quantify
   the possible benefit of a source-restricted caller, but it would still
   leave that caller and its complete bill open.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0. Credit Hanson
Sun, Precious Oyetunji and Aryan Sudhir for the predecessor results above,
and the original manuscript authors for the eight-rotation gadget.
Independent human and formal proof-kernel review are unclaimed.
