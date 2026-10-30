# Source-specific finite-control admission of the pooled machine

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Jose Manuel authored the retained physical controller, parking,
T74 compiler, actual-width root and primitive source, with the contributors
credited in their unchanged notices. This note supplies a source-specific
control-lowering argument, not authorship of those components.

## Statement and exact premise cut

Fix the exact pooled source at PR4270 head
`a929a3fa36301bdfcffe82afd37434dd9e3c4887` and canonical source
`12fa8c5c844be21bfefb38a19503fbd867a11244`. Apply the source-specific
[native theorem](NATIVE-ADMISSION.md) and [whole-call hosting theorem](HOSTING-ADMISSION.md)
to identify its complete groups. Retain only these earlier component contracts
at their stated complete-record interfaces:

1. the completed ordinary B1 endpoint and tariff `tau=332353/332929`;
2. the completed Compact/monomial, signed scalar and Gaussian leaf algorithms,
   including their exact-word/grid and return bills, and the single existing
   `gaussian-normalization-stream/normalizer.py` primitive described below;
3. their fixed preallocated scratch inventories and compositional ownership
   contracts. These contracts include all copies and final head returns.

Then the *new pooled source-specific dispatcher, Count planning, bank access,
private release, recursive continuation and root wiring* admit a fixed
finite-tape controller. They require no further assumption called `U(S1)`,
no unbounded host integer selector, free seek or host recursive continuation.
The construction has precisely the complete endpoint and cost of the source
program under those component contracts. On the complete root domain in
PR4270 PHYSICAL-GLOBAL it retains

```
O_(q,b,B,source)(V g^.99827 log p) time,
O_(q,b,B,source)(V)+F_q occupied and visited cells.
```

The primitive endpoint/cost theorems in items 1–3 are the remaining *named
foundational dependencies* of this statement. Source retention does not prove
all of those mathematical theorems. In particular this note does not claim a
new proof of the entire ordinary BIT backend, Gaussian analytic estimates,
or formal-kernel verification. It removes the
separate uncertainty about how the reached pooled **control and wiring** are
implemented once the declared components are available.

The initial factory constructs its tape inventory from source constants only:
`2q^2+100696842` owned tapes and the fixed borrowed input ports. Its expression
uses the fixed prime q, fixed pool capacities, rank/cover/source counts and
fixed header size; it receives no p, g, r or payload. Source compilation and
inventory construction both precede numerical input. Their enormous but finite
initialization cost and blank-origin marker writes belong to F_q/F_source.

The production observer is `None`. Instrumented Python callbacks and meter
counters are observations outside the constructed controller. All numerical
arguments are finite, valid dense binary words with their declared markers;
this is the caller ABI. No parser for an arbitrary infinite or malformed tape
is being silently supplied.

The exact root domain is `p>=2`, `1<=g<=floor(p^(997/1000))`,
`K=floor(g^(1/500))`, `0<=rho<K`, complete address/spectator/outer-row fields
and the actual r-record hypothesis below. The initial coefficients are on the
p grid in the unit disk. The zero-width identity is a separate trivial entry;
the `g^.99827` invoice is not asserted at g=0.

For finite-width internal arithmetic, a valid entry is a reachable call of
the ideal guarded root, or more generally an entry of height t whose complete
remaining prefix allowance fits the root reserve Delta. In particular a
standalone width-e node requires `t+A(e)<=Delta`, with A(e) defined in §5;
an enclosing caller additionally retains the allowance for its continuation,
reserved-axis work and final normalization. The all-prefix proof below
establishes this invariant for every call reached from the stated public-root
domain. It does not promise successful C arithmetic for every representable
h-bit dyadic word. For example, with M the largest positive h-bit signed
component, `u=M-iM`, `v=M+iM` can have a C component equal to2M, which overflows
that width. The native theorem is an arbitrary-input identity over Q(i);
its fixed-width implementation is restricted by the height/division reserve.

## 1. Literal tape actions and their representation

