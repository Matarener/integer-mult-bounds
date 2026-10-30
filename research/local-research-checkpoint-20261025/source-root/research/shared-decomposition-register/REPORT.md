# Balanced decompositions close the remaining signed-triple repair

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

**Research status: retired at Douglas Colkitt's direction on 2026-10-10.**
Retirement applies to this balanced 16-register, 40-call inventory and its
tested repair campaign. Preserve the proofs and certificates, but do not
resume call-order searches, larger scalar-matrix searches, or incremental
repair enumeration for this inventory without a new mechanism explicitly
changing a premise of the obstruction. This is a research-direction
decision, not deletion of a Git branch or a universal impossibility claim.

**No new supplier or multiplication exponent.** The remaining signed-triple
extension of the 16-register, 40-call inventory is impossible in the tested
common-target abelian model. Together with the
[preceding exclusions](../compressed-sector-register/REPORT.md), this closes
all 50 tested opposite-pair extensions.

The stronger conclusion is useful: retaining the 40 original calls and
adding only signed-triple calls, with arbitrary integer amplitudes, requires
**at least eight additional odd-amplitude calls**. That brings the count to
at least 48, where the retained rank-one moment cannot certify any positive
saving. This is a lower bound, not a claim that a 48-call repair exists.

## 1. Contract and scope

The model is the formal additive rational-frame identity over F2

`prod_j (I_16 + ([A_j]-1) N_j) = [I_3] I_16`,

with arbitrary rank-one scalar idempotents N_j and arbitrary call ordering.
All registers carry independent inputs. Constant scalar mixing is already
permitted through the N_j. Retain exactly the original 40-call inventory:
12 coordinate calls, 12 signed-pair calls, four amplitude-three signed-triple
calls, and 12 unequal-coordinate calls.

This round permits any additional frames

`A = alpha vv^T/3`, where `v in {(1,±1,±1)}` and `alpha` is any integer.

These include the two opposite signed-triple calls left open last round.
Nonzero added frames have rational rank one. Zero frames have no effect.
The proof does not require a determinant-valid choice of additions, so it
also excludes the stated cases after imposing that further requirement.

It does not cover replacements or removal of original calls, additions
in other directions, arbitrary rational amplitudes, other inventories,
mixed-rank recursive bills, or non-abelian interfaces. It is not a barrier
for all small-width networks or integer multiplication.

## 2. The shared matrix equations really are feasible

The previous round proposed checking thirteen decompositions of a common
matrix Q into twelve nontriple idempotents, with its complement T=I+Q
decomposing into the four original triple idempotents and two new ones.

Those equations admit exact solutions. The artifact contains all 42
matrices for three examples:

| rank(Q) | rank(T) | Nontriple row span | Nontriple column span | Commuting? |
| ---: | ---: | ---: | ---: | --- |
| 10 | 6 | 10 | 10 | Yes |
| 11 | 6 | 11 | 12 | No |
| 12 | 4 | 12 | 12 | Yes |

Every supplied matrix is checked to be a rank-one idempotent, and every
one of the thirteen shared equations is checked exactly over F2. Thus
infeasibility of those equations alone would be a false conclusion.
Noncommutativity alone does not rescue the examples either.

The missing condition is that a valid word needs the nontriple calls to
span **all 16 scalar dimensions on both sides**. Combining that condition
with the shared equations gives the obstruction.

## 3. Twelve decompositions form an exact balanced cover

Clear denominators by B=6A. For a character q on symmetric entries,
substitute `[A] -> (1+t)^(q(6A))` in `F2[t]/(t^3)`.
An odd diagonal coefficient sum makes the target `(1+t^2)I_16`.

The earlier audit supplied thirteen characters selecting sixteen original
calls with exponent 2, all other original exponents being zero modulo 4.
Each selection includes the same four triple calls. Remove those four
calls, and omit the one all-coordinate twelve-call remainder.

The resulting **twelve sets B_b** each contain twelve of the 36 nontriple
calls. **Each nontriple call appears in exactly four sets.** The checker
regenerates all twelve characters and verifies this incidence count.

For any signed-triple direction and integer amplitude alpha, each of these
characters gives exponent `2*(alpha mod 2)`. Thus define T as the sum of
the four original triple N_j and all added odd-amplitude triple N_j.
Even-amplitude additions contribute zero at this order. Every valid word
must satisfy the same twelve matrix equations

