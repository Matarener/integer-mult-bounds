# Cross-review of the companion C01 whole-word audit

Status: **PASS for the stated exact formal-word and finite scalar-projection
claims.** No remaining mathematical or implementation blocker was found in
this bounded source review. This is a read-only review, not a second execution
of the companion checker or an independent human review.

Reviewed source hashes:

- `c01-wholeword/check.py`:
  `16cdeef8aabed919c066ad5da45450cfc524024814f550b3415368ed098a38c6`
- `c01-wholeword/PROOF.md`:
  `4bf4ab27640122985b4d2c9f941003d6e9cbda612b0811735f014585fde0d109`

The review also used the already frozen, unchanged design-side source copies
of the PR3605 `bw_transport.py` and `bw_emit.py` to check the claimed event and
frame convention. The design panel payload remains SHA256
`27defe7675576baaebfd45efe40439f491a683bd923b7259c98495db8d3783ac`.
No design source, proof or frozen receipt was changed by this cross-review.
This new review file is supplemental to the earlier design output inventory.

## Formal operator interpretation

`raw_program` constructs the entire literal chronology: expanded initial
corrections, precondition, compensation, A, cut, indexed B warps, B, restore and
cleanup. Initial corrections apply their operator word in the correct order
by reversing the chronological list of letters, then remove it with the
corresponding inverse sequence. `free_replay` left-multiplies free words and
cancels only adjacent inverse pairs. The word action is injective, which is
checked rather than using a commutative projection.

The raw endpoint check covers all 632 arbitrary logical columns plus the 91
zero-input private buffer rows. It compares the complete symbolic output with
the required shear and all helper identities, including zero private outputs.
The literal reverse inverse reverses the whole gate list and inverts each
ADD/SCALE/warp. The signed expected shear is adjusted accordingly.

The same-order dual gate rules are correct. Scalar ADDs exchange source and
target and negate their coefficient; SCALE coefficients are inverted. The
unchanged warp identifier has a separate meaning in the dual alphabet,
namely K inverse transpose. Since free generators can be independently
renamed, the symbolic replay is valid under that interpretation. It does not
identify K with its own inverse transpose. For the inherited unit-modulus
monomial realization, K inverse transpose equals conjugate K; the physical
phase premise is separate and is not checked here.

The proof originally left the last premise implicit. I requested an explicit
distinction between arbitrary invertibility and the unit-modulus monomial
interpretation. The reviewed final proof now states that distinction directly.
The checker required no change.

## Raw word, emitted program and scalar projection

The raw free-word map and the complete scalar projection are distinct models
throughout the reviewed proof. The latter explicitly sets nonscalar events
to identity, uses 632 arbitrary logical inputs, and initializes all eight
centers, 91 cleanup buffers and coefficient work to zero. No scalar-projection
range is asserted to be a physical native-prefix norm.

The producer scripts are pinned before execution. The final loader reads each
producer into a byte buffer, checks that exact buffer against the declared
source hash, and sends the same bytes to the child over standard input.
Child Python invocations use `-I -B` without `-O`, even when the surrounding
checker is optimized. The bootstrap compiles those authenticated bytes with
`dont_inherit=True, optimize=0`, preserving the producer's `__file__` and
command-line arguments. It does not reopen the producer path as executable
source after authentication.
`bind_emitted_prefix` checks the raw-to-compact register mapping and every
zero-frame event against the independently expanded raw prefix, in both
orientations. The changed complete raw word is equal to the source in every
non-compensation field. The emitted suffix from entry adapters onward and
all nonscalar events must also agree exactly as JSON values. Those checks
justify retaining their existing charges, without setting them to zero or
claiming physical phase verification.

The source helper availability check uses actual live register identities
and excludes both entrance and terminal wrapper overrides. This agrees with
the pinned transport defaults and zero-frame phase placement. The unchanged
literal helper and target restoration lists are checked explicitly before
operator equality is accepted.

## Literal primitive price

`lower_scalar` spells out the primitive lists separately from `primitive_price`.
For a nonzero dyadic ADD it emits the initial clear, every binary Horner
doubling and source ADD, every denominator halving, the signed target ADD and
the final clear. Its length is precisely
`3+floor(log2(abs(a)))+popcount(abs(a))+d`. Binary SCALE, negative sign,
COPY and CLEAR are all counted. The full scalar replay counts the emitted
primitive stream rather than multiplying ADD macro counts by a unit price.
It checks agreement with the producer's count and with the panel delta.

