# Exact checkpoint work and lifetime backing for the R437 caller codecs

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Boundary and claim

The primary method is amortized tape complexity. The contrasting method is a
weighted depth-first pebble schedule: an ancestor's saved state remains a
weighted pebble until its child returns; a later sibling reuses the same backing
interval. This distinguishes cumulative work, current live storage, and the
union of every visited cell. No information-theoretic lower bound against other
encodings or schedules is asserted.

We analyze the **unchanged executable** `RoleParking` and `BankParking`, their
unchanged Tape/Word operations, and ywz65's unchanged parking transition table.
The source pins are the canonical files in SOURCES.json at main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. This is the codec used by
`Machine.call` / `Machine.complete_return`. The current R437/OQ4 connection is
PR3967, commit `32af060614fefa9729c86370524c2e72265acd76`, using source
`a24f9ff95c12fd0b6792e3f710569237efd72db2`. Its reported inventory is 28416
families, 660 staged roles and the 21 names in `macro_machine.NAMES`: R=29097.
We use that inventory as an explicitly attributed parameter, not a fresh replay
of the R437 compiler. The component theorem holds for every finite R.

Assume a finite, complete, well-bracketed sequence of calls. Every call first
parks exactly R distinct canonical dense roles, including empty roles, then
parks the ungranted live numerical words. It restores in the opposite order.
Bodies use the retained 12-symbol BODY alphabet, begin at position 1 after
LEFT, and have no internal BLANK or LEFT. Two numerical banks have fixed
capacities C_0,C_1 and fixed widths b_0,b_1 >= 2. Child grants are separate from
saved parent words and are cleared before restore. At cuts there are no live
scratch leases. Only these codecs access the shared stack and port; child
computation may use the same codecs recursively. Invalid or interrupted
command sequences are outside the completed-run theorem.

The theorem covers the checkpoint component, **not** functional refinement of
the residual, whole-word execution, root validity, production of descriptors or
directories, native transport, original-width stock admission, or a whole-caller
constant. Section 6 gives the exact missing join instead of assigning it zero.

## 2. Exact complete stream invoice

For one matched outer stream frame let L be the total body-symbol count and R
the number of roles. Both count empty role records. The exact sequential API
invoice, including role scans, encoding/decoding, port scans, table transitions,
all four empty-port checks, and BEGIN/END, is

| Operation | Exact count |
| --- | ---: |
| reads | 61 L + 23 R + 14 |
| writes | 26 L + 6 R + 2 |
| unit moves | 52 L + 20 R + 10 |

These are API operations, not Python wall time or a fully expanded multitape
transition count. Add `2R+2` for the same auxiliary command-dispatch convention
as PR2769. The resulting auxiliary action total is **139L+51R+28**. Fixed
finite-control role-loop bookkeeping beyond this explicitly defined measure
is not included in that exact coefficient.

Derivation, for a role of length l: its complete park/restore non-table scans
cost `(21l+9, 10l+2, 20l+12)` reads/writes/moves. In particular, park erases the
source body, restore writes the body back, and each rewind reaches LEFT. The
four-bit record has s=4l. The retained PUSH/POP table adds
`(10s+14, 4s+4, 8s+8)`. The frame's four empty-port checks contribute `(8,0,8)`;
BEGIN/END contribute `(6,2,2)`. Summing yields the displayed coefficients.
This derivation uses only a symbol loop and its boundaries, so applies to all
finite l; the finite checks do not establish it by extrapolation.

For the numerical frame, retain PR2769's proven invoice. Let p be the number
of parked (ungranted) words; B their total word-bit count;
`ell_i=max(1,ceil(log2 C_i))`; and

    S = sum over parked words in bank i of (1 + ell_i + b_i).

Its read/write/move counts are respectively

    14S+10B+32p+15,  6S+3B+8p+2,  12S+10B+30p+12.

Including one per inventory slot test and command dispatch gives
`32S+23B+72p+C_0+C_1+31`. Hence one complete paired checkpoint contributes

    checkpoint = 139L + 51R + 32S + 23B + 72p + C_0+C_1 + 59.       (1)

The numerical result is predecessor work, independently exercised here in the
combined stack. Formula (1) is additive over **every call occurrence**. A word
or parent body parked for the next sibling is paid again. The number of calls
cannot be replaced by maximum depth in a time bound.

