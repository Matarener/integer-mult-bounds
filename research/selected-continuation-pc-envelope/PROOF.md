# Source-derived continuation bounds and their admission boundary

## 1. Exact proposition and source instance

Fix the PR2753/PR589 **historical source-selected** caller at base
32890bc5de034ab8fc93ac88ead7279a6a416d04, prime q=213·2^80+1 and dimension64.
Its unchanged `SelectedTopology`, `Catalogue.low_classes`, `SelectedBinding`,
`Specifications.plan`, `compile_plan`, `Cursor` and `compile_node` are the
source interface. Assume admitted mathematical inputs and successful individual
plan construction, including the inherited chart/denominator and prime premises.
Let N be the length of the finite mathematical instruction sequence specified
by the `compile_node` loops in selected mode0. This does not assume CPython can
materialize that sequence as a tuple; the host-length obstruction below shows
why it cannot. There are no axis-specialized residuals in this binding. Plans
and code remain immutable during the run.

Put G=product_(i=0..63)(q^64-q^i). Then

    L = 12,295,296 G + 78,175 <= N
      <= 59,884,739,136 G + 78,175 = U.                 (1)

The exact minimal binary width for a label in [0,N) therefore lies between
359,385 and359,398 bits. The upper endpoint is a safe continuation field width;
it is not a certificate of an instruction-index provider. This result does
not describe PR5413's changed supplier, alter the selected result, or establish
that the historical loader admits the current selected record. The historical
loader's compatibility guard is neither bypassed nor modified. We execute
pinned source definitions/statements without claiming loader activation.

## 2. A uniform residual bound from the actual fallback compiler

For an admitted dimension d and residual rank 1<=r<d<=64, the good Cursor
emits exactly three blocks irrespective of the good plan's command count.
For the fallback put n=2d. The compiler first appends2(n-1) child commands;
each child contributes three Cursor blocks. Its possible terminal sign adds
one block. Gaussian elimination appends one shear for every ordered unequal
row/column pair, even when its coefficient is zero. Thus there are exactly
n(n-1)/2 lower shears and the same number of upper shears. Lower shear
compilation contributes one ADD block; upper shear compilation contributes
CHILD,ADD,CHILD, hence seven blocks. Each pivot swap contributes one child,
hence three blocks. There are s<=n-1 swaps: the last pivot cannot swap.
Consequently the **exact** fallback count is

    B = 6(n-1) + 4n(n-1) + 3s + epsilon, epsilon in{0,1}.

Both the source loop indices and child-stage weights matter; counting commands
as blocks would be wrong. At d=64 this gives 65,786<=B<=66,168, while a good
plan gives3. Thus every selected residual has between3 and66,168 blocks.
This argument is conditional only on the admitted source plan completing;
it does not reprove matrix preparation, finite-field admission or supplier
correctness. The finite checks execute the actual compile_plan and Cursor on
complete small rank-one projector sets as corroboration, not as a substitute
for the loop-count proof.

## 3. Literal outer schedule census

The declared GLOBAL-TEMPLATE has29 events:9 local sweeps,10 idles,9 bridges
and one terminal exchange. SelectedTopology fixes32 replicas,111 ports,
4 pairs and661 owners per local call. All288 literal calls have the following
local opcode counts (both forward and reverse words agree):

    MOVE0:2911, XOR1:24305, COPY2:9, ERASE3:9.

For one LOW at one call, let o be owner count and h_i the opcode counts.
The residual count is r=h_0+h_2. The non-block count is

    a=3o+1+h_1+2h_2+h_3+2r.

There are o gather_routes, o route_scatters, o+1 final clears; XOR emits one
operation, COPY emits two surrounding its residual, ERASE emits one clear,
and every residual emits its begin and end. Therefore r=2920 and a=32156.
The new checker does not instantiate a Catalogue or call a residual factory:
it reads every actual call and authenticates the source loops supporting this
census. Repeated orientation words are counted once.

Idle requests are reconstructed from the actual hosted slot occupancy and
unchanged source pending_axes function, including the zero remainder. Each
of the first nine idle stages has222 nonempty remainders; the last has zero.
This is1998 canonical idle requests, replicated32 times. Each emits five
non-block operations: gather, begin, end, scatter, clear. Thus, per LOW,

    S=288·2920+32·1998=904896 residuals,
    A=288·32156+32·1998·5=9580608 non-block operations.

The remaining operations do not depend on LOW:

    C=9·32·111·2 + 32·4·111 +29 +2 =78175.

