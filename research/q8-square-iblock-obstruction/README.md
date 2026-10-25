# Square i-block obstruction for mixed negative Q8 targets

**Scoped obstruction. No new kappa.** The selected conditional value stays
`0.001672660197076918`.

## Scope and evidence

Original card: `bit-new-register-model`. The scope is **changed**: the card
asks whether a new alphabet escapes the three-register obstruction, and this
package stays inside the existing `F2[Q8]` dirty-register model. The change
and its reason are in [TASK.json](TASK.json). The argument is in
[PROOF.md](PROOF.md).

If an exact word uses only `t_i` calls labelled `i`, then it needs at least
`2 t_i` calls labelled `j`, and trace parity can raise that floor by one.
The inherited bound `5n >= 11t` is therefore never attained on the rays
`t_i = 4 t_j` and `t_j = 4 t_i`. For `4k` copies of `[zi]` and `k` copies of
`[zj]`, no exact word has length `11k`, so every exact word has length at
least `11k+2`. The direct three-call word still costs `15k`.

At seven `[zi]` targets and one `[zj]` target, the same lemma excludes the
count witness `(n_i,n_j)=(7,13)`. The 20-call splits `(9,11)`, `(11,9)` and
`(13,7)` remain open, so this does not decide whether a 20-call word exists.
The direct word has length 24.

Pins for the three predecessor proofs, the catalogue and the selected record
are in [SOURCES.json](SOURCES.json). The selected record and catalogue are
provenance. The three proofs are live inputs and must match their pins.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
python3 scripts/research_package.py --package research/q8-square-iblock-obstruction --check-only
python3.12 -B scripts/research_package.py --package research/q8-square-iblock-obstruction
```

The verifier prints `PASS_Q8_SQUARE_IBLOCK_OBSTRUCTION`. It checks the group
law, direct words for `(4,1)` and `(7,1)` with a restored dirty role,
Sylvester's inequality through dimension 3, one non-identity unitriangular
image fixture, the unique `11k` split and its rejection for `k = 1..32`, and
the four 20-call splits at shape `(7,1)`. Those checks corroborate the
arithmetic. They are not a substitute for the image argument in `PROOF.md`,
and they do not search the surviving splits.

Not run: a satisfiability search of the open splits, Lean, Docker, and the
selected full cold replay. This result changes none of those artifacts.

## Open next questions

1. Does shape `(7,1)` have a 20-call word on `(9,11)`, `(11,9)` or `(13,7)`?
   The relaxation minimum stays 20 until one of those splits is excluded or a
   word is found. A first step is the cubic-tight split `(13,7)`, where
   `rank(X_j)=rank(Y_j)=4`. No such search is included here.
2. Which length in `{13,15}` is the minimum for shape `(4,1)`? This is the
   smallest case of the new ray bound. At 13 calls the count region and the
   square lemma still allow `(4,9)`, `(6,7)`, `(8,5)` and `(10,3)`. The direct
   word has length 15. No exhaustive endpoint search is included.
3. Can any formal saving on these shapes be matched to a physical caller and
   a complete invoice? Nothing here prices scalar routing, restoration,
   hosting, precision or a recursive supplier. That gap blocks any kappa claim.

## Credit

Nick Petalas's PR3570, PR3578, PR3589 and PR3736 retain the cubic identities,
the homogeneous quadratic method, the mixed boundary ranks and the preceding
count region. Their pinned proofs are the premises used here. PR3536 and
PR3558 retain the chronological and cyclic methods, and the lineage recorded
in those proofs stays with PR3517, Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron
Wang/PR2318, Cinna Davis, steph4n-gh and the credited Q8 register sources.

Nick Petalas's open PR #4234 asked the two questions this package takes up:
whether seven `[zi]` targets and one `[zj]` target have a 20-call word, and
whether simultaneous equality can hold on `t_i=4 t_j`. The square-block
collision, the empty equality case on both rays, and the exclusion of
`(7,13)` are the new steps. The #4234 enumeration is not replayed.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
