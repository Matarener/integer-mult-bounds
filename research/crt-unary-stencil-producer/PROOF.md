# A paid unary producer for one source guard stencil

## Claim and scope

`producer.py` gives a uniform, marker-driven tape program for the **one-target**
geometry family

    G >= 1, H >= G, K >= G+4, Y >= J+K, J >= 0, B >= 0.

Here B denotes the spectator/back-bit count, not the radix 2^G. Input is
six protected canonical unary tapes for G,H,K,Y,J,B. On successful admission
the program outputs exactly the stencil returned by the frozen predecessor
`geometry_stencil(G,H,Y,(J,),K,B)` in PR4201 at head
`4f49743a9df0cf7501cdc62bd5707a122fa071e9`.

Unlike the predecessor's host geometry adapter, the new producer pays every
read, write and one-cell head movement used to validate the unary inputs,
perform the required arithmetic, construct the stencil, clear private
workspace and return heads. The predecessor's scanner is then used without
modification. This closes only its supplied-stencil obligation for this
specific unary-encoded, one-target family. It does not produce arbitrary
binary-encoded CRT descriptors, many-target stencils, the full E evaluator,
complete physical placement, or a multiplication supplier.

## Input, machine and ownership contract

There are six fixed protected input roles. A tape of unary value n initially
has permanent LEFT, then n copies of symbol `1`, then END, with an initially
blank infinite tail. Every head enters at its unique permanent LEFT.
LEFT is reserved tape infrastructure and does not occur in input data. The
initially blank tail is part of this representation contract, rather than
a claim that a finite program decides whether an arbitrary infinite tape
is eventually blank. `validate` literally reads LEFT, every unary symbol,
END and the immediately following blank. A wrong data symbol, missing END,
or immediately nonblank END successor is rejected by paid actions.

The producer has eight fixed private unary roles and one fresh owned
stencil role: fifteen tape roles including the six inputs. It creates no
parameter-dependent array, tape family, integer register or transition
alphabet. The private roles are HG, KG, THREE, A, TAIL, JP, YJ and YJK.
They all have permanent LEFT infrastructure like the predecessor's tapes.
Each is initialized by paid actions with an empty END-terminated unary word.

The executable program reads and writes tape symbols and moves one cell at
a time. It never reads a host length, head coordinate, cell container,
action counter, G/H/K/Y/J/B integer, or source geometry table. Its tuples
are fixed role lists or fixed product-alphabet symbols. Every loop branches
on a read symbol or fixed finite control state; the five optional booleans
select named faulty programs used only by the verifier.

On success all six inputs are protected, their heads are at LEFT, every
private data cell and allocated private END marker is BLANK, every private
head is at LEFT, and the owned stencil has LEFT, L atoms, END, head LEFT.
The permanently reserved LEFT markers are not erased. Visiting the blank
cell just after an input END may extend the emulator's finite cell list;
the represented infinite protected tape is unchanged.

Grammar or arithmetic rejection happens before output generation. On these
rejections the program erases all eight private words and the empty output
word and returns every head to LEFT; input data is protected. The guarantee
assumes the input representation's unique permanent LEFT and initially
blank tail. It does not cover a broken tape primitive, an interrupted run,
or arbitrary symbols imitating the reserved boundary infrastructure.

## Paid arithmetic and admission

All successful arithmetic is performed by literal scans:

- `difference(left,right,out)` scans matching unary prefixes. It rejects
  if right is longer. Otherwise it copies the remaining suffix of left
  into out and returns all three heads. Both operands are protected.
- `plus_one` scans/copies its operand and appends one unary symbol.
- `three` writes exactly three unary symbols and END by a fixed sequence
  of actions.
- `positive` reads the first unary cell and rejects an empty word.

The resulting private words are

    HG   = H-G,
    KG   = K-G,
    THREE= 3,
    A    = K-G-3,
    TAIL = G+1,
    JP   = J+1,
    YJ   = Y-J,
    YJK  = Y-J-K.