The reached `records.Tape` is retained from the exact nested PR3087 source
chain in MACHINE-PINS. Its alphabet is `{0,...,13}`, with `LEFT=2`, `RIGHT=3`
and `BLANK=4`. The simulator fields `cells` and `head` describe the physical
tape and head; they are not services available to the higher controller.

Map its finite byte array followed by implicit blanks to a semi-infinite tape,
and map its `head` to the physical head. `read`, `write(s)` and `step(±1)` are
respectively one-symbol observation, one-symbol write and one unit head move.
An array extension by blank cells in `write` represents blanks which already
exist on the physical tape; it is not an extra physical allocation or a seek.
For valid executions no move crosses the left boundary. Bisimulation follows
by induction on these three actions, for every finite tape function and head.
Meter updates may be erased because no production glue branch reads them.

`rewind` moves left one cell at a time until it *reads LEFT*, then moves right
once. `clear` rewinds, erases each body symbol until it reads BLANK, and rewinds
again. Thus neither knows a decoded head coordinate or length. Markers are
physical symbols. Their return positions, probes and erasure are paid.

Machine-owned body words exclude LEFT and BLANK. Gaussian packets contain
binary digits; Count words add RIGHT; continuation bodies use their stated
record symbols. At scope cuts an owned erased marker is rearmed by `origin`,
`arm_empty` or the component's `_rearm` before any marker-seeking rewind.
`enter_child` rearms every parked role; `return_node` rearms and clears them
before restoring an ancestor. This explains why a blank leased marker is not
mistaken for a canonical initialized tape.

## 2. The compilation rule

A control variable ranges over a fixed finite set determined by this source.
A numerical variable is a reference to one of the preallocated physical Tape
roles, or an alias to a Count stored on such a role. A branch may inspect a
symbol, a finite control value or an encoded-comparison result. A repetition
is either over a source-fixed finite set, or a loop implemented by Tape/Count
operations. It may not decode a numerical value to choose a host array index,
allocate a tape or invoke an unbounded host recursion.

For this language a controller is constructed as follows. Specialize every
finite control variable and fixed role selection to states, replace each
Tape action by its literal transition, and connect the finite entry/return
states of the named component subroutines. Expand a source-fixed loop, or
compile its finite loop counter to states. Keep an encoded loop as a backward
edge whose test and update are actual tape subroutines. Inline finite-depth
ordinary function calls. Keep the source's numerical recursion only in the
explicit continuation tape described below.

This is a constructive algorithm for a finite transition table. The finite
sets can be enormous; no practical compilation bound is claimed. Its startup
work and tables depend on the fixed source and q, not p, g or a numerical
payload. Charge that fixed compilation separately as F_source/F_q. This is
not advice depending on input length.

The proof is structural induction on the above statements, together with the
literal tape bisimulation. Every segment has the same observations, writes,
head moves and numerical result as the source. Its transition count is at
most a source-dependent constant times the paid primitive transition count
plus the stated setup. The constant is independent of every numerical input.

Python allocation of temporary wrappers is erased by this compilation. The
live wrappers have a fixed number of lexical registers and fixed role-pool
slots. `ScratchPool` selects the least unused slot from a fixed finite set.
Alias and stale-lease identity can therefore be represented by a finite
alias graph on those registers and slots, with closed unreachable wrappers
reclaimed. No unbounded allocation-generation number is required. The new
glue has no growing list of numerical objects; its `owned` planning list and
argument tuples have source-fixed lengths. The component contracts retain
the corresponding bounded-live-object obligation inside the old primitives.

The runtime source is checked as an exact body, not accepted merely because a
Python class has a plausible name. `machine_admission.py` authenticates the
53-file closure, rederives its nested primitive members, classifies the exact
runtime methods, and rejects the principal forbidden lowering operations.
The written induction, not those finite syntax checks alone, proves the
all-input compilation rule.

### Elementary Count and pool lowering

These operations do not introduce a generalized numerical-oracle premise.
The retained `cardinality.Natural`, `counts.Count`, `cardinal_counts.Count`,
`encoded` and `compact_counts` source bodies operate on canonical binary
words, least significant digit first, followed by RIGHT. After k digit steps,
addition satisfies

