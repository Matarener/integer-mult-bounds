# Independent check of PR4100's good-packet normal form

**No new κ. Finite certificate plus a written re-derivation of one algebraic
identity.** This is not an all-size multiplication theorem, and it does not
review any other part of PR4100.

## Proposition checked

[NORMAL-FORM.md](../unconditional-batched-crt/NORMAL-FORM.md) in Cinna Davis's
PR4100 package states the following. Let R be a commutative ring, C the
m-coordinate reversal, and P an idempotent with a free rank-r image. Suppose
unit-pivot northeast elimination gives unit lower triangular L and R0 with
`T = L P C R0 = E D C`. Put `U = L P L^-1`, `S0 = R0^-1 C L^-1`,
`J = C D^-1 E`, `X = S0 E - J U` and `Q = [[I,0],[X,I]] diag(L,R0^-1)`. Then

    Q N(P) Q^-1 = [[I-E, T], [J, I-JT]],   N(P) = [[I-P, PC], [CP, I-CPC]],

which is one weighted reversed r-coordinate child. The note also states that the
retained `controlled_normalizer.py` builds exactly this X. PR4100's AUDIT.md
uses the identity for the BIT good branch (row "Local-ring split ranks").

## Result

**Written re-derivation.** Given `T = E D C`, each step follows over any
commutative ring: `TS0=U`, `TJ=E` (E and D commute), `ET=T`, `UT=T`
(P idempotent), `EU=U` (im U = im T lies in the first r coordinates),
`UE=E` (U projects onto that summand) and `TX = E-U`. Conjugating
`diag(L,R0^-1) N(P) diag(L^-1,R0) = [[I-U,T],[S0U,I-S0T]]` by `[[I,0],[X,I]]`
gives `I-U-TX = I-E`, lower right `I+XT-S0T = I-JT`, and lower left
`S0E - XE = J` because `JE = J`. I found no gap. The only hypothesis is
`T = E D C`, which needs the Schur block to vanish over R. The note's split-rank
argument covers that, and the verifier checks it on every instance.

**Finite certificate** (`verify.py`, about 7 s, standard library):

| Domain | Mode | Rank-r idempotents | Good packets |
|---|---|---:|---:|
| Z/3, Z/5, Z/7, Z/9, Z/25, Z/27 at m=2; Z/3 at m=3 | every m×m matrix | 2,162 | 1,332 |
| Z/9 m=3; Z/27 m=4; Z/25 m=4; Z/9 m=5 | seeded charts, every axis set | 4,080 | 1,763 |

- Every idempotent census equals the closed form `|GL_m(R)|/(|GL_r(R)| |GL_(m-r)(R)|)`,
  so the exhaustive rows miss no idempotent.
- On each good packet, the elimination factors are unit lower triangular, the
  Schur block is zero over R, every written equality holds, and the conjugation
  equals the weighted reversed child with weights `delta_k`, `delta_k^-1`.
- In the exhaustive domains, the good fraction over Z/q^w equals the fraction
  over Z/q (63/108 = 567/972 = 7/12 for q=3), as expected if the pivot
  itinerary depends only on the residue class.
- **Vendor agreement**, 2,177 cases: the retained `prepare` gives the same
  pivots and a `cross` matrix equal to the written X. On every basis address,
  `execute_addresses` with random head unit weights A equals `B N(P) B^-1`, where
  `B = diag(A, I)`. On every bad chart in this comparison, the vendor rejects with
  "nongeneric low class".
- **Mutation controls**: `X = S0E - J`, the cancellation the note warns
  about, fails in 3,325 of 3,509 checked instances. `X = S0E - UJ` fails in all 3,509.

## Limitations

The table rows are finite. The all-ring claim rests on the written
re-derivation above, which has no formal proof-kernel check. The vendor
comparison uses `f = 1` atom columns. Larger f is covered only by the note's
fiber argument, which I did not execute. This does not check FALLBACK.md, BIT.md
costs, the Schwartz–Zippel bad-packet rate or any downstream caller.

## Reproduce

From the repository root:

```sh
python3.12 -B research/normal-form-exhaustive-audit/verify.py
python3.12 -B scripts/research_package.py --package research/normal-form-exhaustive-audit
```

The expected last line is `PASS_NORMAL_FORM_EXHAUSTIVE_AUDIT`. Exact pins are in
[SOURCES.json](SOURCES.json).

## Open next questions

1. BIT.md bounds the bad low-class fraction by `2*64^3/q` using Schwartz–Zippel
   and charges bad packets at `eta = 1e-16` per request. Is that rate a count over
   a complete header enumeration or a probability over random headers? If headers
   are adversarial, every request could be bad. First step: trace how BIT.md
   generates request headers.
2. FALLBACK.md's 49,911-child bound charges three children per swap.
   Opposite-orientation swaps use one child under `paid_children`, so the bound
   is not sharp. This cannot move κ at `eta = 1e-16`, but a sharp count would
   tighten F.

## Credit

Proposition and retained source: Cinna Davis (PR4100), building on source527,
commdata2338 (PR2160) and Jose Manuel (`controlled_normalizer.py`). This check
produced by Nick Petalas. Apache-2.0.