With R=29097, even L=p=0 has a checkpoint auxiliary cost
`1484006+C_0+C_1`. This is a component calibration, not a legal zero-body
production R437 packet. At the original capacity `C_0=C_1=2^24`, the expression
is 35038438. The executable empty-body calibration uses capacity one per bank;
it does not allocate 2^25 test slots. A q-dependent constant is still real work
that must be absorbed by a valid packet-domain argument.

## 3. Weighted stack potential and exact lifetime high water

For a call v define

    A_v = 2 + R + 4L_v + p_v + S_v.                              (2)

The two F cells start the stream/numerical frames; every stream role has one R
record delimiter and 4l bits; every numerical record has one R delimiter and
s bits. At the completed park cut the parking head has advanced exactly A_v.
The code does not decode A_v into control. It is an external proof quantity.

Let `P(t)` be the sum of A_v over active parked ancestors at a completed cut.
BEGIN/PUSH only extend the current top, and POP/END only contract it. A complete
paired park increases P by A_v and matching restore decreases it by A_v.
During either operation no head exceeds the corresponding completed park top
or descends below its frame origin. The finite transition table verifies these
four local monotonicity/range statements directly. Induction over the properly
nested call word proves the invariant for arbitrary finite depth and any number
of sequential siblings.

For a nonempty complete run beginning with stack head zero, write

    P_max = max over active paths pi of sum_(v in pi) A_v,
    s_max = max(0, all stream lengths 4l, all numerical record lengths s).

The set of visited parking positions is **exactly** `[0,P_max]`; the shared
packet-port positions are **exactly** `[0,s_max+1]`. Thus their lifetime backing
requirement in tape cells is

    checkpoint backing = P_max + s_max + 3.                      (3)

We count positions reached by head movement, including the blank cell at the
stack top. The table reaches that top and the later matched restore scans it.
Each completed record also scans its port terminator and LEFT marker. Hence
these intervals have no gaps; the upper bound is attained. If the run has no
call, its supplied initialization must be counted separately. A pre-existing
opaque stack prefix is outside the owned origin and must be added separately.

After complete return the parking map is empty, but equation (3) remains
unchanged. Removing a pebble releases occupancy; it does not undo previously
visited backing. Conversely, distinct siblings reuse the same interval: their
weights contribute a maximum in (3) and a sum in (1). The 64-sibling test
separates these two aggregations, with exact primitive metering.

For a reusable dense stream role k, let m_k be its largest body length during
the **whole** run, including primitives and preparation, not just CALL cuts.
If its operations stay inside the dense prefix and adjacent blank, that role's
lifetime span is at most m_k+2 cells. Summing `m_k+2` over every permanent role
is valid even when different maxima occur at different times. Neither the
maximum live-symbol total nor the final nonblank count is automatically that
sum. The source's fixed-tape design makes the inventory finite; it does not
identify the maxima for free. Numerical banks/templates contribute at most

    (C_0+1)(b_0+2) + (C_1+1)(b_1+2),                             (4)

including erased slots. This is the retained PR2769 span bound.

A full caller certificate may therefore add (3), (4), all `m_k+2` for canonical,
scratch, handoff and protected-output tapes, borrowed input extents, and any
charged finite source tables. The machine inventory is
`R+(q^2+128)+8+1` such owned stream tapes. This is an exact interface for a
whole-caller reserve proof; it does not by itself prove a bound on their m_k.

## 4. Exact elementary preparation and return scans

The inherited `prepare_child` first computes projected extents, reads a prefix,
and produces the extended Program. It then copies eight complete capsule
bodies and copies three numerical grants. `call` transfers those bodies into
the cleared canonical roles. The following source-bound scan costs make a
specific part of preparation explicit. They exclude producing the copied data.
All source/target heads enter at position 1; the copied target is empty.

| Literal operation | reads | writes | moves |
| --- | ---: | ---: | ---: |
| capsule empty check, append_tape of l symbols, target rewind | 5l+5 | l | 4l+6 |
| transfer l symbols over an old target of length m | 5l+2m+7 | 2l+m | 4l+2m+10 |
| Arena.copy of a b-bit word | 8b+9 | 2b+1 | 8b+12 |
| header write/read/clear, H finite bits | 6H+9 | 2H | 6H+12 |

