# Classify every usable positive rank-one frame

**Scoped proof, with sharp constructions.** For the four-target formal
register endpoint of PR2085, one additional positive rational rank-one
frame is usable in an exact word **if and only if** it is `R=F/m`, where
`F` is one of the four original frames and `m` is a positive integer.
Among words that use it, the exact possible total lengths are

```
{m+7, 2m+6}.
```

The minimum is therefore `m+7`. The result holds with arbitrary finite
restored dirty workspace and address-independent binary mixing. It has no
word-length cutoff. The ordinary eight-call construction remains available
when use of the added frame is optional. This is not a native supplier or
an improvement to the selected multiplication bound.

[PROOF.md](PROOF.md) gives the complete model, universal proof and both
attaining constructions. It retains the formal group algebra of rational
symmetric address matrices and paid factors `I+([F]-1)N`, with binary
rank-one idempotent `N`. Exact equality is imposed on all roles. Positive
means nonzero positive semidefinite; zero and negative frames are excluded
from the classification, as are two added frames and changed endpoints.

The old frames are `A=diag(1,0)`, `B=diag(0,1)`,
`P=(1/2)[[1,1],[1,1]]`, and `Q=(1/2)[[1,-1],[-1,1]]`.
The target is `diag([A+P],[A+Q],[B+P],[B+Q],1,...)`.
For example, `R=A/3` can be used in words of exactly 10 or 12 calls;
`R=2A/3` and every positive off-axis rank-one frame cannot be used at all.

## What the proof adds

PR2910 already forbids the fixed dyadic extra frame at every length.
PR6032 handles the normalized rational-slope minimum, and PR6079 excludes
all words shorter than eight for any one signed scaled frame. None of
those results classifies which positive frames may occur in longer words.
This package supplies that classification and its exact length spectrum.

The determinant identity bounds the number of **old** calls below eight
whenever the positive extra frame is used, even if the total word is long.
The resulting integer circles force an old direction. A character that
annihilates the entire rational added line leaves three possible count
patterns; exponent support forces reciprocal-integer scaling. Subdividing
one or both matching calls in the direct word attains both lengths.

The three multiplicity patterns in PROOF.md are a complete **necessary**
list. The first two are constructed; the third is not asserted to be
realizable. This distinction does not affect the exact length spectrum.
When `m=1`, the added label duplicates an old address and both lengths
collapse to eight.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/bit-positive-frame-use
python3.12 -I -W error -B research/bit-positive-frame-use/verify.py
python3.12 -I -O -W error -B research/bit-positive-frame-use/verify.py
```

The registered runner executes normal and optimized modes. The direct
verifier needs only this package and its three declared predecessor READMEs,
and neither Git nor network access. It checks their hashes, then compiles
the literal local checker bytes instead of importing cached bytecode.

The independent checker derives the determinant families from all 330 old
multiplicity quadruples of total at most seven, obtaining 40 families and
12 survivors of the rank condition. These are not the same 40 count tuples
as PR6079's short-word census. The checker supplies 48 exact support-weight certificates that reduce the
unbounded extra-call count to one divisibility condition. Corroboration
covers 3,840 parameter support checks, 40 reciprocal-scale fixtures, 212 rejected
nonreciprocal-scale fixtures, and 20 rejected rotated frames. It multiplies 128
one-/two-subdivision words and 128 freely conjugated versions, for all four
directions, m in {1,2,3,4,5,7,8,12} and widths 4/6, including temporary
dirty-role writes. All 577 dropped/extra-call, incorrect-fraction, wrong-
direction, dirty-restoration and non-idempotent mutants are rejected.

The primary checks independently verify both rational alphabet/endpoint
symmetries, the four denominator-safe lattice characters, all eight integer
circle domains, and the three residual patterns. Controls include a
nonintegral character that cannot be reduced modulo two, manually computed
noncommuting products, and a negative-frame identity loop outside the
positivity hypothesis. Finite parameter/role grids test the implementation;
the statements for all denominators, word lengths and workspace widths
follow from PROOF.md.

Local environment: CPython 3.12.14, macOS arm64. Source metadata, normal and
optimized verification, and publication/export integrity are checked
separately. No native tariff, formal-kernel proof, independent human
acceptance or new selected-frontier cold replay is claimed.

## Task, overlap and sources

Canonical base `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8;
chooser seed `9da5de6c63f0e0f69135ef2d1c7c085d`. The selected binding-only
orientation passed after materializing its pinned files; it does not
validate the full selected construction.

Task `bit-new-register-model`, scope key `7084092dd726e7ba1f2f`,
**scope changed** to PR6079's all-length positive-use question. This is a
formal alphabet classification, rather than the card's native
larger/nonabelian supplier. The full original card, relevance and stopping
rule are retained in [TASK.json](TASK.json).
[Canonical claim/status](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19233896).

Live all-state searches on 2026-10-28 for rank-one/reciprocal and scaled/frame
PRs, the current handoff and PR6079 were inspected. The local offline helper
searched 18 of 8,348 note records and had no usable remote cache. No matching
all-length classification was found; this limited coverage is not proof of
novelty or a survey of unpublished work.

| Predecessor | Inspected head | Retained contribution |
|---|---|---|
| [PR2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085) | `5302b9bad6345413a0cabb0afd926d84e44c12e3` | Endpoint, model, augmentation method |
| [PR2910](https://github.com/CrocSwap/integer-mult-bounds/pull/2910) | `26ce4ed46112438b237fab54e6da1953c1d16174` | Earlier determinant obstruction and arbitrary dirty workspace |
| [PR6032](https://github.com/CrocSwap/integer-mult-bounds/pull/6032) | `3b098803eb854afbd5d63ad3bf4d75cdb1e515d5` | Support method, normalized slopes, alphabet question |
| [PR6079](https://github.com/CrocSwap/integer-mult-bounds/pull/6079) | `44745c427f710e406cb2d2c6de458b7f93d81f01` | Motivating all-length open question; signed minimum-eight result |

[SOURCES.json](SOURCES.json) pins the first three canonical READMEs. PR6079
is pending context only: no theorem, code, certificate or Git object from
it is required to replay or prove this result. All needed invariants are
rederived here, so this package can be reviewed independently.

## Open next questions

Structured relevance, first steps and blockers are in TASK.json.

1. Can **two** positive added rank-one frames enable a saving? Begin with
   the joint determinant equation and target exponent supports. The
   single-frame rank-one residual argument no longer applies; an exact
   word and full native invoice are required for a multiplication gain.
2. For reciprocal subdivisions, is the third necessary count profile
   `(0,1,3,3,m)` realizable for any `m>=2`? The proof excludes `m=1`.
   Start at `m=2`, or find a coefficient obstruction uniform in `m`. This would classify count-profile realizability; it
   cannot improve the minimum or length spectrum already settled here.

## Credit

Prepared by **apoursh**, with substantial OpenAI Codex assistance in proof,
implementation, and separate agent proof/code audits. Apache-2.0.

Cinna Davis (PR2085/2112), Nick Petalas (PR2910/6032), Philippe Van Velzen's
earlier fixed-frame result as retained in PR2910 and
[Discussion2091](https://github.com/CrocSwap/integer-mult-bounds/discussions/2091#discussioncomment-18935374),
and the retained BIT lineage keep their attribution. Determinant, support
and first-order rank methods are inherited. Agent audits are not human or
formal-kernel approval.
