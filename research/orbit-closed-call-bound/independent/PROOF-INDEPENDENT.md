# Sharp orbit-call bound with arbitrary dirty spectators

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.

The three arguments below use three explicitly different algebras. They share
an abstract call-count conclusion, but none proves that an arbitrary native
controller belongs to these algebras. The root-orbit geometry is the companion
component's source-bound obligation. This independent proof and checker do not
import that component, its historical program, or a Clifford compiler.

## Precise linear-word contract

Let `B>=1` and `h>=0`. There are `2B` data banks with three port coordinates
each, and `h` additional spectator coordinates. The entire matrix therefore
has `n=6B+h` rows and columns. Every initial data and spectator coordinate is
independent and arbitrary. A spectator is a coordinate of this algebraic
module; calling it scalar does not assert a particular physical array width.

A charged local call, up to parameter-independent invertible scalar entrance
and exit matrices, is

`diag(z,x,y,z,x,y)`

on exactly two banks and identity on every other coordinate. The two banks
may be chosen anew. Arbitrary intervening invertible scalar matrices may mix
data and spectators. The word is finite and linear, with no data-dependent
branching or uncharged parameter-dependent generator. The final contract is

`diag(g I_(6B), I_h)`, where `g=xyz`.

Thus spectators return literally, and their dirt cannot leak into data.
Fixed invertible scalar endpoint factors also preserve the rank argument
when interpreted as explicit changes of coordinates; literal return is the
contract in the displayed coordinates after those fixed factors are undone.
The proof does not allow a spectator initially promised to contain a useful
parameter-dependent function of the data.

## BIT: the dual-number specialization

Work over `R=F2[C2^3]`, with commuting generators and `x^2=y^2=z^2=1`.
The map `x -> 1+e`, `y,z -> 1` to `F2[e]/(e^2)` is a ring homomorphism:
`(1+e)^2=1` uses characteristic two. Every matrix factor has an image
`A_(j,0)+e A_(j,1)`. Constants have zero first coefficient. Each charged
diagonal has exactly two varying diagonal positions, so its first coefficient
has rank two. Constant invertible entrance/exit factors preserve that rank,
even if they mix all data and dirty spectators.

For a chronological product `W=A_L ... A_1`, the first coefficient is

`W_1=sum_j A_(L,0)...A_(j+1,0) A_(j,1) A_(j-1,0)...A_(1,0)`.

There may also be any number of constant bridge factors; they add no terms.
Rank subadditivity and `rank(P A Q)<=rank(A)` give `rank(W_1)<=2L`, where L
counts charged calls only. The target specializes to
`diag((1+e) I_(6B),I_h)`, so its first coefficient has rank exactly `6B`.
Consequently `L>=3B`. No assumption that spectators remain unmixed at an
intermediate time was used. The result permits arbitrarily many dirty
spectators returned at the endpoint.

## Complex C4: two evaluations, not a derivative of x^4

Over `C[C4^3]`, evaluate at `(x,y,z)=(1,1,1)` and `(i,1,1)`. Both maps
respect the generator relations. If `A'_j,A_j` are the two evaluations, then

`A'_L...A'_1-A_L...A_1 = sum_j A'_L...A'_(j+1) (A'_j-A_j) A_(j-1)...A_1`.

Every parameter-independent bridge contributes zero. Each charged call has
difference rank two, with two entries `i-1`, and scalar invertible entrance/
exit factors preserve that rank. The target difference is
`diag((i-1)I_(6B),0_h)` of rank `6B`. Thus again `L>=3B`. This holds for
arbitrary complex scalar bridge coefficients, hence for Gaussian dyadic ones.
It does not use a derivative inconsistent with the relation `x^4=1`.

An inverse generator is a real distinction here: `x^-1=x` in the BIT group,
but `x^-1` evaluates to `-i` in this complex test. The checker includes an
actual word mutation that is invisible to the BIT regular action and fails
the C4 regular action.

## C3-covariant source rotations require the cover

Suppose the alphabet also has a source rotation O satisfying
`O x O^-1=y`, `O y O^-1=z`, `O z O^-1=x`, and `O^3=1`.
The previous one-character specializations do not extend by merely declaring
O to be a scalar constant: conjugation cannot turn the scalar `1+e` (or i)
into 1. This is an actual algebraic obstruction to that proposed shortcut.

Instead use the three-dimensional regular C3 cover. Let O cyclically permute
the three coordinate axes and represent

`X=diag(t,1,1)`, `Y=diag(1,t,1)`, `Z=diag(1,1,t)`.

