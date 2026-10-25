# Range and exact lattice certificate for the two frozen recovery words

Fix the literal PR4106 and PR4015 WORDs and their full tensor-native semantics.
Let lambda be any positive integer and put t=lambda−1. Let h=2^z for an
integer z and let P be a nonnegative integer. At the decoder entry, suppose
all real and imaginary components of the 224 borrowed X/Y fields, uniformly
over every owner and payload coordinate, lie in h Z and have magnitude
strictly below 2^P h. Owned output and private fields can contain arbitrary
dirt: each must be cleared before its first numerical use, as checked by the
standalone interpreter. No magnitude premise is imposed on unread dirt.

Both frozen words have the following **common sufficient exact format**:

```
q = h · 2^(−9−3t),
W = P + 28 + 6t signed bits per real or imaginary component.
```

Every visited component, scalar partial and Gaussian interior fits this
format. Hence the specified arithmetic incurs zero rounding or overflow.
This is an entry-domain implication and sufficient format, not a claim that
this format is minimal or that an actual recursive caller supplies that entry
domain. Logical frame/output correctness remains the independently replayed
PR4106 premise; this certificate analyzes both complete arithmetic schedules.

## Component induction

A field carries a quadruple (M,g,a,b), meaning

```
|component| < 2^P h M · 2^(a t),
component ∈ h · 2^(−g−b t) Z,
```

for nonzero M; the canonical M=0 bound means exact zero. Entry borrowed
fields have (1,0,0,0). A CLEAR produces zero. A signed addition combines
nonzero fields using M=M1+M2 and the componentwise maxima of g,a,b. If one
operand is proved zero, retain the other bound exactly. Signs can only reduce
the actual magnitude, so this induction does not assume independent values
or discard a harmful correlation.

An exact ±1/4 coefficient changes M to M/4 and g to g+2. The implementation
observes the unscaled source, the first halving (M/2,g+1,a,b), and the final
halving before accumulation. Thus division is not silently treated as a
rounding primitive, and its intermediate lattice requirements are included.
All observed exponents are bounded by the common q exponent below.

Tensor monomial wrappers and full cover maps are signed component
permutations, hence preserve magnitude and lattice. This relies on the
source native/cover semantics uniformly over owners; a cover is not presumed
to be an owner-local payload permutation.

For one coordinate Gaussian line C_q, use the direct pair-first lowering

```
s=x+y, d=x−y;
outputs=((s+i d)/2,(s−i d)/2).
```

The source producer proof writes the second output as (d+i s)/2, which is
i times the direct C_q second output; this is a phase difference, not a
componentwise identity. Either expression has the same range and lattice
bounds. This proof uses direct C_q and the frozen word's already charged
native monomial wrappers; no extra uncharged phase operation is inserted.
Signs in the inverse line leave these component bounds unchanged. If input
components are bounded by L, pair sums are bounded by 2L, cross numerators by
4L, and output components by 2L. The halving refines the lattice by at most
one bit. A rank-one native line at tensor depth lambda performs this rule
once in each of its lambda coordinate layers, retaining the original order
inside each layer. Scalar port coefficients still act once, not lambda
times. Before layer j, magnitude is at most 2^(j−1)L and the lattice has
refined by j−1. Since 1≤j≤lambda=t+1, all its interiors are dominated by

```
pair sums:       (2M, g,   a+1, b+1),
cross numerators:(4M, g,   a+1, b+1),
completed output:(2M, g+1, a+1, b+1).
```

These are grouped upper bounds, not identities for every interior grid.
They bound all earlier-layer outputs too. Native calls have no active private
scope in either word. Private fields are created dirty, cleared before use,
and required to be zero at scope exit; the maximum active private count is16.

The tensor/native arithmetic and proof pattern are credited to the canonical
`research/qq16-all-depth-producer-grid/PROOF.md` and its native predecessor
lineage. Its producer numerical constants are not reused for the decoder.
`range.py` is a new standalone interpreter that imports no inherited
executable. Its caller must authenticate the literal input words first.

## Whole-word constants and the changed cut

Induction over all 3,713 candidate and 3,813 baseline events, including the
unchanged prefix, query acquisition, response and suffix, gives in both cases

```
maximum M = 171043 < 2^18,
maximum g = 9,
maximum a = maximum b = 3.
```

The maximum M first occurs after W0 at zero-based candidate event3697,
baseline event3797. All224 final component-envelope quadruples agree.
Every component therefore has magnitude strictly below
`2^P h · 2^(18+3t)` and belongs to `h·2^(−9−3t) Z`.
In units of q the magnitude is strictly below
`2^(P+27+6t)=2^(W−1)`, proving the signed-width statement. Because each
intermediate is on the q lattice, the explicit halvings are exact in this
format, including their divisibility requirements.

The new arithmetic does increase one temporary's local envelope. Candidate
event1714 is the first D+=E operation (physical host Z10 receiving Z11), with
bound (460,4,2,2). The baseline's single-source D has bound at most
(230,4,2,2). This local doubling is included, rather than transferred through
an unchanged-DAG claim. Each of the eight completed query fields has the
same bound (11864,4,2,2) in both words: immediately before candidate event2434
and baseline event2536. Thus the new pair sum is already dominated by the
completed query envelope. More generally, a same-support pair contributes
its two positive source envelopes to an agreeing query row, so sharing that
sum cannot exceed the full row's nonnegative sum. The entire following
response and suffix consequently reproduce the same envelope bounds.

The first literal word difference is earlier, at index37, due to deferring
the tenth host's X-copy. A deferred uninitialized slot is not a numerical
intermediate. The interpreter rejects any attempt to read it before CLEAR.
The host's charged restoration remains part of the whole-word calculation.

## Separate finite checks and limits

A second numeric recurrence in `audit_depth` does not use Bound, the grouped
rule or the symbolic dispatcher. It explicitly expands every coordinate
Gaussian line. At depths1,2,3,8 both complete words have identical magnitude
bounds 171043,1195465,9220309,298371196093 and grid exponents9,12,15,30.
These check the finite arithmetic behind the induction; the preceding
symbolic proof, not a sampled-depth test, supplies the universal quantifier.

The result shows that this particular sufficient format needs no widening
for the paired word. It does not say that the two schedules attain equal
true maximum magnitudes, that their errors coincide under an arbitrary
rounded format, or that their separately optimal widths coincide. An
existing caller's input conversion, physical layout/movement, native
workspace, recursive tariff and supplier caps require their own contracts.
