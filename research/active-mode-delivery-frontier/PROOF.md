# Sharp paid cost of canonical active-mode delivery

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Fixed source and delivery contract

Use PR5720's exact F9-SOURCE-DAG-ALL8 backward word. Omit only its explicit
unimplemented physical_add tail. The 632 independent inputs comprise 112 X,
112 Y and 408 helpers. Owned scratch starts at zero. The eight mode rows R
satisfy RR^T=56I. Their captured payloads are c_j=R_j Y/4. A complete repair
changes the main scalar endpoint from X-AY to X-Y, where A=I-R^T R/4,
and preserves every Y and helper target.

A channel takes one scalar linear combination of these original mode arrays.
It uses a paid canonical transport from ground frame 0 to one frame g. It can
then add scalar multiples of that payload to any currently available fields
in frame g, at any number of times. The payload can remain in owned storage
between those times. All such control times use the unchanged source word;
the payload is not recomputed from a changed live field. Its normalized value
is constant in that frame. A different frame, address word, extra query,
changed source word, or feedback-dependent payload is outside this contract.

A rank-r canonical transport costs H_r, with H_r positive and nondecreasing
for r>=1. The actual rank is the Clifford Gaussian grade, checked below for
each attaining transport. The theorem grants free arbitrary rational scatter
coefficients, arbitrary payload availability times, and free final correction
of every helper whose original start frame is ground. These relaxations can
only help a proposed delivery. Native and ordinary implementation costs are
not made free in the attaining word.

A channel is clean if its endpoint, after quotienting those helper outputs,
is a linear combination of the eight desired main mode vectors and has zero
other main or Y output. The complete delivered correction has rank eight in
this output quotient because R has eight independent rows.

## 2. Complete response spaces

For a cut t and current field d, let v_(t,d) be the scalar endpoint response
to a unit additive impulse at that field. Propagate endpoint columns backward
through the literal word. For an ADD d+=a s, the source column becomes
v_s+a v_d. For COPY d=s it becomes v_s+v_d and v_d becomes zero. CLEAR makes
v_d zero; SCALE multiplies it. Frame changes update the set of available
fields. Native warp words are evaluated on their common fixed vector as in
PR5720. This is a necessary scalar quotient, not a new physical theorem.

At frame g and time t, the possible scatter response is the span of all
v_(t,d) with current frame g. An invertible coframed ADD or nonzero SCALE
preserves that entire span. Thus there is no need to repeat elimination at
such an event. The replay still updates every column and checks each contact.
It checks every other span change and every final frame. Identical complete
field-column lists may share a result. Zero columns cannot add a direction.

For each column, separate its main part into an R^T component and a nuisance
component by a fixed rational left inverse of R^T. Keep all Y coordinates and
all helper coordinates whose original start is not ground in the nuisance.
The ground-helper coordinates are the explicitly granted free quotient.
Eliminate nuisance columns while retaining mode components and exact control
witnesses. Each dependence supplies one pure-mode vector. Reducing those
vectors gives exactly the attainable mode subspace: these are the standard
column-kernel image operations, not a bounded coefficient search.

The complete source has 5,331 distinct checked frame states and 3,963 distinct
projected endpoint columns. Only eight rank-eight frames have a nonzero clean
response before full rank. They give 41 frame states and 41 response vectors.
The final full frame gives all eight modes. No rank below eight has a clean
response. The eight frames are 254, 274, 279, 280, 281, 619, 621 and 624.
All positive witnesses are retained in CUTS.json.

Temporal reuse is checked separately within the same pass. For each frame g,
collect the span of its response columns over every time, not just one cut.
The elimination processes 5,715 distinct frame/column pairs. There is still no
clean response at rank below eight. The result has one mode direction at each
of the eight rank-eight frames and eight at the terminal full frame. These
sixteen exact witnesses are in TEMPORAL.json. Rank-nine histories need not be
expanded further: the terminal state already provides the entire eight-mode
quotient, and no rank-nine channel costs less than H8.