Conjugation by O cyclically permutes these matrices, and `XYZ=t I_3`.
For BIT take `t=1+e`; for C4 compare `t=1` and `t=i`. These are valid
representations of the stated semidirect relations. Faithfulness on the
entire semidirect group algebra is not required for a necessary condition.
The word "regular" describes the C3 cover, not a claim of that larger
faithfulness.

Each of the six varying local port blocks contributes rank one, so the local
first-coefficient/difference rank is six. The target contributes rank three
per data row and zero per spectator, giving `18B`. The same product argument
gives `6L>=18B`. Every spectator lifts to three cover coordinates and still
has identity target. The allowable free bridges must have identical constant
images at both evaluations (or zero dual first coefficient), including the
displayed cyclic cover permutation. Arbitrary native source automorphisms or
phase adapters are not automatically such bridges.

## A sharp word: three local calls per pair

Pair the `2B` banks into B disjoint pairs. On one pair let
`D=diag(z,x,y,z,x,y)`, and let P cycle the three port rows in each bank by
the same orientation. P is a parameter-independent scalar permutation.
The three matrices

`D`, `P D P^-1`, `P^2 D P^-2`

are diagonal; in every one of the six positions their product contains each
of x,y,z exactly once. Since those generators commute, their product is
`xyz I_6`. Applying this word to all B pairs gives exactly
`diag(xyz I_(6B),I_h)` with `3B` charged calls. All spectators may be dirty
and remain unchanged. Therefore the lower bound is sharp in each stated
grammar. Constants and port permutations may be free in this algebraic
count; that is not a physical claim that their scans are free.

This construction uses scalar permutations of *port rows*, without renaming
any source generator. A physical source rotation is a different operation;
its admission uses the separate covariance argument above. On the cover the
same scalar port word acts blockwise and still has the claimed endpoint.

If a tensor version of the grammar defines `x=product_j x_j`, and similarly
for y,z, with commuting independent copies of the same generators, the word
remains an identity. Specializing one `x_j` and all other generators to 1
gives the same lower bound. This conditional algebraic extension does not
provide an all-chunk native implementation or a physical recursive invoice.

## Independent finite checks and controls

The checker represents the group action directly on every regular basis
vector. It does not multiply the companion checker's group-ring coefficient
matrices. At `B=1,2,4` and `h=0,1,3`, it constructs literal local permutations,
their scalar port conjugations and the complete word. It compares all 1,104
BIT regular input columns and all 8,832 C4 regular input columns, including
every spectator column. These are faithful regular actions of the respective
commutative groups, so the comparisons fix the full formal operator of these
monomial words. Reversing the commuting call product is accepted in both
grammars for all nine cases.

For BIT, coefficient augmentation and first coefficient are reconstructed
from the regular action on zero-address inputs. Equivariance is then checked
on every remaining address column, so this extraction cannot silently omit
a coefficient. A free transvection that mixes an arbitrary spectator into
an active x port is conjugated around the local call; its actual derivative
matrix changes, remains invertible at augmentation, and retains rank two.
This executes the spectator-mixing case covered by the written proof.
Independent exact Gaussian elimination checks the complex evaluation ranks.
The C3 matrices, covariance, fourth-power relation and full target variation
are checked exactly; the BIT cover's three first-coefficient projectors have
the same explicitly verified cyclic support pattern.

Nine adverse cases execute production acceptance predicates:

- Omit one local call, or repeat the wrong port conjugate: the full operator
  endpoint fails.
- Add a dirty spectator into a public row: all public-input columns still
  pass when spectator dirt is suppressed, but the complete matrix fails.
- Leave a data coefficient in a spectator: literal return fails.
- Label a paid full-common transform as one local call: its derivative rank
  is six rather than at most two.
- Replace a positive x occurrence by its inverse: BIT accepts, C4 rejects.
- Label a parameter-dependent full transform as a free bridge: its two
  evaluation matrices differ.
- Combine the cyclic source rotation with the old one-character y image,
  or reverse the cover rotation: the actual covariance identity fails.

Each rejection checks its exact intended error and repeats the same candidate
with only that predicate disabled, outside the rejection catch. These are
predicate-sensitivity checks, not a claim that disabling one predicate would
pass every other independent obligation. Normal and optimized Python 3.12
must emit identical complete receipts. Fresh absolute external outputs use
exclusive creation.

The finite verification and written all-B/h proofs do not certify root
geometry, native adapters, source windows, scalar cost, dirty-copy capacity,
rounding, physical controllers, storage or an outer multiplication theorem.
Those obligations remain separate; in particular no new kappa is claimed.
