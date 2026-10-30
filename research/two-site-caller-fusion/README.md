# Two-site caller cleanup by a phase-complete Bruhat factorization

The actual q2/q3 J callers improve from stock+8 to **stock+4** by changing
two existing unary sites and deleting the whole U-coordinate tail recovery.
The first replacement is a physical monomial with Gaussian quadratic Z
phases; the second is one native2f child. This is outside the preceding
single-site/X-character restriction. Neither caller has a favorable native
bill or gives a new κ.

| q | Banks n | Ambient arity m | Changed source sites | Complete histogram | Native mass | Stock |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 6 | 12 | 31,51 | H2=36,H4=1 | 76 | 72 |
| 3 | 8 | 16 | 39,97 | H2=64,H4=1 | 132 | 128 |

Histogram ranks are in units of f. The words are complete at the two listed
q values for every positive f. Every independent original field, including
both pivot owners and every public field, ends at its literal `F_k J` gauge.
No right input gauge is discarded. Each original-field column is an exact
operator on all physical addresses, not a clean-input or selected-column test.
No all-q caller is inferred from these two fixtures.

## Isolated whole-bank rank-distance lemma

At the two cuts, let V transport the first bank to the second, and let C be
the correction required after deleting the selected tail. The actual words
have both transported direction column and dual row supported on one bank.
The required correction is on that same bank. The two replacement operators
therefore obey

```
W = L U^-1 R,
L = C_jj A_j G_i,    R = A_j^-1 G_j.
```

For a Clifford's binary symplectic matrix `[[A,B],[C,D]]`, put r=rank(B).
Product subadditivity and inverse invariance give
`r(U)+r(W) >= |r(L)-r(R)|`. Exact Gaussian Bruhat factorizations
`L=LL F_a LR` and `R=RL F_b RR` attain the bound with
`U=RL LR`, a physical monomial. Then `W=LL F_a F_b RR` has arity |a−b|;
the overlapping canonical native chirps square exactly to Pauli X.
All Gaussian phases belong in the actual monomial adapters and whole-field
units. This is a general lemma for the stated isolated two-site interface,
not a lower bound for arbitrary callers.

For the two actual source transports, `(r(L),r(R),r(U),r(W))` is respectively
`(4,2,0,2)` and `(8,6,0,2)`. Offline factoring of L/R is a witness-generation
calculation; neither L nor R is executed by the caller. The emitted U circuit
and selected W recipe are explicit in the retained words. The
[construction proof](source/two-site-continuation/PROOF.md) and
[independent review](source/two-site-independent-audit/REVIEW.md) give the
transport orientation, exact phase vectors and proof boundaries.

## Complete physical binding and paid work

[ADMITTED-TWO-SITE-FUSIONS.json.gz](source/two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json.gz)
contains the current literal event schema, complete serialized inverses and
used-only forward/inverse native pools. Every event's signed tableau is
rebuilt from its literal circuit. Every selected recipe, embedding, global
Gaussian phase and f-mod4 whole-field unit is checked. There are 14 used
definitions per fixture and 74/130 forward-plus-inverse native links.
The actual child arities2f/4f obey the pinned proper-child caps at ambient
12f/16f. No dirty helper or private zero field is introduced.

`admit_fusions.produce` freshly rebuilds and checks the complete admitted
words from fixed scientific witnesses. The independent `audit_two_sites.check`
does not import that generator or its general-Clifford tensor engine. It
derives the old-source tail correction and two-sided transport with a separate
literal X-character model, checks the emitted general-Clifford U/W in physical
coordinates, and glues the local equality to every original-input column.
It checks the serialized inverse primitive by primitive, so both literal
inverse orders follow for the full word.

Native rank zero is not zero runtime. Every D/P/X/unit instruction is a paid
full-field scan, and every scalar ADD remains paid. The later replacement's
two monomial adapters use at most eight instructions plus one whole-field
Gaussian-unit control, in addition to the native child. The exact event
lists retain the source's scan macros. Finite controller lowering, address
arithmetic, source access, numerical precision, physical ownership/width
windows, tape/storage and complete outer transfer remain obligations.
The native mass comparison does not pay those costs or admit a supplier.

## Bounded continuation

After the q2 mass 76 word, the registered replay checks every nonempty subset
of its three remaining tail natives and every pair of existing prefix unary
sites:7×703=4,921 cases. Of these, 4,887 corrections involve more than one bank
and 34 fail two-sided transport isolation. There is no eligible isolated pair.
This is authenticated reproduction of the author's general-Clifford census,
with independent row-only/column-only rejection controls and a bank-permuted
two-sided positive control. It is not a second independent census engine.

The census concerns fixed existing sites, a single-unitary-Clifford bank
correction and isolated transported row AND column. Coupled two-bank
corrections, nonisolated annihilation, inserted or additional sites, changed
source/response chronology and owner/output boundaries remain outside it.
The initial finite-ray exploration also leaves homogeneous strata unresolved;
its retained receipts are archival provenance, not a global optimum.

## Fixed-word retiming boundary

Four exact path-pairing witnesses prove native rank mass at least stock for
Clifford-frame retiming of each named common-frame ADD graph:

| Word | q | Source mass | Retiming floor | Path ranks per f |
| --- | --- | --- | --- | --- |
| Repaired two-fusion | 2 | 80 | 72 | 6×12 |
| Repaired two-fusion | 3 | 136 | 128 | 8×16 |
| Admitted two-site | 2 | 76 | 72 | 6×12 |
| Admitted two-site | 3 | 132 | 128 | 8×16 |

