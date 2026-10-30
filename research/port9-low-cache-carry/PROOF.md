# A paid low-cache producer for the port9 column1 carry leaf

Prepared by AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
The new result is a literal tape embedding and composition. The arithmetic
frontend is JoyboyBrian's PR5332, head
`8e96c889b924957c599687be56b19fce9161cad3`,
`research/bit-low-carry-lowering/{controller.py,offset.py,PROOF.md}`.
The complete-owner rotation, cleanup and released G20 column are Ali
Romman's PR5849, head `35ee8364ccfe54d6d5ec154fbf74993624b0a0d4`,
`research/runtime-quarter-carry/`. David Arias's PR2776 supplies the
retained local tape/counter machinery. Charles Bethin, Jose Manuel,
Nick Petalas, Tekalign, ToikY and the retained G20/native/ROW lineage
keep their source attribution and notices. Neither predecessor algorithm
nor its general theorem is claimed as new.

## 1. Fixed column and supplied-input contract

Fix `q=5`, an eight-by-eight low matrix, row zero, and the actual released
port9 inverse column1 (zero-based indexing)

```text
(-1/4, 0, -1/2, 0, -1/4, 0, 0, 0)^T.
```

The integer quarter weights are therefore
`(-1,0,-2,0,-1,0,0,0)`. The pinned PR5849 route evidence supplies this
column. PR5332's decoder accepts exactly these fixed weights and selects
positions `0,...,7` from a cache of `D=64` low digits, each with `b=3`
least-significant-bit-first bits. All program construction happens before
runtime inputs arrive. The program is not compiled for a runtime carry.

The entry contract is the following 19-tape bank, up to independent
translations of tape origins.

| Tape | Entry and exit role |
| --- | --- |
| 0 | Complete Boolean owner in `[P] x [Q] x [S]` order; rotated in place |
| 4,5,7 | Preserved canonical marked binary `P,Q,S`, respectively |
| 17 | Preserved 192-bit old low-matrix cache, followed by its END marker |
| 18 | Owned blank output extent; retains the three raw bits of one new low digit |
| 9 | Owned blank temporary code extent; returns blank |
| 14 | Owned blank coefficient-descriptor tape; returns blank at its allocation origin |
| 2,3,8,10,11,12,13,15 | The generic kernel's eight private `WORK` tapes; return blank at their origins |
| 1,6,16 | Arbitrary spectators; their contents and heads are unchanged |

Here `P,S` are arbitrary positive integers and `Q` is an arbitrary
canonical odd integer at least three. Let `V=PQS` and
`L=bit_length(Q)`. The owner and marked extent inputs have the exact
PR5849 layout and their heads start on the first payload bit. Tape17's
head starts on cache bit zero; its END marker is at relative position192.
Every cache digit is supplied canonical in `{0,...,4}`. The cache is a
complete presented matrix cache, not merely the three influential digits.
The supplied blank extents and absence of overlapping owners are premises,
not facts inferred by inspecting a single blank cell.

The program validates the eight consumed cache digits and its endpoint
through the unchanged frontend. It does not validate all unconsumed cache
digits, matrix invertibility, or membership in `GL_8(F5)`. Those are separate
caller properties. The stated algebraic endpoint holds for all canonical
cache values, including ones outside that matrix group.

**Claim.** For either compile-time orientation, the composition computes
the actual column's low digit and quarter carry from this supplied cache,
performs the complete-owner permutation `x -> x +/- C mod Q`, retains
the new low digit on tape18, preserves the old cache and all borrowed
descriptors and spectators, clears tape9, tape14 and all eight kernel
work tapes, and returns every head to its entry position. It obeys the
whole composed-leaf allowances

```text
transitions <= 393V + 600L + 30000,
sum of visited tape-interval lengths <= 43V + 8L + 500.
```

These are conservative bounds, not optimality claims. The following proof
establishes the unbounded valid-input statement; finite tests corroborate
the translation, source binding and implementation.

## 2. The actual arithmetic and its finite range

Write `l_j` for digit `j` of the selected old row, and put

```text
N = -l_0 - 2*l_2 - l_4,
t = 4^-1 N mod 5,  with 0 <= t < 5,
k = (N - 4t)/5,
C = 4^-1 k mod Q,  with 0 <= C < Q.
```

Both inverse fours exist because the moduli are odd. In particular the
first inverse equals four modulo five. The definition of `t` makes `k`
an integer. The five other selected digits have zero weight but are still
read and range-checked by the frontend.

This is the high correction of the source column, not a rational-floor
approximation. Let `z` be the column's low-input product in `Z/(5Q)`,
using the modular representatives of its quarter coefficients. Then
`4z = N mod 5Q` and `z = t mod 5`, so

```text
4(z-t)/5 = (N-4t)/5 = k mod Q.
```