The code performs each rewind and target erasure included here. For example,
`transfer` first clears all m old target symbols, consumes all l source symbols,
and rewinds both roles. It cannot be charged only l writes. H is the sum of
fixed finite field widths, so it depends on compiled program and bank capacities,
not the runtime program-history length.

If T is the sum of the eight capsule-body lengths and the three grant widths
are b_0,b_1,b_1, the raw read/write/move action sum for these copies, subsequent
empty-target adoption, numerical grant copies, and finite-header cycle is

    21T + 18(b_0+2b_1) + 14H + 311.                            (5)

This is a distinct count convention from (1): no extra command-dispatch or
inventory-test charge occurs in these elementary primitives. It can be added
to (1) if those auxiliary charges are desired. Formula (5) includes the Program
and directory bodies **at their actual serialized lengths**. For a protected
result of length o overwriting a parent current role of length m, add
`11o+5m+17` for the actual `complete_return` transfer.

These identities follow by summing the literal Tape loops. The verifier
extracts the authenticated `append_tape` AST, whose sole external value is
BLANK; it runs the full retained implementations for transfer, Word.copy and
FiniteFields. The extraction does not execute the directory producer and is
not claimed to do so.

## 5. Chronological history is real parked and copied data

The `Program` grammar gives, including LEFT,

    P_h = 2I + L + 6 + h c,    c = Q + 2I + 90.

Here I and L are fixed index/residue widths, Q is the compiled source-code
width, and h is the number of chronological STEP records. This length identity
is predecessor work. The actual `children.extend` body rebuilds the fixed-width
ROOT, copies every old STEP byte and appends one new STEP. It does this for good,
pair and unit children, including half-width units; history is not reset by a
unit child. Therefore the produced child has exactly P_(h+1) symbols, with the
parent's body restored. The verifier executes this authenticated function body
in 20 fixture contexts, with actual Word arithmetic. Its incoming fields are
fixture objects; it does not execute Callback acceptance or validate a production
source specification. The length proof follows the literal grammar for every
admitted extension, independently of those acceptance tests.

Each canonical parent Program is among the parked roles. Along d nested calls
whose incoming history is h_0 and whose widths and vocabulary stay fixed, the
Program alone contributes exactly

    4 d (2I+L+5) + 4c [d h_0 + d(d-1)/2]                      (5a)

to the peak parking **body bits**. Its record delimiters and all other bodies
are additional. This follows by summing `4(P_(h_0+j)-1)` for j=0,...,d-1.
Hence replacing history at every level by its initial h_0 omits the quadratic
term `2c d(d-1)`. This is a lower bound on this particular codec's full parked
stack, not a universal storage lower bound or an objection to the admitted
geometric-volume absorption.

Likewise, the extended Program's capsule copy and adoption alone contribute
`21(P_(h+1)-1)` variable read/write/move actions to (5). Repeated siblings copy
and park their chronological Programs again. The root-coupled history premise
is thus needed for an actual named source term, not merely a loose big-O symbol.
The original program identity/ordinal and accepted-source contracts remain
necessary; this length calculation cannot authenticate an arbitrary history.

## 6. The remaining gamma and stock join

For a call occurrence, a transparent ledger is

    gamma_v = checkpoint_v + elementary_preparation_v
              + result_transfer_v + Pi_v.                     (6)

Pi_v is the as-yet uninstantiated cost of source-code and prefix validation,
`layout.child_extents`, `read_prefix`, `binding.child_program`, temporary-data
cleanup, closing geometry, context creation/restoration/closure, remaining
canonical/scratch boundary scans, and any producer work charged to this boundary.
The adopted child's **whole** residual computation belongs to its recursive
bill, separately. No term in Pi_v is declared zero or inferred from (1).
In particular, PARK does not produce a directory, evaluate a historical
coefficient, establish volume validity, or check original-width stock.

The retained logical ledger is

    M_j = 8 V_j + 32 Delta_j + E(V_j,h_j,L,I,Q).

