# Independent preimplementation mixed-width caller review

Context: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority 7, Cinna Davis's retained PR4100 CRT construction. Primary caller
code was not read before this oracle and analysis. The all-active-target
omission argument is predecessor coverage in PR4169/PR4174, not new here.

## Declared widths and literal row embedding

For a supplied global ell>=2 and each declared height h in {ell-1,ell},
the full local Beneš program has 2h-1 rows on exactly 2^h wires. For h=ell
use local row r at global row r. For h=ell-1 put it at

    e(r)=r when r<=ell-2, and e(r)=r+2 otherwise.

The omitted global rows are exactly ell-1 and ell. The map is strictly
increasing and injective into 0,...,2ell-2. Comparing the ascending and
descending portions of the universal bit sequence shows that each active
local row targets the same numerical bit as its global row. The idle rows
are identities; they must not read the nonexistent high bit of a short axis.

The global ell convention must be explicit. If it is supplied separately
and every axis is short, preserve both all-idle rows. Replacing source ell
by max(h_i) silently would alter its literal schedule and potentially its
separate guard parameters. The finite oracle's two named fixtures choose
ell=max(h_i); its row embedding is checked independently for ell=2,...,64.

## Caller correctness and reused omission argument

Fix a balanced tree level. Its nodes are disjoint. Every active target lies
in a node's right child, and every numerical shift is determined only by
that node's left-child coordinates and fixed moduli. None of those left
coordinates is an active target at this level, so all shifts remain constant
through every global row. A switch table omits its own target bit, and reads
only its own other bits plus these unchanged left controls. It consequently
omits all active target bits, and simultaneous/serial target applications
commute. This is the predecessor argument, now applied to the declared row
embedding; placement, raw macros and repair remain separate.

Completing the rows applies each axis's full declared-size modular rotation,
which fixes every target value >= its modulus at the endpoint. Intermediate
wire labels need not stay valid. Tree levels compose to the retained padded
balanced map. On globally valid tuples this equals the direct scaled-CRT
map. To invert the literal program, reverse tree levels and global rows,
using the same positive-offset tables from the current unchanged left child.
Every individual switch is an involution. No initialization of padded fields
or control values is assumed.

Two tempting lowerings are invalid. Gating each microscopic switch on current
target validity can suppress the rest of a path that temporarily enters
padded labels. Replacing the declared-size network by a minimal-width network
on low bits can move invalid labels in the larger declared field. These are
mutation counterexamples, not claims of bugs in the retained predecessors.

## Separate oracle evidence

`independent_mixed_oracle.py` uses the earlier separate FIFO Beneš compiler,
retained byte-for-byte as `independent_benes_oracle.py` and authenticated by
SHA256. It reconstructs left-child scaled CRT integers by exhaustive search,
rather than calling the retained `decode_group` or primary implementation.
An atomic numerical rotation model and the direct globally valid CRT formula
are separate endpoint references.

Before primary inspection, ordinary replay passed:

- Moduli (5,7,11,13), declared heights (3,3,4,4): all 16,384 dirty tuples,
  5,005 valid tuples, 458,752 forward/inverse global-row executions, and
  1,638,400 active-target omission comparisons.
- Moduli (5,3), declared heights (3,3): all 64 dirty tuples, 15 valid tuples,
  640 forward/inverse global-row executions and 640 omission comparisons.

Both padded endpoint maps are bijective, preserve the globally valid set,
agree with atomic rotations, and return every tuple under the literal inverse.
The first validity-gate witness is size4, s=3, c=1, x=1 with literal trace
(1,1,3,2): gated output3 differs from required2. The minimal-low-bit witness
is declared size8, s=3, c=1, x=5: wrong6 instead of fixed5.

The oracle uses host arrays, caches and brute arithmetic. It is semantic
corroboration, not a fixed-tape, full E evaluator, raw macro, native/precision,
outer multiplication theorem or new-kappa certificate. Separate-agent Codex
review is not independent human review or proof-assistant verification.

## Credit and remaining obligations

Cinna Davis supplies PR4100's CRT factorization and source networks. PR4169
and Hiroki KUMAZAKI's PR4174 retain credit for the simultaneous omission and
placement arguments. The unchanged earlier FIFO oracle supplies numerical
network semantics; no new Beneš routing mechanism is claimed.

Remaining work includes the complete E evaluator, production reservoir and
exception classification, ordinary callee, raw compact macro/repair tariff,
and full numerical/native/outer theorem integration. Selected-frontier
certification remains outside scope.
