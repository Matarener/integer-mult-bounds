# Retimed hybrid p17 controller: conditional kappa 0.003001053

This package constructs a conditional integer-multiplication exponent saving

\[
\boxed{\kappa=0.003001053},\qquad
T(n)=O\!\left(n(\log n)^{0.996998947}\right).
\]

The increase over the conditional `0.00268647` proposal in
[PR4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416) is
`0.000314583`, or about **11.7099% in kappa**. It is also **1.3869% above**
the concurrent `0.00296` proposal in
[PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440).
These compare asymptotic exponent savings, not practical running times.

The hybrid mechanism replaces selected full native invocations with directly
paid rank-one shears. Those stages produce no native helper outputs. Their
replacement also removes their transverse stage transform from every
productive endpoint and every idle request. A balanced controller with
17 main pairs gives the stronger complete moment after all these changes
are charged. The final construction uses the improved helper boundaries
from [PR4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441),
whose complete local native receipt is independently replayed here. The
updated PR4441 also certifies this same combined profile at `0.00300105`;
our final endpoint exceeds that value by `0.000000003`.
A separate native BIT construction admits saving `0.00312`, which supplies
the ordinary BIT premise of the outer proof.

The frontier refresh found PR4440's independently developed query-thinning
construction and PR4441's helper retiming while this work was in progress.
The p17 schedule agrees with PR4440. After checking compatibility, we
replaced our initial fifteen-tail helper pruning with PR4441's stronger
supplier. A later refresh at 20:27 UTC found PR4441 had already combined the same
profile at a stronger endpoint than our initial certificate. We audited
that update, adopted it as the publication parent, and tightened our exact
endpoint. The complete updated PR4441 branch is retained unchanged as an
explicit source dependency. This package adds independent physical and
phase evidence, a broader bounded controller search, its own p6 BIT
supplier, and the small endpoint refinement. The combined profile itself
is concurrent work, not claimed as a new discovery unique to this package.

This is a source-bound finite certificate and a conditional transfer proof.
It retains the PR4359/PR4416 line's stated native, whole-job matching,
spectator, mixed-compiler, precision, storage, analytic, fixed-tape and
exact-recovery premises. The scripts do not formally verify the full
multiplication theorem. The selected record at this package's base commit
still has kappa `0.0023`; this package does not change that record.

## Construction

The source complex controller uses local operators

\[
F_s=D_sS_y(Q^{-1}),\qquad B_s=D_sS_x(-Q).
\]

Here `Q` is the central rank-one transform and `D_s` acts on the eight
transverse axes of stage `s`. The complete controller has an exact
factorization over the rational Laurent ring in `Q,D_0,...,D_34`.
Substituting `D_s=I` preserves that identity, including both `Q` and its
inverse. This substitution has a physical implementation: copy the source
into an owned scratch field, make its rank-one query, add the result into
the other main field, and erase the scratch field. The original source
field is preserved. Copies and scratch fields receive no productive credit.

The selected controller has these exact parameters:

| Parameter | Value |
| --- | ---: |
| Main pairs | 17 |
| Balanced cut | 8 |
| Original local stage positions | 35 |
| Retained-idle mask | 280378328416255 |
| Native-stage mask | 28633115307 |
| Native invocations | 19 |
| Direct shears | 16 |
| Paid direct rank-one queries | 1792 |
| Ambient rank retained for the proof | 281 |

Stages `0`, all odd stages `1,3,...,33`, and stage `34` are native. Every
internal even stage `2,4,...,32` is a direct forward shear. Stage zero
therefore retains the original source geometry. All sixteen middle idle
requests become identity maps. The remaining initial and terminal idle
requests have ranks `16,24,...,72`; each rank occurs on 448 physical fields.

The retimed native supplier changes 117 helper entrances, 42 helper exits
and 395 scalar contact frames. It preserves the logical scalar actions,
their order and coefficients, every warp contact, all main boundaries,
and the owned center program. Its 408 independent helper outputs have
profile `{4:26,5:2,7:29,8:42,9:309}`. The complete local paid profile is
`{1:2253,2:515,3:445,4:102,5:40,8:8}`.

