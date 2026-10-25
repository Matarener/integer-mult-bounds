# Signed literal provider and native legality

This package introduces the provider interface
`signed-framed-literal-v1`. It accepts the final PR4183 closed-cut word,
including its signed dirty prelude, interleaved source reads and five
rank-four helper endpoints. It does not claim that the older
`A / scatter / B / C` exporter already accepts that interface.

The scientific input is the frozen R438 word and geometry, authenticated
by the compressed-file hashes in [NATIVE.json](NATIVE.json). The candidate
recipe is reconstructed directly in [native.py](native.py), separately from
the predecessor's two implementations. Its full literal-record hash is
`5f301f0d668ded1028b7603c5ea9c88271e390fb9060ce8e118aad7d9927a7fd`.
The insertion is after original ERASE23889, and helper469 closes by the
rank-seven query to517 followed by the retained rank-one query to FULL.

## Exact local contract

Every ordinary input is independent: 111 sources, 111 public targets and
438 dirty helpers. The single private stream starts at literal zero.
The provider checks each complete orientation in two representations:

1. A bitset calculation checks all 660 Boolean columns and the public shear.
2. Sparse signed integer rows check exact source and helper identities,
   every COPY snapshot and ERASE equality, and both complete inverse
   compositions. This calculation never reduces coefficients modulo two.

Both words have nine COPY episodes in each orientation. During each episode
the original source and private copy are immutable, and every ERASE compares
the complete integer rows. There is no recursive MOVE while that private
copy is live. Consequently this exact-copy statement is stronger than
equality modulo two. It is still conditional on executing exact child
operators; an approximate child return requires its own rounded cleanup
theorem.

The candidate restores all 111 source and 438 helper integer rows. Its
public integer lift differs from the frozen word by `-2 h469` on exactly
51 targets, with every other output unchanged. The Boolean public map is
therefore the same. Signed row-l1 prefix peaks are `1300/1444`
forward/reverse, compared with `1302/1446`; the largest coefficient
magnitude is 22 in either word.

“Helper restoration” here means restoration of the decoded dirty function
with the declared terminal frame. Physically, 433 helpers retain a FULL
residual and five retain their specified rank-four residuals. Helper469
retains the FULL address swap. None of these statements turns that
physical residual into an identity operation.

## Frame specialization and actual function semantics

The provider derives integer span and annihilator bases from all 636 frozen
root frames. It verifies their dimensions and orthogonality, all executed
nested MOVE inclusions, every signed ADD's common frame, all COPY frames
and the actual final frame of every register.

It additionally selects an independent subset of the original root rows
for every frame and checks that its Gram determinant is a positive power
of two. Both the emitted span basis and its annihilator also have
power-of-two Gram determinants: the 1272 determinants have histogram
`{1:56,4:652,16:500,64:64}`. This matters because rational row reduction
alone would not justify reduction in every odd characteristic.

The checked determinants prove that the original root span and emitted
bases retain their ranks over every odd-characteristic field. Their
orthogonal projectors are defined over `Z[1/2]`, so the rational containment
and orthogonality identities specialize there as well.

For a projector P, let

```
D_P(u,v) = ((I-P)u+Pv, Pu+(I-P)v).
```

For nested P and Q, the relative transport is `D_(Q-P)=D_Q D_P`.
If a physical function f is in frame P, its decoded function is
`c=f composed with D_P`. A correctly priced nested MOVE preserves c;
a common-frame signed ADD changes the decoded functions by the same
integer addition; a COPY into frame zero produces the decoded source.
The unchanged source permits its later exact erasure.

Induction over the emitted events therefore gives the audited integer
recurrence on arbitrary input functions, with Boolean values obtained by
reduction modulo two. This is a written all-function argument supported
by the finite frame certificates. The covered domain is arbitrary dirty
Boolean-valued functions on pair-address space over odd-characteristic
fields, with exact completed child operations. It is not a formal-kernel
proof, a rounded-child theorem or an all-size physical machine construction.

## Byte-level native translation

The first five fields of every raw record are unchanged. The sixth field
in the frozen word is a section annotation, whereas the historical C++
consumer uses it as the COPY rank. The provider performs exactly this
schema conversion:

| Operation | Native six-field record |
| --- | --- |
| MOVE | `[0, destination, before, after, rank, 0]` |
| signed ADD | `[1, destination, source, coefficient, frame, section]` |
| COPY | `[2, source, 660, source_frame, 0, 7]` |
| ERASE | `[3, source, 660, source_frame, 0, 0]` |

No operation is deleted, reordered, combined or newly charged by this
lowering. Serialization is six little-endian signed 32-bit integers per
record. The two emitted binary hashes are:

```
frozen:   a4c3c14e242a78b14367710d571f61a7126118089fe9888512d766570514dce9
candidate:35b4d967ab9325a5e9bd433c121f73791b9bb79a299626fbccc6377c01dc074d
```

Reverse programs read records in reverse order, swap MOVE endpoints,
negate ADD coefficients, turn an ERASE into a fresh COPY from its unchanged
recorded source, and turn the corresponding COPY into an ERASE. Both
integer inverse orders are verified separately. Inverse COPY work is
charged; a saved forward query does not make the inverse free.

The complete forward native invoices are:

| Word | Records | Unit ADDs | Nested MOVEs | COPY queries | Total queries | Rank mass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen |38927|36005|2904|9|2913|5101|
| Candidate |38868|35947|2903|9|2912|5101|

Every local recursive rank is at most 7, strictly below local dimension 8.
The complete histogram change is `e7-e6-e1`.

## Bridged formal columns and precision

The provider also replays the inherited signed orientation schedule and
twin-bridge rule, using its independently constructed forward/reverse
event arrays. The global public endpoint checks in this part are over F2:

| Stages | Independent ordinary columns | Dirty helper columns | COPY episodes | Unit bridge ADDs |
| --- | ---: | ---: | ---: | ---: |
|5|882|438|45|666|
|9|1326|438|81|1998|
|11|1548|438|99|2664|

Every one of the 6, 18 or 24 bridge omissions changes the respective complete
Boolean endpoint, for both input words. These are 96 defect-sensitive
controls in total. Literal private cleanup is supplied by the separate
integer local replay and unchanged-source invariant, rather than inferred
from the Boolean global endpoint.

The cancellation-free forward/reverse majorants are
`8402567/630744` for the frozen word and `8401795/630740` for the candidate.
Using the inherited envelopes gives

```
P5 = 64 F^3 R^2       : 114 bits, charged 128
P9 = 2^18 F^5 R^4    : 211 bits, charged 256.
```

Both words fail the older 104/192 caps. The exact positive bounds decrease,
but the charged precision stays the same for this matched comparison.
These envelopes are scalar coefficient bounds; the complete routing,
rounding and all-size invoice are stated separately in
[RECURSION.md](RECURSION.md).

## What the unchanged native replay proves

[native-check.py](native-check.py) is an optional compiler-dependent replay.
It authenticates the five bundled historical source/header files, copies
those exact bytes to a fresh output directory, compiles them without edits,
and executes the authenticated `stage_cohort.py` bytes with assertions
enabled and without importing bytecode caches.

The replay freshly passed for both emitted words with Apple clang 17 and
Boost 1.87. The unchanged `legality_h.cpp` agrees with every invoice above,
all declared final frames and all COPY lifecycles. It checks 2,385 distinct
MOVE-containment pairs; COPY geometry is checked by the provider separately.
The historical stdout text says `COPY24` even when compiled with `NCOPY=9`;
the structured receipt correctly records nine copies and nine erasures.

The empty cohort selection means that the old checker's zero
source-owner/donor intersections are vacuous. They do not verify the
new physical fill. That obligation is independently handled by
[owner.py](owner.py) and [OWNER-PROOF.md](OWNER-PROOF.md). Likewise, the
C++ receipt's hardcoded nondegeneracy flag is not accepted as evidence;
the exact Gram audit above supplies that evidence for the local framebank.

The unchanged `columns_k.cpp` is deliberately run as a rejection control.
For both words it exits 2 with exactly `payloadfiniteprefix2^104`, before
its scalar replay, and produces no passing receipt. Its cap is not raised
or suppressed. The portable bridged checks above are a new verifier with
an explicit larger precision invoice, not a passing old scalar pipeline.

For reproduction, supply a Boost include directory and a new output path:

```sh
python3.12 -I -B research/bit-carrier-owner-admission/native-check.py \
  --boost-include /absolute/path/to/boost_1_87_0 \
  --output /absolute/path/to/new-native-replay
```

`NATIVE-CXX.json` in that output records the compiler identity, complete
commands, source and stream hashes, exit codes and structured results.
Portable verification does not execute this optional command.

The old `xcheck_p.py` H4 grammar expects a literal reversed A/B cleanup,
and the old global emitter derives helper widths from FULL terminal
frames. Those assumptions do not describe the changed signed prelude and
five partial terminals. No old H1–H5/global-pipeline PASS is claimed.
The new provider, the explicit owner dispatch and the conditional complete
invoice identify the required replacement interfaces. Binding them to an
all-size physical caller, its coefficient grammar and exact returned
rounded-child contract remains a separate obligation.

The finite provider and fresh C++ legality results establish no new kappa.
Written and checked with substantial OpenAI Codex assistance; no independent
human or formal-kernel review is claimed. Apache-2.0.