Its bound `M_j < (10+2^-125)V_j` assumes minimal widths, coupled chronology,
admitted q, canonical complete directories, correct stock and the actual source
lifetime inventory. Its geometric identity `V_j=V_root/(WN)^j` also requires
complete physical prefix multiplicities and the fresh-row quotient. We retain
these premises and David Arias's credit. We do not infer their hypotheses from
our small bodies or this codec test.

A sufficient closing certificate would supply: (i) a local bound
`A_v <= a_q M_j` for each current-source call at level j; (ii) per-role bounds
`m_k <= c_(q,k) max_j M_j` including every preparation/primitive phase; and
(iii) an upper bound on Pi_v and the actual capsule lengths T. Equations (3)
and (4) then give a uniform visited-cell reserve with explicit constants; (1),
(5), (6), and the actual number of calls give its complete boundary-time charge.
This avoids both summing every sibling's storage and charging only one sibling's
work. For example, the retained good/fallback bounds of one/49911 child calls
are multiplicities for time, never additional simultaneous parked ancestors.

One contrasting encoding has a quick stop test. Suppose a replacement omits
empty roles and instead prefixes each of K nonempty records with a fixed-width
role label of g=ceil(log2 R) bits, retaining the same four-bit body encoding
and one record delimiter. Its record overhead is K(g+1), versus R here. At
R=29097, g=15, it saves this storage only for K<=1818 (strictly K<29097/16).
A production cut retaining all W=28416 nonempty family roles cannot meet that
condition: this replacement pays at least 454656 overhead cells versus 29097.
This rejects only that straightforward indexed-record design at such cuts;
bitmap, compressed-label or changed-ownership encodings need their own complete
codec proofs. No further search or new mechanism is asserted.

Until that certificate is bound to the production source, the sharp physical
reserve coefficient and complete gamma remain open. Passing the component
checks does not authorize the historical logical coefficient 11 as a physical
visited-cell coefficient. It also does not make PR3967's 46-bit controlled
packet a volume-valid `660*3^4096`-bit root. No stock-margin arithmetic or new
frontier parameter is asserted.

## 7. Evidence and attribution

The verifier authenticates all declared live source bytes, loads the five
retained component modules directly, and supplies an inert `loader.activate`
shim only to avoid activating the unrelated full compiler. No tested codec
body, table, Tape operation or Word operation is replaced. Observer subclasses
record positions but do not select controller transitions. In particular,
`parking_machine.Machine.visited` alone omits direct codec accesses; our observer
records both paths. No bytecode cache is trusted by the registered runner.

The committed receipt covers 32 deterministic randomized forests (397 complete
paired calls), 65 calls with 64 siblings, the R=29097 empty-role calibration,
18 copy/transfer length pairs, four grant widths, three header schemas, a three-grant checkpoint, and 20 literal history extensions.
All three operation counts equal the symbolic formulas; every visited set equals
the claimed interval; parent word aliases and the empty stack boundary restore.
Controls distinguish live-only storage, cumulative sibling storage and empty
role overhead, and reject an interior marker. The tests are component evidence
for the derivations, not a whole multiplier proof or independent human review.

Credit Jose Manuel / jmbarrancoml for the fixed-role physical caller and PR2769
numerical codec/invoice; ywz65 / PR2635 for the parking transition table;
David Arias / PR2753 for the logical source, inventory and conditional reserve;
Nick Petalas and retained continuation/Word/record authors. R437 applicability
retains ai-nanachi / PR3647, zxv / PR3690, Ali Romman / PR1043, Sagar Thakrar /
PR3700 and the credited selected/native lineage. PR3936, PR3950 and PR3967 are
the immediate stream audits. We add the full stream invoice, combined lifetime
high-water law, elementary preparation accounting and precise producer join.

Complementary reserve results are Nick Petalas / PR2708's route nonblank-volume
bound, Ross Richardson / PR2874's packet prefix-return backing identity, and
Kumagi / PR2882's complete packet-loop named-array maximum/private-action
interface. Live GitHub reads during this session confirmed their exact heads
2982489cc00a17bd1c7ee1e206e975eda9bcb64d,
08dd02bd8d8b1fadc5fe8589c2d2875d21fe5fce, and
02483f1b4414286b86d807bf2e8a8b9ddc7cd487 respectively. They explicitly leave
physical reuse/whole-reserve joins open. We do not reprove or import their bounds
as a completed physical m_k inventory. They are useful inputs to that next join.