Two retained literal interpreters replay both orientations on all 632
arbitrary local input columns. All 320 changed transport or helper-boundary
recipes are lowered with their exact absolute phases. The retiming
subsumes our original fifteen deleted helper tails; no extra lifetime
deletion remains. Relative to that earlier version, the final controller
saves 3344 paid calls.

The nineteen native invocations have 7752 distinct helper inputs; the
seventeen main pairs contribute 3808 more inputs. The complete unit
therefore has **11560 independent productive fields** and **69273 paid
requests**.

See [NATIVE.md](NATIVE.md) for the physical construction and source binding,
and [PROOF.md](PROOF.md) for the complete conditional transfer.

## Complete rank invoice

The table gives the productive and paid multiplicities of the complete
raw unit. A blank entry means zero.

| Rank | Productive multiplicity | Paid multiplicity |
| ---: | ---: | ---: |
| 1 | | 44599 |
| 2 | | 9785 |
| 3 | | 8455 |
| 4 | 494 | 1938 |
| 5 | 38 | 760 |
| 7 | 551 | |
| 8 | 798 | 152 |
| 9 | 5871 | |
| 16 | | 448 |
| 17 | 448 | |
| 24 | | 448 |
| 25 | 448 | |
| 32 | | 448 |
| 33 | 448 | |
| 40 | | 448 |
| 41 | 448 | |
| 48 | | 448 |
| 49 | 448 | |
| 56 | | 448 |
| 57 | 448 | |
| 64 | | 448 |
| 65 | 448 | |
| 72 | | 448 |
| 73 | 448 | |
| 153 | 224 | |

The rank-one moments are `T_1=260798` and `P_1=259998`, with surplus
`800`. Writing `T_tau` and `P_tau` for the two moments at `tau=1-C`,
the numerical discovery root of `T_tau-P_tau` is about
`0.003001054183175`. The proof uses the exact rational tested saving
`C=0.003001054` and the smaller final saving `kappa=0.003001053`.

## Turning the raw moment into an admitted rule

The raw productive and paid ranks overlap. The proof composes complete
native units chronologically before applying any global cover. It uses
distinct productive owners, preserves every paid position, and retains
separate owned scratch banks for suspended invocations.

Take `v=17160` native factors, a paid cutoff `18^v`, and a productive floor
`19^v`. After the complete product, raise each smaller productive endpoint
to that floor with an explicitly paid transform on disjoint coordinates.
Split every oversized paid request, including these completion requests,
at the same cutoff. Thus every final paid rank is strictly smaller than
every final productive rank.

The exact interval calculation certifies

\[
\alpha=\frac{P_\tau}{T_\tau}<1-\frac1{10000000000},\qquad
\gamma=\frac{259998}{18^C T_\tau}<\frac{9991}{10000},\qquad
\delta=\frac{11560\cdot19}{18^C T_\tau}<\frac67.
\]

The full paid moment, including both original tails and paid productive
completion, is bounded by

\[
\alpha^v+2\gamma^v+2\delta^v
<\frac{262144250000429}{262144449839104}<1.
\]

The proof then derives sufficient finite uniform-compiler parameters from
this enlarged word and checks the complete outer inequality ledger. It
recomputes the scalar, movement, owned-bank and precision envelopes for the
expanded finite program. The enormous tensor and uniform words are given
as finite recipes; they are not materialized or claimed to be practical.

The BIT side uses six main pairs and thirteen native invocations. It keeps
the complete original idle operators, tensors the native program before a
single delayed cover, and obtains the exact ordinary saving

\[
\frac{9750334599}{3125000000000}=0.00312010707168>0.00312.
\]

The native replay covers all 7039 arbitrary BIT input columns and all 117
owned-copy episodes. The BIT proof is in the `bit/` directory.

## Reproduction and evidence

From the repository root, using Python 3.12:

```sh
python3 -I -O -B research/kappa-hybrid-controller/verify.py
```

