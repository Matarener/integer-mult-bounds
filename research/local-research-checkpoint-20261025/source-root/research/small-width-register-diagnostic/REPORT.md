# Small-width register diagnostic: first bounded round

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

**Follow-up completed:** the [unequal-coordinate round](../unequal-coordinate-register/REPORT.md)
closes the proposed W=4, 11-call target in the enlarged 25-direction alphabet
by an exact integer-count obstruction. The fractional 5W/2 bound below
remains correct, but its apparent four-register opening is now superseded.
The follow-up also gives a larger inventory that passes the count and
determinant tests, without constructing an operator word.

**No new supplier or multiplication bound.** This round closes a natural
bit-side projector alphabet for every register count, rejects one fixed
complex-side schedule, and identifies a specific larger bit alphabet that
escapes the tested rank bound. It does not establish that the larger alphabet
contains a saving network.

The published selected conditional result at the start of this round is
`κ=0.000723571590007464`, at main commit
`12a4934d15006e8c10f9b2264f13f8f341be802b`.
This working research branch also contains earlier notes with historical
selected values. They are not the publication status.

## Decision

Do not expand a coordinate/pair-projector search to more registers. The
obstruction below already covers every W, and it extends to the whole signed
cube alphabet, including three-coordinate vectors `(±1,±1,±1)`.

The next concrete bit candidate alphabet is the union of those 13 lines with
the 12 signed-permutation lines of `(1,1,2)`, using integer multiples of their
rank-one orthogonal projectors. Its denominator-cleared second-order
character screen has exact optimum **5W/2**, rather than **3W**. Thus it does
not rule out W=4 with 11 calls. This is a scoped opening in an obstruction,
not a network, scalar identity, or feasibility certificate for the full
second-order matrix equations.

Do not broaden the complex search by declaring arbitrary address operations
free. The fixed-word failure below leaves directional Hadamards, different
interleavings, coefficients, endpoints, and register counts untested. No
complex candidate has earned a full construction run.

## 1. Models and admission obligations

