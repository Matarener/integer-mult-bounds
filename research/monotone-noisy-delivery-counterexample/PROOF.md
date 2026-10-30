# A finite monotone-tariff counterexample in the immutable-channel quotient

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Fix the original backward word retained in the archive with SHA256
`595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7`.
Its compressed word has SHA256
`934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775`.
Use the immutable-channel common-fixed-vector scalar response model of
Ali Romman's [PR5745](https://github.com/CrocSwap/integer-mult-bounds/pull/5745),
as retained by Nicholas Stone's
[PR5845](https://github.com/CrocSwap/integer-mult-bounds/pull/5845).

In this model a fixed-frame channel has an immutable rational linear
combination of the eight original modes as its payload. It may add rational
multiples of that payload at any recorded cut to a field in its frame.
Its canonical delivery charge is H_r for the grade r of that frame.
Repeated contacts in the same frame use one channel. Ground delivery costs
H_0=0. Payload preparation, all scatter, channel lifetime and compensation
of originally ground-frame helpers are granted without charge, exactly as
in the response-space relaxation. Main outputs, all Y outputs and all
originally non-ground helpers remain retained constraints.

The finite witness in WITNESS.json has 22 channels with delivery profile

    H_0 + 14 H_7 + 7 H_8.

It realizes all eight desired modes on the retained outputs. Therefore an
8 H_8 delivery floor for arbitrary finite channel counts is false for
general positive nondecreasing tariffs in this quotient. For example,

    H_0=0, H_1=...=H_7=1, H_8=H_9=15

gives charge 119, strictly less than 120. More generally this witness beats
8 H_8 exactly when H_8>14 H_7. No claim of channel-count or tariff optimality
is made.

## Response identity

Index modes by 0 through 7. Let R be the archived 8 by 112 rational mode
matrix, satisfying RR^T=56 I. Write E_j for the output vector whose first
112 coordinates are row j of R and whose other retained coordinates vanish.

The new joint response uses frames

    0, 661, 662, 663, 664, 678, 679, 691, 692,
    728, 730, 989, 993, 1003, 1007.

Frame 0 has grade zero. Each other listed frame has grade seven. There
are 61 contacts, each with an exact rational coefficient and a literal
cut/field pair in WITNESS.json. Let v_f be the retained output response to
unit payload at all contacts of frame f with those coefficients. Exact
forward evaluation of the frozen word gives

    sum_f v_f = E_4 + E_5 + E_6 + E_7.                  (1)

This is the new finite identity. It concerns the sum of noisy channels,
with cancellation on every retained nuisance coordinate. No census of
single-frame or pair obstructions is used to prove it.

PR5745 supplies clean grade-eight responses E_j. The certificate uses its
seven directions with j in {0,1,2,3,5,6,7}, with their cited frame/contact
witnesses. Their frames are respectively 254, 274, 619, 279, 280, 624 and
281. The last direction has two contacts; each other direction has one.
Checking those contacts is part of the new complete witness replay, not
an independent audit or a new claim about predecessor construction.

For an arbitrary original mode vector u in Q^8, assign payload u_4 to
each of the fifteen channels in (1). Give the clean E_j channel payload
u_j for j<4, and u_j-u_4 for j>4. All these payloads are immutable original
mode combinations. The resulting retained response is

    u_4 (E_4+E_5+E_6+E_7)
      + sum_(j<4) u_j E_j + sum_(j>4) (u_j-u_4) E_j
      = sum_j u_j E_j.                                (2)

There are 15+7=22 channels and 61+8=69 contacts. Equations (1) and (2)
give the advertised finite quotient completion and its invoice.

## What is checked

The verifier imports no predecessor executable. It loads the authenticated
source word and R from the existing archive, then propagates 22 independent
channel symbols forward through all 22,585 events. Each contact occurs
immediately before its zero-based event index. The current frame must match
the channel frame. The source has 641 scalar slots: 632 original fields,
eight extra owned C slots and the unused C0 slot.

The quotient treats native transport as identity on the common fixed vector,
while checking entry and exit frames. Adapters and phase markers are erased
as in the cited scalar quotient. Scalar ADD, SCALE and CLEAR act literally.
All contacts follow the original mode-collection prefix. The verifier checks
that every relaxed centre-tail physical ADD has zero channel response on
its C input; those tail events consequently add zero to this impulse replay.
This is not a native phase or common-fixed-vector existence proof.

There are 274 retained original fields: 112 main fields, 112 Y fields and
50 non-ground helpers. The verifier checks (1) on each of these fields and
checks every one of the 274*8=2,192 coefficients in (2). All nine C-slot
responses vanish at return. Of 358 exempt original ground helpers, 189 have
a response to some independent channel symbol and 113 have a nonzero
residual after substituting the payloads in (2).

Eight controls change a contact coefficient, move a contact to cut zero,
change a frame, understate a grade, reverse a payload coefficient, delete
the ground channel, replace the strict tariff gain by equality, or violate
tariff monotonicity. Each must fail. The generated RESULT.json binds the
complete result to hashes of the verifier, witness and source archive.

## Consequences and limits

The result answers the arbitrary-monotone continuation in PR5845 with a
larger positive witness. It does not settle the initially proposed
three-frame question, or the minimum number of noisy channels. PR5845's
at-most-nine-channel theorem remains outside this contribution's audit
scope and is compatible with 22 channels.

Ali Romman's [PR5823](https://github.com/CrocSwap/integer-mult-bounds/pull/5823)
already supplies an arbitrary-finite-channel floor for concave power tariffs
H_r=r^q H_1, 0<q<=1. Our witness has H_8/H_7=15, whereas those powers have
H_8/H_7<2. This finite example therefore does not challenge that floor.
The 14 H_7+7 H_8 invoice is also plainly greater than 8 H_8 for those powers.

A response-model completion need not lift to an operator identity on the
full native field. No such lift, preparation circuit, channel storage or
return word is supplied. The 113 ground-helper residuals are not physically
repaired here. Scalar operations, native phases, borrowed-channel restoration,
ownership, precision, stock, tape movement and a complete recursive caller
bill remain unproved or unpriced. This is a finite quotient certificate,
not a physical supplier, a new kappa or a multiplication theorem.

## Credit

Nicholas Stone's PR5845 posed the monotone-tariff continuation and supplies
the two-frame/nine-channel context. Ali Romman's PR5745 supplies the word's
canonical delivery model and clean directions. Its temporal response code,
retained byte-for-byte in PR5845, was used for discovery. It is not imported
by this verifier. Ali Romman's PR5808 and PR5823 supply the distinct
mixed-rank and concave-power obstructions, which are cited without replay.

Retain flyingviper's PR5720/PR5755, Cao Yifan, Cinna Davis, Dugongue and all
mode, native, controller and caller contributors credited in the unchanged
source archive. The new joint response, complete quotient payload assembly
and displayed general-monotone tariff counterexample are this contribution.
Independent human and formal proof-kernel review are unclaimed.
