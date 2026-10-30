# A two-vertex tail envelope for five-label prefix completion

Local research prepared for SHIN09-git with substantial OpenAI Codex assistance.
Apache-2.0. No new kappa, supplier, seven-label census or maintained-engine change.

## Result

A remaining-edge distance bound can safely reject a partial singleton walk
when it can no longer supply every required pairwise XOR. Checking two future
points against their **shared** tail budget is stronger than checking their
individual reachability. [PROOF.md](PROOF.md) gives the full implication and
the explicit prefix 010201320, which passes the old controls but cannot supply
masks 20 and 28.

The pair constraint has an exact simplification: every jointly reachable
future-pair difference already equals a difference between the current endpoint
and a point that is either old or individually reachable. The final kernel
therefore needs no future-pair loop. The original ordered-route formula is
checked separately for equality on all 21,640 prefixes.

At five labels and length twelve:

| Standalone comparison traversal | Entered prefixes | Universal words |
|---|---:|---:|
| Unpruned canonical traversal | 21,640 | 828 |
| Existing remaining-label and parity-union bounds | 14,317 | 828 |
| Those bounds plus credited cap 11 | 13,990 | 828 |
| Also individual future-vertex reachability | 7,519 | 828 |
| Also the shared two-vertex tail constraint | 7,326 | 828 |
| Cheap bounds plus individual reachability, without cap 11 | 7,543 | 828 |
| Cheap bounds plus shared tail constraint, without cap 11 | 7,350 | 828 |

The two-vertex rule rejects 67 partial prefixes that pass the remaining-label,
union, cap-11 and individual-vertex tests in the full prefix domain. In the
pruned traversal this removes 193 additional entered nodes (2.57% relative to
7,519). Prefix counts are exact; they are not elapsed-time savings.

The separately implemented even-position-block oracle checks 139,954 restored
canonical words using at most five labels. It independently returns the same
3,695 simple closed words and all 828 universal words. The full witness sets
are compared and their hashes recorded. Every complete simple word is checked
at all twelve prefix depths: 44,340 completion checks, including 9,936 universal
completion checks and 2,427 distinct live prefixes.

A second trial converts possible per-class difference support into a lower
bound on final collision excess. It adds zero rejections beyond the existing
controls and the individual-vertex envelope in this complete domain. It is
retained as a negative result, not integrated into the traversal.

## Scope and decision

The core distance lemma needs a simple path, singleton coordinate steps,
a fixed closing vertex and total length, and pair-XOR universality. Its proof
does not use cap 11 or the concurrently claimed matching-capacity lemma.
Passing the bound does not construct a completion. No claim of mathematical
novelty for triangle inequalities is made.

The executable study is bounded to the five-label, length-twelve comparison
and raw controls at (3,6) and (4,8). It does not establish practical usefulness
at seven labels. The stronger predicate is sound but is not recommended for integration in its current implementation; the complete timing comparison below is negative.

## Complete runtime measurements and stop decision

TIMINGS-FINAL.json records 147 sequential fresh Python processes: 21 adjacent
blocks of seven modes, with rotating/reversed order. Startup, imports, source
reading, full traversal and output are included. No verification suite ran
concurrently. OS caches were not flushed; other host contention was uncontrolled.
These are descriptive local measurements, not timing thresholds.

| Mode | Median full process time |
|---|---:|
| Unpruned | 0.180372 s |
| Existing cheap bounds | 0.209854 s |
| Cheap bounds plus cap 11 | 0.354314 s |
| Cheap bounds plus cap 11 plus individual reachability | 0.361713 s |
| Cheap bounds plus cap 11 plus shared tail (simplified) | 0.351661 s |
| Cheap bounds plus individual reachability, no cap 11 | 0.237047 s |
| Cheap bounds plus shared tail (simplified), no cap 11 | 0.228014 s |

Without cap 11, the simplified shared-tail version takes a median paired
**9.25% more** time than the cheap bounds (faster in 1/21 pairs), **3.02% less**
than the individual-vertex version (18/21), and **27.76% more** than unpruned
traversal (0/21). The 48.66% reduction in entered nodes versus the cheap bounds
still does not pay for filtering. With cap 11 retained, the shared-tail version
saves 2.60% relative to individual reachability (18/21 faster pairs).
All 147 processes return the identical 828-word hash.

