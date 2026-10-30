# Jensen criterion and one hypothetical P104 compiler benchmark

## Change and mathematical scope

The fixed PR5565 paid invoice can satisfy the retained compiler's sufficient
arithmetic at C=.0033000005 **if** 145 distinct original rank-nine helper
targets per FULL can be replaced by independent rank-four and rank-five
targets with no added paid jobs. This is a hypothetical target contract,
not an available split construction or funded kappa. Its exact numerical
benchmark passes with the complete normalized charge below
`.949537674806338372278839`.

There are two separate contributions here: a transparent sufficient
criterion obtained by applying existing weighted Jensen to the credited
rank-one-tail endpoint, and one source-frozen numerical application of that
criterion. Neither Jensen's theorem nor the existing generic compiler is
claimed as new. The numerical application changes completion choices from
the earlier fixed17/18 setting; it does not refute that setting's obstruction.

For positive paid ranks, set `P1=sum(p_r*r)`, `w_r=p_r*r/P1` and
`mu=sum(w_r*ln r)`. At t=1-C, weighted Jensen gives

```
P_t/P1 >= exp(-C*mu).
```

If `ln(c)>mu`, the source endpoint u=C obeys
`gamma_C<=alpha*exp[-C*(ln(c)-mu)]<alpha`, where alpha=P_t/T_t.
If also `b*B<=P1`, completion satisfies delta<=gamma_C. Thus a raw-positive
invoice has all three strict subunit ratios under these sufficient conditions.
Failure of this sufficient criterion is not an impossibility theorem.

The benchmark uses one fixed offset u=C_test at both declared points.
At the goal C=.0033, s=u-C=5*10^-10, so the paid tail is P_(1+s),
not P1. The explicit correction is
`gamma_u<=alpha*exp[-C*(ln(c)-mu)+s*ln(72/c)]`.
Completion is bounded separately through gamma_C; no monotonicity in u
is assumed. The full proof and native hypotheses are in [PROOF.md](PROOF.md).

The one fixed tuple is c12, b13, u=.0033000005, v32768, rho=.99985,
reserve10^-6, theta39/40 and logarithm power22000. Both original-paid
splitting and paid completion are charged in `alpha^v+2gamma_u^v+2delta^v`.

| Quantity | Goal C=.0033 | Tested C=.0033000005 |
|---|---:|---:|
| Complete raw surplus, lower bound | .390090597791418330922234 | .389976323560029949280648 |
| Alpha, upper bound | .999998370208957866277402 | .999998370686390670134519 |
| Fixed-u gamma, upper bound | .999780978264439535254920 | .999780978737406788178684 |
| Delta, upper bound | .830893792462845886251572 | .830893792830358397762175 |
| Complete normalized charge, upper bound | .949522820057250844365688 | .949537674806338372278839 |

At the test point, eta is enclosed above
`1.90676400670345622153594E-234`, while theta^22000 is below
`1.26341307714121684274046E-242`. Exact capacity, shifted exits and
initial range pass. The first passing integer for
`(14000000000*j+1)^22000<2^j` is1185397; predecessor1185396 fails.
Thus H=16595558000000000 is sufficient for this majorant under its native
compiler hypotheses. No uniform word is materialized, and this is not a
minimum native program, minimum tensor power or optimal parameter tuple.

## Task and overlap

Package `research/p104-jensen-compiler-benchmark` changes scope from the
`scalar-to-moment` construction card to a conditional numerical compiler
benchmark before construction. It does not meet that card's physical gain
gate. The actual contribution base is the available exact older canonical
`32890bc5de034ab8fc93ac88ead7279a6a416d04`; newer source/guidance state is
recorded separately and must be refreshed before publication.

All scientific inputs remain pinned to historical PR5565 head
`9af814164b9dfc21f19ec737959d67cb71488c95`. Its structural paid profile is
`{1:2203,2:459,3:493,4:92,5:168,6:18,7:14}` and helper profile
`{4:83,5:5,8:14,9:425}`. The nomination selects145 distinct original
rank-nine parents from425 and removes their credits, giving hypothetical
helpers `{4:228,5:150,8:14,9:280}`. Produced children are not reused.
No current13 or historical15 split receives extra credit.

The complete hypothetical invoice has66726 paid jobs and15424 targets,
rank masses241268/242028 and surplus760. [INVOICE.json](INVOICE.json)
contains every local, query, idle and main-target coefficient. The source
word census counts MOVE dimension differences and declared helper endpoint
ranks only; it establishes no new arbitrary-input or native proof.

The retained22:19:56UTC checkpoint records newer main
`d7633ce230196a1d5d061347de7a0fd8be512ed6`, unchanged guidance and selected
kappa .003027288235. It reports a newer author construction at public
head`3db0f4bb618f8607874f888b410715ea606ddb36`, conditional claim.00310261.
That claim is not independently admitted by this benchmark and does not
retarget its frozen9af inputs. The checkpoint also records archival merges
of PR5592/5596/5597 as `partially_reviewed` and `merged_for_archive_only`;
those dispositions are not scientific acceptance or selected promotion.

