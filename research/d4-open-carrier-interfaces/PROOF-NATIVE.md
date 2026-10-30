# Exact native D4 carriers and the isolated four-helper factor

The fixed OPEN source carrier, reverse source carrier and four-helper bus have
native rank histograms respectively

| Word | Rank 1 | Rank 2 | Rank 3 | Native queries | Rank mass |
|---|---:|---:|---:|---:|---:|
| OPEN | 8 | 40 | 16 | 64 | 136 |
| Reverse | 20 | 56 | 4 | 80 | 144 |
| Four-helper bus | 8 | 40 | 20 | 68 | 148 |
| Bus with explicit helper-value restoration | 8 | 40 | 24 | 72 | 160 |

All four words are freshly replayed in four exact orientations. The
last row is a separately charged completion of the bus. These are
finite, exact local interfaces at the stated geometry. They do not constitute
a native rounded supplier, a physical tape schedule, or a multiplication
bound.

## Inputs, sources and conventions

The sole mathematical inputs to `check_native.py` are the explicitly supplied frozen
geometry and compiler. The geometry SHA256 is
`93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd`.
The exact Gaussian-dyadic compiler SHA256 is
`2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`;
its source at scientific commit
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` is
`research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py`.
The authenticated compiler bytes are the bytes executed, with compiler
assertions retained even under outer Python `-O`. Historical carrier and
factor sources and their original receipts are retained separately in `frozen/`.
They are provenance, not executable dependencies of the new checker.

There are 12 source fields, 12 target fields and four helper or audit fields.
Every field is an independent arbitrary 128-coordinate Gaussian-rational
array. The exact linear identities consequently extend over the complex
numbers. No field is assumed zero. OPEN and reverse use no ordinary helper:
their four extra audit fields are untouched arbitrary spectators. The bus
uses all four arbitrary dirty helper fields.

The selected h7 labels are

```
A = (7, 2, 50, 55)
B = (13, 61, 8, 56)
C = (117, 64, 69, 112).
```

This is one selected D4 block. It does not certify coverage of the omitted
labels or other blocks of a larger parent geometry.

Matrix products below act rightmost first. The compiler spelling
`a.then(b)` denotes `b a`. For a declared frame U, a physical field stores
`U x`, where x is its logical value. A native transition from U to V is the
actual operator `V U^-1`; it changes that frame without changing x.

Define

```
C_v = ((1+i) I + (1-i) X_v)/2,
F = X_33 F_7,
E_A = D C_7,    E_B = D C_13,    E_C = D C_117,
V_A = D C_13 C_117,
V_B = D C_7 C_117,
V_C = D C_7 C_13.
```

Here D is the radical four-point Walsh operation in the chart with columns
`(7,13,117,5,53,30,96)`, including the exact `-i` correction in the frozen
construction. The checker compares the historical invariant product for F
with `X_33 F_7` including global phase. In particular `C_v²=X_v` exactly.
All subsequent lowerings retain the global, linear and quadratic phases.

For coordinate j and group g, put
`p=G_g[j], q=G_(g+1)[j], r=G_(g+2)[j]`, with groups read cyclically. The
source input frame is `C_p`, the target input frame is `C_q`. The ordinary
fixed-ID return frames are `F C_q^-1` for the source and `F C_p^-1` for the
target. A bus helper starts in `E_A`. An untouched audit field starts and
ends in the identity frame.

## Actual scalar and native words

All three words first move the sources to their `E_g` frames and targets
to their `E_(g+1)` frames. The complete chronological event lists in
`artifacts/NATIVE.json.gz` (decompressed) include every native transition and every scalar primitive.
The following description is for one coordinate j; four disjoint copies
are used.

For OPEN, the physical A source is the carrier. Move it from `E_A` to
`E_B`, add it to target A, and swap it with the physical B source. Return
that B field to its ordinary source return frame. Move the carrier to
`E_C`, add it to target B, and swap it with the physical C source. Return
that C field to its ordinary source return frame. Move the carrier through
`V_B` to `V_C`. Move target C to `V_C`, then deliver the carrier to it.
Return the three targets to their declared return frames.

Before raw cleanup the physical source IDs hold logical values `(C,A,B)`.
Swap physical A with C and then A with B. These are paid raw field swaps;
they transport the actual output frames together with the values.

For reverse, move carrier A to `V_A`, physical source C to `V_A` and target
A to `V_A`. Deliver to A, then swap carrier A with C and return physical C.
Move the carrier to `V_C`, source B to `V_C` and target C to `V_C`. Deliver
to C, then swap carrier A with B and return physical B. Move the carrier
to `V_B`, move target B there, deliver to B, and return the carrier and all
targets. Before cleanup the source IDs hold `(B,C,A)`. Raw swaps A/B and
then A/C restore the source IDs.

For the bus, swap helper H with source A at `E_A`, and return physical A.
Use H as the OPEN carrier through B and C, performing the corresponding
contacts, deliveries and physical source returns. Finish H at `V_C`.
Raw swaps H/C, H/B, H/A restore the public IDs and isolate the dirty helper
on its original physical helper ID. This last operation restores the ID;
it does not cancel the helper's native output channel.

Every common-frame delivery is checked at its actual cut. Every contact
swap is checked to have equal frames. Each whole-field swap is executed as

```
a += b
b -= a
a += b
b = -b.
```

This is valid for arbitrary a,b and uses three signed complex ADDs and one
complex negation. Raw ID swaps use the same four primitives and are
explicitly charged even when the transported fields have different frames.
No native query is inserted within a raw swap, and no common-frame
interpretation is asserted for its intermediate mixed values.

The scalar bills, before native-query monomial adapters, are:

| Word | Deliveries | Contact swaps | Raw swaps | Signed complex ADD | Complex NEG |
|---|---:|---:|---:|---:|---:|
| OPEN | 12 | 8 | 8 | 60 | 16 |
| Reverse | 12 | 8 | 8 | 60 | 16 |
| Four-helper bus | 12 | 12 | 12 | 84 | 24 |
| Bus plus helper-value restoration | 12 | 12 | 12 | 84 | 24 |

All four orientations of each of the four words have the same
listed scalar and native histograms. ADD and NEG here are whole-field
complex operations; they are not rounded scalar primitives or tape steps.
For a field of length N, a direct componentwise implementation of these
word-level operations uses twice their listed counts times N in real ADD
or real negation operations, before native children and monomial adapters.

## Full arbitrary-input boundaries

At each public source/target pair the OPEN boundary is

```
W_OPEN = [ S  0 ],
         [ J  T ]