```
low_k(a)+low_k(b)=low_k(result)+2^k carry,
```

with carry in `{0,1}`. Subtraction has the corresponding borrow in `{0,1}`.
`multiply_small(c)` has carry in `{0,...,c-1}` for its fixed source constant
c. `divide_small(c)` reads the digits in reverse and maintains prefix
`P=cQ+remainder`, `0<=remainder<c`. Normalization removes only leading zero
digits and writes the canonical single zero word when needed. All exit paths
seek the marker; none receives a decoded tape position.

The unbounded product is the literal MSB-first Horner recurrence
`result=2 result+bit*factor`. General division maintains `prefix=dQ+R`,
`0<=R<d`: after the next input digit it doubles Q and R, adds that digit,
and subtracts d once if necessary. Comparison keeps only the last unequal
digit until the length markers are reached. Its order variable has three
states. These invariants prove exactness by induction on scanned digits.
They also prove termination because the source cursor crosses one finite
word once; the nested addition/subtraction scans are over finite words.

`Counter` stores its full remaining value on tape and only its finished flag
in control. In decrement, the maximal low-zero run becomes ones and the next
one becomes zero, with the highest zero removed. It therefore subtracts
exactly one. Charging one unit to each bit flip and each corresponding
outward/return move gives O(n+log(n+1)) actions for a complete countdown from
n, including construction and erasure. `power_two(k)` performs k counted
doublings and produces an explicitly stored k+1-bit word. This cost is paid
by that word, not by the bit length of k.

`fixed_power` has a source-fixed exponent. Its capped multiplication returns
`min(cap,a*b)` because factors are nonnegative; the cap shortcut is used only
when the other factor is positive. `atom_width` keeps the least satisfying
root in `[low,high]` and replaces that interval by the appropriate integer
half. The interval strictly shrinks. For `floor_power`, cap=target+1 preserves
strict overshoot, so subtracting one from the least upper root gives the
floor only when required. Thus the root plan uses polynomially many digit
operations on its explicitly produced descriptor words. On the admitted
root domain those words have O(p) digits.

The elementary routines retain at most a fixed number of current operands,
one next value and their counters; predecessors close before the next loop
iteration. `ActiveWidthPlan.owned` only receives the fixed expression results
and the two source-fixed branches. Its sole numerical repetition multiplies
the existing `stock` word and decrements the existing counter, without
appending wrappers. A finite list of these live aliases suffices.
More concretely, counting both root branches and expanding the two four-name
loops gives at most54 retained `keep`/`literal`/`plus`/`times`/`scaled` results.
The deepest elementary chain, `floor_power -> atom_width/fixed_power -> product
-> Count.product -> add`, needs fewer than16 additional operand/counter roles:
at most four root/bisection words, two power words and four Horner/add words
at once. Literal construction needs two, and encoded division needs four.
Thus fewer than70 slots suffice for planning, inside its actual256-slot pool.
None of these counts depends on a descriptor's numerical value.

`ScratchPool.acquire` scans a fixed list of slots and tests its finite live
ownership map. Its physical `empty` check reads BLANK, steps once left to
LEFT, then steps right. The lease wrapper's meter differences are observer
data and can be erased. The runtime global-namespace adaptation is specialized
once at the finite source allocation sites by the compilation rule. The
elementary Count/pool argument above proves this part of the lowering; only
the old numerical primitives retain their own stated fixed-scratch contracts.

Host type and nominal-module checks are static facts about the specialized
source, not payload tests. Completion sanity assertions may be erased only
when implied by the proved component ABI. For example the inherited ordinary
`RootSession.erase_work` compares a simulator dictionary with the two-tape
parking baseline. That equality is a consequence of its retained completed
ordinary return contract; it is not used here as a free inspection of an
unbounded physical tape. Alternatively a literal scan of the visited parking
region validates it in its paid ordinary/return bill. Neither interpretation
supplies a new pooled root or ordinary endpoint theorem.

