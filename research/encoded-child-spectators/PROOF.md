# Encoded shared atom powers at the child-spectator boundary

## 1. Statement and exact source boundary

Let q be the fixed source radix, let the admitted Ring modulus be A=q^w,
w>=1, and let each e_i be a borrowed canonical unsigned Word of width I.
For one to three distinct owned Count outputs v_i, the operation computes

`v_i <- v_i * A^(e_i)`.

The e_i and Ring/arena inputs return byte-for-byte unchanged at canonical
head 1. The caller supplies, or the setup creates, one distinct owned blank
counter role. It is returned blank at head 1, including its erased visited
backing. This is not an arbitrary-dirty loan. Output and workspace aliases
are rejected. Fixed output-role selection and fixed q are compile-time data;
e_i and w are never decoded into host integers or loop bounds.

The actual source is the eight-file closure in SOURCES.json, at canonical
base 20ecf2891d80b5acf18d980b2164fb44ea7faa90. Authentication checks its sealed
inventory, complete SHA256 and Git blob pins before executing any source.
The private Counter class contains the exact frozen class AST, with only
its Tape constructor bound to the single reusable blank role. The full Word,
Count, Natural, Counter, radix, Layout and Geometry methods are retained.
Only Geometry is extracted from numeric.py; native forms, source admission
and Callback are deliberately not imported or certified here.

The claim is successful valid-input source-method equivalence and an exact
source-action delta. It is not complete physical machine refinement, a full
caller/supplier admission or a multiplication exponent improvement.

## 2. Algorithm and encoded-loop proof

The old multiply_atom_power does the following for each output separately:

1. Create a Counter from e_i.
2. For each of its e_i decrements, run the complete radix_power validator.
3. On each of that validator's w yields, multiply v_i by fixed q.
4. Close the Counter and every validator temporary.

The new multi-power method first constructs and immediately closes a Counter
for each e_i, using only its finished Boolean to select zero versus positive.
If all are zero it returns, matching the old absence of a radix traversal.
Otherwise it runs one complete radix_power. At each yield it independently
counts down every positive e_i and multiplies its v_i by q once per decrement.
The new iteration order is radix digit, output role, atom. The former order
was output role, atom, radix digit.

Each v_i is multiplied by q exactly w*e_i times in either word. These
multiplications commute, touch no other v_j, and leave each Count head
canonical. Therefore the exact result is v_i*q^(w*e_i)=v_i*A^(e_i).
For each individual output, its sequence of Count values and Count primitive
operations is identical, even though operations on different outputs are
interleaved differently. Thus all Count multiplication work is unchanged.
The source radix validator is exhausted exactly once if any exponent is
positive; its prime-power checks and final cleanup remain active.

Counter construction copies the complete encoded Word, including padding;
decrement uses a finite borrow flag; multiplication by q uses a carry bounded
in terms of fixed q. The active-role list has at most three entries. There
is no numerical-width-dependent control table or cached host value of w/e_i.

After each Counter.close, the canonical body and every previously visited
body cell of its role are blank. Initially the role is blank. By induction
the next exact Counter constructor sees the same empty entrance as the
original Tape constructor supplied. Old erased suffix cells remain charged
backing. The one-role reuse is therefore an explicit sequential lifecycle,
not a sum-of-live-sizes claim that forgets retained cells.

## 3. Exact counter tariff

Vectors below are `(reads,writes,unit moves)` in one source-action lane.
Let b=bitlength(e), z=I-b. Counter construction reads the I-bit input once
through its full source loops and trims high zero digits. Its record invoice is

```
J(0,I) = (2I+5, 3I+3, 4I+8),
J(e,I) = (2I+3, I+1+2z, 2I+4+2z),  e>0.
```

The input Word copy has the separate **index** invoice

`C(I) = (3I+3, 0, 2I+4)`.

For example, the initial rewind reads LEFT and moves twice. The I digit
iterations read the Word twice per digit and move once, the terminating
RIGHT test reads once, and the final rewind reads I+1 cells and moves I+2.
No numerical Word writes are omitted.

Closing a positive, not-yet-consumed Counter with B=bitlength(e) costs
`(2B+5,B+1,2B+6)` record actions. For zero use B=1. Define

`P(e,I) = J(e,I) + (2 max(1,b)+5, max(1,b)+1, 2 max(1,b)+6)`

as the complete probe constructor/close invoice. A fully consumed Counter
ends as ZERO,RIGHT; its close costs `(7,2,8)`.

For a decrement from k>0, let t be the number of trailing zero bits.

| k class | Record decrement invoice |
| --- | --- |
| k=1 | (6,4,8) |
| k=2^j, j>=1, B=j+1 | (2B+3,B+2,2B+4) |
| otherwise | (2t+5,t+1,2t+4) |

Since `sum_(k=1)^e v2(k)=e-popcount(e)`, summing these classes gives

`D(e)=(7e-2popcount(e)+1, 2e-popcount(e)+2b+1, 6e-2popcount(e)+2b+2)`.

The complete rundown tariff is `R(0,I)=P(0,I)` and, for e>0,
`R(e,I)=J(e,I)+D(e)+(7,2,8)`. The independent checker instead sums the
individual decrement cases, importing neither this closed-form implementation
nor the primary/runtime code. The control suite additionally compares both
formulas with the real source Counter at 26 zero/power-of-two/neighbor cases.