T = F C_p^-1 C_q^-1,
J = F X_p,
S = F C_r^-1 C_p^-1        for g=A or B,
S = V_C C_p^-1            for g=C.
```

Every S and T has native rank 5 and every J has rank 7. The raw reverse
boundary is

```
W_reverse = [ J  0 ].
            [ J  T ]
```

Thus all its transported source diagonal channels have rank 7. These are
the actual boundaries before any optional source normalizers. A
common-F normalization and a specially wrapped backward alphabet are
separate constructions, covered by the companion normalization proof.

After all paid raw cleanup swaps the four-helper bus is exactly

```
W_bus = W_OPEN direct_sum H_0 direct_sum H_1 direct_sum H_2 direct_sum H_3,
H_j = F C_(B[j])^-1 E_A^-1.
```

Each H_j has native rank 3 with its exact phase. Every helper-to-public
and public-to-helper block is zero. The helper inputs are arbitrary, and
their full values survive through the isolated invertible maps H_j.
Their physical outputs are `H_j h_j`, rather than `h_j`.

If the caller requires the original physical helper values, append the
four actual native queries `H_j^-1` on those four output fields. The
checker executes this tail and verifies
`W_bus followed by H^-1 = W_OPEN direct_sum I_4` on all 28 arbitrary
fields. It costs four extra rank-3 queries, raising the mass from 148 to
160, with no extra scalar ADD or NEG. This bill is separate from the
mass-148 factorization and provides no saving over using OPEN directly.

The marginal bus histogram over OPEN is four rank-3 queries. Equality of
these cost differences with the ranks of the isolated H_j channels is
specific to this frozen word and does not prove a universal sharing
obstruction for changed words, endpoints, or coupled helper use.

## Physical-ID query paths versus transported values

The product of native queries executed on a fixed physical ID is not
necessarily the operator acting on one transported input value: scalar
swaps move those values between IDs.

| Word | Fixed physical source query products | Transported source diagonal | Fixed helper query products | Transported helper channel |
|---|---|---|---|---|
| OPEN | A: rank 3; B,C: rank 5 | rank 5 on all 12 | identity spectators | identity spectators |
| Reverse | rank 5 on all 12 | rank 7 on all 12 | identity spectators | identity spectators |
| Bus | rank 5 on all 12 | rank 5 on all 12 | rank 1 on all four | rank 3 on all four |

The checker separately accumulates the native query products on each ID
and verifies them against that ID's entrance and pre-cleanup return
frames. It separately reads the transported diagonal channels from the
complete output operator. These are different, explicitly recorded
contracts. In particular the bus's rank-1 fixed-ID helper path cannot be
used as a rank-1 bound for its transported dirty helper output.

## Literal inverse, inverse-transpose dual and dual inverse

Let the chronological primitive list be `L_1,...,L_m`, so the complete
matrix is `W=L_m ... L_1`.

* The literal inverse lists `L_m^-1,...,L_1^-1`. A native unitary K becomes
  `K^-1=K†`, an ADD reverses its coefficient, and a NEG is unchanged.
* The inverse-transpose dual lists `L_1^-T,...,L_m^-T` in the same
  chronological order. For a complex-linear native unitary,
  `K^-T=conjugate(K)`, not `K†`. The checker constructs the literal
  conjugate circuit, retaining its exact phase. An ADD
  `dst += e src` becomes `src -= e dst`; NEG is unchanged.
* The dual inverse is the literal reverse inverse of that dual list,
  namely `(W^-T)^-1=W^T`.

The transpose is the ordinary algebraic transpose of the full complex
matrix; it is not the conjugate transpose. The inverse of a binary
address permutation is a separate operation within a monomial recipe.

For `W=[[S,0],[J,T]]`, the independent expected blocks are

```
W^-1 = [ S^-1           0    ],
       [ -T^-1 J S^-1   T^-1 ]