## 3. Actual finite and encoded state

The production `Machine` has fixed mode/root flags, event, subgroup, cover,
program counter, target and child-rank selectors. The new values are bounded
by

```
events = 10802, subgroup < 322560,
cover < Gamma=|O(73,2)|,
pc < 65536, target < 731, rank < 73.
```

There are at most 31,632 instructions in an actual group, below the retained
PC bound. The header uses `1+14+19+2628+16+10+7=2695` bits. No numerical width
is written into those finite selector fields. Widths, row counts, field
lengths, precision, coefficient multiplicity and global root width remain on
Count tapes. `divide_small(73)` returns only a remainder in `{0,...,72}`;
that finite remainder is the source's left-leaf selector.

`binding.group(event,subgroup,cover)` receives only bounded labels and never
payload. The matrices have fixed dimension 73. Its rank/unrank, Gaussian
elimination, phase/recipe keys, dictionaries and instruction lists have fixed
finite domains. They can all be tabulated into control by the compilation
rule. This charges neither a variable-sized matrix nor a payload seek as a
free action. All cover labels are allowed; the statement is not an enumeration
of Gamma.

The new `ActiveWidthPlan` is reached with the actual divisor
`L=binding.families*binding.cover.size=322560 Gamma`. Its numerical operations
are Count copies, shifts, comparison, binary Horner products, long division,
fixed-exponent products and encoded root bisection. Their digit carries and
borrows are finite; the unrestricted quantities remain words. Binary Horner
multiplication and division have their standard prefix invariants. `fixed_power`
has a source-fixed exponent and capped encoded products. `coarse_depth`
strictly contracts the encoded width. All planning loops halt on valid finite
inputs and have polynomial descriptor cost; they do not enumerate the numeric
value of an exponential row count in host memory.

Only finite pool/role allocation occurs before numerical input. During entry,
`sealed_constructors` prohibits a new physical Tape or Arena. Scope activation
is a finite specialization of known allocation sites into pool leases. It can
be statically monomorphized at those source sites; namespace monkey-patching
is not an operation of the resulting machine. The ordinary backend's own
allocation/refinement claims remain in its component contract.

## 4. Complete bank access and continuation

The bank layout is
`[prefix][family][cover][unused rows][complete within-row packet]`.
`BankPackets.gather` starts at the bank marker and scans every family and
cover in order. Unselected packets are skipped by encoded Counter; selected
ones are copied to fixed local roles. `scatter` performs another full scan,
copying every unselected packet and the new selected packets into a complete
replacement. `commit` then copies that return into the owned current bank and
disposes the old local work. The borrowed original root source is not used as
a mutable bank. Heads rewind by marker search, and each return is consumed
before reuse.

Let V_node be the whole current bank. Every group therefore pays O(V_node)
for acquisition, replacement and return; its fixed source/cover multiplicity
changes only the constant. There is no per-field random access or omitted
scan in that bound. A complete child packet has volume V_node/L, including
all its spectators, arbitrary correlated data and r coefficient records.

Before descent `primitive_boundary` requires all scalar/leaf/monomial/native
scratch closed and their protected outputs consumed. The child capsule copies
only the selected packet and its encoded descriptors. It keeps component_bits,
spacing, guard and the coefficient multiplicity unchanged, changes rows to the
exact unused quotient, width to `rank*columns`, and appends the literal remaining
axes to `after`. It then writes the finite header and parks the current fixed
roles. It enters internal `node` mode, not the public disk-valued root entry.

There are 20 current/header/descriptor roles and 731 bank/private roles, hence
751 parked roles. `Parking` writes each body symbol in four binary bits, then
ROLE_END=13, and writes FRAME_END=12. Encoded bodies use only binary symbols,
so the delimiters are unambiguous. Its stack head remains at the physical top,
not at an encoded unbounded address. Restore walks backward to delimiters,
uses one reverse tape to recover the exact order, and restores roles in reverse
fixed role order. The older frame remains untouched. The two loops use marker
observations and unit moves; no frame length or stack position enters control.

