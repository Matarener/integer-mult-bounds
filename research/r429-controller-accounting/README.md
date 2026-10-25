# Returned-owner costs and section limits for the coded R429 caller

The three-snapshot R429 local word saves 132 rank units, but its nine deleted
width-eight helper families return 72 units to idle work at each call. This
package reconstructs every remaining owner role and the complete paid profile:
the net saving is **60 per call**, and the known two-N terminal completion
exceeds stock by **864**. It also proves a variable-row-section obstruction for
the same alternating controller. No new supplier or kappa is claimed.

The local word is the existing [PR3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645)
construction, head `99b901c9b5ac70cf441b3d7e585cc7b8744b5359`.
Its 651-column integer/F2 identity is inherited, not re-executed here.
The new checks bind its actual literal frame and COPY events to the invoice,
reconstruct the changed physical allocation and check all its pending operators.
The 72-unit return was already noted in PR3645 and
[PR3672](https://github.com/CrocSwap/integer-mult-bounds/pull/3672);
the additional coverage here is the complete allocation, histograms,
all-exponent comparison and terminal/section boundaries.

## Exact results

With 111 ports, nine stages, 32 replicas, ambient rank 64 and stock 28,416:

| Quantity | Exact result |
| --- | ---: |
| Retained physical owner roles | 123,552 |
| Returned idle rank per replica | 648 |
| Net saving across 288 local calls | 17,280 |
| Complete pruned prefix mass | 1,791,072 |
| Known two-N terminal charge per replica | 888 rank-one children |
| Completed mass | 1,819,488 |
| Stock rank budget | 1,818,624 |
| Excess over stock | 864 |

The completed mass exceeds the **old candidate** by 11,136. That is a different
comparison from the 864 excess over stock.

For `C(a)=sum H[r]*r*(64/r)^a` and every real `a>=0`, the complete pruned
prefix is cheaper than the old profile by at least `17280*8^a`. This compares
paid child profiles whose endpoint contracts differ. The known completed
profile still satisfies `C(a)>=1819488>64*28416`. A replacement terminal
must cost at most **860 rank-one units per replica** merely to satisfy the
strict zero-exponent budget, before any other charges.

Under the stipulated ordinary-coverage ledger, `L=2B+1` stages and `n` ports
have deficit `(L-1)n-3L-2Bn=-3L`. This is an all-parameter accounting
implication, not an emitted hosted construction for every B.

For invertible matrices `A_s` agreeing with `J` outside row sets `P_s`, the
alternating endpoint `E=A_(L-1) A_(L-2)^-1 ... A_1^-1 A_0` agrees with `J`
outside their union. Actual binary `J=I+KR` has 111 zero diagonal entries.
Nine stages with at most three repaired rows therefore leave at least
**84 diagonal mismatches**. Identity closure requires at least **37 odd
stages** under that repair limit. A count of mismatched diagonals is not a
rank lower bound; the proof and checker retain an explicit counterexample.

See [PROOF.md](PROOF.md) for the exact premises and derived consequences.
The independent section review adds two precise finite consequences. The actual
scalar defect rank lies between **9 and 36**, and is exactly 9 when every stage
has the same-reader form `A_s-I=W_s R`. All **70,626** admissible three-row
sections and all 120 root return lines are checked: exactly **2,270** sections
admit a block, precisely those containing row 80, and their sole block is the
singleton mask 32. These scalar/root-line facts do not supply a native decoder
or its price. They are separate from the written arbitrary-field theorem.

## Verification and evidence

Use CPython 3.12 from the repository root:

```sh
python3.12 -B scripts/check_research_commit.py --package research/r429-controller-accounting --check-source-history
python3.12 -B scripts/research_package.py --package research/r429-controller-accounting
```

[VERIFY.json](VERIFY.json) registers explicit checks. Frozen inputs are
self-contained; [ORIGINS.json](ORIGINS.json), [FROZEN-SHA256.json](FROZEN-SHA256.json)
and [ADAPTATIONS.json](ADAPTATIONS.json) preserve original bytes and enumerate
path/receipt adapters. Authenticated source bytes are compiled with assertions
enabled, including nested imports and extracted source functions, even under
optimized parent Python. Mathematical receipts are compared in full with JSON
scalar types preserved. Only original absolute provenance paths are relocated.

The historical owner audit and complete generic code-controller replay remain
separate from two fresh independent implementations. The latter reconstruct
owner sets/histograms and binary row-section data without importing producer
code. The native remainder stage uses the retained PR2653 operator checker:
23 distinct pending factorizations, all 111 physical root lines, **326,784
ADDRESS basis columns**, and wrong-axis/missing-factor controls. It is not a
third independent implementation. The generic controller's 63 added code
factors preserve the old borrowing windows; the endpoint remains coded.

[EVIDENCE-INDEX.md](EVIDENCE-INDEX.md) maps claims to executable coverage and
inherited premises. [REVIEW-OWNER.md](REVIEW-OWNER.md),
[REVIEW-SECTIONS.md](REVIEW-SECTIONS.md) and
[REVIEW-VERIFICATION.md](REVIEW-VERIFICATION.md) preserve separate AI mathematical
and verification reviews. Finite exact computation, written all-parameter proof and formal-kernel
proof are distinct; this package supplies the first two only.

## Scope and limits

The 888 terminal and 444 FULL-gather source-ascent counts are costs of named
constructions, not lower bounds for every decoder or observer. Scalar
augmentation rank does not provide an accessible native factorization at a
hole cut. Both original-input gauges, arbitrary helper values, cleanup and
source access must be retained in any replacement.

The owner result restricts the fixed placement without repacking. The section
result assumes the alternating common-code controller and the stated row
repairs. New coverage, wider observers, different codes/controllers or changed
endpoints can change these conclusions. Native child interiors, terminal
owner allocation, source scans, rounded cleanup, precision, full storage,
fixed-tape execution and joint outer transfer remain unadmitted. No selected
frontier file is changed.

## Open next questions

Can a fully priced decoder remove the actual ordered endpoint within the
strict remaining budget? Start from its complete arbitrary-input map at the
physical hole cuts, pay both gauges and every source/output/cleanup visit,
and compare the resulting histogram. A scalar rank factor alone is not that
construction.

Can a changed controller escape the row-repair or coverage premises? State
the changed contract before searching, then bind its complete operator and
owner invoice. The 37-stage necessary condition provides no attaining caller.
[TASK.json](TASK.json) records these boundaries and the explicit assigned scope.

## Sources and credit

Scientific inputs retain base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`;
publication guidance and catalogue revision 7 are pinned at
`12fa8c5c844be21bfefb38a19503fbd867a11244` in [SOURCES.json](SOURCES.json).
The R438 word and local boundary lineage belong to Ali Romman/PR1043;
Sagar Thakrar/PR2423 supplies transport and rehosting; commdata2338/PR2653
supplies the pending-projector audit, with PR1307 geometry ancestry.
Retained source headers and manifests preserve the earlier
DreamingOfClouds/eumemic/PR589/555/543/545/510 notices.
James Reed/PR3672 independently recorded the published local arithmetic.
The source-code, pruning and recursive-audit findings here were prepared by
Ross Richardson with substantial OpenAI Codex assistance.

[RELATED-WORK.json](RELATED-WORK.json) records exact nearby heads and scope
comparisons. Live overlap coverage is a search aid, not a novelty certificate.
Separate AI review is not independent human acceptance. Apache-2.0.