The verifier authenticates the retained source inputs, reconstructs the
complex Laurent factor and the integer invoice, replays the changed native
helper boundaries and direct query phases, and checks the complete
strictification and outer arithmetic. It preserves all 54 outer predicates
and adds an explicit fourth functional guard for the actual BIT atom
exponent `0.0032`. It uses independently implemented
rational interval calculations and compares regenerated receipts with
the committed result. Acceptance guards remain active under `-O`.

The separate historical frontier audit is reproducible with
`python3 -I -O -B research/kappa-hybrid-controller/frontier/audit.py`.
Its independent outward integer interval engine checks updated PR4441
and the fixed-profile ceiling; [frontier/REPORT.md](frontier/REPORT.md)
states its exact scope.

`VERIFY.json` registers both replays and their 51 live input paths. `SOURCES.json`
pins repository provenance; `EXTERNAL-SOURCES.json` records the retained
source closure used by the native gates. `RESULT.json` and `certificates/`
contain the exact receipts. Explicit `--source-root`, `--bit-source-root` and `--retimed-source-root`
arguments allow separately prepared source checkouts. The default paths
use the already committed PR4416 source export and the original BIT files.
The retimed supplier additionally uses the unchanged PR4441 package and
its original source dependencies in the repository root.

The search is a separate discovery artifact under `search/`. Its dynamic
program considers all cuts and native-count states in the stated
minimal-cut path family through `p=120`. Its scores use floating-point
arithmetic. Only the selected positive construction is promoted to exact
Laurent, native, phase and interval certificates. No global optimality or
barrier for other controllers is claimed.

## Open next questions

1. **Allow more local choices than native or direct.** A partly executed
   supplier could retain some helper outputs while removing transverse
   work. First derive its arbitrary-input operator and complete paid
   invoice, then add that proven choice to the controller search. A local
   tariff alone does not establish a valid supplier.
2. **Search beyond the minimal-cut path family.** Other idle masks,
   controller graphs or asymmetric directions could improve the balance.
   First produce an exact Laurent factorization and price every physical
   idle before attempting a transfer. The present finite search gives no
   obstruction outside its stated family.
3. **Reduce the sufficient tensor power.** The higher-moment method in
   [PR4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433)
   reduced the predecessor's finite constants without changing kappa.
   Updated PR4441 already applies it to this invoice using power 1024.
   To port that smaller sufficient power into this independent proof,
   rederive the compiler constants with the ambient rank 281 retained
   here and include every paid completion tail. A smaller power does
   not itself improve the limiting kappa.
4. **Independently review the inherited transfer premises.** Replay the
   exact native and arithmetic gates first, then check the all-column
   matching, common-weight cover, precision and effective recovery
   arguments against this enlarged program. Finite checks alone do not
   settle those asymptotic premises.

The same questions, including first steps and blockers, are recorded in
`TASK.json`.

## Sources and credit

Prepared for Cinna Davis (`1337isnot1337`) with substantial OpenAI
assistance. The final contribution supplies an independent source-bound native,
phase and conditional-transfer certificate for the retimed p17 profile,
with a slightly larger certified endpoint. The work also includes
the bounded controller search and a separately replayed p6 ordinary BIT
supplier. Our initial helper-tail pruning is subsumed by PR4441.

Credit the concurrent
[PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440)
for the independently developed query-thinning mechanism and identical
p17 schedule, and
[PR4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441)
at `ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9` for the helper retiming
used in the final supplier. The combined result in updated PR4441 at
`5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39` is the publication parent
and is credited for the already combined profile. Both were prepared for the same contributor
in parallel sessions. Neither source is presented here as an uncredited
new invention.

This work builds on zxv's
[PR4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359)
native reconstruction and delayed cover; the user's compiler refill and
native tensor work in
[PR4405](https://github.com/CrocSwap/integer-mult-bounds/pull/4405),
[PR4412](https://github.com/CrocSwap/integer-mult-bounds/pull/4412),
[PR4414](https://github.com/CrocSwap/integer-mult-bounds/pull/4414), and
[PR4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416);
and Jacob Alan Sussman's finite mixed compiler, Theorem 1G / PR4268.
The BIT local word retains DreamingOfClouds's PR589 and eumemic's
PR555/PR543 lineage. Retained source files preserve their own notices.
New contributions are under the repository's Apache-2.0 license.
