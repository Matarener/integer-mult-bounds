# Source-bound finite-control and invoice audit

Source: zxv PR6092, head `39df190f3a8a04cccb88ef1a6ca9aad39ed0364d`,
retained in `predecessor/` with PREDECESSOR.json byte pins. The audit accepts
its simultaneous local two-tape step convention, resident read-only program
and coin, W clean work bits, and width-dependent compiled unary word. It does
not impose an addressed-access tariff or require one width-independent word.

## Literal transition table and call boundary

Put `<` at program position0, the L instructions at positions1..L and `>`
at L+1. Entry and exit program head position is1, the first payload cell;
data head position is0. For the empty word position1 is the right marker,
and the same chronology still works. Two Boolean accumulators a,b start0.
There are four modes F, FR, I, IR. A direction request selects the entry
mode F or I; that same mode is restored at return. This is a subroutine call
boundary: the final marker transition emits return to its caller. The caller
has to invoke the next call; execution does not silently restart the word.
No extra counted instruction is hidden in that return signal.

In this table each row is one local transition, with both tape heads allowed
to move simultaneously. The program tape is never written. `action` reads
only the scanned data bit and a,b. A direction request is not a stored second
program and does not depend on W.

| Mode, scanned symbol | Data action | Program move | Next mode / return |
|---|---|---:|---|
| F, payload | apply instruction | +1 | F |
| F, `>` | none | -1 | FR |
| FR, payload | none | -1 | FR |
| FR, `<` | none | +1 | F, return |
| I, payload | none | +1 | I |
| I, `>` | none | -1 | IR |
| IR, payload | apply inverse instruction | -1 | IR |
| IR, `<` | none | +1 | I, return |

Payload actions: L/R move the data head by -1/+1 (exchange on inverse);
A/B XOR the scanned bit into a/b; X XORs1 into the scanned cell; C XORs a;
T XORs ab. All actions other than L/R are self-inverse, and the program
head motion is independent of data. `transition_table()` expands these
rules into 256 concrete rows over mode, symbol, a,b and scanned bit. Other
marker/mode pairs are undefined and rejected. The simulator's indices denote
head locations; they never select the transition rule or supply a distance.

Starting F, there are L executing payload transitions, one right-marker turn,
L return transitions and one left-marker return. Starting I, there are L
seek transitions, one right-marker turn, L inverse payload transitions and
one left-marker return. Both therefore cost 2L+2, include two marker steps,
visit program cells0..L+1 and return to1. Every transition moves the program
head exactly one cell. Data movement occurs only in the executing pass and
is exactly the number of L/R symbols. This proof is independent of L and W.

The same explicit modes return at the subroutine boundary, and the data
invariants below return a,b. This is functional invertibility at declared call
boundaries, as in the source. It does not prove injectivity of every internal
mode transition across arbitrary off-contract global configurations.

## Gate invariant and signed endpoint

For an X gate, unary walks go from home to its target and back. For CNOT,
walk home/control/target/control/home with A,C,A; its distinct control is
unchanged by C, so the second A clears a. For Toffoli the sequence is
home/control1/control2/target/control2/control1/home with A,B,T,B,A.
Distinct unchanged controls clear b and a. In all cases the resulting data
map is the corresponding gate, heads return to home and a=b=0. Reversing
any macro and inverting walks proves the identical assertion backward.
Concatenation gives the full-word invariant. This proof uses no clean-data
assumption; only accumulators start clean. All walks stay within the convex
hull of home and operands, hence inside the declared 2W+2 cells.

The source gates never target the coin. The macro's only data-write symbols
X/C/T act at the gate target; hence coin nonwriting holds at every step, not
merely at endpoints. W-1 adjacent swaps plus extraction and sign copying
use 2+3(W-1)+1=3W CNOTs to produce q=floor(x/2) and r=x mod2.
The extraction first clears x0; after swaps the top cell is zero, permitting
the old sign bit to be copied into it.

In a controlled increment c0=t and c(j+1)=c(j)*old_x(j). After
x'(j)=old_x(j) XOR c(j), the identity
c(j+1)=c(j)*(1-x'(j)) holds: it is0 if c(j)=0 and otherwise equals old_x(j).
Descending cleanup preserves each lower carry until used. Thus the work
bits clear. Positive sign sets t=r(1-u); negative sign sets t=ru, then
negates q+t by complement and a second controlled increment with t=1.
The identities are S(x,2,u)=q+r(1-u) and S(-x,2,u)=-q-ru.
The retained residue equals (sign*x) mod2 in both cases.

For W>=2, q lies in [-2^(W-2),2^(W-2)-1]; q+t lies within
[-2^(W-2),2^(W-2)], so its negation fits in W signed bits. Complement before
the final increment is a W-bit bijection, with ordinary modular increment
realizing the stated signed result on this range. This includes x=-2^(W-1),
where forming -x first would overflow: this kernel halves before negating.
Each gate is an involution, so reversing the complete clean-work execution
restores the exact initial x, residue0 and work0 without writing the coin.

A ripple increment contributes (X,C,T)=(2W-2,W,2W-2). Adding extraction,
the two t preparations/cleanups and, for negative sign, complement plus
second ripple, gives (+):(2W-2,4W+2,2W) and
(-):(5W-2,5W,4W-2), exactly the source counts.
For D=2W+1 each X/C/T macro has length at most2D+1,4D+3,6D+5;
this accounts for all traversed gaps and yields the source O(W^2) bound.
The readonly program costs L+2 cells and is reused in both directions.

## First working trace and validation boundaries

At W=2, sign+, x=-1, coin0, initial data is [1,1,0,0,0,0].
The half endpoint is [0,0,1,0,0,0] (S(-1,2,0)=0, residue1).
The frozen compiler emits L=192, hence386 transitions per direction and
194 program cells. In forward execution: positions1..192 execute, position193
turns left, positions192..1 rewind, position0 returns right to1. Inverse
has the same positions with seek first, then inverse actions. The residue
and work return to0 and x returns to-1. All this is checked by the replay.

| Obligation | Result |
|---|---|
| Width-independent local marker table and exact return invoice | Constructed and proved above; finite table executed independently |
| Gate macro accumulator cleanup, data extent, coin never written | All-address induction above; 640 finite placement/payload cases |
| Signed endpoint, residue/work restoration and extrema | Written range/ripple proof; 528 exact half round trips |
| Source counts/program hashes | Recounted and compared to retained RESULT for covered widths |
| Program preparation O(W^2 log W) and counter-space bound | Source claim retained; no literal compiler implementation audited here |
| Event52/89 historical source binding | Source statement retained; original 9,589-event source not independently replayed |
| Resident coin delivery, clean allocator, actual caller guard | Preconditions, not established by this audit |
| Complete physical caller, native errors, selected admission/kappa | Not claimed |

The five failure controls remove a marker turn, reverse inverse walks
incorrectly, retain an accumulator, omit rewind, or append a coin write.
They must fail under both ordinary and optimized Python. A passing finite
replay authenticates bytes and corroborates this contract; it is not a
formal or independent human acceptance of the all-width argument.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; source and
predecessor credit remains in README.md and the unchanged source notices.
