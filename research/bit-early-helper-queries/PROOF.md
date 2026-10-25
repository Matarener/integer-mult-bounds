# Forward BIT helper queries at the source entrance

This file gives a source interface. It does not give a new kappa value.

Use the retained PR589/PR555 word at repository commit
`1ec1119972c9aefe42525172d07b332fcff81cb4`. The source is
[WORD.json.gz](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-rebuild/bit/sources/pr589-regenerated/WORD.json.gz).
Its compressed SHA256 is
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
The source has 111 X fields, 111 Y fields, and 439 independent helper fields.
Its nine owned center queries remain paid.

The rescheduling uses the entrance prologue from
[PR5388](https://github.com/CrocSwap/integer-mult-bounds/pull/5388), with its
[proof at commit 568717635d8d11175a80024c9c596e16f54b1ea4](https://github.com/CrocSwap/integer-mult-bounds/blob/568717635d8d11175a80024c9c596e16f54b1ea4/research/native-helper-query-bank/PROOF.md).
This BIT source needs no scalar first-departure basis change or helper
completion child.

## Exact source cuts

Every helper starts in frame zero. Before its first MOVE, it is never the
destination of an ADD. Earlier source instructions can read it. Thus every
first-departure row is exactly its original helper input. The scalar matrix
of all 439 such rows is the identity.

Of these first MOVEs, 286 have rank one. Each of the 111 port lines has between
two and five of them. The receipt gives all owners, event indices, frames,
and prior read counts. All helpers finish at the same full rank-eight frame.

Let P be the projector on one port line. Write Q=D_P, D=D_(I-P), and R=D_I.
The two earliest first-query helpers on that line give two independent Q
observations. Their final job is R=DQ. Select these two helpers at every port.
This gives 222 local observations with no input, output, or observation
normalizer. All other helpers keep their original jobs. A later global stage
requires the separate port-route extension below.

## Optional common-axis maps

The larger 286-query interface can use one common rank-one axis. For a source
root r, put u=r/2, so u has squared norm one. Let e be the first coordinate
vector. If u=e, set K=I. Otherwise set v=u-e and

    K = I - 2 v v^T / (v^T v).

Then K is symmetric, K squared is I, and K e=u. For the head and tail address
coordinates, use the block map diag(K,K). This is in coordinates where the
fixed tail reversal has already been removed. Conjugation by that fixed
reversal gives the native convention.

For a projector A, the address matrix in these coordinates is

    D_A = [[I-A, A], [A, I-A]].

Direct rational matrix products give

    D_(u u^T) diag(K,K) = diag(K,K) D_(e e^T),
    D_I diag(K,K) = diag(K,K) D_I.

Thus input map K, observation map K, and output map K give the common Q
observation and preserve the full R target. The checker verifies these exact
16-by-16 identities for all 111 source lines. It also compares every line with
the actual source first-frame basis. The maps are fixed address maps in the
retained common-cover contract. This check does not claim direct execution of
a dense address map on a smaller cover.

The direct two-per-port interface does not need these maps.

## Matching the actual global stage chart

The local identity R=Q D_(I-P) does not identify R with the fresh-stage helper
job Q D_B automatically. The retained global controller moves main data through
port-specific routes. A helper must also have an explicit route.

Use the actual 15-by-15 matrix rho from
[BIT-P3-NATIVE-BINDING.json](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-rebuild/bit/BIT-P3-NATIVE-BINDING.json).
For each port, its old local projector L has rank eight and the fresh plane B
has rank seven. The source matrix satisfies

    rho^2 = I,
    rho P rho = P,
    rho L rho = P+B.

Give a selected helper the input rho xi. Apply rho to its held observation
and to its final output. The resulting observation is Q xi, since rho fixes
P. The output is D_(P+B) xi = Q D_B xi. Thus it has the same Q and fresh D as
the main controller port. The source accepts these separately routed inputs
because its helper-to-main block is zero on all source columns.

The checker loads and hashes the actual binding. It checks all 111 matrices,
the three head identities, and the corresponding 30-by-30 native address
identities. The same matrices embed at every stage by placing B on that
stage's seven axes and fixing all other axes. This uses the retained fixed
right-route contract on one common future cover. No smaller cover is assumed.

For 222 selected helpers, a fresh-stage call adds 666 fixed cover-route maps:
one at each input, observation, and output. It adds no native child. The
222-cut source replay and all helper target ranks remain unchanged. The local
stage can omit these routes. A complete caller must pay ordinary movement for
the added maps.

## Rescheduling the existing child

For each selected helper, copy its entrance value into a fresh owned raw field.
Run its actual first rank-one MOVE on that raw field. Copy the result into a
fresh owned observation field. Apply the observation map only in the optional
common-axis variant. Keep the raw field for the source cut.

Then run the original source. Omit only the selected first MOVEs. At each
omitted event, the original helper still has its unchanged entrance value.
The raw field has exactly the value and frame that the child would produce.
Swap these whole fields and their frame tags. Clear the owned raw field. The
persistent source state is now exactly the original state after that child.
The source can continue with every later instruction unchanged.

Induction over the replacement cuts proves the whole source identity. In
particular, all reads in the initial Y prefix receive the correct original
helper values. No dirty persistent field is cleared. The old value left in
an owned raw field is a duplicate. The transformed persistent field retains
all its input information. Clear each owned observation after its last use.

For 222 selected queries, the extra work is 444 owned COPYs, 888 owned CLEARs,
222 whole-field SWAPs, and at most 444 extra owned fields. There is no new
paid child. The 286-query common-axis version uses 572 COPYs, 1144 CLEARs,
286 SWAPs, at most 572 owned fields, and 843 nonidentity head chart maps.
Ordinary field movement and storage still need a complete caller tariff.

## Forward source for both shear directions

At each port the original main entrance frames are P and zero. The exit
frames are I and I-P. Its scalar main map is (x,y) to (x,y+x). Therefore its
physical main block is

    F = [[D, 0], [DQ, D]].

Let S swap the two external main fields. Then

    S F S = [[D, DQ], [0, D]].

Since Q squared is I for BIT, this is the opposite shear direction with the
same Q. The swaps act only on the main fields. The helper prologue and every
helper output remain unchanged. This uses the forward physical source twice
with different main assignments. It does not use a reverse first-departure
claim.

The reverse-source census is different: it has 253 first rank-one helper
MOVEs, but every one of its 439 first-departure rows contains a main input.
The forward raw-helper argument does not establish a reverse helper bank.

## Changes to helper arguments before the source

At the end of the prologue, let a helper pair hold normalized inputs xi_h and
xi_k, observations Q xi_h and Q xi_k, and raw fields with the corresponding
native frames. To make the invertible change

    xi_k += Q xi_h,

update its stored input, its observation, and its raw field. The observation
update is

    Q xi_k += xi_h,

because Q squared is I. For two helpers on the same port and stage, the raw-field update adds the
stored input rho xi_h. No new native child is required. In the common-axis variant the raw update uses K_k xi_h.
All source inputs must be fixed before the original source begins.

The checker verifies this update on all 439 arbitrary helper columns for 111
disjoint pairs. It also runs the complete source and all 222 replacement cuts
on those changed inputs, keeping both I and Q coefficient columns. The source
then returns R times the changed helper vector.
This is a coupled output block. It is not the original independent helper
job list until a complete controller proves the required decoding. No helper
target may be credited twice or removed from the invoice.

## Checks and limits

Run from the repository root:

    python3 -B research/bit-early-helper-queries/verify.py
    python3 -O -B research/bit-early-helper-queries/verify.py

Both runs give `PASS_BIT_EARLY_HELPER_QUERIES` and the same exact report. They check all 661 persistent input columns, all owned input columns,
the complete source frames, all actual global port routes, both the 222- and
286-cut variants, the nine
original COPY lifetimes, and the full original paid profile:

    1323 H1 + 1342 H2 + 79 H3 + 44 H4 + 102 H5 + 11 H6 + 19 H7.

The helper target profile stays 439 H8 in the interface without feedback.
The verifier rejects changed bytes in each of the four declared source inputs.
It also rejects a wrong held input, a wrong frame-tag swap, a dirty owned input,
an uncleared raw field, and an uncleared observation.

The exact rational address identities extend to each column multiplicity by
using K tensor I_f and P tensor I_f. The scalar owner program is unchanged.
Its sums are not tensor powered. The all-column source identity permits
arbitrary operator-valued helper inputs, so the stated pre-source feedback is
a valid substitution when every stored copy is updated.

No profitable caller, outer multiplication assembly, precision allocation,
full GL cover materialization, or native payload execution was run here. This
interface alone does not improve kappa.

The retained source and its
[attribution](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-rebuild/bit/README.md)
remain unchanged. The source credits eumemic, Anthropic Claude assistance, and
its cited predecessors. This BIT adaptation and checker have substantial
OpenAI Codex assistance.