Every subtraction is executed and its underflow test is charged. Reading
G's first cell enforces G>=1. The H-G subtraction enforces H>=G. The
K-G and then KG-3 subtractions followed by `positive(A)` enforce exactly
K>=G+4. The two Y subtractions enforce Y>=J+K. J and B are nonnegative
by their unary representation. Thus admission is implemented inside the
paid program rather than delegated to a host inequality test.

Importantly, subtraction underflow occurs before writing its output.
Therefore every allocated private word still has a complete END marker
when rejection cleanup begins. Arithmetic rejection cannot leave a
partially written unterminated scratch word for the eraser to search.

## Stencil identity for all admitted geometry

Let L=2H+Y+B. Indexing positions is used only in this written proof and in
the observer verifier, not by the executable producer. In the predecessor's
MSB-first address layout, the two H-bit digit fields precede the Y-bit
target region and B spectator bits. Its one-target stencil has the form

    S^(H-G) D^G  S^(H-G) D^G
    S^(Y-J-K)  GUARD^(K-1)  S^(J+1)  S^B.

Each D block has exactly its first/last atom marked as begin/end. The two
G-bit D intervals therefore occupy precisely the low G bits of each
H-bit digit field. Their threshold bits are both zero, as required by the
predecessor's not-all-ones digit test.

The guard begins at position 2H+Y-J-K and ends just before
2H+Y-J-1, giving exactly K-1 higher bits of the K-bit source window. The
omitted bit J is its parity bit and is part of the following J+1 SKIP
cells. The program emits these lengths from the computed unary words,
without converting an endpoint or length to a host coordinate.

For width K-1 the required thresholds are

    low  = 2^(G+1),
    high = 2^(K-1)-2^(G+1).

Put a=K-G-3. Admission gives a>=1. Their exact MSB-first bit patterns are

    low  = 0^a 1 0^(G+1),
    high = 1^a 1 0^(G+1).

The guard has a leading segment of a atoms `(low0,high1)`, one pivot
`(low1,high1)`, and a trailing segment of G+1 atoms `(low0,high0)`.
Its length is a+1+(G+1)=K-1. Begin is set only on its first leading atom;
end is set only on its last trailing atom. All other cells are the exact
predecessor SKIP atom. This proves atom-for-atom identity with the frozen
adapter for every admitted input, including G=1, H=G, K=G+4, J=0 or B=0.

The output is owned and remains available to the unchanged consumer.
Its finite product alphabet is independent of geometry; the program does
not place an unbounded integer into a tape cell or a finite control flag.

## Exact successful producer action invoice

One action is one Tape.read, Tape.write or one-cell Tape.move. Host simulator
administration and observation are outside that unit-cost model, exactly as
in the predecessor. These are literal invoked actions, not a host-computed
macro tariff substituted for unexecuted scans. For an END-terminated unary
word of value n, each macro's successful action count is:

| Macro | Entry and action count |
|---|---|
| rewind from coordinate n | 2n+1; n appears only in this proof |
| validate(n) | 4n+10 |
| difference(a,b), 0<=b<=a | 8a+15 |
| plus_one(a) | 8a+14 |
| three | 17 |
| skip/digit/leading_guard/trailing_guard(n) | 6n+5 |
| erase(n), entering at LEFT | 5n+7 |

For example, difference(a,b) performs 3a+b+8 reads, a-b+1
writes and 4a+6 moves, totaling 8a+15. The counts include operand
returns and output END. Rewind reads its final LEFT cell as well as
every visited cell on the way back.

Let N=G+H+K+Y+J+B be total unary input symbols and

    W=H+K-2G+2Y-J+2

be total private unary symbols across the eight derived words. Summing
the fixed sequence of macros gives:

| Stage | Actions |
|---|---|
| initialize nine empty words | 27 |
| validate six inputs | 4N+60 |
| all positivity/arithmetic operations | 8H+16K+16Y+130 |
| output atoms, END and output return | 8L+46 |
| erase eight private words | 5W+56 |
| final input-head checks/returns | 6 |

Thus the exact normal successful setup invoice is

    T_prod = 33H+25K+38Y-6G-J+12B+335.

Under admission K<=Y and L=2H+Y+B, so

    T_prod <= 63L+335 = O(L).

