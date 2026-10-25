# Init-only outside-restriction core

Formal work by conorholds with substantial OpenAI Codex assistance.

`OutsideRestriction.lean` imports only `Init` and follows the explicit-law
pattern in the retained `SharedPiece.lean` and `CutCore.lean` files.
The exact file compiled under Lean 4.21.0 with warnings as errors, serially
under a 256 MiB process-tree watchdog. The two function-equality theorems use
Quot.sound; the vanishing and coefficient-extraction theorems have no axioms.
See [VERIFY.md](../VERIFY.md) for the command and the unformalized boundaries.

`FiniteOutside.lean` further constructs the finite scalar combination itself
by recursion on a list and derives additivity, annihilation and coefficient
recovery from the individual coordinate maps and their biorthogonality. Its
six declarations (including one addition-rearrangement helper) have no axioms.
It needs no abstract combination-map premises and no Mathlib import.

The exact desired claim is:

> If every ambient vector is a sum of a vector in C and a vector in L,
> restriction to C is injective on additive functionals annihilating L.
> Consequently, an actual outside-coordinate relation that vanishes on C
> has every coefficient zero: the relation vanishes on the entire ambient
> space, and evaluation at the actual outside basis vectors recovers its
> individual coefficients.

The first two theorems prove equality of additive maps and the injectivity
statement directly from their operation laws. The final theorem derives the
coefficient conclusion from explicit laws for an abstract combination map:
additivity, annihilation of L, and its coefficient evaluation on the outside
actual basis vectors. It does not assume independence of the restricted
duals. These deductions apply uniformly to the t2 and t3 nonadapted d3
remainder once its written dimension argument establishes C+L=S.

Formal coverage is deliberately limited. The two files do not import
Mathlib's linear maps/subspaces or discharge the characteristic-zero/actual-
basis instantiation. The finite scalar sum is constructed in FiniteOutside;
OutsideRestriction retains the shorter abstract-map interface. The written proof must still
establish dim(C intersect L)=2 and hence C+L=S, identify outside restricted
duals with actual coefficient functionals, instantiate the combination laws
from their biorthogonality, and establish all E8/correction geometry. The finite combination laws are
now derived from individual additivity and actual biorthogonality, rather
than being assumed by the strongest formal theorem. The
file supplies no adapted r0 result and no complete Lean E8 invoice theorem.

No arithmetic-only replica of the 8771/8871 profile case split was added;
the reusable restriction-injectivity deduction is the new formal coverage.
