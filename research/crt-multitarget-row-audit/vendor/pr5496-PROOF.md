# Current numerical offsets to a physical CRT micro-row

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## The exact boundary

Use the admitted `RowEntry` domain of Ali Romman's PR5353: a power-of-two
axis count d, declared h_i in {ell-1,ell}, ell>=2, pairwise coprime moduli
2<=s_i<2^h_i, arbitrary padded current coordinates 0<=x_i<2^h_i, one
compiled tree node [a,a+n) and one global row. The source is its literal
sequential padded-axis tape, not a host list of numeric values. Eight
distinct protected numerical words are supplied with the retained legal
heads. Fixed topology, input ownership and the source numerical-operation
model remain predecessor premises.

Let b=a+n/2, P=1+sum_{i=a}^{a+n-1}h_i, and A be the non-idle right axes
of this global row. The result is an owned stream containing, in axis
order, the h_i bits of the **micro-row output** for every right axis
b<=i<a+n. Delimiters are L, then one coordinate followed by `|` per axis,
then R. No active axis means no allocation or tape work and no output;
the original source already represents the identity row. When some axes
are idle, their coordinates are copied into the returned stream unchanged.

All borrowed source/dirty words and entry heads return unchanged. The
numerical outputs, new descriptors, produced ROM and complete unselected
layer output, producer workspace and query countdown are retired. The
owned coordinate result remains until `close`, which erases it and closes
the original Entry. Successful calls leave every new physical head at
zero; the inherited numerical ports have their retained head-one exit.
Failure rollback and arbitrary dirty backing acquisition are not claimed.

This theorem closes an actual encoded-numerical-output to physical-query
boundary. It is not the full three-epoch exceptional key, a full CRT row
permutation of all payload addresses, or a complete multiplication theorem.

## Numerical input and encoded descriptor compatibility

The unchanged PR5353 RowEntry and PR5053 producer reconstruct the actual
current left child. On a valid left child they return k_A; an invalid left
child disables it by k_A=0. For each right axis i, their sequential output
contains

    c_i = k_A * (product_{j=a}^{i-1}s_j)^(-1) mod s_i,

followed by a whole-rotation updated value. The inverse exists by pairwise
coprimality. All preceding right moduli are included. We consume the offset
word and **discard the updated-value word by a charged scan**: a complete
cyclic rotation is not one Beneš micro-row.

For an active axis, the join reads its original modulus directly from the
borrowed source, translates each numeric bit to the producer's finite bit
symbol, and pads with zeros against the actual unary P guide. It similarly
copies exactly P bits from the actual numerical offset stream, enforcing
the guide and field delimiters. This creates a singleton offset list
`L [P bits] | R`; no decoded integer or host-built offset list is used.
Compiled h_i and the selected local-row constant are written in binary and
zero-padded through that same guide. The finite topology is the only source
of those constants. The ROM program itself is precompiled without any
input values and passed to the join.

The existing PR5092 producer requires W>=h_i+3. A node has at least two
axes, and every modulus is at least two, hence every admitted h_j>=2.
Consequently P>=h_i+2+1=h_i+3. Taking W=P meets its width contract; its
modulus and singleton-offset guards follow from the numerical theorem.
The local row is g for a long axis, and g or g-2 on the two active pieces
of a short axis, with global rows ell-1 and ell idle. This is exactly the
pinned `local_row` function, and lies in [0,2h_i-2].

Thus the unchanged encoded producer emits the exact canonical Beneš
network for the rotation x->x+c_i mod s_i on x<s_i, fixing padded wires.
Its selected `rom` is L followed by exactly N_i=2^h_i bits and R. Its
`layers` output contains all 2h_i-1 layers; the join pays to erase it even
though the query needs only one selected layer. Both producer outputs are
consumed on their original backing lists, through local tape operations.
There is no verifier-supplied row or source table lookup in execution.

## Physical query and the current-coordinate convention

The query copies the actual current h_i-bit coordinate to an owned
little-endian countdown and a separate output coordinate. The ROM scan
visits every produced row bit in order. Until selection, a zero test scans
the countdown, returning its head, and a nonzero countdown is decremented
by ordinary borrow propagation and head return. At scan position j, while
selection is enabled, the countdown represents x_i-j. Hence precisely
position x_i sees zero and selects its row bit. Since 0<=x_i<N_i, selection
always occurs before R. After selection, the scan continues to R without
changing the chosen bit. The countdown is then erased.

If the local row is r, its source target bit is min(r,2h_i-2-r). The join
moves to that compiled bit position in the owned coordinate, XORs the
selected bit and returns the head. This is exactly `Caller.row`'s table
action. No check x_i<s_i suppresses a query. A Beneš implementation of a
padded permutation can pass through padded coordinates at intermediate
rows; the queried coordinate must be the current one.

At a fixed node, the left child is unchanged throughout its micro-rows.
Right offsets depend on the successive modulus prefixes, not on the
current right coordinate values. The numerical producer's current-child
convention therefore gives the same offsets as the source caller at each
row. Each active right axis receives its proper current-coordinate query;
idle axes retain their coordinate. These facts prove the whole returned
right-node row stream equals the corresponding slice of `Caller.row` for
every admitted source state, not merely the verifier examples.

## Ownership and a reused producer bank

The numerical producer and RowEntry stay unchanged and retain their full
63-port lifecycle. New header, coordinate, countdown and output ports are
distinct from all borrowed roles. The join allocates one fixed PR5092
service bank, then invokes the same program for each active axis on the
same bank. Its private tapes return blank with heads zero by the producer
theorem. The join erases both generated output roles and all four headers
before the next invocation. These steps establish the next call's entry
premises without constructing a new ROM or replacing the bank backing.
Restoring the emulator's initial head configuration represents those
already returned physical heads, not a free head jump.

