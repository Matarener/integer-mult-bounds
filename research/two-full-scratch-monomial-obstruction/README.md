# Identity scratch does not unlock full monomial two-FULL routing

**Negative result. No new κ.** The selected conditional exponent stays
`62009/20000000`.

The separated-address theorem allows arbitrary restored identity scratch, and
the grade note allows full monomial routing, but only on exactly two owners.
Neither theorem grants both extensions. For every finite scratch count, the
projected product `T2 W T1` still has rank at least one full copy of the
monomial algebra above `diag(0,0,I,...,I)`. Monomial outer matrices cannot
close that gap. The endpoint `diag(g0,g1,I,...,I)` with two pure high-rank
targets is impossible in this algebra, at every sufficiently large tensor
width.

## Scope and evidence

Original card: `complex-new-helper-inventory`. Scope status: **refined**. The
card asks whether one changed helper inventory survives a complete bill. The
request actually taken is open handoff 8 on
[discussion 1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134766),
as sharpened by the scratch question in
[discussion 4902](https://github.com/CrocSwap/integer-mult-bounds/discussions/4902#discussioncomment-19144315).
The predecessor package states that its scratch theorem and its full-monomial
theorem are not simultaneous. This note supplies the missing simultaneous
obstruction. It does not emit a helper word or replay the seventeen-axis group.

The proof is in [PROOF.md](PROOF.md). The verifier authenticates the two
predecessor proofs, checks the target-rank arithmetic, and corroborates the
subspace rank on a noncommutative graded model (`S3` times an additive rank).
One hundred ninety-two invertible witnesses, both shear orientations, and
central ranks 0, 1 and 30 keep the gap equal to `|S3|`. A scratch-only input
does not produce that extra copy. Zeroing the clean transverse factor, or
cutting off below `2t`, drops the rank. Those controls are part of
[verify.py](verify.py). They are not a Clifford enumeration.

Source pins are in [SOURCES.json](SOURCES.json). The two live inputs are the
predecessor proofs at the pinned base. They are not copied.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/two-full-scratch-monomial-obstruction --check-only
python3 -B scripts/research_package.py --package research/two-full-scratch-monomial-obstruction
```

Direct checks, each under two seconds here:

```sh
python3 -I -W error -B research/two-full-scratch-monomial-obstruction/verify.py
python3 -I -O -W error -B research/two-full-scratch-monomial-obstruction/verify.py
```

Both print `PASS_TWO_FULL_SCRATCH_MONOMIAL_OBSTRUCTION` with `gap=6`. No
native suite, Lean build, selected cold replay or compiler/outer replay was
run.

## Open next questions

1. Can a FULL shear that reads a scratch owner, rather than only a monomial
   matrix between the two macros, avoid the extra copy of B? This matters
   because the intermediate rank bound uses that the first shear reads the
   other main owner only. The first step is one explicit scratch-reading shear
   and its projected image. The blocker is that the native two-FULL schedule
   does not contain that macro.

2. Does one already-transformed helper state, entered as a non-identity
   summand, change the projected rank? This matters because identity scratch
   is the only extra owner this note allows. The first step is to name that
   helper's input operator and price the optimistic bill before any search.
   The blocker is the predecessor's warning that such a state is not absorbed
   into `L`, `W` and `R`.

## Credit

The separated-address nullity theorem and the two-owner full-monomial grade
note are Chris R / Clear1nsight's `research/two-full-central-obstruction`,
including the Cinna Davis / 1337isnot1337, Cao Yifan, zxv, Jacob Alan Sussman,
Ali Romman, Dugongue, Nick Petalas and Richard Hoekstra lineage recorded
there. The scratch question is JoyboyBrian's handoff on discussion 4902.
This package only proves the simultaneous rank gap those results leave open.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