The equation is a written all-size action derivation. Primary verification
also compares observed literal counts against it on each finite case;
finite equality alone is not the proof of the equation for unbounded input.

## Exact visited-cell space and composition

This space measure counts every visited tape cell, including cells erased
at the end and owned input/output. It is stronger than merely counting
nonblank cells at the endpoint. The protected roles visit N+18 cells,
including each immediate blank after END. Private roles visit W+16 and
the stencil L+2. Therefore

    S_prod = N+W+L+36
           = 4H+2K+4Y-G+2B+38
           <= 6L+38.

The unchanged predecessor scanner adds one private counter role and one
owned BAD-mask role, reusing the produced stencil. This is seventeen
fixed roles for the composed program; no private-role reuse is claimed.
For M=2^L its separate established scanner invoice is

    T_scan = 8ML+15M+13L+18.

All producer actions precede it, including producer cleanup, so the complete
one-target producer/consumer time is exactly T_prod+T_scan, at most

    8ML+15M+76L+353 = O(ML).

Its visited cells are exactly

    S_comb = S_prod+(L+2)+(M+2)
           = M+6H+2K+5Y-G+3B+42
           <= M+7L+42.

These are counts in the explicit logical finite-alphabet cell/head model.
Encoding fixed alphabet symbols/control as bits changes them only by
parameter-independent constants. They are not Python runtime predictions
or an exact coefficient for an unspecified physical transition table.

## Evidence and controls

`primary_verify.py` imports the literal producer and authenticated frozen
predecessor machine/adapter bytes, never a `.pyc` cache. Its host integers,
list inspection and direct formulas are observer/oracle work, not paid
producer steps. It checks 145 admitted producer geometries, including a
500-bit output and zero J/B and tight admission boundaries. It compares
every emitted stencil atom with the frozen adapter, exact observed action
and space invoices, protected input, blank private data/markers and every
head return. Four compositions execute 5,760 complete addresses through the
unchanged scanner and compare every output bit with its frozen adapter
baseline and the exact unchanged scanner action invoice.

Four arithmetic failures and three malformed unary encodings must reject,
with allocated private/output data blank and all heads returned. Five
faulty programs must fail their named observations: included parity,
wrong lower pivot bit, wrong upper pivot bit, omitted private erasure and
omitted owned-stencil head return. The three semantic mutants are also
executed through the unchanged scanner and must change its actual mask.
An AST guardrail rejects producer host arithmetic, indexing, host-length
primitives and simulator observer fields; this is a review aid, not a
formal machine certificate.

Both retained consumer/adapter modules are SHA256-authenticated before
compile/exec, including an overridden consumer path. Corrupted temporary
copies containing an execution-failure marker must reject at that hash
check, before their appended marker can execute.

Independent source-predicate, cost and source-code review are separate
evidence. In particular, atom identity with a predecessor adapter and
agreement with the unchanged scanner do not alone certify the original
CRT source predicate or every inherited caller assumption.

## Attribution and remaining obligations

The source guard predicate, scan proposal and arithmetic context come from
Cinna Davis/PR4100. Hiroki KUMAZAKI/kumagi's PR4169/PR4174 supply retained
repair/placement context. PR4201 supplies the literal dense-guard consumer,
finite atom format, host adapter and scanner cost derivation; this package
adds a paid unary one-target producer, not that earlier scanner result.
Retain Douglas Colkitt/OpenAI and the inherited NOTICE lineage. Substantial
OpenAI Codex assistance was used for implementation, proof and separate
agent review. No human review or formal-kernel verification is claimed.
Apache-2.0.

## Open next questions

- Produce these unary descriptors from the actual source representation,
  with paid parsing/conversion and a legal caller contract. Unary input
  construction and binary/uniform descriptor production are not priced here.
- Extend to multiple target intervals with paid ordering, disjointness and
  correct digit ownership; this one-target program does not establish that
  wider mechanism.
- Compose the classifier with paid extraction, repair, keys, sorting,
  reinsertion, ordinary callees and full E arithmetic. Precision, native
  physical placement and the outer multiplication theorem remain open.
- No selected frontier, kappa value or full CRT supplier is changed by this
  bounded lowering result.
