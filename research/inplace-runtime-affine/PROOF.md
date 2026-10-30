# Direct same-owner completion of the runtime affine kernel

The exact retained source is fixed-tape-affine-shear at main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. Its proof and finite-control source
are authenticated inputs. The local macro, symbol and machine contracts are
unchanged. This proof uses the predecessor's all-size split, conversion,
coefficient and erasure lemmas; it does not claim independent reproof of them.

## Complete interface

For positive binary P,Q,G,S and0<=c,C<Q, tape0 contains the entire arbitrary
Boolean stream on [P]x[Q]x[G]x[Q]x[S] between LEFT and RIGHT markers. Its head
starts on the first payload bit. Six descriptors are canonical LSB-first words
for P,Q,G,S,c+1,C+1. The eleven private tapes are blank, at independently chosen
origins. These physical roles are distinct. Tape1 is an arbitrary spectator;
there is no empty-output premise. All extents, coefficients and payloads are
runtime tape data, never assembler arguments or host callbacks.

The result on the same tape0 moves each input coordinate to

    (p,x,g,y +/- (c*x+C) mod Q,z).

All markers and the owner's head return to their original positions. Descriptor
bytes/heads are preserved. Every private cell and head returns blank to its
original origin. Tape1 is never read, written or moved. In the linked half
program, Q is odd and at least3; the coefficient tape is owned blank input,
prepared and erased by the unchanged source descriptor routines. The remaining
interface is unchanged. Generic c,C can be zero or nonunits, including Q=1.

## Complete gather before overwrite

The source invariant gives a split r=C+c*x mod Q for each x group. Its gather
pass scans the complete source into the two owned buckets. Their total payload
length is V=P Q^2 G S. At the gather boundary, source0 is on its RIGHT marker;
every original bit is already present in exactly one bucket. The source proof
has already advanced through every prefix, x, gap and record and retained the
correct split state for emission. No later emission reads source0 as input.

Rewind source0 to its first bit at this boundary. Emit through the same two
bucket segments, with the destination changed from tape1 to tape0. The local
copy macro writes its destination without a blank test, so overwriting old
payload is legal. Its source is a distinct bucket. Each old bit is already
retained before any overwrite, and each bucket bit is consumed exactly once.
Thus the predecessor's output permutation is installed in the original owner.
The final RIGHT marker is written at the same volume endpoint. Rewind that
owner and execute the unchanged complete private erasures.

This argument covers both orientations: their gather and emit segments differ
as in the source, but both gather the entire source before emission. It also
covers arbitrary payload values and independently translated tape origins.
The unchanged source loops prove termination. No bank rename, inverse call,
productive clean owner or free source retirement is required. The source's
direct owner pattern from signed-dyadic-scaling is credited, not claimed new.

## Exact all-size transition and space deltas

Compare an in-place call with the source separate-output call on the same
valid stream, descriptors and private origins. The instruction path is the
same except for these items:

- Remove output initialization: one scanned blank branch, one LEFT write and
  one unit move. This removes exactly three transitions.
- Move the source rewind from final cleanup to the gather/emit boundary. In
  both positions its starting head is the same source RIGHT marker. Its path
  depends only on source symbols and marker locations. Before overwrite the
  payload is unchanged. This has exactly the same transition count.
- Retarget emission and the output rewind to source0. The old and new marked
  streams have the same length V. Record copy reads only bucket values and
  writes destinations; destination payload values cannot affect the path.
  Both final rewinds have the same count for either Boolean payload.

Every other counter conversion, cyclic reset, bucket motion and erasure has
the same path. Therefore T_inplace=T_source-3 for every valid input. The source
bound T_source<=1024V gives the same complete bound here. Linked half setup and
coefficient erasure are unchanged, so their exact delta is also minus3 and
the same1024V allowance includes them.

The source output tape visits its complete interval of V+2 cells, including
markers. The new unused tape1 visits only its initial head for the interpreter's
span convention. The source owner already visits the full interval during
gather, and its new writes and rewinds visit no additional cell. Every other
tape's visited interval is unchanged. Hence visited_span_inplace equals the
source span minus V+1, including all erased work and markers. The retained64V
bound therefore applies. Arbitrary untouched tape1 contents are not new visited
workspace; the full private capacity remains charged. Sequential calls may
reuse only the proved returned private regions.

## Adaptation and independent execution

The optional keyword selects the output role, omits its initialization, places
the owner rewind before emission and avoids a duplicate final source rewind.
DELTA.json lists every source edit. With inplace=False the exact original
instructions for all four tables match, including all state destinations.
The new tables use only local symbol branches/writes, unit moves, fixed jumps,
halt and reject. Static validation excludes all operations on tape1.

The retained sparse and dense interpreters are separate implementations. The
dense coordinate oracle uses direct gather addresses, not bucket traversal.
The checker compares every final cell/head and physical step/span between
engines, checks the exact resource deltas against source execution, and tests
complete physical inverse pairs. Controls cover wrong owner, private residue,
wrong head, direction, malformed descriptors, nonlocal moves, a regenerated
missing-rewind table and extra endpoint-preserving work. Typed table/receipt
comparison and source authentication remain active under Python optimization.

## Remaining boundary

This is the complete later-target stream primitive. It does not produce general
runtime coefficient descriptors, transpose earlier fields, allocate a whole
recursive owner bank, stage low-cache data, perform full G20 route dispatch,
implement rounded/native children or prove P3 and outer admission. Those costs
are not zero. No selected assumption is discharged and no new kappa is claimed.