If B symbols are parked, a frame stores exactly `4B+751+1` symbols. The forward
and reverse scans take O(B+751) reads, writes and moves. The header is part of B;
its 2695 bits are paid. The proof works for every finite body word and nesting
depth. The bounded exhaustive symbol tests are only controls for this written
prefix-code/stack invariant.

At return the child's output is first moved to a protected tape. Active roles
are rearmed and cleared, exactly one parent frame is restored, and the header
must identify the previous child instruction with its exact target and rank.
The complete result replaces that target; source-only group reconstruction
reinstates the bank selection. No buried ancestor is scanned during a child.
Numerical recursion uses this tape protocol and one interpreter loop, not the
Python call stack.

## 5. Halting, grid, cleanup and asymptotic payment

At an internal node `e>=73`, every child has width
`r floor(e/73)<=48 floor(e/73)<e`. There are finitely many source groups and
instructions. The encoded counters and every component halt by their contracts.
Strong induction on e therefore proves halting of every call satisfying the
guarded arithmetic ABI above; the root
flag and empty-stack check identify the genuine root halt.

First use strong induction over Q(i) to prove the ideal internal endpoint,
allowing arbitrary dirty packet correlations. A direct stopped
node uses the completed exact Gaussian leaf on its entire selected axis set.
At an internal node the remainder leaf processes `e mod73` axes, and every
rank-r call has width `r floor(e/73)<e`. Substitute its inductive exact
endpoint into the native theorem, then the hosting theorem's complete group
identity. This returns `C^(tensor e)` with all spectators, dirty helper packets
and the current complete bank in their specified positions. The physical
continuation returns implement this substitution literally. No recursive-root
refinement is a premise of the induction.

The whole common grid is expanded once at the public root. Internal capsules
retain the complete h-bit values of those guarded reachable calls, with no
unit-disk recheck and no independence assumption. They do not admit every
h-bit pattern merely because it is representable. Exact HALF/C arithmetic
uses the literal parity/headroom guards proved below; no recursive Q_p operation
is inserted. The scalar instruction program has finite literals and PCs;
private Z release calls `require_zero` on the entire extent **before** clearing
it. Leaf and normalization outputs are consumed before their owners are reused.
The root normalizes once and truncates once. This proof preserves each actual
cleanup, source and head-return contract instead of deleting it at an abstract
call boundary.

### All-prefix denominator and magnitude bound

Use the ideal well-founded rational procedure first, with the exact group
endpoints from the companion proofs, then simulate it on integer words. This
order avoids assuming the grid correctness that is being proved. Define
height t by

```
z in 2^-(p+t) Z[i], |z|<=2^t.
```

All entries and program points below refer either to this ideal computation
or to its guarded physical simulation. The ideal linear identities continue
to hold outside this height domain, but physical success is not asserted
there.

The retained all-prefix argument is in
`selected-complex-layer-closure/PROOF.md` §6, frozen here byte-for-byte.
Its instantiation for the actual pooled rank mass is
`complex-pooled-full-admission/PHYSICAL-GLOBAL.md`, lines216–233; the exact
integer guard is recomputed in `physical_global_bridge.rate_certificate`.
Here is that induction with its meanings made explicit. A completed
`C^(tensor u)` or inverse has dyadic denominator dividing `2^u` and absolute
row sum at most `2^u`; it raises incoming height by at most u. At every
depth-first program point previous children are complete, so only their
completed widths contribute. The entire mass per cover is 23,431,680. Set

```
s=23431680 Gamma, E=2^100000, B0=s+E, C0=2^210000.
```

The finite full-source allowance is bounded by
`groups*(maximum_group+1)*10*Gamma<E`, with maximum_group=31632. It covers
every scalar recipe's internal prefix (denominator at most8 and row L1 at
most9), all common-view adapters and literal incidentals. Monomial phases,
copying, checking zeros and moving banks raise no numerical height. A direct
leaf has additional height at most8e: each of its e elementary C axes has a
four-input signed numerator, one exact half and unit phases, so even its
uncompleted numerator prefixes fit that allowance. If A(e) bounds additional
height at every interpreted coefficient point, including a pending child,