The lower bound is for every positive f and arbitrary Clifford frame gauges,
including gauges that mix tensor coordinates. It fixes the literal physical
input/output boundaries, unary holonomies and common frame at each scalar
ADD. It does not prove source masses 76/132 or 80/136 optimal, and it does not
apply automatically to changed responses, helper couplings, scalar rewrites
across native sites or changed endpoint contracts. It is not a universal
kernel or arbitrary same-matrix caller certificate.

For equal-dimensional Lagrangians define
`d(U,V)=mf−dim(U∩V)`. Intersection dimension gives a metric, and invertible
linear maps are isometries. A unary edge G between endpoint Lagrangians has
tariff `d(L_v,G L_u)`. Pairing strands straight or crossed at each common-frame
ADD partitions every edge once into boundary-to-boundary paths. The triangle
inequality bounds each path's tariff by its holonomy's native B rank.
All paths in the four witnesses have full ambient rank; their sum is stock.
This maximizes the path-certificate objective, not the minimum source bill.
Pairing graph edges does not swap or copy independent field values at an ADD.

The [source proof](source/trajectory-pairing-search/PROOF.md), preceding
[metric proof](source/pauli-caller-retiming/TRAJECTORY-PROOF.md) and
[independent review excerpt](FIXED-WORD-REVIEW.md) state the exact model.
The registered replay reconstructs every edge/path, literal holonomy circuit,
signed tableau, all-f phase, source-unary chronology and serialized inverse.
A separate direct crossed-strand traversal agrees. Every independent audit
field is compared to the frozen certificate. Wrong routing, an omitted edge,
omitted actual BANK_SWAP transport and the weaker all-straight witness reject.
No proposer search is rerun; historical trial counts are discovery records.
These holonomies are lower-bound witnesses, not executable child proposals,
so no new native supplier recipe is inferred.

## Reproduce and source binding

From the repository root, using Python3.12 and the standard library:

```
python3.12 -B scripts/research_package.py --package research/two-site-caller-fusion
python3.12 -B scripts/check_research_commit.py --package research/two-site-caller-fusion --check-source-history
```

The registered normal and optimized commands execute the same authenticated
mathematical source bytes with historical assertions active. Direct
`python3.12 -I -B research/two-site-caller-fusion/verify.py` also supports
`-O` and `--json`, needs no Git/network and writes no package files.
The [replay map](REPLAY-MAP.md) lists every executed function and distinguishes
fresh checks from original cold witness generation and archival searches.

[BINDINGS.json](BINDINGS.json) binds the complete 24-file author freeze,
independent review freeze, every named external input and all runtime bytes.
Large immutable JSON files use deterministic gzip transport, with separate
original logical-byte SHA256/length and transport SHA256/length. Read-only
in-memory aliases preserve every original byte; no files are materialized,
executable data deserialized or runtime dependencies fetched. Compression
does not reduce mathematical review scope. Transport, logical-payload,
malformed-gzip and source-byte mutations reject.

The portable shared implementations are the unchanged reviewed adapters from
PR4074. Their original sources and exact path/hash deltas are retained. The
new `two_site.py` guard is repinned only to the actual executed engine bytes.
Exactly four recipe compile/embedding functions are copied verbatim from the
original utility, excluding unused cold-producer imports; the verifier checks
their exact source text against the retained original. All assertions in the consumed functions remain unchanged and active;
unused cold producers are outside this registered replay. Original absolute receipt paths are authenticated
provenance, not required local directories. Only registered/direct wrapper
commands are advertised as portable; archival source CLI paths keep context.

Wrong-direction native pointers, a phase defect only at f=2 mod4, an omitted
first monomial and reversed noncommuting correction order reject. Opposite
whole-field i/−i gauges on U/W are accepted as an equivalent positive control.
The saved independent loader controls are retained; its writing wrapper is
not called in read-only exports. The portable loader directly compiles the
same authenticated bytes without reading bytecode caches, and a live legacy
assertion control also runs under the optimized parent.

## Task, credit and limits

Canonical scientific base20ecf2891d80b5acf18d980b2164fb44ea7faa90 and
priority revision 6 are provenance. [TASK.json](TASK.json) records the explicit
assigned continuation and changed `joint-query-controller` card scope; the
original broad card is not solved. [SOURCES.json](SOURCES.json) gives immutable
canonical blobs; pending research bytes have explicit local-source hashes
and original provenance rather than invented Git pins.

[PR4074](https://github.com/CrocSwap/integer-mult-bounds/pull/4074), exact
5758f0f3042b740ce872b5b0ae974917bd07016d, is the direct source construction.
Its two fusions and earlier scoped gates retain credit. PR4069 supplies the
fixed-core J caller/native ancestry; PR4055/4056/4057 are separate earlier
caller contributions. Generic phase/lift results in Clear1nsight3987 and
ToikY4002, and Clear1nsight's distinct3989/4045 interface/volume work, are not
claimed as new here. icekylinx/PR531, Rohan Arun/kernel92, retained compiler,
Gaussian-phase and caller notices remain intact under
[source/vendor/credits](source/vendor/credits). Existing3630/3632/3645/3649/3655
and separate BIT4021/4023 are outside this contribution.

Ross Richardson with substantial OpenAI Codex assistance in construction,
proof, separate audit and packaging; Apache-2.0. Separate AI contexts do not
constitute independent human review or formal-kernel acceptance. Local exact
verification, written proof, hosted CI, physical admission and a multiplication
theorem remain distinct. No global caller obstruction, all-q caller, positive
supplier, compatible BIT, new κ or selected-frontier change is claimed.

## Open next questions

[TASK.json](TASK.json) records the question, smallest first step and blockers.
A coupled correction or changed reader/owner boundary must first provide one
complete original-input word and its full native/scan/owner/volume bill. The
remaining four native units cannot be declared saved by a partial inverse
identity. An all-q caller would additionally need its literal transport,
site chronology and owner interface proved; q2/q3 do not supply that induction.