The first terms are both directed family XORs for each bridge and the exchange;
29 checkpoints follow the schedule events, and node/return contribute2.
`Catalogue.low_classes` visits exactly G classes, by the retained GL mixed-radix
bijection. It is not instantiated or enumerated here. Hence
N=AG+C+sum B over SG residual visits, proving(1). This bounds *all* low-dependent
good/fallback choices, rather than silently assuming good plans everywhere.
The actual N and pattern of good/fallback residuals have not been computed.

## 4. Binding the source continuation field

`Machine.__init__` currently passes max(len(p.operations)) into FiniteFields.
Python len is restricted to Py_ssize_t, and L already exceeds sys.maxsize on
the tested64-bit host. A compressed instruction object with the original len
interface cannot represent this source word. This is an interface obstruction
separate from the cost of producing or retaining its instructions.

The pinned FiniteFields constructor itself accepts arbitrary positive integer
bounds and allocates max(1,(bound-1).bit_length()) bits per field. The literal
source `Machine.call` writes pc+1; `complete_return` reads it back into self.pc.
A reachable recursive call occurs at a block instruction. The final instruction
is return, so its successor satisfies0<=pc+1<N<=U. Therefore a PC field bound U
can represent every reachable source continuation. Encoding and decoding the
same fixed width are mutually inverse by the elementary binary expansion.

The checker extracts and executes those exact write/read statements, unchanged
FiniteFields, unchanged Tape and Meter. At pc=L-2 it verifies restoration of
L-1, exceeding host len bounds. This is a **header statement fixture**, not a
claim that this chosen PC is itself a recursive call site, nor a replay of
parking, numerical context, payload, or the selected full machine. Its value
is a guaranteed in-range source address and an exact codec stress case. The
reachability theorem above, not that fixture, covers actual call sites.

For total schema width H, one write, one read and one clear starting at the
canonical head use exactly6H+9 reads,2H writes and6H+12 moves in the unchanged
Tape meter. Five capacity bounds of8 and the source root/mode bounds1/2 give
H=359415 in the fixture; other arena/index capacities add their own bit widths.
Each operation's tape cost is linear in H. Host Python shifts/large accumulators
are not unit-cost runtime arithmetic: straightforward bit complexity may be
quadratic in H. The fixed-q finite-control interpretation is inherited, and
no new uniform runtime or stock tariff is inferred from a Python execution.

## 5. The explicit index-provider and malformed-state obligation

An envelope is not exact indexing. To substitute a representation in the real
Machine, an immutable provider must certify an exact count N (or an equivalent
exact valid-PC predicate), return **the original operation and Residual object**
at each0<=p<N, preserve source factory/observer traces under the agreed contract,
and account for fetch work and retained storage. Its source binding must include
all outer LOW-dependent lengths. No such full selected provider is built here.
The source runtime fetch at `operations[self.pc]` is left unchanged; no claim
that an arbitrary callable or claimed count satisfies these requirements.

There is a second necessary distinction. A FiniteFields schema with bound U
admits all labels below U, potentially including N<=p<U. Thus replacing N by U
alone does **not** preserve rejection of forged continuation labels. The theorem
covers reachable valid executions. An adapter requiring the old malformed-state
contract must separately validate decoded PCs with the exact provider domain
before any fetch or side effect. A wider bit field with only p<U is insufficient.
We deliberately do not ship a count-for-len production patch that hides this gap.

Compilation of the certificate scans the finite literal template, calls and
hosted axes, then performs64 big-integer factors for G and constant-many bound
operations. It does not visit SG factories, lows or blocks. Stored bound integers
have O(log U) bits; retained source/template data are explicitly paid. The
cardinality computation and header encode cost are not claimed constant in q
or dimension. No reduction in source matrix compilation, index queries, runtime
plan mutation checks, complete stock, tape inventory or multiplier exponent
has been established.

## 6. Provenance and next obligations

Jose Manuel's PR2753/PR589 caller, compile_plan, Cursor, codec and GL catalogue
supply the exact source. PR2234's Proth witness7 and the later physical controller
check are reused, not rediscovered. Earlier source/correspondence audits and
JoyboyBrian's PR4791/PR5495 explain the compressed-index motivation; PR5495 is
not a proof dependency. Retain all original Apache-2.0 notices. New certificate,
proof and controls: JoyboyBrian with substantial OpenAI Codex assistance.
No human or proof-kernel acceptance is asserted.

Open next questions: derive exact outer prefix lengths/indexing with its full
factory/identity observer contract; prove exact restored-PC admission for that
provider; account for the resulting header and lookup costs in the selected
loader/resource model. Start with the actual source call/return boundary,
not another synthetic huge-number roundtrip.