Consequently `(z-t)/5 = C mod Q`. Changing representatives of the
quarter coefficients changes `z` by a multiple of `5Q` and does not
change this residue. For an entire high input the familiar split is
`(l+5h)S = t + 5(hS + carry)`; the present leaf supplies only this one
inhomogeneous carry coordinate after the caller's homogeneous map.
It does not implement that homogeneous map.

Since each influential digit is in `{0,...,4}`, `-16 <= N <= 0`.
Together with `0 <= t <= 4`, integrality gives `-6 <= k <= 0`.
More explicitly let `d=l_0+2l_2+l_4=5a+r`, with `0 <= r < 5`.
Then `t=r` and `k=-a-r`. The generating polynomial

```text
(1+z+z^2+z^3+z^4)^2 (1+z^2+z^4+z^6+z^8)
```

counts the 125 influential triples by `d`. Applying the displayed map
gives the exact reachable-code multiplicities:

| k | -6 | -5 | -4 | -3 | -2 | -1 | 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| triples | 4 | 18 | 32 | 30 | 28 | 12 | 1 |

Thus all seven codes occur. At `Q=125`, their respective carries are
`61,30,124,93,62,31,0`, because `4^-1=94 mod125`.
The retained example `l=(2,3,2,1,1,1,0,0)` gives
`N=-7`, `t=2`, `k=-3`, `C=93`.

The 125 triples exhaust the arithmetic dependence of this fixed column,
not all physical cache contents or all possible owner payloads. Preservation
of irrelevant cache data and arbitrary Boolean owner contents follows
from the instruction and loop invariants below.

## 3. Literal embedding of the frozen frontend

Compile the unchanged PR5332 frontend with

```text
compile_frontend(5, (-1,0,-2,0,-1,0,0,0),
                 positions=range(8), cells=64).
```

Its five logical tapes map to physical tapes `(17,18,9,5,14)`.
Its alphabet symbols map as follows:

| Old symbol | Physical symbol |
| --- | --- |
| `None` | `BLANK` |
| `0` | `ZERO` |
| `1` | `ONE` |
| `2` (END) | `RIGHT` |
| `3` (LEFT) | `LEFT` |

Translate every old branch by this symbol map and relocate each target.
An old move or write has an explicit successor; emit the same physical
primitive followed by a `goto` to that successor. Old goto, halt and
reject instructions each require one physical instruction, with a linked
halt becoming a goto to the next component. This translation changes no
branch predicate, written symbol, head displacement or execution order.
Induction on the old instructions proves equal tape contents and relative
heads at each translated instruction boundary. One old transition takes
at most two physical transitions.

There are exactly two prefix instructions: move tape14 right by one and
jump to the translated frontend entry. If its owned blank allocation
origin is `o`, the old frontend therefore enters with its descriptor
head at `o+1`. Its offset component writes LEFT one cell to the left,
at `o`, writes canonical `C+1` from `o+1`, adds RIGHT, and returns to
its first bit. This alignment is essential for the later eraser.

The unchanged decoder scans the supplied cache through relative bit192,
checks END, and returns its cache head. Its finite states accumulate
the selected digit bits. Its leaf writes literal three-bit `t` and
five-bit `k+8` values. All possible leaves and all twenty retained offset
branches are compiled before the input exists. Runtime dispatch physically
reads the five temporary code bits on tape9 and follows the corresponding
finite branch; it never asks the host to choose `k` or to calculate `C`.

The selected offset machine reads the actual marked Q on tape5 and emits
the canonical positive `C+1` descriptor. PR5332's finite transducer proof
covers arbitrary binary length for every odd `Q>=3`, including its
explicit small-modulus branches. It uses no runtime arithmetic or
computed-address instruction. The frontend then erases the five code
bits on tape9 and restores all five logical heads. Its output tape18
retains three raw bits for `t`; it is not a marked variable-length
descriptor. At this boundary tape14 is the sole head offset from the
composed entry: it is correctly on the first descriptor bit `o+1`.

## 4. Complete owner rotation and descriptor retirement

Link one unchanged generic PR5849 table of the selected orientation.
Only instruction addresses and its final continuation are relocated;
its primitive operations, branches and symbol values are retained.
This table preserves the descriptor on tape14, the P/Q/S inputs and
their heads. It never reads, writes or moves heads on tapes1,6,9,16,17,18.
Therefore the frontend's retained low output, cleared temporary tape
and preserved cache cannot be disturbed by the rotation.

The generic table physically splits each Q axis into lengths `Q-C` and
`C`, gathers complete S-bit records into its two private buckets, and
emits the segments in the rotated order for every prefix in `[P]`.
A record originally at coordinate `x` therefore moves to `x+C mod Q`
in the positive orientation; reversing the segment order realizes
`x-C mod Q`. This is a complete Boolean-stream permutation, including
arbitrary dense payloads and `C=0`. It neither inserts an extra Q axis
nor renames a separate output owner. Its retained proof establishes
that all private counters, buckets, markers and old tails are erased,
with all eight WORK heads restored.

