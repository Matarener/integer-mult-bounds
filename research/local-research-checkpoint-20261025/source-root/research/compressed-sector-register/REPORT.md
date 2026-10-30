# Two opposite pair moves cannot repair the balanced inventory

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

**No new supplier or multiplication exponent.** A compressed second-order
rank argument excludes all six signed-pair and all twelve unequal-coordinate
opposite-pair extensions left open by the
[previous audit](../saturated-character-register/REPORT.md).
Together with its earlier exclusions, 46 of the 50 tested extensions are
now excluded. Four signed-triple variants, equivalent by symmetry, remain
undecided. No scalar matrices or chronological word have been constructed.

**Follow-up:** the [balanced-decomposition audit](../shared-decomposition-register/REPORT.md)
closes all four remaining cases. It supplies feasible shared matrix systems,
including a noncommuting example, but proves that the full-word span
requirements make a target-budget signed-triple repair impossible. The
remaining-case discussion below records this round's earlier stopping point.

The point of this round was to test an interaction mechanism before
launching a word search. The two added pair moves do not provide enough
interaction to repair the constrained scalar sector. The obstruction is
independent of call order and permits arbitrary rank-one scalar idempotents.

## Model and scope

The retained model is the common-target abelian group-ring identity over F2:

`prod_j (I_16 + ([A_j]-1) N_j) = [I_3] I_16`.

Each N_j is an arbitrary rank-one scalar idempotent. All registers carry
independent inputs, with no uncounted clean workspace. Rational additive
frames A_j come from the preceding 40-call inventory, plus two calls +A,-A.
Here A is amplitude 1 or 2 times one of its 25 projectors. The additional
calls have independent scalar idempotents and can be placed anywhere.

This is not an exclusion of general 42-call networks, other frame
inventories, arbitrary rational rank-one matrices, or non-abelian models.
No statement about a fundamental multiplication barrier follows.

## Compressed-sector lemma

Set B_j=6A_j and use characters q with odd diagonal coefficient sum,
substituting `[A] -> (1+t)^(q(6A))` in `F2[t]/(t^3)`.
The target is `(1+t^2)I_W`.

As proved in the preceding audit, a character for which all call exponents
are even and exactly W are 2 modulo 4 forces the selected N_j to form a
complete mutually annihilating rank-one decomposition of I_W. Call its
selected set a saturated basis.

Let S be the intersection of some nonempty collection of saturated bases,
and C their union. Define

`P = sum_{i in S} N_i`,   `d = |S|`.

Since S belongs to a saturated basis, P is an idempotent of rank d.
Every j in C-S shares a saturated basis with every i in S, so

`P N_j = N_j P = 0`.

Let E be all remaining calls: `E = {all calls} - (C-S)`.
Suppose another character q has even exponents on every call in E, and
only l of those exponents are 2 modulo 4. Then any valid word requires

`d <= l`.

**Proof.** Write its factors as
`I + t a_j N_j + t^2 b_j N_j`, with a_j the parity of the exponent and
b_j its second binomial coefficient modulo 2. Compress the quadratic
coefficient on both sides by P. Its single-factor contributions from C-S
vanish. Any two-factor quadratic contribution has the form
`a_j a_i P N_j N_i P`. If either index lies in C-S it vanishes by
annihilation. If both lie in E it vanishes because a_i=a_j=0.
Thus the compressed quadratic coefficient is exactly

`sum_{j in E, exponent(j)=2 mod 4} P N_j P`.

Its rank is at most l, since every N_j has rank one. The compressed target
coefficient is P, of rank d. This proves the inequality. The argument uses
no proposed ordering and does not assume that the remaining N_j commute
with P or preserve its image.

## Signed-pair extension: rank four is required, rank two is available

Take A to be the projector on `(0,1,1)`, with extra calls indexed 40 and 41.
There are nine distinct saturated bases. Their intersection is the four
original triple calls, indices `15,18,29,32`. Hence d=4.
Their union leaves only original calls `10,11,37,38` and the two new calls
uncovered. Consequently

