# A sharp price floor for fixed scalar contacts

## Claim and domain

Fix the ordered ADD, COPY, SCALE, INIT and CLEAR records and their frames.
Fix the main entry and exit frames. Each helper has an independent public
input. Its scalar endpoint is its own input, with no other input term.
Keep the source frame interface: a register carries one field in one
canonical chart. A transition between two charts is a paid Gaussian job
between monomial maps. No joint query on several registers is introduced.

Allow every binary subspace as an intermediate chart, any number of
transitions between contacts, and arbitrary public helper entry and exit
charts. No nesting condition is imposed. Grant every added ordinary map
for free. The result is therefore a favorable bound for this larger model.

For every power tariff r^t with 0 < t < 1, the PR5580 word attains the
maximum of helper credit minus paid transition cost in this model.
Thus changes confined to these paths or endpoints cannot improve its
complete recursive moment. The scalar contacts themselves can change
this bound. This is not an optimum over all P104 words.

## Exact native rank for two charts

For binary subspaces U,V of F2^n define

    d(U,V) = dim(U) + dim(V) - 2 dim(U intersection V).

This is the subspace distance. It is a metric. In particular, an arbitrary
path from U to V has sum of edge distances at least d(U,V).

Use the canonical chart G_U in the pinned Clifford source. Ignore Pauli
signs only in this rank calculation. Its image of the Z Lagrangian is

    L_U = {(x,z): x in U, x+z in U-perp}.

To check the formula directly, put the basis of U first in an invertible
matrix G and put H=G^-1. The source chart conjugates the first dim(U)
coordinate C gates by D_Q P_G, where Q=I+H^T H. A Z vector z has image
x=G P G^T z and z'=z+Qx, where P is the first-coordinate projector.
Then x is in U and x+z' is orthogonal to U. Both spaces have dimension n,
so the inclusion is equality. The zero and full charts give the same rule.
The symplectic action of each chart is an involution. The square of the
chart is a Pauli, not necessarily the identity including its phase.

The intersection L_U intersection L_V is parameterized by x in U
intersection V and x+z in (U+V)-perp. Its dimension is

    n - dim(U) - dim(V) + 2 dim(U intersection V).

The X block of G_V G_U^-1 therefore has rank d(U,V). Monomial maps
preserve the Z Lagrangian. They cannot reduce this rank. The retained
Gaussian normal form gives monomial left and right factors and one
rank-d Gaussian. All scalar phases belong to the factors. The price is
d(U,V), not abs(dim(U)-dim(V)) for a nonnested pair. For example, two
distinct lines cost rank two even though their dimensions agree.

These identities concern one address column. For width f, lift each
native operator columnwise, with its scalar phase raised to the f-th
power. Each rank-d block then has d*f address axes and remains a rank-d
job in the source width convention. Owner scalar coefficients are not
tensored. No identity on a sum is inferred by tensoring that sum.

## Internal paths

For nonnegative a,b and 0<t<1, (a+b)^t <= a^t+b^t. Combine this with
the metric triangle inequality. Every transition path between two
consecutive contacts A and B has cost at least d(A,B)^t. A direct native
transition attains the bound. This applies separately to each register
and to every gap, including the fixed main endpoints and owned contacts.
It requires no search over intermediate subspaces and no finite cutoff.

## Helper endpoints

Let A and B be the first and last contacts of a public helper. Let E,F
be any proposed entry and exit charts. Put a=d(E,A), b=d(B,F), and
h=d(E,F). The metric inequality and subadditivity give

    h^t - a^t - b^t <= d(A,B)^t.

Paths with more transitions can only reduce the left side. Thus helper
credit, after the endpoint path cost, is at most the credit obtained by
starting at A and ending at B. This conclusion also permits a rank-zero
helper in the favorable bound. No extra productive field is credited
for such a helper. A helper with no contact has credit at most its path
cost, so its net contribution is at most zero.

The endpoint normalization mechanism is inherited from PR5550 and
PR5567. If the helper's physical map is M_left H_r M_right, put
M_right^-1 before the word and M_left^-1 after it. The resulting job is
H_r on an independent input. These are two ordinary monomial maps per
helper, not two new Gaussian calls. The proof above grants all such
ordinary costs for free; it does not assert that they vanish physically.

## Binding and equality for PR5580

The verifier replays all 735 public inputs and eight owned lifetimes with
the unchanged source scalar checker. It then reads every contact in the
literal word and computes every consecutive distance. All required source
chart pairs also pass the native X-block rank test.

The paid floor is

    {1:2211, 2:459, 3:494, 4:94, 5:163, 6:18, 7:14}.

The corresponding helper core is

    {4:83, 5:4, 8:15, 9:424}.

The source differs from these two profiles by exactly one rank-five paid
job and one rank-five helper target. Both belong to register 711, which
has no scalar contact. They cancel for every tariff. Every other required
interval is already at the bound. This proves equality of the complete
signed local profiles, not just equality at one numerical exponent.

The source caller uses 18 copies of this local word. All other caller
terms are fixed in this comparison. Multiplication by 18 and addition
of those fixed terms preserve the bound. No root approximation is needed.

## Verification boundary and next step

The finite checks bind the written general proof to the exact source.
They are not a formal-kernel proof. The retained source checker, native
compiler and framework assumptions retain their prior review status.
The full physical caller, ordinary budgets, outer ledger and rounded
multiplier are not re-run here. No new kappa or supplier is admitted.

A useful next change must alter a contact, scalar realization, query
interface, or productive target model. The active changed-contact and
basis searches remain outside this result. The distance formula can be
used as a lower bound before a new candidate is physically compiled.

Credit Matarener for PR5567, Chris R/Clear1nsight for PR5550,
DreamingOfClouds for PR5561/5568, GamingPuzzled for PR5569, and the
PR5580, PR5544/5545 and retained P104/native/compiler authors. This is an
application of standard subspace distance and concavity; no general
mathematical priority is claimed. Ali Romman with substantial OpenAI
Codex assistance. Apache-2.0.
