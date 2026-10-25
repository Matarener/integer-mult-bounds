# Compact independent certificate for the lost-free P112 bound

**Independent verification and proof certificate; no new kappa.**

PR3625 (Matarener/Mark, with Claude assistance), frozen at
`5cc87895e86a951d43f4725b122a4bcd2675bc43`, proves that every lost-free
P112 plane-port set has at most 56 ports. This package independently recovers
that bound with **112 positive rationally weighted eight-frames**, rather than
requiring completeness of a 4,032-frame census, its 288-fold incidences, or
port transitivity. Every one of the 112 actual selected labels has exact
weighted coverage one, and the weights sum to 14. The original theorem and
family remain credited to their authors.

The primary checker parses the frozen selected archive directly and uses
integer parity. A separately authored checker uses explicit nine-component
vectors and independent dense elimination. Neither imports any predecessor
executable or the discovery program. The normal replay uses only the Python
standard library. `COVER.json` is the proof object, not a solver transcript.

## Exact statement and proof

The ambient space is **F2^9**. A port has a norm-one label q and a plane
with orthonormal basis (q,r). A set S is lost-free when q-orthogonal ports
in S have pairwise orthogonal planes. All four cross pairings are required.

For each certified orthonormal eight-frame F, the planes of S intersecting F
supply 2|S intersect F| orthonormal vectors. An orthonormal list is independent:
dot a vanishing linear combination with each list member to recover its
coefficient. Thus 2|S intersect F| <= 9, and |S intersect F| <= 4.

Write w_F for the positive rational certificate weight. Exact coverage gives

    |S| = sum_F w_F |S intersect F| <= 4 sum_F w_F = 4*14 = 56.

This is a finite source-bound certificate plus a written all-assignment
linear-algebra argument. It does not enumerate possible planes or assume
that the 112 listed frames are all the frames. It does not require a
fourteen-frame partition; PR3373 already excludes that partition. The claim
is not that 112 is a minimum certificate support or that 56 is attainable.

## Tariff audit

Retain the predecessor's **fixed** charged model C_B(s)=B+2(112-s), B=72.
Then s<=56 implies C_72(s)>=184. This exceeds the cited 164/160 incumbent
tie allowances; it is not a lower bound on every implementation's block cost.
For a changed block B, the same size bound only requires B<=52/48 to permit
a tie, or B<52/48 to permit a strict improvement. Those conditions are
necessary, not sufficient: no lost-free 56-set is constructed.

The exact arithmetic also isolates two prose discrepancies in the retained
PR3625 README. At fixed B=72, s=32 costs **232**, whereas its introduction
calls the predecessor 32-set's total 224. Its second open question says
sizes 33–36 would beat 224, but their fixed-72 costs are **230,228,226,224**;
strictly beating 224 starts at **37**. A separate block tariff could explain
a different 32-set invoice; that invoice is not established here. The source
is retained unchanged, and this finding does not invalidate its size proof.

Other thresholds at fixed B=72 are: any positive saving against 1792/9 needs
s>=49; ties at 164/160 need s>=66/68; strict inequalities need s>=67/69.
The existing 32-plane witness is independently checked algebraically, without
claiming a physical decoder or adopting its stated invoice.

## Reproduce

From canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90` plus this package:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-lost-free-fractional-cover
```

Expected markers: `PASS_P112_COMPACT_FRACTIONAL_COVER`,
`PASS_INDEPENDENT_COMPACT_FRACTIONAL_COVER`,
`PASS_COMPACT_COVER_REAL_CLI`, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
The registered commands include optimized, isolated checks. Each verifier
checks 7,168 Gram entries and all 112 rational coverage equalities.

Sixteen primary and nineteen independent mathematical/schema rejection
controls include omitted frames, wrong Gram entries, negative weights,
degenerate planes, and typed ports. The primary exact checker rejects a
weight perturbation of 2^-100. A five-port fixture on an actual certified
frame passes every q-q and q-r test and every individual Gram-I2 test but
fails r-r orthogonality; dropping that premise invalidates the dimension
argument. Five real optimized CLI faults, followed by a restored positive,
check certificate, source, witness, duplicate-JSON and false-receipt failure
paths on owned copies. Frozen inputs are never mutated.

The selected 6,095,634-byte source archive and
`research/plane-port-copy-budgets/RESULT.json` are needed outside this package
for scientific replay. The archive compressed/member hashes and the budget
file hash and cited values are checked. Retained pending source files have original head/path/blob/SHA256
records in `ORIGINS.json`; no pending Git objects or network are required.
The original 4,032-frame census, transitivity, CP-SAT <=51 evidence, full
supplier replay, native execution, proof assistant and hosted CI are separate
from this certificate. This does not improve the selected exponent.

## Discovery, overlap and credit

The repository picker drew nonce `abd26268e2352963323cb91c9c701880` once,
recursive interfaces, priority revision 6. The coverage-law card was changed
to a deliberate independent check of the fresh lost-free obstruction.
Current main, live handoffs, Discussion1587 and targeted open/historical PRs
were checked. PR3356/3373 concern disjoint packing, PR3370/3387 concern even
group/query repair, and PR2484's fractional colouring concerns a fixed plane
graph. No matching compact lost-free frame certificate surfaced; incomplete
Discussion coverage is not a novelty guarantee.

Discovery enumerated frames independently as proposals and used installed
NumPy least squares only to select support. Exact Fraction elimination then
recovered the positive rational weights; an initial approximate
rationalization was rejected and preserved. Neither enumeration completeness,
floating feasibility nor discovery software is a proof premise. The public
certificate is accepted only by exact arithmetic. No solver installation,
new dependency, or stronger-bound search was used.

Credit Matarener/Mark and Claude for PR3625's theorem; Philippe Van Velzen
for the lost-free family, witness and pricing; ctoth/Discussion1587 for the
plane-port contract; JosieElliston for the copy budgets; Sagar Thakrar/PR2484
for earlier label work; Nick Petalas/PR3356/3373, Tekalign/PR3370 and the
retained E8/native/compiler/selected-source lineage. This contribution adds
the compact cover, independent implementations and explicit arithmetic
findings. Prepared for ToikY with substantial OpenAI Codex assistance,
including separately authored AI checking and scope review. No independent
human or proof-kernel acceptance is claimed. Apache-2.0.

## Open next questions

1. Can one supply an exact certificate of a smaller universal bound, especially
   <=48, or an actual lost-free set of size >=49? Start with the precise plane
   constraints and a proof-producing method. The predecessor's solver-only
   <=51 is not certified here; this cover proves only <=56.
2. Does a real decoder have a cheaper complete block invoice? Pin its actual
   terms, ranks, physical access, dirty restoration and consumer before using
   a different B. The fixed-72 arithmetic alone does not price that program.
3. Can the cover be made simpler? A smaller denominator/support or human-readable
   symmetry orbit could improve reviewability, but no minimum is claimed and
   fourteen disjoint frames must not be searched again under the same premises.
