# The path-level reopening condition

The finished full-stabilizer obstruction is in `FULL-STABILIZER-PROOF.md`.
The extra observation here does not give a complete caller or a κ improvement.

## Scalar additions cannot repair a uniform path deficit

Suppose the isolated original-Y coefficient of a fixed finite bank circuit is

    U_Y=sum_(j=1)^K a_j U_j,

and every product path U_j has at most `2^((m-d)f)` nonzero entries per row,
for some d>0 and chunk parameter f. Scalar factors do not increase support,
so the support of U_Y is at most `K 2^((m-d)f)`. A full m-coordinate native
operator has `2^(mf)` entries per row. Therefore a necessary condition is

    K>=2^(d f).

For K fixed independently of f this fails at sufficiently large f. Polynomial
K(f) is also insufficient. In particular16 scalar paths do not fix a four-
coordinate vacancy for arbitrary f:16 is only the f=1 support threshold.
This is separate from precision and cancellation; cancellations can only
decrease the support. A topology producing exponentially many paths in f
would need its complete all-size work and stock invoice.

It would be wrong to apply this lemma to **every** path in every normalized
OPEN network. The admitted normalized forward cross already supplies an
explicit full-rank path, as follows.

## An actual full-native path, using the normalized alphabet

The physical normalized OPEN forward block at stage s is

    F_s,physical = [[T_s,0],[T_s K_s,T_s]],
    T_s=F_s,   K_s=C_q C_p^-1 pre_s

in the orthogonal common2/own-fresh5 chart, with any exact representative
Paulis retained in the monomials. Take the **forward cross** at stage0 and
diagonal progress at all other stages. The resulting coefficient path is

    U_path=(F_(L-1)...F_0) K_0
          =(F_(L-1)...F_0) C_q C_p^-1 pre_0
          =F_global X_p pre_0.                              (1)

This is exact, including phase, since all coordinate C gates commute and
`C_p^-2=X_p`. The final factor pre_0 is monomial. Thus the path has full
native rankm on every port, and rankmf on f tensor columns. This statement
uses the source-bound **normalized forward cross** T K; it does not assume
a changed raw reverse-J interface or infer anything about its admission.

`path_witness.py` verifies (1) on all12 actual ports and L=1,3,5,9. It checks
complete signed tableaus and independently fixes the exact Gaussian phase at
n17 for one A and one C port. The written identity is valid for all f and L.

A literal bank exchange can place original Y on the forward source lineage.
This exchange is paid and its bank-dependent logical code must be retained.
The circuit's exact arbitrary-input physical block makes the path well
defined. This does not establish the whole caller's monotone fronts or final
operator. The original B1 clearance instead routes original Y through the
deficient inverse cross; the new topology must change that fact.

## One concrete topology worth a bounded algebraic attempt

Use three public banks and a directed cycle of **normalized forward** OPEN
calls, with explicit bank permutations and signs. Retain the three distinct
operator codes until the entire scalar circuit clears. Require every original
input lineage to take at least one source-to-target forward cross of the form
(1). This changes the factorization responsible for the unary-insertion bound:
the original-Y coefficient can contain a full-native path rather than only
the product beginning with `F_0 P_0 R` of rank3/5.

The next mathematical obligation would be one exact finite free-operator word
that clears every unwanted cross coefficient on all three arbitrary inputs,
while retaining those full-native diagonal paths. It should be attempted in
the admitted local alphabet before any frame or numerical search. A generic
scalar three-bank cycle does not automatically clear when its kernels are
different noncommuting operators. No clearing word is supplied here.

The local forward query bill remains the inherited
`H_1=8,H_2=40,H_3=16` per call, with ordinary/private helpers0. Raw bank
permutations and all monomial normalizers are paid whole-array operations.
For example, one12-port three-bank cyclic permutation can be lowered as two
raw swaps per port, at most72 complex additions and24 complex negations,
using the explicit three-addition/one-negation two-field swap. Any inactive
bank's native progress also remains paid. This proposal supplies neither a
favorable complete native moment nor a stronger κ; its value is that it has
an actual full-rank operator path and is outside the proved unary insertion
class, without appending a full terminal vacancy decoder.

This remains local. Source, normalizer and compiler pins are inherited from
`FULL-STABILIZER-PROOF.md` and are checked in `FULL-NATIVE-PATH.json`.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