This temporal check is essential. A single-time exclusion alone would not
exclude reuse of one paid payload at several times. The positive control has
two noisy responses whose difference creates a clean mode across two times.

## 3. Sharp tariff theorem

First suppose every channel is clean. The source calculation proves that
each nonzero channel has r>=8. At least eight channels are required to produce
a rank-eight mode correction, because one scalar payload has mode rank at
most one. Therefore the total canonical delivery cost is at least 8H8.
This remains true for any number of clean channels and arbitrary temporal reuse.

The same lower bound holds without the clean-channel requirement if there
are at most eight channels. Write the full output correction as VB, where
each column of V is one channel response and B contains its payload
coefficients on the eight independent modes. The desired correction has
rank eight. Thus there must be exactly eight channels, V has rank eight,
and its column space equals the desired mode subspace. Each column is then
clean in the stated quotient. The first argument applies.

Eight explicit rank-eight deliveries attain the bound. Thus 8H8 is the exact
minimum in these stated models for every positive nondecreasing tariff.
The original removed center allowance is also 8H8. No recursive-paid saving
is available from these models. Nine or more jointly noisy channels can have
a larger response span whose nuisance cancels only after combining payloads;
the rank argument does not exclude that model. Nor does it exclude changes
to the native frame/address contract or to the underlying word.

## 4. A legal complete attainment

For each mode, use the earliest retained rank-eight single-field witness.
The source already holds c_j in an owned ground field C(j+1). Remove its
original helper-precompensation ADDs. At the witness cut, transport that owned
field from ground to the specified frame, subtract it from the witness field,
and CLEAR the owned field. No arbitrary helper is overwritten or erased.
The target fields, one for each mode, are bound in RESULT.json.

The new transport is the conjugate canonical frame map for the backward word.
The retained exact compiler lowers it to a rank-eight Gaussian child with
ordinary monomial wrappers. The compact phase-sensitive engine checks the
entire tableau and absolute phase, and a separate literal zero-column check
agrees. A global-phase mutant is rejected for each of the eight maps.

Replay the complete program with all 632 original columns and the original
noncommuting native warp words. Only adjacent inverse words cancel. The result
is X-Y on the main rows, Y unchanged, all 408 helper identities, the original
final frames, and zero on all nine owned fields. All scalar ADD contacts are
coframed. Omitting a paid transport is rejected as a coframe mismatch; restoring
the removed helper debit or reversing an injection sign fails the complete
endpoint test.

The raw construction also contains operations on proved zero owned data.
Remove only zero-source ADDs, zero SCALEs, zero-to-zero COPYs, and redundant
CLEARs that do not change a frame. Replay the emitted word again. This removes
eight ADDs and eight CLEARs. WORD.json contains the complete resulting word.
The original source word also receives a full independent-input replay.

The paid profiles agree exactly:

    2201 H1 + 412 H2 + 510 H3 + 127 H4 + 40 H5 + 8 H8.

The completed direct-delivery word has 16,578 ADDs, 32 CLEARs and 1,164 SCALEs,
with peak nine live owned fields. The original has 16,130 ADDs, 16 CLEARs and
1,164 SCALEs, with peak one. Thus this concrete completion is dominated by
the original: 448 extra ADDs, sixteen extra CLEARs and eight extra live owned
fields, with no paid gain. It is a legal witness for the paid optimum, not an
improved implementation. The original center implementation is already the
better upper bound among these two words.

## 5. Boundaries of the result

The mathematical lower bound uses the scalar necessary quotient and the fixed
canonical delivery contract. It is not a lower bound for general active feedback.
The positive program adds exact new native transports but inherits the frozen
source's existing native implementation contracts. The formal-word endpoint
check retains all original inputs and warp words; it is not a fresh execution
of every historical physical wrapper or a complete multiplication caller.

No compiler, outer theorem, finite precision, stock or tape admission is
claimed. The paid result is sharp within the model; a different eight-channel
word could have different ordinary cost. The explicit direct completion here
is worse than the original. The selected frontier is unchanged. No formal
proof-kernel or independent human review has occurred.
