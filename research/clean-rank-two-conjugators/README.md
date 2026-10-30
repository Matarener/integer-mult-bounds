# Ten CNOTs for the three-reflection rank-two clean compiler

This contribution was produced by Nick Petalas.

The rank-two clean square-zero operation has a literal implementation with
three coordinate reflections and **ten scalar CNOTs**, improving the sixteen
CNOTs of JoyboyBrian's merged [#5007](https://github.com/CrocSwap/integer-mult-bounds/pull/5007).
This is a scoped algebraic construction with a written proof and exact finite
corroboration. No scalar-network minimum or new kappa is claimed.

Let g be any linear involution in characteristic two. Four data roles
`a,b,c,d` are arbitrary and helper `h` starts at zero. The complete action is

```text
a <- a + c + g(c)       b <- b + d + g(d)
c <- c                  d <- d                  h <- 0
```

The full five-input action, even when h is dirty, is the displayed data map
and `h <- g(h)`. Thus the clean return is exact; an arbitrary dirty helper
does not satisfy the restored-workspace contract. [WORD.json](WORD.json)
contains all thirteen primitives in chronological order, using role indices
`a,b,c,d,h = 0,1,2,3,4`. Every scalar XOR and inverse operation is included.
[PROOF.md](PROOF.md) derives the new stream by sharing scalar conjugators.

At complete stationary coordinate-reflection price R, CNOT price C and
additional clean-resource reservation/return charge H, the new local bill is
`3R+10C+H`. The explicitly priced dirty rank-two stream in #5007 costs
`4R+4C`; its two disjoint four-operation pieces have no adjacent cancellations.
The new clean word is cheaper precisely when **R > 6C+H**, improving the
previous specified-word comparison `R > 12C+H`. This compares specified streams,
not globally optimal scalar networks. Common basis transport, if needed, must
be charged equally on both sides. No native R, C or H is supplied.

## Evidence and reproduction

From the repository root, CPython 3.12 and its standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clean-rank-two-conjugators/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clean-rank-two-conjugators/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clean-rank-two-conjugators
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clean-rank-two-conjugators --check-source-history
```

Substitute a local CPython 3.12 path elsewhere. Expected output includes
`PASS_CLEAN_RANK_TWO_CONJUGATORS reflections=3 CNOTs=10 no_new_kappa`.
The read-only verifier generates a receipt bound to every package file and
the cited live inputs. It does not import or execute predecessor code.

The checker proves the complete five-input formal endpoint in F2[C2] by
coefficient arithmetic. A separate literal bit-array interpreter checks all
1,024 two-address states, including all 256 clean-helper states, and every
basis column for every involutory permutation on one through six addresses.
All thirteen individual primitive omissions and three boundary controls are
checked. These finite domains corroborate the field-uniform written identity;
they do not prove an unbounded statement by enumeration.

## Scope, overlap and limitations

This takes Open next question 2 of #5007, a changed compiler-side scope of
`bit-new-register-model`. The change matters because the exact reflection
count alone leaves scalar encoding and restoration costs unpaid. It does not
meet the card's native-supplier acceptance gate. The first verified improvement
is packaged without extending the search to other ranks or claiming optimality.

Canonical base is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The prescribed selected-baseline command passed after its inputs were
materialized in this sparse checkout. It authenticates metadata only.
The initial overlap cache paginated 405 open PRs and 5,290 Discussion records
on October 27, 2026. Sparse local note coverage was incomplete; separate Git
searches covered main's complete README tree, with additional merged-PR
searches and the live #5007/#4912 bodies. No competing shared-conjugator
result was found. Unpublished work, arbitrary diffs and omitted history remain
limits; a no-match search is not a novelty certificate.

Native reflection implementation, physical routing/frames/tapes/hosting,
the availability and price of the clean function, recursive admission and
the complete multiplication theorem remain unresolved. Lean, Docker,
the selected scientific replay and predecessor executables are unrun.
Independent human and formal proof-kernel review are unclaimed.

The verifier uses bounded Python-managed allocations, a Power of Ten rule-3
deviation. Width is fixed at five and address size is at most six. The largest
state enumeration has 1,024 entries; permutation enumeration is at most 720
per size. Functions are below sixty lines, checks use explicit exceptions
under `-O`, and both registered runs treat warnings as errors. No external
solver, recursion, subprocess or generated code is used.

## Open next questions

Can an actual native caller supply the stationary primitive prices and one
returned clean role with `R > 6C+H`? Begin with one literal rank-two caller
and price every data movement, inverse scalar map and clean reservation.
Those native contracts and the complete invoice are the blockers.

## Credit

JoyboyBrian #5007 supplies the clean three-projector construction, its exact
reflection-call minimum and the explicit scalar-optimization handoff.
Nick Petalas #4912 supplies the dirty optimum and split compiler. ywz65
#2716 supplies the involution-product identity and arbitrary-coupling compiler
context. Adam Gall #1911, eumemic #288, Ali Romman #468, woklerx #1443,
Gareth Davidson #1333, Arham Tahir #1589 and Cinna Davis #2290 retain the
register-model lineage credit. The new contribution is the shared-conjugator
ten-CNOT stream and its improved specified-word price comparison. New work
is Apache-2.0.