We use the group-ring register formulation described in
[PR #288 at its inspected revision](https://github.com/CrocSwap/integer-mult-bounds/blob/475a088b5862f75f0b10596cfd6842d19531a5ec/research/negative-results-paradigm-search/README.md).
Its README SHA-256 is recorded in the certificate. This round did not replay
its unbundled searches or independently prove all its broader obstructions.

On the bit side, a paid move is

`F_j = I_W + ([A_j] - 1) N_j`,

where `A_j` is a rational 3-by-3 shear matrix, `[A] [B]=[A+B]`,
and `N_j=u_j v_j^T` is a rank-one scalar idempotent over F2:
`v_j^T u_j=1`. Fixed invertible scalar mixing can be absorbed into these
idempotents. The common all-role target, after normalizing the final scalar
permutation, is `[I_3] I_W`. Every register carries arbitrary input. There
are no uncounted zero-initialized helpers. This is the **abelian common-target
model**; the theorem below does not cover mid-word free changes that enlarge
the frame group or different per-role targets.

For the tested bit alphabet, every nonzero A has rational rank one and
corresponds algebraically to one smaller interchange plus its compiler
adapters. A positive identity would still need the full fixed-tape,
exceptional-class, precision, stock, and finite bridge accounting.

On the complex side, use Gaussian-dyadic directional Hadamards

`G_(d,c) |_(x,x+d) = (1+i)/2 * [[1,1],[1,-1]],  c.d=1`,

where `c.x` labels the two members of a pair. Scalar idempotents have integer
vectors u,v with entries in `{0,±1}` and `v^T u=1`. Two specified intermediate
address CNOTs are allowed. This is an algebraic necessary-condition model,
not a declaration that all its adapters have zero tape cost.
The retained [Clifford interface](../../notes/general-clifford-frames.tex)
explicitly charges rank-zero adapters as movement and scalar work;
[compact routing](../../notes/compact-control-movement.tex) supplies the
binary changes of basis with a bit-side cost. Those bills and coupling
conditions remain obligations for any future positive construction.

The exact replay in `replay.py` keeps distinct group elements distinct. A
successful one-column reduction is never accepted as a uniform identity.

## 2. Bit result: an all-W obstruction for signed-cube projectors

**Claim in the above register model.** Suppose each paid frame is

`A_j = alpha_j v_j v_j^T / (v_j^T v_j)`,

where `alpha_j` is an integer and the nonzero vector v has coordinates in
`{0,±1}`. Then any common-target identity needs at least `3W` rank-one calls.
This allows arbitrary ordering, arbitrary scalar idempotents, arbitrary W,
and all 13 projective directions in this alphabet. A common rational change
of basis of the whole alphabet and target does not evade the argument.

This specializes augmentation/rank ideas already present in the community
barrier work. No novelty or priority claim is made for the underlying method.

### Second-order character lemma

Clear denominators by B=6A. For an integer linear functional lambda whose
diagonal coefficient sum is odd, the target exponent is
`lambda(6I) = 2 mod 4`. Map the group generator `[A]` to
`(1+t)^lambda(B)` in `F2[t]/(t^3)`. Negative integer exponents are permitted:
`1+t` is a unit, and its first two coefficients depend only on the exponent
modulo 4. This is a homomorphism on the common denominator lattice.

Write `k` for the number of odd exponents and `l` for the number congruent to
2 modulo 4. The coefficient of t in a correct word is zero, so for the odd
moves, assembling their scalar vectors as U and V gives `UV=0`. Therefore

`rank U + rank V <= k`.

The coefficient of `t^2` from odd moves, including their individual quadratic
coefficients and all ordered cross terms, is `U R V` for some k-by-k matrix R.
The even moves contribute at most l additional rank-one matrices. The target
coefficient is `I_W`. Hence

`W <= min(rank U,rank V) + l <= floor(k/2)+l`.

In particular, put

`f(b) = min(b mod 4, -b mod 4)/2`,

whose values on residues 0,1,2,3 are `0,1/2,1,1/2`. Every such character gives

`W <= sum_j f(lambda(B_j))`.

This is a necessary condition. Its satisfaction does not solve the matrix
equations, higher-order equations, or the full group-ring identity.

### A certificate charging at most one per paid frame

Average characters over signed coordinate permutations. Take weight 2 on
the orbit of `lambda(B)=B_22+B_12`, and weight 1 on the orbit of
`lambda(B)=B_22+B_02+B_12`. Each orbit average still has target cost one.
The combined target cost is 3. The averaged cost of one projector is:

| Number of nonzero coordinates of v | Odd alpha | alpha=2 mod 4 |
| --- | ---: | ---: |
| 1 | 1 | 0 |
| 2 | 1 | 2/3 |
| 3 | 1 | 0 |

For alpha=0 mod 4 it is zero. Thus every paid rank-one frame costs at most
one in the combined inequality: `3W <= number of paid calls`.

The certificate computes every signed direction and amplitude residue with
exact rational arithmetic. It also retains the simpler pair-only proof.
The three-coordinate direction `(1,1,1)` escapes that simpler proof, but
**does not escape the combined proof above**.

## 3. A specific larger alphabet survives this screen

Add the signed permutations of `(1,1,2)`. Their norm is 6, so the same
denominator clearing and the same group-ring character lemma apply. The
preceding combined cost of an odd-amplitude new projector is `5/3`, which
breaks the one-unit-per-call estimate.

We did not stop at finding a failure of one certificate. The exact checker
enumerates all **2,048** symmetric-matrix character residue choices with odd
diagonal sum. There are 19 distinct signed-permutation-averaged profiles.
For this weighted-character method, matching rational primal and dual
certificates give an optimum of **5/2**.

The primal uses the following orbit averages:

| Weight | Character |
| --- | --- |
| 3/4 | `B_22` |
| 3/2 | `B_22+B_01+B_02+B_12` |
| 1/4 | `B_00+B_11+B_22+2B_01+2B_02+2B_12` |

Each paid frame in the enlarged alphabet has combined cost at most one.
The dual assigns masses `3/4,3/4,1/4,3/4` to the odd-amplitude norm
`1,2,3,6` classes and zero to the even-amplitude classes. Every enumerated
character profile has dual cost at least one, and the masses sum to 5/2.
Symmetrizing any feasible character weighting preserves the target and
per-frame bounds because the alphabet is invariant under signed coordinate
permutations. Thus the dual covers the whole specified character-bound LP,
not merely a few selected characters.

For W=4 this gives a lower bound of 10 calls. It leaves the proposed 11-call
target open. This does not show that 10 or 11 calls are achievable, nor that
other lower bounds cannot exclude them. It isolates an explicit alphabet
change that this diagnostic cannot dismiss.

## 4. Complex result: one eight-call schedule is excluded

The tested word has eight paid positions t=0,...,7. The paid register is
`r=t mod 3`, and the coordinate Hadamard is on axis `floor(t/3)`. At every
position, `u=e_r` and `v_r=1`; each of the other two entries of v ranges
independently over `{0,±1}`. This permits nine feedback choices per move.

Before position 2, apply address CNOT `bit 0 -> bit 1` on register 0.
Before position 5, apply address CNOT `bit 1 -> bit 2` on register 1.
The target is the full three-coordinate Hadamard on each arbitrary input
register. Its relation to the selected C primitive uses the retained diagonal
phase adapters, whose physical charges would need inclusion for a supplier.

Reduce Gaussian dyadics modulo 5 by `i -> 2`; then `(1+i)/2 -> 4` and the
inverse coefficient is 2. The exact checker follows one input basis column.
It computes all reachable states after four forward moves and all states
that can reach the required output through the four remaining moves.

* All `9^8 = 43,046,721` feedback words are covered.
* The two middle-state sets contain 157 and 471 distinct vectors.
* Their intersection is empty.

Every exact characteristic-zero word in this family would specialize to a
matching middle state. Therefore the empty intersection excludes this fixed
family. This is an independent enumeration, not an SMT UNSAT claim.
All individual inverses are checked on every basis vector for every feedback
choice. A nine-call unmodified schedule is a positive control and has a
matching state; the uniform group-ring replay also accepts its naive word.

This does not exclude other coordinate orders, free insertions, directional
Hadamards, mixing vectors, Gaussian coefficients, arbitrary monomial free
maps, terminal adapters, or W=3 in the full register model.

## 5. What the exploratory solvers did and did not establish

`screen.py` was used to formulate exact necessary equations. An initial broad
bit run over 36 coordinate/pair matrices hit its 60-second solver limit.
An initial dense complex encoding was stopped for excessive memory; a second
encoding reached its 1.5 GB solver allocation cap. The smaller one-column
counterexample-guided formulation hit its 60-second limit without a candidate.
These outcomes are **unknown**, not negative results. They are development
observations, not the basis of either exclusion above.

The structured bit and complex words were rejected by the solver. The bit
character proof is stronger than that fixed-word test, and the independent
complex meet-in-the-middle enumeration verifies its rejection without Z3.
Positive naive schedules and deleted-child negative controls exercise both
encodings. `replay.py` separately checks full uniform identities and includes
finite-field aliasing and one-column-only cancellation controls.

## 6. Target budget and next admission gate

The numerical targets remain worthwhile:

* `m=3,W=4,s=11` supports coarse bit saving `79/1000` by exact integer-power
  comparison. It does not support the slightly higher `0.08` design point.
* `m=3,W=3,s=8` supports complex saving `3/40`.
* With the hypothetical bit saving `0.079`, stopping fraction `3/40`, and the
  retained ordinary leaf saving, the effective bit saving is
  `29231153797/400000000000`, above the admitted `0.07` target and below the
  stopping fraction. The outer target `1/16` still needs its domain extension,
  complete suppliers, bridge, and strict implementation margins.

The failure of an obstruction does not justify a larger numerical search.
The next design task should specify one operator word using the `(1,1,2)`
orbit and explain how it cancels unwanted operator terms while moving all
four independent inputs. Apply the determinant and complete second-order
matrix equations before a full group-ring search. Independently identify a
complex word that changes a premise of the failed fixed schedule.

Stop if the only rationale is that the scalar moment has room. Do not enlarge
W or solver time until an actual interaction pattern survives these tests.

## Reproduction

The authoritative small certificate needs only Python's standard library:

```sh
python3 -B research/small-width-register-diagnostic/certificate.py
python3 -B research/small-width-register-diagnostic/replay.py
```

To rerun the optional SMT checks, install `z3-solver` (tested with 5.1.0) and
use `screen.py SIDE --structured --timeout-ms 60000 --output PATH`.
The `--control positive` and `--control negative` options fix naive words
with all calls or one omitted call. A timeout has no mathematical meaning.
The broad default bit catalog is now excluded by the stronger written proof;
repeating its unconstrained search is unnecessary.

No selected certificate, production verifier, integration branch, or main
branch was changed by this round. No new result was pushed or announced.