`Q := I_16 + T = sum_{j in B_b} N_j`.

There are no chronological cross terms in these equations: all exponents
are even, so every factor has zero linear coefficient.

## 4. A balanced-decomposition rank lemma

Factor the 36 nontriple matrices as `N_j=u_j v_j^T`. Let

* c be the dimension of the span of all u_j;
* d be the dimension of the span of all v_j;
* r be rank(Q).

Then the twelve equations and their fourfold incidence imply

**`c + d + r <= 36`.**

Here is a proof that does not restrict the matrices to projections in a
common basis, commuting matrices, or any particular rank of Q.

For a set B_b, form U_b from its twelve columns u_j and V_b from its twelve
rows v_j^T. Since U_b V_b=Q, the column space of Q is contained in the
span of its selected u_j, and the row space of Q is contained in the
span of its selected v_j. Sylvester's rank inequality gives

`rank(U_b) + rank(V_b) <= 12+r`.

Select c-r indices whose u_j classes form a basis of the global column
span modulo col(Q). Select d-r indices similarly for the global row span
modulo row(Q). The two selections may overlap; count such an index once
in each selection. In B_b, the first selection has at most
rank(U_b)-r members, and the second at most rank(V_b)-r. Hence their combined
incidence in B_b is at most 12-r.

Summing over all twelve sets, each selected index is counted four times:

`4(c+d-2r) <= 12(12-r)`.

Rearrangement gives the stated inequality. This argument only uses the
rank-one factorizations and the displayed shared equations.

## 5. A uniform word forces both spans to be full

Choose the character `q=(0,0,1,0,0,1)`, in entry order
`(00,11,22,01,02,12)`. It gives target exponent 2 modulo 4 and annihilates
every signed-triple frame modulo 4, for **every integer amplitude**.
Indeed for v=(1,±1,±1),

`q(6A) = 2 alpha (v_2^2 + v_1 v_2)`,

which is a multiple of 4. Thus all original and added triple factors become
the identity in the truncated ring. Only the 36 nontriple calls remain.

The quadratic coefficient of their product is a sum of scalar multiples
of N_j and N_j N_i. Its column space is contained in the span of all u_j,
and its row space in the span of all v_j. The target coefficient is I_16.
Therefore **c=d=16**, regardless of call ordering.

The rank lemma now requires r<=4. Since Q+T=I_16, rank(T)>=16-r>=12.
But T is a sum of only four plus o rank-one matrices, where o is the number
of added odd-amplitude triple calls. Consequently

`12 <= rank(T) <= 4+o`, and therefore **`o >= 8`**.

In particular the two-call extension has o=2 and cannot work. All four
signed-triple directions are covered directly, without relying on a
numerical search or a finite-field sample of a uniform word.

## 6. What this means for the budget and search

The original inventory has 40 rank-one calls, so any repair of the stated
kind needs at least 48. With m=3 and W=16 its retained rank-one moment is

`(s/48) * 3^a`.

For s>=48 it is greater than one whenever a>0. Thus this repair family
cannot provide a positive primitive saving under that bill. Adding even
amplitudes does not help the obstruction: they disappear from the relevant
second-order equations while still consuming calls if their frames are
nonzero.

**Retire this inventory and the tested opposite-pair repairs as a search
target.** The useful next proposal must change a named premise: the
nontriple call inventory or shared-decomposition incidence, the frame
alphabet in a way that escapes these character equations, or the recursive
interface. This result does not justify a broad register-count sweep or
unbounded perturbation search.

There are still untested modifications, such as mixed-direction additions.
This note does not rule them out. Before pursuing one, require an explicit
mechanism that changes the rank budget above and retains a target-strength
moment. A loophole in a scoped obstruction is not evidence of a construction.

## 7. Reproduction and limits of verification

Run `python3 -B research/shared-decomposition-register/audit.py`.
The standard-library checker regenerates the balanced incidence structure,
checks the characters and integer-amplitude residue rule, verifies all
three explicit shared-system controls, and reproduces the numerical rank
consequences. The controls include a noncommuting example and demonstrate
why omitting the full-span requirement would invalidate the conclusion.

The rank lemma is a written proof; the finite checker verifies its input
data, not arbitrary matrices by exhaustive enumeration. This is not a
Lean formalization or a verification of the underlying multiplication
theorem. No production supplier, selected bound, or publication claim has
changed.