Finally run the unchanged PR5849 `descriptor.erase` on tape14.
If `n=bit_length(C+1)`, it erases the n payload bits and the right
marker, scans back to LEFT, erases it, and returns to `o`. Since
`1 <= C+1 <= Q`, `n <= L`. The frontend's offset proof has already
cleared any provisional high descriptor tail. Thus all of tape14's
owned work is blank, not merely its final logical descriptor. No
marker or displacement is left to communicate a hidden carry to a
later caller.

Combining the three preserved interfaces proves the claimed endpoint.
Tape18 is intentionally retained as an owned new-low output. A second
full invocation requires its own valid blank-output precondition; simply
running the whole producer twice is not a bank-restoration test. The
negative rotation is the inverse permutation for this same computed
carry under the preserved old cache. It is not asserted to be the carry
of the full forward matrix route.

## 5. Whole composed-leaf cost and compilation boundary

PR5332 proves the complete frontend bounds, with all source scans,
dispatch, old code erasure and head returns included,

```text
F = 64Db + 256L + 2048 transitions,
2Db + 4L + 32 visited cells.
```

Here `D=64`, `b=3`, so `F=14336+256L` and the second expression is
`416+4L`. The translation has at most twice F transitions. Add the
two alignment/entry instructions, the generic kernel's retained
`393V` bound, and at most `8n+8 <= 8L+8` descriptor-erasure transitions.
Replacing a halt by a continuation goto costs one transition in either
representation; no extra free linker transition is assumed. Therefore

```text
T <= 2 + 2F + 393V + 8L + 8
  = 393V + 520L + 28682
  <= 393V + 600L + 30000.
```

This safely reuses the generic all-positive-extents bound even though
the narrower contract has `Q>=3`. It is a complete-leaf bound rather
than the rotation-only cost with its producer omitted.

For space, use the sum of visited intervals over all 19 tapes, including
initial head positions, markers and cells later erased. Translation
does not enlarge a logical component's tape intervals. Summing the
generic `43V` bound, the full frontend interval bound, and two extra
positions for origin alignment is conservative even where components
visit the same cells. Descriptor erasure visits only its already
constructed interval. Hence

```text
W <= 43V + (416+4L) + 2
  <= 43V + 8L + 500.
```

Arbitrary translated origins do not alter interval lengths. Untouched
spectator content is preserved; it is not counted as newly visited
storage. Neither bound asserts that every caller provides the required
blank regions or complete owner for free.

The program is finite and independent of the runtime P,Q,S, cache and
carry values. Its fixed `q,D,b`, weights, positions and orientation
permit compiling every decoder/offset branch and linking the generic
table before inputs arrive. PR5332 supplies a deliberately loose
pre-input instruction envelope `10^6 D q^2 (b+1)^2`; the embedding
uses at most twice its instruction count plus the fixed linked tables
and two entry instructions. The program table, its construction and
its storage are nonzero setup obligations. This statement does not
insert a compiler setup charge into a claimed global supplier budget.

## 6. Actual owner shape, evidence and limits

For row0/column1, the target high digit is cell1 in row-major order.
In a complete 64-coordinate high matrix owner, its actual coordinate
presentation would have

```text
P = Q,
S = Q^62 * Z_spectator,
V = Q^64 * Z_spectator.
```

The theorem accepts that presentation if supplied. Small Q125 fixtures
with `P=S=1` test the local complete-owner leaf at another valid shape;
they do not materialize the high-matrix owner above or establish that
the caller supplies its ROW heads and volumes. Additional small P/S
fixtures test interface geometry without changing that distinction.

The bounded verification plan exhausts all 125 influential low triples
through the actual compiled frontend, checks all seven reachable
codes in both orientations at Q125 in two literal interpreters, and
uses smaller moduli and nontrivial P/S fixtures for interface controls.
Full cell states, heads, transitions and visited intervals are compared.
The written frontend and segment-loop invariants, not a few payload
basis vectors, supply correctness for arbitrary canonical caches,
positive extents and Boolean payloads. Invalid selected digits and
malformed endpoints, a descriptor-origin mismatch and omitted cleanup
are discriminating controls. Final receipts record which checks ran;
this proof alone is not a claim of completed test execution.

Q1 is outside this composition because the unchanged PR5332 frontend
requires odd `Q>=3`; PR5985's separate unit-modulus bypass is not
imported. The complete per-matrix low cache and the marked owner are
supplied inputs. Cache creation, selection from the whole `T` catalogue,
whole-T staging, low-type commit and retirement, homogeneous high routing,
ROW binding, ancestor stock/P3, source construction and a favorable
complete supplier invoice remain open. Tape18's retained digit must
eventually be committed or erased by a paid caller operation.
No source/native/analytic theorem is newly admitted, none of the five
framework assumptions is discharged, and no selected-frontier or kappa
change is claimed. Independent human and formal proof-kernel acceptance
remain unclaimed.