W^-T = [ S^-T   -S^-T J^T T^-T ],
       [ 0       T^-T          ]

W^T = [ S^T  J^T ].
      [ 0    T^T ]
```

These products are constructed separately from the replayed gate lists.
The same rules apply to each isolated helper diagonal. The four checks
are for these declared raw boundaries; they do not replace the separate
backward-alphabet normalization obligation.

## Full-phase checking, coverage and executable controls

Each physical output row is a sum of integer multiples of exact Clifford
operators applied to the 28 independent input fields. Native queries
left-compose these operators. ADD and NEG manipulate the actual rows,
including every intermediate primitive of every swap.

An operator key includes the complete signed Pauli tableau and its exact
Gaussian-dyadic zero-address column. Two Clifford operators with identical
signed Pauli action differ by a scalar: their quotient commutes with every
Pauli, hence is scalar on this irreducible representation. Equality of
the nonzero zero-address column fixes that scalar. Therefore equality
of these keys establishes equality on all 128 addresses, including phase.
The digest is an index only: an explicit collision gate compares the
underlying exact payload whenever an index is reused.

After cancellation of identical exact operator terms, each actual output
row equals its separately derived expected row. This is a sufficient
all-input certificate covering 28 field columns and hence all 3584
physical address-basis columns. The checker does not claim to enumerate
3584 independent full-program simulations. Its accepted equality uses
only exact operator composition and identical-term cancellation, with no
sampled input or assumption that distinct operator keys are linearly
independent.

For a rejected mutation, different sums of Clifford keys alone would not
prove unequal operators. The checker therefore searches the actual
128-address basis and emits an input-field/input-address and
output-field/output-address witness with unequal exact Gaussian
numerators over one common dyadic denominator.

Each of OPEN, reverse and bus is actually run with an omitted raw cleanup
swap, an incorrect contact-swap subtraction sign, an omitted delivery ADD,
and a global i phase inserted into a native target return query. The bus
is also executed with an extra dirty-helper-to-public ADD. All 13 defects
must fail the same production endpoint predicate with the named endpoint
error and a concrete Gaussian witness. Unexpected errors are rejected;
unexpected acceptance raises outside the catch.

For each of the three phase defects, deleting phase sensitivity at that
same predicate causes actual acceptance; the same rejection oracle then
fails with `expected_rejection_missing`. These three executed deletions
show that global phase is semantically necessary at this gate.

An additional cancelling `+ADD,-ADD` pair is executed at a legal delivery
cut. It preserves the complete endpoint and is accepted there, but the
same production bill predicate rejects its 62 ADDs against OPEN's claimed
60. Endpoint equality and the complete invoice are therefore separately
exercised. Finally, omission of an actual helper inverse query in the
optional completion fails its same all-column endpoint predicate with an
explicit helper-coordinate discrepancy. Together there are 18 recorded
semantic, deletion and cost control outcomes.

## Native adapters and their paid implementation

Every positive-rank query is lowered as an exact monomial/native-Fourier/
monomial product. Both monomial legs, their affine address maps, quadratic
phases and scalar global phases are in the receipt. Every lowering is
compared to its actual query using signed Pauli data and exact phase.

The numbers of monomial legs are 128 for OPEN, 160 for reverse, and 136
for the bus, in every checked orientation. All are nonidentity in this
unfused lowering. The optional four helper inverses add eight legs, giving
144 in every orientation. These are paid monomial-operation upper bounds, rather than exact
physical tape-pass counts. A literal decomposition into D, P, X and scalar
phase uses at most four such map applications per leg.

A monomial is an explicitly supplied map
`|x> -> i^phi(x) |A x xor b>`. The companion
`PROOF-NORMALIZATION.md` supplies two paid implementations. One uses a
separate destination array whose storage must be counted. The other
phases coordinates in place and rotates address cycles with at most
`N-1` complex-value swaps, each three ADDs and one NEG, no extra complex
field, and bounded binary address counters. Cycle-leader discovery can
take `O(49 f N²)` binary work for `N=2^(7f)`. Applying that recipe to each
listed leg gives, per leg, at most `3(N-1)` coordinate complex ADDs,
`N-1` coordinate complex negations and N Gaussian-unit phase
multiplications, plus that binary work. It is an unfused upper bound;
it is not a physical tape realization or a free-permutation convention.

The scalar table above excludes these adapters explicitly and the
receipt reports their complete number separately. The underlying
positive-rank native children retain their own implementation and
precision obligations. No whole-word intermediate norm, rounding-grid
bound, workspace owner schedule or physical head-return claim is made.

## Reproduction and limits

Use a fresh output path:

```
python3 check_native.py --geometry frozen/geometry/D4-BUS-INPUT.json \
  --compiler frozen/compiler/clifford_exact.py --output /tmp/fresh-carrier-CHECKS.json
```

Existing outputs are rejected before any audit work. Normal and optimized
Python are required to produce identical complete receipts. The receipt
contains the checker hash, both input hashes, exact frame definitions,
all four complete event lists for the three main words and the optional
helper-restoration word, full endpoint operators, native lowerings, cost
bills and physical negative-control witnesses. It has no output-location
or runtime-dependent fields.

Tensoring every exact base operator across f independent address-bit
positions preserves composition, inverse and each exact operator
identity. The symbolic row proof uses cancellation of identical
operators, which remains valid after tensoring, rather than an
unjustified tensoring of a sum identity. Thus the displayed local
interfaces lift to arbitrary f under the declared tensor-word
interpretation. This mathematical lift does not supply a routed caller,
native precision, rounded cleanup, physical access, whole-helper
ownership, or a multiplication theorem. The finite replay and this
written tensor argument are not formal-kernel proofs.
