# Exact norm and error bounds for the accumulated P104 word

## Contract

Use PR5802 at `9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62`.
There are 770 public fields, 28 owned labels and 25,980 events.
Each field is a vector in a finite dimensional complex Hilbert space.
Assume the retained native chart maps are unitary, with their required phases.
A MOVE then preserves the decoded vector. Coframed ADD, SCALE and COPY act
by the literal rational coefficients. This contract applies at every column
multiplicity for which that native premise holds. It is not an addresswise
maximum norm statement or a new proof of the native premise.

Inputs have no initial error. Each initial field has norm at most B. INIT,
CLEAR and COPY are exact. CLEAR resets only its own field. In the first error
model, each completed MOVE, ADD and SCALE can add a defect to its destination.
In the second model, only MOVE can add a defect. All internal child, wrapper
and arithmetic errors must fit the stated completed-operation allowance.

## Exact input norm

Let R(t,r) be the input coefficient row at cut t for field r. Cut t is after
the first t events; event indices start at zero. The maximum of its L1 norm is

```
P = 131072 = 2^17, at cut 24502, field 93.
R(24502,93) = -65536 e86 + 65536 e739.
```

The triangle inequality proves `||x(t,r)|| <= P B`. Set input86 to minus a
unit vector and input739 to that unit vector to attain P. Invert each initial
unitary chart to obtain physical inputs of the same norm. Thus the constant
is sharp for this word and input norm. It replaces a product of separate
scalar and native norm bounds under the stated unitary premise.

## Exact independent-defect transfer

Let C(t,r,j) be the coefficient of the defect inserted after event j in field r
at cut t. The checker propagates signed coefficients. It takes absolute values
only when it forms a norm. INIT and CLEAR remove their own row; COPY replaces
its destination row. These operations do not remove errors already exported.

For independent defects of norm at most epsilon, the sharp response is
`epsilon * sum_j abs(C(t,r,j))`. Choose collinear defects with the signs of
one attaining row to attain this bound. Literal scalar executions check these
fixtures, and reverse substitution checks the same coefficient rows.

| Rounded sites | All-prefix maximum | Final-public maximum | Strict absolute guard bits, prefix / final |
|---|---:|---:|---:|
| MOVE, ADD, SCALE | 1361937 | 65823/2 | 21 / 16 |
| MOVE only | 458752 | 659 | 19 / 10 |

For example, an absolute defect allowance `epsilon <= B*2^(-t-21)` gives
all-prefix error strictly below `B*2^-t` in the first model. One fewer bit
fails that independent-defect guarantee. These are not claims about the
smallest precision of an actual rounded child.

## Relative completed-operation errors

Let p_r be the ideal input-row L1 norm before an event. Use actual operands
in the following defect contract. Let u be a common relative allowance.

| Operation | Defect bound | a_j | c_j |
|---|---|---|---|
| MOVE r | u times norm of input r | p_r | 1 |
| ADD r += q s | u times (norm of r + abs(q) times norm of s) | p_r + abs(q) p_s | 1+abs(q) |
| SCALE r *= q | u times abs(q) times norm of input r | abs(q) p_r | abs(q) |

Define `J(t,r)=sum abs(C(t,r,j))*a_j` and
`K(t,r)=sum abs(C(t,r,j))*c_j`. Let E be the greatest error over all fields
and cuts. Every defect is at most `u*(B*a_j+c_j*E)`, even if defects are
correlated or depend on the state. Therefore `E <= u*(B*J+K*E)`, where J and K
are the separate maxima. Both maxima occur at cut24502, field93, in each model.

| Rounded sites | J | K | Uniform prefix guard |
|---|---:|---:|---:|
| MOVE, ADD, SCALE | 56663088 | 2428962 | 26 |
| MOVE only | 23855104 | 458752 | 25 |

If `u*K<1`, then `E <= B*u*J/(1-u*K)`. For every integer t>=0,
`u<=2^(-t-g)` gives `E<B*2^-t` with the displayed guard g, since J+K<2^g.
One fewer bit fails this sufficient formula. This does not prove that the
relative feedback inequality is attained by a real rounded implementation.

Final outputs admit a stronger implication. For each final public row r,

```
E_final(r) <= B*u*(J_final(r) + K_final(r)*u*J/(1-u*K)).
```

The smallest uniform integer guard for this formula is 23 for all completed
operations and 19 for native-only errors. The checker evaluates every final
row at `u=2^-g`. The bracket increases with u, so the same guard works for all
t>=0. It tests all smaller guards, including the stability condition u*K<1.
The exact final pairs and rational comparisons are in RESULT.json.

## Erasure boundary

Of 30 CLEAR events, 29 erase nonzero ideal data. Only event25851, field778,
has a zero ideal row. Thus the old word's known-zero recovery proof does not
transfer. This theorem retains exact owned reset. It does not implement that
reset or price a recovery scan. A separate fixture proves that an error copied
to a public field survives CLEAR of its owned source.

## Verification and attribution

The independent rational interpreter checks all798 input columns, coframes,
nested MOVE paths, lifetimes and the full endpoint. A signed forward error
pass covers every event. A transpose pass checks every final error coefficient
and score for all798 outputs. Reverse covectors check all attaining rows and
all30 pre-erasure ideal rows. These algorithms were written and checked by the
same assistant; they are not independent human review.

The operand-weighted feedback method comes from Adam Gall / PR2096, ywz65
and PR2878. PR2878's old-word constants and known-zero recovery result are
not transferred. PR5802 supplies the accumulated word and its native premise.
The new contribution is the sharp current-word input and independent-defect
response, plus the exact conditional relative-error and final-output bounds.
All source bytes and notices are retained. No new kappa is claimed.