## 4. Complete source-action difference

Let E=sum e_i, k be the number of positive exponents, and rho the complete
residue-Word invoice of one source radix_power validator at the actual
modulus and Word width. Put u=1 if k>0, otherwise 0. Old-minus-new differences are

```
residue:  (E-u) rho,
index:    -w*k*C(I),
record:   sum_i R(e_i,I) - sum_i P(e_i,I) - w*sum_(e_i>0) R(e_i,I).
```

The old implementation has one Counter per exponent and E radix traversals.
The new method has all probes plus w rundowns per positive exponent, sharing
one radix traversal. All output Count operations cancel from the difference.
These equations include every additional probe, index copy, countdown and
clear; negative lanes are retained. The verifier meters rho independently
outside the compared interval, with every validator allocation and cleanup.
Its value is not supplied by a presumed O(1) arithmetic primitive.

This is not a universal cost improvement. With one exponent e=1,w=1, both
methods have one radix traversal and one rundown, while the new one adds a
probe and index copy. The complete same-output losing control executes both.
Use the exact formula to establish affordability at a proposed source site;
any runtime selector or new parameter guard has its own implementation cost.

## 5. Actual Layout.child_extents integration

For parent width n, f=floor(n/64), delta=n-64f, define the unchanged physical
embedding phi(x)=x for x<64f and phi(x)=x+2delta otherwise. For child starts
a=phi(first), b=phi(second), width c, the method validates c>0, disjointness,
body bounds, physical contiguity of both complete chunks, and that no chunk
crosses the original external gap. It then forms powers with exponents

`e=(a, b-a-c, 2n-b-c)`.

Before the gap factor is installed, the three Counts are
`(B*A^e0, A^e1, S*A^e2)`. Exactly one receives G: the first if a>=n, the
last if b+c<=n, otherwise the middle. Consequently

`B' G' S' A^(2c) = B G S A^(2n)`.

More strongly, the unchanged phi and complete source guards preserve the
ordered three spectator regions, not merely their volume. Returned Counts
retain the source's one-high-zero marginal format and canonical heads.

The adapter authenticates the complete Layout source and rewrites only its
three power-call expressions. The first two become deferred no-ops; the third
invokes the shared method on all three output/exponent pairs. All exponents
and output Counts are live at that point, before any gap multiplication or
release. Their intervening arithmetic depends only on geometry, not on the
Count values. It is therefore legal to defer the first two updates. Every
other statement, rejection guard, marginal conversion and finally cleanup
remains from the exact frozen method. The rewrite fails unless it finds the
expected three complete argument lists in source order.

## 6. Measured interval and completed coverage

Each comparison starts with the same canonical borrowed size/depth/child
Words, modulus/Ring, before/gap/suffix Counts, templates and unused spectator
Word. It includes the encoded size/64 division, real Geometry and Layout
construction, fields=depth+1, complete child_extents, marginal output disposal,
and geometry/field/column cleanup. Both variants preserve every borrowed byte,
head and live numerical owner; all newly created record and numerical backing
is erased. The observer checks full serialization without influencing runtime
control, and Word.inspect raises during the measured computation.

Fifteen pairs cover good, across-bank unit, head/tail pair and head/tail half
geometry at w=1 and3; a width 70 internal-child geometry; q=5 and an even-column
case; and the no-remainder/rank 42 boundary. OS seed 4 selects the nonunit
spectators. These are admissible geometry instances, not claims of literal
top-level reachability of every chosen current native source or of a complete
selected GL64 payload. q=3/5 fixtures do not instantiate the asymptotic large-q
supplier hypothesis. The identity/cost equations are uniform on their stated
valid-input domain; finite timings are additional observations only.

The named pairs save between about 28.49% and59.20% of complete source actions.
The width 70 pair is7,046,111→5,038,964 (28.49%). Each tested pair has the same
additional per-bank numerical peaks (index 21,residue 6). This does not prove
a complete joint physical reserve. Counter-role backing and all other newly
created source record backing are retained in the receipts, including erased
cells. No arbitrary dirty array is silently cleared or acquired.

## 7. Remaining boundaries and failure scope

The action units are retained source Tape/Word reads, writes and unit moves.
Python execution times in TIMINGS.json are single same-input observations;
there is no claimed physical-step tariff, stable wall-clock speedup or optimality.
The loop/control compiler, finite-q source setup, actual allocator and original
root-width stock retain their own costs. A supplied blank record role is not
a free dirty register. Malformed modulus contexts still reject, but the source
validator can retain its failing quotient/remainder, and loop interchange can
change partial outputs before rejection. Full malformed-input/interrupt rollback
is outside the successful admitted-input equivalence.

This fills the encoded atom-power/child-geometry component left separate by
PR4025/4062. Context/directory/admission composition, source-bound whole payload
handoff, coefficients, native routing, copied state, physical lifetime maxima,
precision and full supplier admission remain separate. No κ is inferred.

Credit: Jose Manuel/jmbarrancoml, David Arias/PR2753, ywz65/PR2590,
ToikY/PR4025, Chris R/Clear1nsight/PR4062 and the retained source/record/caller
lineage. Tekalign (`tekuuu`) with substantial OpenAI Codex assistance;
Apache-2.0. Frozen inputs are unchanged.