```
A(e)<=8e                         (direct leaf),
A(e)<=A(48f)+s f+E               (internal node, f=floor(e/73)>=1).
```

The exact inequalities `2B0(73-48)>=s+E` and `E<=Ef` imply by induction
`A(e)<=2B0 e`. This covers parked parent values because they occur at prior
program points. The reserved-axis leaves, root phases and final normalization
add at most18g in total. The checked inequalities

```
32*73*B0^2<C0, 2B0+18<C0
```

therefore give `A_layer<(C0 g)=Delta` at every relevant prefix.

This is also the domain argument needed by the physical induction. If the
node enters at height t, its direct-leaf or internal prefix envelope gives
height at most `t+A(e)` throughout that node. Before a child, the actual
previous-child widths and scalar-prefix charges have already been included
in its incoming t; its further allowance is the recursive A term, not a reset
to unit height. The same prefix envelope retains all unfinished ancestor
continuations, and the separate18g charge covers the public root's remaining
reserved leaves and normalization. Thus the root proof bounds the entire
continuation, including those caller/root tails, by Delta. Its initial height
is zero. This proves that every reached child has the necessary division
and magnitude reserve; it is not an extra arbitrary-internal-input premise.

Set the physical grid to `2^-(p+Delta)` and word width to
`h=p+2Delta+3`. A height-t value has integer numerator divisible by
`2^(Delta-t)` and absolute numerator at most `2^(p+Delta+t)`.
Thus its numerator lies strictly inside the h-bit signed interval since
`t<=Delta` and `2^(h-1)=2^(p+2Delta+2)`. Immediately before an exact `2^k`
division the charged post-division height satisfies `t+k<=Delta`;
the discarded k bits are zero. Headroom also covers every unhalved signed
numerator prefix by the same all-prefix allowance. Consequently the ideal
rational procedure and the integer-word execution coincide at every prefix
reached from the admitted guarded root, for all recursion depths and arbitrary
correlations within that domain. More generally the same physical endpoint
induction applies to a standalone node at height t with `t+A(e)<=Delta`;
its caller must separately preserve any continuation/root-tail reserve.
Completed child
cancellation recovers divisibility on that same grid. Bit-backend internal
states are opaque bits; they are interpreted as coefficients only after
their completed permutation endpoint returns.

### Literal HALF and C-word refinement

In authenticated `scalar_words.shifted`, scalar HALF reads the low bit,
rejects a one, emits input bits1 through h-1, then repeats the input sign bit.
This is exact arithmetic division by2 on signed two's
complement words. DOUBLE writes low zero and rejects unless the two highest
input bits agree, exactly the signed headroom condition. Source rewind and
the extent-counter closure are actual finally-block tape scans.

In authenticated `signed_linear.linear_word`, for the fixed two- or four-input
sign rows the digit recurrence is

```
sum_j signs_j low_k(x_j)=sum_(i<k) digit_i 2^i +2^k carry_k.
```

The carry set `{-1,0,1,2}` is closed. In a C row its first output digit must
be zero before it is discarded. The routine emits the next h digits using
input sign extension, and checks the next digit against the output sign.
A four-input numerator divided by2 needs at most h+1 signed bits, so this
last comparison is precisely representability in h bits. An aligned two-input
sum has the same one-extra-bit bound. Induction proves exact signed output,
and the finally block restores all borrowed source heads. The grid result
above makes every exactness and headroom check succeed on the valid recursive
domain just specified. The finite signed-word checks also exercise rejection
outside that domain; representability alone is not its admission condition.
There is no HALF oracle or free real-number operation at this cut.

