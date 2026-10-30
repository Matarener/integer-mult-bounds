# Architectural κ ceilings and a price frontier for productive helpers

**The rank-eight productive-helper path is exhausted at a fixed local bill;
productive-helper recursion as a whole is not proved exhausted.** This package
turns that distinction into a usable mathematical filter for new constructions.
It supplies no new admitted κ and changes no selected result or task allocation.

The selected conditional result at canonical main
`32890bc5de034ab8fc93ac88ead7279a6a416d04` is
[PR5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413),
κ=.003027288235. The newer P104 candidates change the local paid profile, so
an old fixed-profile ceiling does not exclude them. Their strongest retained
candidate is [PR5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551),
κ=.00304153, head `1123635a6f63f23638df9459c994160e5e649d30`, still an
unselected author-checked proposal at this checkpoint.

Read [PROOF.md](PROOF.md) for the complete architecture, universal reductions,
closure theorem and rigorous numerical method; [CLAIMS.md](CLAIMS.md) for the
post-.0023 claims and their different admission boundaries. [RESULT.json](RESULT.json)
contains every exact sign, root bracket, discount interval and source-derived
histogram. Canonical provenance is in [SOURCES.json](SOURCES.json);
[ORIGINS.json](ORIGINS.json) includes the exact commit/tree/blob paths for all
retained extracts, including pending PR heads. Their offline checks need no
cached PR branch and make no publication-ancestry claim for those pending heads. [RESEARCH-CONTEXT.json](RESEARCH-CONTEXT.json) records overlap coverage
and live heads. Submitted for review as
[PR5554](https://github.com/CrocSwap/integer-mult-bounds/pull/5554);
publication does not imply scientific acceptance.

## What is actually proved

For an autonomous local provider with v ports, rank-eight fresh blocks, one
rank-one query per port, and the retained prefix/suffix idle law, **all**
controller lengths, splits and FULL/QUERY masks reduce to a strictly convex
sequence indexed only by the FULL count n. The exchange/convexity argument
extends credited [PR5405](https://github.com/CrocSwap/integer-mult-bounds/pull/5405)
and [PR5409](https://github.com/CrocSwap/integer-mult-bounds/pull/5409).
The P104 applications and the architectural per-FULL discount curve are new
results in this package, without a claim of exhaustive novelty.

The supremum of the relaxed raw moment saving lies in these intervals:

| Local contract | Supremum interval over every length/split/mask |
|---|---|
| #4610 native word | (.00302177587077, .00302177587079) |
| #5413 complete neutral signed bill | (.00302728824993, .00302728824995) |
| #5544 P104 productive word | (.00304057807630, .00304057807631) |
| #5545 P104 single contact | (.00304117181649, .00304117181650) |
| #5551 P104 coupled contacts | (.00304153116714, .00304153116715) |
| Neutral bill with all eight H8 completion calls free | (.00807671283977, .00807671283979) |

The last row is a hypothetical upper relaxation, not an attainable supplier.
The first two sharpen retained ceilings; the P104 rows extend submitted
fixed-caller crossings to this unbounded architecture. Native source validity
and the five selected framework assumptions remain inherited, not freshly replayed.

The new **price frontier** is especially useful when a local mechanism changes.
Let L(t)=sum P_r*r^t - sum H_r*r^t, t=1-C. There is an explicitly defined
geometry-only threshold lambda_8(t) such that the entire path has a favorable
raw invoice exactly when L(t)<v*lambda_8(t). Therefore a changed provider
must reduce net debt by more than min_(n>=1) C_n(t)/n. A new three-value gate
certifies that minimum over all n, with no large-controller search.

For the #5551 baseline, the necessary net saving per FULL is:

| Target C | Minimum saving per FULL, rounded down | Optimal FULL count |
|---|---:|---:|
| .0031 | .80638594481 | 18 |
| .0033 | 3.54923453123 | 17 |
| .0034 | 4.91394927369 | 16 |
| .004 | 12.96623724304 | 14 |
| .006 | 38.56153416704 | 9 |
| .01 | 85.66448729816 | 5 |

These are rank-power moment units, not scalar ADD counts or wall time.
All new repair requests reduce the net saving; compiler, BIT and outer losses
need additional margin. Even making the neutral bill's eight paid H8 jobs free
still misses .01 by more than 21.85249430914 units per FULL.

## Search directions and stopping rules

| Architectural regime | Decision justified by the proof | What reopens it |
|---|---|---|
| Same bill, different tensor depth, integer batching or funding precision | Cannot exceed its raw crossing through the stated moment-preserving compiler closure | A changed fully charged bill or a different compiler method |
| Same local provider, arbitrary retained FULL/QUERY path | Stop controller-only κ search at its all-length cap above | Changed local debt, query price, fresh-block rank, targets or idle law |
| Compatible menu of autonomous providers with the same port/main contract | No mixture beats the best menu member at the candidate exponent | A cross-boundary consumer or a changed state/interface contract |
| Same path, redesigned native/helper factorization | Open; use the price frontier before building a controller | Complete changed local paid/helper invoice crossing the required discount |
| Coded/coupled outputs and centre removal | Open; a decoder/consumer can retain more raw headroom, but all conversions must be priced | Actual native lowering, independent targets and complete compiler/outer join |
| Other graphs, observation/state retention, larger geometry or changed coverage | Outside these ceilings | Derive that architecture's own complete optimistic bill |
| COMPLEX improvement with the selected admitted BIT budget fixed at .0034 | Cannot obtain κ>=.0034 under that fixed outer contract | A higher funded BIT budget or a changed outer transfer |

A large architectural impossibility theorem would additionally have to bound
L(t) over **every** legal native provider. This package does not prove that
missing lower bound. The productive-helper framework is broader than a
rank-eight path, so none of these caps is a universal multiplication barrier.

## Reproduce and screen a new bill

Python 3.12, standard library; no heavy scientific replay is required:

```sh
python3.12 -B scripts/research_package.py --package research/kappa-architecture-frontier
python3 -B research/kappa-architecture-frontier/verify.py --price research/kappa-architecture-frontier/EXAMPLE-PROFILE.json --C 0.0034
```

The example's JSON contains `ports`, `paid`, and `helper_targets`. Replace these
with a source-bound autonomous profile only after checking the main/path contract.
The pricing command reports exact discount bounds and an all-n ratio certificate.
Positive discount means the supplied bill still needs that much net saving per
FULL; negative discount is raw margin, before extra costs. It does not inspect
a native word or admit a supplier. Ambiguous interval signs or a minimizer
beyond the explicit 4096-FULL computational cap fail as unknown. The all-n theorem
applies only after the sign gate succeeds.

Direct offline replay of the retained package also works:

```sh
python3 -I -B research/kappa-architecture-frontier/verify.py
python3 -I -O -B research/kappa-architecture-frontier/verify.py
```

The fresh checker binds four complete source invoices, proves six all-n/all-larger-C
exclusions, checks thirteen all-n price gates and 912 small-mask controls, and
compares the entire exact result. Proof and source applicability still need human
or formal review. [VALIDATION.md](VALIDATION.md) records actual executed checks.

## Open next questions

1. **Prove a native local-debt lower bound.** Start at C=.0034: can any legal
   rank-eight native factorization under the same contract beat #5551 by more
   than 4.91394927369 moment units per FULL? A positive answer needs a full
   word; a negative answer must cover arbitrary factorizations, not one poset.
2. **Close a coded consumer instead of refining its root.** The p19 proposal
   [PR5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440) explicitly
   leaves chain-to-native-event compilation open. Bind and price one complete
   actual path; symbolic diagonalization alone does not discharge that obligation.
3. **Change an architectural invariant.** Start with one changed query/idle
   law, retained-state interface or geometry and derive an optimistic full bill.
   Do not transfer the path's cap until the new law is shown equivalent.
4. **Validate the written universal proof.** The novel ratio frontier and its
   all-n gate are small targets for human or formal checking. Finite Python
   controls do not replace that audit.

Structured questions, blockers and a bounded first step are in [TASK.json](TASK.json).

## Credit and significance

[Ali Romman](https://github.com/aliromman) supplies the earlier path ceiling,
owned/transposed/direct caller and P104 descendants;
[Cinna Davis](https://github.com/1337isnot1337) supplies productive helpers and
paired/query controllers; [Chris R](https://github.com/Clear1nsight) supplies
independent convexity and admission work; [Cao Yifan](https://github.com/intqwq)
supplies the native profile; [Dillon Amburgey](https://github.com/dillona)
supplies the coupled provider; [Jacob Alan Sussman](https://github.com/jacobalansussman)
supplies mixed-target recursion. Preserve [Gareth Davidson](https://github.com/bitplane),
[David Arias](https://github.com/DavidAriasC), [thu-nmrc](https://github.com/thu-nmrc),
the compiler/precision work of [zxv](https://github.com/zxv), and the predecessor
credits/notices in the unchanged source extracts. [LITERATURE.md](LITERATURE.md)
separates direct predecessors from related spectral-potential literature.

Prepared for [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
The practical contribution is an exact stopping rule for controller derivatives
and a measurable admission target for new local mechanisms, while keeping
unproved architectural exclusions out of research-agent guidance.
