# A rational shear removes eight coefficient instructions

This scoped construction was produced by Nick Petalas. Apache-2.0.

## Supplied boundary and changed hypothesis

Ali Romman's PR #5646 supplies a 112-by-30 source kernel J and a
30-by-112 reader kernel D over Q[C2^9], after its ten published basis
operations. The source has 208 nonzero coefficients and the reader has
9,968. Its supplied boundary satisfies DJ=0. David Ganz's PR #5634
supplies the four-shear borrowed-centre identity, and PR #5640 supplies
its grouped implementation and tariff. These are cited premises, not
results independently audited by this contribution.

The alphabet here charges one coefficient ADD for each nonzero rational
translation coefficient. Its fixed rational coefficient and translation
are explicit. This is the same coefficient-support tariff as #5646;
this count does not price an arithmetic implementation, movement or tape.
The changed hypothesis is that the new basis shear may have denominator
five as well as a power of two. The published single-dyadic-ADD local
optimum does not exclude it.

## Explicit change

Number centre coordinates from zero. Set c=3/40 and

    E = I_30 + c e_5 e_4^T,
    E^-1 = I_30 - c e_5 e_4^T,
    D' = E D,             J' = J E^-1.

The off-diagonal matrix unit squares to zero, so the displayed inverse
is exact over Q and over Q[C2^9]. Only the following entries change:

    D'_5 = D_5 + (3/40) D_4,
    J'_4 = J_4 - (3/40) J_5.

Thus J'D'=JD and D'J'=E(DJ)E^-1=0. This holds as a formal kernel
identity, hence in the 512-address regular action and any representation
of these nine commuting involutions. Extra tensor axes, if present,
are spectators only. This does not assert an implementation at every
uniform algorithm size.

For arbitrary data a and arbitrary dirty centre z, execute

    z += D' a
    a += J' z
    z -= D' a
    a -= J' z.

After the third step the centre is exactly its initial z because D'J'=0.
The last step therefore returns ((I+JD)a,z). No initial centre is zero,
discarded or granted independent productive-target credit. The old and
new words each have four rectangular shears and thirty borrowed fields.
The algebra proves the all-input statement; the literal payload replay
is a finite instruction-order control.

## Strict coefficient bill

The replay reconstructs the supplied factors from the exact pinned
response, inverse-character certificate, port directions and ten-step
basis. It then applies only the displayed new shear. It does not invoke
the predecessor verifier or repeat its rank/inverse/local-minimum audits.

The changed source column still has twelve nonzero coefficients.
Reader row five loses four entries, changing from 892 to 888. All other
reader rows and source columns are unchanged. Consequently

    old: 2 (208 + 9968) = 20352 coefficient ADDs,
    new: 2 (208 + 9964) = 20344 coefficient ADDs.

The factor two counts a coefficient once in each sign of its shear.
The verifier executes and counts every one of these instructions in a
512-address payload, compares all output addresses and restores all
30 dirty fields. An exact comparison of every coefficient of the changed
two-term product proves the endpoint equality without sampling payloads.
Reversing the new basis recovers every supplied factor entry exactly.

The common coefficient denominator changes from 960=2^6*3*5 to
1200=2^4*3*5^2. There is a larger power of five, although no new odd prime.
In both words, the largest absolute coefficient is one, the maximum
absolute row sum of J is 9/4, and that of D is 1036/15. These are endpoint
factor bounds, not a physical arithmetic-interior or error theorem.

## Scope and stopping rule

This is a finite explicit rational-kernel construction with an algebraic
change-of-basis proof. It improves the declared coefficient tariff by eight.
No global optimum is claimed, including among rational two-row changes.
The first strict improvement ends this investigation. No new kappa,
complete paid recursive invoice, selected-frontier update, arithmetic
precision/tape bound or complete multiplication theorem is supplied.