The single normalization primitive is specifically
`gaussian-normalization-stream/normalizer.py` with the retained proof
`gaussian-normalization-stream/PROOF.md`, “Exact signed transducer” and
“Complete cost and storage”. Its contract is encoded h>=2, N>=1, 0<=D<=h;
it returns exact `((1-i)/2)^D z` on an integral common grid, preserves source
and descriptors, returns heads, and erases its ten fixed scratch roles and
work markers. Its complete tariff is O(2hN), including caller return copy.
Here D=g<=h and common-grid divisibility has just been proved. No pooled
root endpoint or recursive implementation is hidden in that primitive contract.

For completeness, `grid_boundary.GridBoundary.expand` appends Delta low
zeros and Delta+1 high sign bits to every p+2-bit component. Its stored integer
therefore becomes `2^Delta` times the original integer, on the new grid, and
the value is unchanged. Every component and Gaussian record is traversed by
its encoded countdown. After the exact internal endpoint the source executes
`S_g`, `C^(tensor g)`, `S_g`, then `b^g`, where
`b=(1-i)/2` and S is diagonal `(1,i)` on the selected bit. The unary identity
`b S C S=[[1,1],[1,-1]]/2` proves the root endpoint by tensoring, including
the scalar b^g. Reserved leaves and restored row padding are part of this
same C tensor, by the internal/group endpoint above; their zero rows remain
zero by linearity and are checked before deletion.

Finally `GridBoundary._truncated_component` records the OR of the discarded
Delta bits and copies the signed quotient. It increments that quotient only
when its sign is negative and the discarded OR is one, before checking the
final output sign-extension bits. For signed integer n this is exactly
truncation of `n/2^Delta` toward zero, including a quotient of -1 rounding to
zero. No recursive entry truncates. H0 has absolute row sum one, so the ideal
output is in the unit disk. Componentwise truncation decreases absolute
component values and has error less than2^-p per component, giving error
less than `sqrt(2) 2^-p` and a unit-disk output. The p+2-bit result has ample
signed headroom for components in [-1,1]. The grid scans, sticky/sign/carry
flags, return copy and erasure are all literal O(V) operations with the fixed
sixteen-role pool, independent of recursion depth.

On the admitted root family, descriptor lengths are O(p), h=O(p), and actual
r satisfies `r>=2^(b(log2 p)^2)` with fixed b>0. For every fixed k,
`p^k/r<=2^(k^2/(4b))`. Hence the finite source's polynomial Count, planner,
validation and per-record setup is paid uniformly by the complete records.
The completed local primitive bills and all bank/stack scans yield exactly

```
O(V_node ((e log p)^tau+1)), tau=332353/332929.
```

No coefficient record is invented from a coarse label. The new controller
adds no positive-rank child. Thus PR4270's complete rank histogram and strict
moment remain unchanged, and its stopped-tree proof still gives `.99827`.
The outer proof's positive gap to `1/580` is unchanged.

At a descent, parked numerical data are at most
`4(1+731/L)V_node` plus paid metadata. Successive active volumes decrease by L,
so all parked ancestors occupy at most

```
4(1+731/L)V/(1-1/L),
```

before the fixed current/capsule/output copies. Root padding enlarges volume
by less than two; the grid enlargement is a fixed source constant. Each role's
head visits at most a constant multiple of that volume plus its own polynomial
metadata. The fixed physical inventory and the stack therefore have both
occupied and visited space O(V)+F_q. Erasing a simulator byte array does not
assert deallocation of its host backing capacity.

## 6. What has been discharged

This is an all-parameter written controller/wiring refinement for the exact
pooled source, with a constructive finite-control compilation and a complete
physical ledger. It does not depend on executing the astronomical production
q/O(73,2) instance. The finite audit checks source identity, lowering side
conditions, literal tape/parking bodies and corruption witnesses. It is not
a formal-kernel proof or a certificate accepting every inherited theorem.

There is no remaining *new pooled-controller* U(S1) premise. The separate
native and hosting obligations are proved by the companion documents and
compose through the exact interfaces above. The earlier named component
contracts and Gaussian analytic/outer-transfer estimates remain foundational
dependencies of the assembled conditional multiplication theorem. Renaming a
component contract as a checked theorem would not close a missing dependency.
