# Fixed-target encoding audit

This is a source and mathematical audit with two separately implemented
encoders, not an independent human review or a proof-assistant formalization.
The older SMT/bitvector code is `model.py`. The new direct-CNF encoder
`cnf_model.py` imports no Z3 or `model.py` code. It uses the separate row-tuple
and set implementation in `exact_checker.py`.

## What is quantified

The target is exactly `diag([A],[B],[I])`, with
`A=(1,4,3)`, `B=(2,4,3)`, `I=(1,2,4)`. The model has three arbitrary-input
registers. Both encoders constrain all nine entries of their final matrix
over the full 168-dimensional algebra `F2[GL3(F2)]`. In particular, the
third diagonal is `[I]`; every off-diagonal entry, including dependencies on
the dirty third input, is zero.

For each of exactly `n` positions the direct CNF chooses:

1. Three Boolean coordinates of `u` and three of `v`.
2. Exactly one of six coordinate-CNOT labels.
3. The constraint `(u0 AND v0) XOR (u1 AND v1) XOR (u2 AND v2) = 1`.

The last constraint is precisely `v^T u=1`, so neither vector is zero and
`uv^T` is a rank-one idempotent. There are 28 such pairs over F2, hence 168
legal factors at every position. There is no bridge, retained-direct-order,
common-label, label-frequency, register-order, or target-conjugacy restriction.
No symmetry reduction or heuristic pruning is used. Every position is a legal
paid factor, not an optional identity slot.

The original SMT chooses the same six labels using a bounded three-bit
integer instead of six one-hot bits. These two choice encodings are
surjective onto exactly the same paid alphabet.

## Transition equations and orientation

Let `S_t[r,c,h]` denote the coefficient of group element `h` in entry `(r,c)`.
For the chosen factor `F=I+uv^T([g]+[I])`, each column satisfies:

```
q_c[h]        = XOR_r (v_r AND S_t[r,c,h])
translated[h] = q_c[g^-1 h]
delta[h]      = q_c[h] XOR translated[h]
S_(t+1)[r,c,h]= S_t[r,c,h] XOR (u_r AND delta[h]).
```

All six labels are involutions, so `g^-1 h=g h`. The independent encoder
computes this permutation by directly XORing row `j` into row `i` in each
group tuple. The original encoder uses packed matrix multiplication.
An exactly-one-label constraint makes the OR of the six gated translation
coefficients equal the selected coefficient.

Every transition equation is emitted for every one of the 168 group
coefficients and all nine matrix entries, even when a support bound fixes a
state coefficient to zero. No endpoint or transition condition is dropped.
The initial state is the identity over the group algebra. The final entries
are constant full coefficient vectors of the target.

## Boolean clauses

Each AND and XOR is represented by its complete truth-table Tseitin clauses,
not a one-direction implication. Negation is a signed literal. Clause
simplification removes only true clauses, false constants, duplicate
literals, or clauses containing complementary literals. The literal numbered
1 has a unit clause forcing it true; actual allocated variables start at 2.
Constant, repeated-input and opposite-input gate cases are handled by Boolean
identities and exhaustively tested.

Thus, for fixed factor choices, the transition equations determine the state
uniquely. A satisfying CNF assignment decodes to a legal word attaining the
endpoint. Conversely, replaying any legal attaining word fills all state and
gate variables and satisfies every clause, provided the proved support
condition below holds. Tseitin gates add no restriction on the chosen word.

## Why the support bounds preserve every solution

Write `B_t` for the radius-`t` ball in the six-generator address group.
Starting from the identity, after `t` calls every polynomial's support lies
in `B_t`: each step forms XORs of existing coefficients and left translates
them by one coordinate generator. Cancellation only removes support.

Every paid factor is an involution. With `N=uv^T`, `N^2=N`; with
`q=[g]+[I]`, `q^2=0` since `g^2=I` and the characteristic is two. Scalar
entries commute with group coefficients, so `(I+Nq)^2=I`.

Consequently a solution can be replayed backwards from its diagonal target.
After `n-t` backward calls, input column `c` has support in
`B_(n-t) T_c`, where `T_c` is that column's target group element. This is a
right translate: `(R diag([T_c]))[r,c]=R[r,c][T_c]`.
Every solution therefore has

`support(S_t[r,c]) subset B_t intersect (B_(n-t) T_c)`.

Fixing coefficients outside this intersection to zero is admissible.
No assertion about natural matrix equality is used in this proof.

## Why free scalar mixing is covered

Move free scalar changes of basis through the paid coordinate operations.
Their conjugates replace the coordinate projector by all rank-one
idempotents. Conversely, given `u,v` with `v^T u=1`, extend `u` by a basis
of `ker(v^T)` to obtain a scalar change of basis conjugating a coordinate
projector to `uv^T`. The 28 conjugates are also enumerated in the controls.

Augmentation maps every `[g]` to 1, so it sends every paid factor to identity.
The target also has identity augmentation. The net free scalar transformation
in a normalized attaining word is therefore identity. The normalized factor
alphabet covers the free-mixing model specified in the claim.

## Exactly eight versus at most eight

An eight-call UNSAT certificate excludes exactly eight. Because `F^2=I`,
any attaining word of even length at most eight could be padded with repeated
pairs to length eight. Thus exactly-eight UNSAT excludes all those even
lengths. It does **not**, by itself, exclude length seven or all shorter odd
lengths. There is no general parity assumption about word equality here.

The pinned predecessor reports an exhaustive exclusion through length seven
for this direct-nine target, but that large census was not rerun in this
pilot. Combining a validated eight-call certificate with that prior result
would inherit its trust obligations.

A separate exactly-seven certificate for the same fixed target avoids that
dependency: pair padding then excludes every odd length at most seven.
Validated certificates for lengths seven and eight, together with the
independently checked direct-nine word, establish minimum nine **only in
this exact three-register model**. Whether these certificates have actually
been obtained is stated in the final `RESULT.json`; this audit alone does not
claim their existence.

## Checks and remaining trust

The original 15 control groups include all 28,224 address products, all
28,224 two-factor actions, every paid factor, all scalar projectors,
504-column direct-nine replay, dirty-restoration failure, and the known
natural alias. The independent CNF controls additionally test every Boolean
gate case, all 168 one-factor full matrices, 32 mixed two-factor matrices,
and eight fixed-word positive/negative solver cases with and without support
bounds. The known alias passes the natural representation but fails the
formal endpoint.

DRAT-trim is a separate C proof checker from the SAT solver. Positive,
corrupted-proof and mismatched-formula controls calibrate that interface.
A successful checker validates the saved CNF, not arbitrary source code.
The link to the research question rests on the explicit equivalence argument,
the reproducible generator and its recorded tests and hashes. This package
does not claim a formally verified compiler or proof-assistant-checked model.