Ratios are medians of adjacent paired ratios, not ratios of separate medians.
Host speed varied across exploratory batches; only the final source-bound
within-block comparisons above support these percentages. The unpruned mode
also beats cheap rules in this tiny Python domain. That does not refute their
usefulness in other engines or dimensions. Individual reachability computes
only its needed pair support and pays no unused joint-distance work.

**Stop:** retain the simplified lemma, strict witness and negative integration
evidence. Do not patch a maintained engine or launch a larger census on this
basis. A distinct implementation must demonstrate improved complete caller
runtime before integration is justified.

## Reproduce

Python 3.12, standard library only. Download this directory, then run:

~~~sh
python -I -B verify.py
python -I -O -B verify.py
python -I -O -B test_mutations.py
python -I -B benchmark.py --pairs 21 --output NEW-TIMINGS.json
~~~

The verifier checks the complete expected receipt and source hashes. It reads
local Python source directly, without accepting existing bytecode. It changes
no files; --emit-receipt is an explicit authoring path that prints a new receipt.
Benchmarking refuses to overwrite its output. No Git, network, GPU or compiler
is needed for these direct commands.

From the repository root:

~~~sh
python -B scripts/research_package.py --package research/five-label-prefix-completion
~~~

## Overlap, provenance and credit

Base bee95ce88f9f19802f0613f92838895cd0e14a1f, priority revision 7,
selected kappa 60403/20000000. Handoff-first selection followed
[PR4992](https://github.com/CrocSwap/integer-mult-bounds/pull/4992).
The initial fresh search found Ali Romman's active
[matching-capacity claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903#discussioncomment-19139042).
This study therefore takes the separate reachable pair-support contract, with
no endpoint-degree or preserving-edge matching theorem. The complete overlap
coverage and limitations are in OVERLAP.json.

Credit Ali Romman / PR4992 for the sharp cap and current handoff; Mihir Srivastava /
PR4907 for the five-label proof and explicit partial-prefix question; Nick Petalas /
PR4894 for matching balance and / PR3005 for union support and the position-block
oracle representation. Retain Ross Richardson / PR943 for the prefix-walk model,
Nicholas Stone / PR2973 for the corrected parity boundary, unpaidmoon / PR4148
for the high-weight question, and James Reed / PR3096 for the audit lineage.

The core distance rule and both enumerators import no predecessor executable.
The final overlap comparison alone calls the unchanged PR5001 feasible_splits
function, frozen as reference5001.py with its original notice and full proof
in reference5001.md. SOURCES.json binds those bytes at the refreshed main; all
consumed runtime bytes are package-local. The rest of that verifier is not run.
The PR4992 head is an attributed cap comparison source, not a live Git dependency
or a selected-theorem endorsement.
The independently enumerated full small-domain witness set also checks the
cap-11 comparison's safety in exactly this domain. No independent human,
second-agent, or formal proof-kernel review is claimed.

## Final overlap comparison with PR5001

A 06:37 UTC refresh found PR5001 completed and retained at main
f259dabc7d70e0db8d6d36bfda888f008bbfecc1. Its source head is
fe3226ea4e36469f43c6b116c5b98cc221a9b1af. The scientific baseline and timing
sources are unchanged; this branch was advanced to the refreshed main, whose
priority revision and selected record match the starting base.

The separately transcribed matching-capacity test agrees with the author's
frozen function on all **108,195** nonempty-prefix/omitted-coordinate cases.
All actual completed-cycle splits remain admitted in 203,225 comparisons.
Every one of the **67** strict shared-tail prefixes still passes the matching
condition. Thus those cases are complementary to that exact predicate, not
rediscoveries of its rejections. This does not establish general dominance,
complete PR5001 replay, or a combined maintained-engine runtime result.
The timings above do not include the matching test.

## Open next questions

First profile a maintained small-domain caller before attempting integration:
can incremental bitsets or cached Hamming envelopes amortize the filtering
cost while retaining exact full-set equality? Stop if complete caller runtime
does not improve. A larger seven-label census needs a separate budget and is
not justified by fewer nodes in this tiny experiment.

A separate maintained-engine integration of PR5001 was claimed by JoyboyBrian
at the final refresh. This package does not enter that task. Any future joint
integration needs a pinned caller, full unchanged leaf receipts and a new
complete runtime comparison.
