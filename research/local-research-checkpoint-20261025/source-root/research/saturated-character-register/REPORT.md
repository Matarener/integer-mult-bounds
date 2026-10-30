# Saturated characters close the balanced 40-call inventory

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

**No new supplier or multiplication exponent.** The 16-register, 40-call
inventory from the [preceding diagnostic](../unequal-coordinate-register/REPORT.md)
cannot implement the required word, in any order and with any rank-one
scalar idempotents in the stated common-target abelian model. This is a
matrix obstruction missed by the scalar character-count relaxation.

Repeating that inventory does not repair it. A bounded test of 50
opposite-pair additions rejects 28 and leaves 22 undecided. The undecided
cases are inventories, not circuits or evidence of a stronger bound.

**Follow-up:** the [compressed-sector audit](../compressed-sector-register/REPORT.md)
raises this to 46 exclusions out of 50. It closes all signed-pair and
unequal-coordinate extensions, superseding the proposed signed-pair next
step below. Only four symmetry-equivalent signed-triple variants remain
undecided by these tests.

## Contract and scope

Retain the formal group-ring identity over F2

`prod_j (I_W + ([A_j]-1) N_j) = [I_3] I_W`,

with rational additive frame group, rank-one scalar idempotents N_j,
and arbitrary independent input on every register. Constant scalar
mixing is already allowed through the N_j. The tested A_j are precisely
the previous inventory: four copies of each coordinate projector, two
copies of each signed pair projector, one copy of three times each signed
triple projector, and one copy of each unequal `(1,1,2)` projector.
Thus W=16, there are 40 calls, and sum A_j=16I.

This result does not exclude arbitrary 40-call words, other inventories in
the same alphabet, arbitrary rational frames, or non-abelian interfaces.
It is not a multiplication lower bound. No finite compiler, complex
supplier, or outer-domain extension is established here.

## A saturated count is a basis decomposition

Put B_j=6A_j. For a character q on the six symmetric matrix entries with
odd diagonal coefficient sum, substitute

`[A] -> (1+t)^(q(6A))` in `F2[t]/(t^3)`.

The target becomes `(1+t^2) I_W`. Suppose every call exponent is even.
Then no factor has a linear term; its quadratic term is N_j if its exponent
is 2 modulo 4, and zero otherwise. Hence the exact word requires

`sum_{j in S(q)} N_j = I_W`.

If |S(q)|=W, write N_j=u_j v_j^T, with nonzero u_j,v_j. Form the square
matrices U with columns u_j and V with rows v_j^T. Then UV=I_W implies
VU=I_W. Therefore, for distinct i,j in S(q),

`N_i N_j = N_j N_i = 0`.

This is stronger than the scalar inequality |S(q)|>=W. The selected
rank-one maps form a complete, mutually orthogonal decomposition into
one-dimensional scalar sectors. Orthogonal here means annihilating
products; it does not assume a Euclidean inner product or symmetric N_j.

## The exact inventory has four isolated sectors

Enumerating all 2,048 character residues gives 104 characters with even
exponents and exactly 16 selected calls. These give **13 distinct bases**.
The exact finite certificate lists one character and the 16 call indices
for each basis.

Every basis includes all four triple calls, indexed 15,18,29,32 in the
certificate. The union of the bases includes every one of the 40 calls.
Consequently each triple-call N_i annihilates every other N_j in both
orders, regardless of the chronological order chosen for the word.

Take a nonzero x in image(N_i). Then N_i x=x and N_j x=0 for every j!=i.
On this scalar sector the whole word acts as `[A_i]`, whereas the required
target acts as `[I_3]`. But A_i is rank one and I_3 is rank three, so these
are distinct elements of the additive rational frame group. Contradiction.

The contradiction already appears at second order. Choose the character
`q=(0,0,1,0,0,1)` in entry order `(00,11,22,01,02,12)`.
Each triple call has exponent zero modulo 4, while the target has exponent
2. Every factor therefore fixes its isolated scalar sector modulo t^3,
and the target does not.

This proves impossibility for **all orders and all scalar mixing**, rather
than failure of a particular search. Repeating every call r times and
taking W=16r repeats each saturated basis into a basis of size 16r.
Every triple copy is still isolated from every other call, so the same
proof applies for every positive integer r. The checker explicitly tests
r=2 as a control; the arbitrary-r statement follows from this argument.

## A small, priced escape test

Two additional calls with frames +A and -A preserve the determinant
condition. They also fit comfortably within the proposed coarse bit
budget: the hypothetical 42-call rank-one moment at a=2/25 is below one,
as checked exactly by

`42^25 * 3^2 < 48^25`.

No placement or scalar idempotents for these extra calls are assumed.
The checker tests each of the 25 projector directions with amplitudes 1
and 2, giving **50 inventory variants**. It recomputes the saturated bases
after inserting the two extra calls.

The following generalization of the sector test supplies rejection
certificates. For any call i, co-membership in a saturated basis implies
N_j N_i=0. Seek a character with target exponent 2 and exponent zero on
every remaining call, including i itself. On image(N_i), annihilation
handles the first group, and zero exponent handles the second group.
Every factor fixes that image modulo t^3, contradicting the target.
This proof remains independent of call order.

| Extra projector direction | Amplitude | Variants | Rejected by this test |
| --- | ---: | ---: | ---: |
| Coordinate | 1 | 3 | 3 |
| Signed pair | 1 | 6 | 0 |
| Signed triple | 1 | 4 | 0 |
| Unequal `(1,1,2)` | 1 | 12 | 0 |
| Any of the 25 directions | 2 | 25 | 25 |

Each rejection includes an explicit character and the calls that must
have zero exponent. **Not rejected is not feasible:** no complete
second-order matrix solution or uniform word is supplied for the other
22 cases. In particular, a pair of opposite frame moves does not cancel
when assigned different scalar idempotents, and whether that interaction
can implement the target is the unresolved construction problem.

## Decision and next bounded question

Retire synthesis of the exact 40-call inventory, including enlarged
register counts obtained merely by repeating it. Adding scalar mixing or
spending more time on call ordering cannot evade the proof.

If this family receives one further mechanism test, the smallest departure
is a **42-call inventory with an opposite signed-pair move**, rather than a
new register-count sweep. It changes the equality conditions while keeping
the determinant and numerical target budget. The next obligation is to
construct compatible noncommuting scalar maps satisfying the full matrix
identities, or prove that two extra calls cannot couple the constrained
sectors adequately. Passing the current screen does not favor this route
over a genuinely different coding family; it only identifies an explicit
remaining question.

Do not start a broad 16-register word search solely because 22 variants
survive. Require an interaction pattern or a stronger necessary matrix
test first. Even a positive bit-side word would still need a complex
counterpart and the compiler and outer-theorem work.

## Verification

Run `python3 -B research/saturated-character-register/audit.py`.
It uses only the Python standard library and the preceding inventory
generator. It regenerates and compares all certificate data, checks the
13 bases and their coverage, rejects the doubled inventory, tests all 50
extensions, and verifies the hypothetical moment by integer arithmetic.

A valid 48-call coordinate word is not rejected by either sector screen.
All six decompositions of I_2 into two rank-one F2 matrices are exhaustively
checked to have the asserted orthogonality. These are controls on the
finite implementation, not a formalization of the written general lemma.
The artifact is an exact finite certificate plus a written proof, not a
Lean proof or a verification of the underlying multiplication theorem.