`E = {10,11,15,18,29,32,37,38,40,41}`.

The character `q=(0,0,1,0,0,3)`, in symmetric-entry order
`(00,11,22,01,02,12)`, is even on all of E. Only calls 37 and 38 have
exponent 2; the others have exponent zero modulo 4. The lemma would require
`4 <= 2`, a contradiction.

Signed permutations of coordinates preserve the original inventory and
map this extension to the other five signed-pair variants. The checker
also verifies all six directly, without relying on that symmetry argument.

## Unequal-coordinate extension has the same obstruction

For A the projector on `(1,1,2)`, the nine saturated bases again have the
four triple calls in their intersection. This time

`E = {15,16,17,18,28,29,32,33,40,41}`.

Choose `q=(0,0,1,2,0,1)`. All exposed exponents are even, with only calls
16 and 17 contributing quadratic terms. Again d=4 and l=2.
All twelve signed unequal-coordinate variants are checked directly.

## Full bounded screen

| Added opposite frame pair | Amplitude | Cases | Excluded |
| --- | ---: | ---: | ---: |
| Coordinate | 1 | 3 | 3 |
| Signed pair | 1 | 6 | 6 |
| Signed triple | 1 | 4 | 0 |
| Unequal `(1,1,2)` | 1 | 12 | 12 |
| Any of the 25 directions | 2 | 25 | 25 |
| Total | | **50** | **46** |

The new checker reproduces all 46 exclusions directly with the compressed
lemma; it does not rely on a solver's rejection or on an unknown search
outcome. Each certificate records the saturated bases, their common
sector, the exposed calls, and the character witnessing insufficient rank.

All 50 inventories retain the determinant and numerical budget tests.
For example, the hypothetical 42-call rank-one moment at coarse saving
0.08 satisfies `42^25 * 3^2 < 48^25`. This arithmetic supplies no network.

## The one remaining case, up to symmetry

The four amplitude-one signed-triple extensions have no saturated bases
of this kind. They are equivalent by signed coordinate permutation, so
the remaining question can use the representative `A=P_(1,1,1)`.

There is still a useful necessary matrix system, before any ordering
search. Let T be the sum of the four original triple idempotents and the
two new idempotents. Each of the original thirteen saturated characters
now selects 18 calls, including all six of these. It therefore requires

`Q := I_16 + T = sum_{j in B-S} N_j`

for each of the thirteen original bases B, where S is the four original
triple calls and each B-S has twelve members. Thus the same Q has thirteen
specified decompositions into twelve rank-one idempotents, while I+Q has
a specified decomposition into six. In particular,

`10 <= rank(Q) <= 12`,   `4 <= rank(T) <= 6`.

Also ker(Q) and ker(T) intersect trivially and have combined dimension at
least 14. These are constraints on the aggregate matrices: **they do not
imply that the individual calls preserve these kernels.** Treating those
kernels as invariant register blocks would add an unjustified restriction.

The audit checks the thirteen eighteen-call selections for this residual
system. It does not solve them. A sensible final bounded test of this
particular family is to find compatible scalar idempotents for these
shared decompositions, or exclude them. Only after that should a schedule
or higher-order word search begin. Failure to exclude this case is not
positive evidence that it can achieve a uniform identity.

## Decision and validation

Retire signed-pair and unequal-coordinate repair searches for these
inventories. Raising solver time or permuting the same calls cannot help.
There is no reason to expand register counts or perturb directions
blindly on the basis of this result.

Run `python3 -B research/compressed-sector-register/audit.py` using only
the Python standard library. It regenerates the cases, directly verifies
each rejection certificate, compares the stored results, and rejects a
deliberately corrupted rank certificate. A valid 48-call coordinate word
and four valid coordinate words extended by consecutive inverse pairs are
not rejected. The controls cover one direction from each frame class.

The artifact is a written proof plus exact finite checks, not a Lean
formalization. No production verifier, selected supplier, or publication
claim is changed.