The finite producer register configuration is fixed control. Reentering
its fixed start state has constant cost, included in the conservative
adapter allowance below; it is not an input-sized store reset. Initial
blank owned backing remains an explicit storage premise. Erasing cells
does not release or subtract their retained capacity.

The source and numerical output heads rewind by local movement. Numerical
results are retired only after every offset has been consumed, so no
output lifetime is silently shortened. `close` disposes of the coordinate
result and calls the original Entry close exactly once. All malformed
or rejected executions remain outside the successful cleanup theorem.

## Complete local time and retained-storage invoice

Let L=2+sum_{i=0}^{d-1}(3h_i+4), N_i=2^h_i, and

    F = L + (n+1)(P+2)
        + sum_{i in A}[(N_i+1)(h_i+1)
                      + N_i(2h_i-1) + 2h_i+4].

The inherited Entry, including numerical computation and retirement, costs

    T_entry = 2^20(P+2)^4 + 2^16(P+2)^2 + 128(L+P+n+1).

The complete producer is charged once per active axis at m=1, W=P:

    T_rom(i) = 2*10^6 P^2 (N_i+1)^3 (h_i+1)^4.

The new serialization, current-coordinate query, updates, returned-stream
emission, every header/ROM/layer erase and every added rewind cost at most
4096F source-tape/control operations. One direct count is: each additional
source symbol is scanned a fixed number of times; each header/offset/skip
word uses O(P) charged reads/writes/moves; each row query visits at most
N_i positions, with at most two h_i-bit scans plus head returns at a
position; disposal scans both output lengths N_i and N_i(2h_i-1)+O(h_i).
The displayed routines use fewer than 64 primitive tape operations per
unit represented in F. Between these charged accesses there are fewer
than 64 finite tests, assignments and compiled-loop transitions, including
fixed-role dispatch and the per-invocation fixed control reset. Thus 4096F
is a deliberately loose complete bound, not a timing extrapolation.
Compiled topology/ROM-program creation and supplied-input serialization
are external setup, explicitly not runtime numeric decoding.
Activity uses the fixed compiled node/width/row predicate, not a linear
membership scan of all active axes. The emulator watchdog is the displayed
T_rom(i), computed from compiled P and h_i; no fixed finite watchdog limits
the admitted all-size successful execution theorem. External resource
timeouts remain test limits, not machine rejection.

The full invoice is

    T_join <= T_entry + sum_{i in A} T_rom(i) + 4096F.

This adds compatible fixed-alphabet source-operation bounds. It is not a
claim that all numerical control was lowered to one binary transition table.

Let J_i=N_i(h_i^2+3h_i+1). Use the predecessor Entry retained-backing bound

    B_entry = 57(P+2)+3(P-2)(2P+4)+6+3P+4n+4,

and, including the four producer inputs of total length 4P+9,

    B_rom(i) = 100(P+2)+5P J_i+N_i(4h_i-1)+10(h_i+1)+4P+9.

The single bank's sum of per-role historical maxima during this finite
row is at most sum_i B_rom(i). We deliberately use this conservative sum,
not the unjustified maximum of aggregate bounds. The two coordinate/
countdown ports and returned stream add at most

    B_extra = 2(max_{b<=i<a+n}h_i+3)
              + sum_{b<=i<a+n}h_i + n/2 + 3.

Hence total new owned retained backing is bounded by
`B_entry + sum_i B_rom(i) + B_extra`. Input source L and protected numerical
backing 8(P+2), plus any supplied exterior blank capacity, remain borrowed
and separately charged. The verifier sums distinct physical backing
identities, so ROM/header aliases in observer wrappers are not double
counted. No arbitrary cross-session persistent-bank theorem is implied.

## Evidence and limits

The first source fixture is (7,3), widths (3,2), current state (1,1).
Five separately encoded row invocations follow the actual state sequence
(1,1), (1,1), (1,3), (1,3), (1,3), (1,2). The last query must run on
padded coordinate 3. Test-harness serialization between invocations is
explicit; this is not an uninterrupted physical whole-level execution.
Invalid left padding disables the offset and returns identity. Four
faults change the supplied offset, selected local row, required padded
query or complete-layer disposal, and are detected at semantic or ownership
checks. The source four-axis discriminator has preceding-right-modulus
offset3 rather than the incorrect7, but the new full h=4 producer/query
replay exceeded its180-second resource limit and produced no completion
receipt. It is explicitly uncompleted; the executed new full pipeline
evidence is h=2. The quantified argument is source-relative and does not
depend on claiming that uncompleted test passed.

Finite checks corroborate the written source-composition and countdown
arguments. Initial axis-record production, a uniform binary compiler,
full three-epoch exceptional key, global ROM reuse, full E(p,ell), native
and outer multiplication admission remain unresolved. There is no new
kappa or selected-frontier claim, human acceptance or formal-kernel proof.

## Credit

Ali Romman supplies PR5353's actual row-entry contract; JoyboyBrian supplies
the retained PR5053/5219 numerical modules and PR5092 control producer.
Retain Hiroki KUMAZAKI's current-coordinate and mixed-width caller,
Cinna Davis's CRT/Beneš construction, ToikY's encoded arena/DFS proof,
Tekalign's original-coordinate stream work, Jose Manuel, Ryanson Jonathan,
unpaidmoon, Douglas Colkitt/John-Michael Smith and all pinned notices.