This supports the stated component price change 79,072 to 58,491 forward and
79,096 to 58,515 dual, conditioned on the companion's executed receipts.
The common saving is 20,581 per real component, or 41,162 for two components.
The panel bill 31,214 to 10,633 agrees with the design and its separately
executed Horner microcircuit audit. No additional work-buffer or helper
initialization is hidden by these exact counting rules.

## Exact range and grid theorem

The normalized integer-dyadic row representation is sound. `row_add` aligns
both denominators before addition; `normalize` removes only the common power
of two shared by all coefficients. Row updates produce new dictionaries, so
COPY's temporary sharing of an immutable row object does not introduce a
later aliasing mutation.

The metrics observe every changed destination after every literal primitive.
Unchanged rows retain their previously observed values. Initial logical rows
have norm one and private rows are zero, agreeing with the metric initialization.
Therefore the maximum of the observed exact absolute row sums is exactly
`max_j ||A_j||_infinity`, including intermediate Horner work. The maximizing
row witness gives an attaining input by assigning each independent real input
the sign of its coefficient. This proves the all-input unit-cube range claim
for the specified scalar projection. Scaling gives M times the input bound.

For the grid theorem, every stored row denominator divides 2^D, so common-grid
inputs in 2^-g times the integers remain in the grid with g+D fractional bits.
At each newly largest positive exponent, canonical normalization guarantees
an odd coefficient exists; `Metrics.observe` records one. The corresponding
basis input at scale 2^-g proves necessity of that D over the unrestricted
common-grid domain. This does not prove a physical native guard-bit minimum.
The proof makes that limitation explicit.

The companion's reported exact dual range increases from 169 to 181, and its
positive-envelope exponent increases from 95 to 97. These are retained as
worse bounds, not suppressed by the lower primitive count. The forward exact
range 302 and extra fractional grid bits 4/5 have their stated restricted
scalar-projection meaning. Positive-envelope propagation uses absolute values
and therefore provides a separate conservative bound, not the exact attained
row sum. The strict power-of-two bit conversion is correct for the nonzero
maxima used here.

## CLEAR semantics and precision boundary

A CLEAR is an explicitly charged zero assignment in the scalar model. The
counter increments when its pre-clear symbolic linear form is nonzero. This
means some admitted input makes that clear erase nonzero content; it does not
mean every numerical input is nonzero at that instruction. I requested this
wording clarification, and the reviewed final proof now says “nonzero linear
forms.” The implementation was already consistent with that statement.

The 91 private zero buffers have a different, literal zero contract: allocation
and free events check their exact rows are zero, and all their uses are checked
against the active allocation set for the operations occurring here. Eight
final center clear assignments are not promoted to a reversible cleanup proof.
The proof separates these assignments from physical erasure, native child
precision, roundoff feedback, strict-zero restoration and all-size tape costs.

The fixed-point observation is valid as a conditional exact implementation
statement: sufficient range and the proven input/grid assumptions make each
listed scalar primitive exact, so no rounding tie is exercised. It supplies
no implementation of the physical COPY/CLEAR contracts.

## Loader-only update

The initial review covered checker
`793a5ad6ab49640f732aed19788e4eb30f7af6fe30709ac917ae07c80959f725`.
For the updated checker I isolated the new authenticated-buffer loader block
inside `produced_programs`. Replacing only that block with its previous
path-execution implementation reconstructs the exact former checker hash.
Thus no mathematical interpreter, cost, domain, witness or acceptance code
changed in this update. The proof hash above is also unchanged.

The companion's final `VALIDATION.json`, SHA256
`9eef8187df474a4b4ccdfb0410f92c66ad920a2c23fab2ca9456e032564685d2`,
records successful normal and optimized replay with identical receipts.
It records that removing only `checker_sha256` leaves the entire mathematical
receipt unchanged. The current `CHECKS.json` SHA256 is
`bd442037a8dc9c2a27f6a1b1e8b1e45e5c934cb7129cee2db2f85d1c20f26ec1`;
I checked its binding to the new checker hash. This review inspected those
bindings and the exact loader-only difference; it did not repeat the
companion's mathematical executions.

## Review outcome

The two requested documentation clarifications were applied and re-read at the
hashes above. The authenticated-buffer loader update is also accepted.
No checker defect or numerical inconsistency requiring an additional
mathematical run was found during this review; no checker was rerun here.
Root integration should
bind the companion's executed receipt to these exact checker and replacement
bytes, preserve the worsened dual bounds, and retain the native/rounded and
full-multiplication-theorem exclusions. No broader optimum, new kappa or formal
kernel proof follows from this pass.