Current physical helper/basis/contact/pivot/global-caller ownership remains
with its source authors. No actual145 cuts, target input fields or realizing
word are supplied. Splitting a paid rank-nine operator into disjoint axes
on the same owner does not create two independent productive inputs. The
zero added paid bill is a substantial explicit realization hypothesis.

The complete native chronological product, whole-job adapters, spectators,
owned banks and restoration remain conditional. No actual scalar, basis,
movement, normalization, denominator, growth, precision, storage, tape,
row-stock or newly expanded U/R/W/P/G constants are supplied. No source1000
or prior1100 ordinary cap transfers. BIT and changed-consumer outer admission
are unrun; even a retained54+4 predicate count is not universal for a changed
route. The selected kappa is unchanged.

## Validation

Python3.12 standard library:

```
python3 -B scripts/research_package.py --package research/p104-jensen-compiler-benchmark
```

The original root accepted and executed one frozen normal/optimized pair.
Complete result SHA256:
`938f8b2fbbf60da5cccf257f47dd88c06aae7ad09c4fa8a2d87470b35a8797e2`.
The pair took2.816191074seconds, sampled descendant RSS46694400bytes under
the unchanged150-second/512MiB serial guard. These are original local
execution facts, separate from later portable registered/export validation.
Root acceptance, guard receipt and complete output equality are retained.

The wrapper authenticates all internal source/package bytes before launching
the byte-preserved checker. It reproduces the entire original result with
zero excluded fields. The qualified positive-C engine is unchanged. Direct
tail transport uses `r^(1+s)=r²/r^(1-s)`, so no negative-C call or new
transcendental engine is introduced. All acceptance arithmetic uses integers
and exact rational intervals; decimal conversion is outward printing only.
The absolute10^-320 mesh retains a positive eta lower bound.

All24 original controls reject. They distinguish genuine numerical failures,
target/invoice and custody mutations, theorem-domain checks and scope sanities.
In particular, old17/18 completion has delta>1, sourcev1024 loses this
charged sufficient expression, and sourcep1000 fails eta capacity. Omitted
positive-tail controls enforce complete accounting; they do not claim a
truncated numerical expression must fail. Ordinary-cap transfer is a scope
sanity, not an actual counterexample word.

`verify.py --integrity-only` authenticates bytes without scientific execution.
Ordinary replay uses a bounded private child, writes only temporary files,
and supports normal/-O, read-only Git-free export, spaces in paths and an
empty PATH. Portable validation remains a publisher step until its actual
receipts are recorded. An independent static agent review found no material
blocker before execution; [REVIEW.md](REVIEW.md) is preserved byte-exact.
No independent numerical implementation, human review or formal acceptance
is claimed.

Two literal nomination fields in the preserved result require context:
`parameters.funded_C` is a proposed target label, not a funded claim, and
`parameters.minimal_j_not_computed` records the pre-execution nomination.
The actual computed grid result is the separate `uniform_threshold` object,
which certifies j1185397 and its predecessor. Frozen bytes are not rewritten.

## Credit

[Hoeffding (1963)](https://doi.org/10.1080/01621459.1963.10500830), weighted Jensen statement, printedp14/PDFpage3 equation1.9,
is reused through the curated primary-source literature note. No novel
Jensen theorem is claimed. PR4416's rank-one-tail endpoint and zxv's
higher-moment/generalized-logarithmic-majorant proof are credited reuse;
the latter is authenticated at Git blob
`0a736ca89e1eafb73a30e1f2589cc45e6b5f76c3`.

Credit Hexapode for PR5565; Ali Romman for P104/PR5544/5545/5580;
thu-nmrc5551; GamingPuzzled5569; DreamingOfClouds5561/5599;
zxv and Cao Yifan; Jacob Alan Sussman's integer flow/productive recursion;
Cinna Davis and all retained native, controller, compiler, geometry,
precision and analytic predecessors. Current strategy, source rebinding,
finite application and packaging for Chris R/Clear1nsight with substantial
OpenAI Codex/Astra assistance. Reused engine and source licenses are retained.
Apache-2.0. Agent review is not independent human or formal acceptance.

## Open next questions

The smallest useful physical continuation is a coordinated, released
realization of distinct independent helper targets with a complete signed
paid/ordinary delta. This benchmark does not authorize that search. An
actual realization also needs native/product/adapter and owner proofs,
expanded finite constants, precision/tape/stock and applicable BIT/outer
admission. Independent human/formal review of the general sufficient
criterion and source majorant is useful separately. See [NEXT.md](NEXT.md).
