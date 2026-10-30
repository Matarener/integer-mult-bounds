# Exact readout frontier for partitioned independent walks

**Elementary scoped proof with independent finite corroboration; no new κ.**
This resolves the Q=10,11 question in Nick Petalas's
[PR #6036](https://github.com/CrocSwap/integer-mult-bounds/pull/6036) and identifies
exactly when the absolute readout floor is attained. In the five-source binary
model, allow any number k >= 2 of restored walks, independent dirt, arbitrary
repeated labels and interior zero revisits. For total query count Q, the least
sum R of even-parity readout costs over all 31 nonzero masks is:

| Q | Minimum R | Status |
|---:|---:|---|
| <7 | no covering system | rank obstruction, retained |
| 7 | 112 | retained #2779/#6036 |
| 8 | 92 | retained #2851/#6036 |
| 9 | 80 | retained #2883/#6036 |
| **10** | **72** | **new exact minimum** |
| **11** | **66** | **new exact minimum** |
| **>=12** | **62** | **new saturation threshold and extension** |

The predecessor's pair-count floor was 66 at Q=10 and 62 at Q=11, while its
best searches found 72 and 66. The [proof](PROOF.md) shows that those witnesses
are optimal. It proves sharp pair-sum bounds: eight points of F2^5 produce at
most 25 distinct nonzero pair sums, and nine points produce at most 28.
The argument uses affine relation codes, Hamming-weight counting and a
three-parallel-pair decomposition. It does not depend on the computer census.

At Q=12 one ten-label walk covers every nonzero pair sum. Inserting an existing
label distinct from both endpoints into an edge preserves support and avoids
zero edges, so the floor remains attainable at every larger Q. This closes the
readout sharpness question in this model; it neither changes the alphabet nor
prices a new physical supplier. The no-undercut tariff conclusion was already
known. Path cost X is not minimized here, and readout-optimal witnesses need
not minimize 38Q+2R+2X.

## Reproduction and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/partitioned-walk-exact-frontier/verify.py
python3.12 -I -O -W error -B research/partitioned-walk-exact-frontier/verify.py
python3.12 -B scripts/research_package.py --package research/partitioned-walk-exact-frontier
python3.12 -B scripts/check_research_commit.py --package research/partitioned-walk-exact-frontier --check-source-history
```

The verifier imports no predecessor executable and needs neither Git nor network.
VERIFY.json registers normal and optimized replays. SOURCES.json records exact
predecessor bytes as historical provenance; there are no external live inputs.

Two different finite representations corroborate the geometric bounds:

- **Point normalization.** A full-span support containing zero can take a basis
  to 1,2,4,8,16. The remaining two or three labels give just 325 and 2,600
  configurations. This is a covering family, not one representative per orbit.
  Lower-span sets have at most 15 differences. The size-eight histogram is
  {20:90, 22:160, 25:75}; size nine gives
  {21:60, 22:60, 23:810, 25:660, 27:750, 28:260}.
- **Kernel codes.** oracle.py independently represents the nonzero point columns
  by their binary relation code, and counts weight-one/two error cosets. It
  enumerates 120 and 6,435 generator-column multiplicity vectors, retaining 31
  and 827 admissible vectors. Orbit weights recover 2,430,400 and 7,689,240
  full-span point sets containing zero. Four tiny-domain literal censuses check
  the weighted counts. This oracle shares neither the point normalization nor
  the walk cost computation.

The replay also checks all query-count partitions at the boundary, literal
restored witnesses, direct even-subset readouts, support-preserving padding and
semantic failure controls. The proof establishes the unbounded-Q statement;
finite padding checks corroborate its implementation. Final coverage and a
canonical result digest are printed by the verifier.

Both registered modes passed on CPython 3.12.14 (macOS arm64), with identical
canonical reports: 2,925 normalized supports, six witnesses checked by literal
even-subset enumeration, twenty padding witnesses checked by parity dynamic
programming, and seven rejection controls. The latter reject a corrupted
histogram, a missing basis direction, incorrect claimed Q=10/11 witness costs,
a zero edge, a changed witness and relaxed per-port parity. The result SHA256
(sorted compact JSON, UTF-8) is
`b35ef32a08d40076719f57d88fb56863383667f65da7cddc01d4ec379f225b2d`.
No selected construction, native supplier, Lean or full cold replay was run.

## Scope and contribution process

Base: canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision
8, selected conditional κ=0.003125804. TASK.json retains the original
`connector-alphabet-change` card verbatim and explicitly marks the scope
**changed**: this is a released sharpness question in a fixed alphabet. The
selected-source baseline passed. The handoff's literal walk model replaces the
card's unrelated changed-alphabet experiment; no physical budget is inferred.

Family-expansion decision:

1. Sources are #6036 at `1cf36dd5f4d484a6c764f2b73f4f1e21c3eb3108`,
   Wentao Li's #2779 at `1f2a413f9e27ce9609924f7ab196548c4cbe43d8`, and the
   retained Q=8/9 packages #2851/#2883. Merged status is not mathematical acceptance.
2. Boundary is independent dirt and per-walk even parity over F2^5; no shared
   dirt, transfer-coupled schedules or same-walk replacement is covered.
3. R is an exact readout cost. Path cost is reported for witnesses but not
   optimized. Native realization, routing, restoration outside this abstract
   contract, precision, stock, compiler and outer costs are not supplied.
4. The result decides the predecessor's explicit sharpness question and first
   saturation threshold. The prior tariff obstruction is retained.
5. The paired-stage growth and chain-multiplicity handoffs require harder
   structural steps; this question admitted a short proof and a clear stop.
   A further construction round needs an actual changed caller and its full bill.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19232829)
replies to the released #6036 handoff. Live all-state PR title/body searches,
recent handoffs and the retained Q=7/8/9 notes were inspected. The overlap helper
had no remote cache and only partial local coverage in this sparse checkout;
live connector/browser checks supplied targeted coverage, not a historical
census or a novelty certificate. Existing packages and shared code are unchanged.

## Open next questions

Can a transfer-coupled or shared-dirt interface outperform its complete charged
boundary? First specify one producer/consumer, shared-prefix billing, restoration
and path costs, then compare the full tariff against the retained six-query
endpoint. The missing changed caller and complete billing contract are blockers;
this exact independent-dirt frontier does not supply them. No larger search in
the same readout model is needed to settle its query-count frontier.

## Credit

New proof and checker by **apoursh**, with substantial OpenAI Codex assistance
in derivation, implementation, independent subagent review and verification.
Apache-2.0. Nick Petalas #6036 supplies the question, pair-sum reduction,
arbitrary-label/multiple-walk extension and Q=8/9 witnesses. Wentao Li
#2779/#2851/#2883 supplies the independent-walk model and earlier exact minima;
Arham Tahir #1898 supplies the tariff. Retain their mutable-source lineage,
including Ross Richardson #943 and TennisBowling #1524. Elementary binary-code
counting is used without a worldwide-priority claim. AI-assisted review is not
independent human or proof-kernel acceptance.
