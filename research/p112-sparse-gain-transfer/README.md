# Mixed two-port terms cannot beat the P112 full-group invoice

For the fixed P112 full-group mask, **every rational strict fit costs at least
334 if each term has a query touching at most two scalar ports or a reader
touching at most two scalar ports**. The sparse side may differ between terms.
There is no restriction on fitting rank, term count, query dependence or
cancellation of forbidden entries between the two orientation classes.

Therefore any cheaper decoder must contain at least one term with **at least
three source ports and at least three reader ports in that same term**.
This is necessary, not sufficient. The package does not prove an unrestricted
334 floor or improve the selected multiplication bound.

The [mixed proof](MIXED-ORIENTATION.md) treats the complete matrix equation as
a gain-incidence problem on matrix positions. Repeated copies of one frozen
factor retain one shared gain. An old independent basis transfers to a
characteristic-two field, where all diagonal entries can be made nonzero and
then normalized simultaneously. Factor supports only shrink; permitted free
entries may change. Every characteristic-two strict fit on the physical mask
expands to I334, giving the invoice floor. See also the
[independent mixed proof audit](INDEPENDENT-MIXED-PROOF.md).

## What the package establishes

| Result | Hypothesis | Conclusion |
|---|---|---|
| [Mixed strict-fit transfer](MIXED-ORIENTATION.md) | Each rank-one term has a two-port query or a two-port reader; the choice varies by term | Termwise support subsets over a characteristic-two field, with free fitting entries allowed to change; invoice at least 334. |
| [Uniform-side companion](PROOF.md) | Every query is two-port, or every reader is two-port | Explicit equality of the uniformly sparse-side supports and shrinking opposite supports; no common-recovery premise. |
| Common group gauge | One invertible within-group similarity makes every term sparse on at least one side | Complete-group supports and tariffs are unchanged, so the mixed floor applies in the original coordinates. Per-term gauges are not covered. |
| [Common recovery](COMMON-RECOVERY.md) | Literal two-port queries; disjoint indicator marks recoverable inside the intersection of their actual reader supports | Preserves the exact indicator endpoint. The extra premise is unnecessary for the strict-fit cost floor. |
| [Mixed coefficient/reader transfer](SCALAR-DEMAND-AND-BRIDGE.md) | Queries lie in the canonical span; each term uses at most two coefficient marks or at most two actual reader ports | Preserves the exact canonical endpoint with both factor supports shrinking; invoice at least 334. Literal query supports may exceed two ports. |
| Seven-query bridge | Two declared triangles plus one paired bridge, with any exact rational reader matrix | Local invoice at least 18, including extra zero-target reader columns. |

The coefficient-space companion also permits mixed orientations. Within the
canonical span and exact canonical endpoint, a saving requires a term that
combines at least three canonical marks and has at least three actual reader
ports. This extra conclusion does not apply to arbitrary exterior queries.

The mixed theorem strengthens the splitting budget. For each term, choose a
partition of its source support into chunks of size at most two and, separately,
such a reader partition. Let `delta_source(t)` and `delta_reader(t)` be their
extra complete-group charges. Both are nonnegative. Splitting each term on its
cheaper side preserves the endpoint and gives

    C + sum_t min(delta_source(t), delta_reader(t)) >= 334.

Thus a C <= 296 decoder requires at least **38 units of mixed splitting
overhead for every choice of these partitions**. No partition optimizer or
feasible decoder is supplied. The earlier uniform-side inequalities remain
valid consequences.

The canonical residual query has three ports. For sparse local completion,
it is refined into its ordinary pair and residual unit with the same full
three-copy reader. The verified charges remain 6+1=7. This preserves the exact
canonical endpoint and the total invoice 334.

## Exact scope and reproducibility

The physical cover and labels are pinned through the two inputs in
[SOURCES.json](SOURCES.json). The mask fixes own identity blocks, forbids
cross entries between nonorthogonal complete physical groups, and leaves
the remaining blocks free. A common nonzero diagonal is normalized to one
without changing supports. All prices are binary pairing ranks of complete
source and reader group closures.

From the repository root, with Python 3.12 or later and its standard library:

```sh
python3 -I -O -Werror -B research/p112-sparse-gain-transfer/verify.py
python3 -I -O -Werror -B research/p112-sparse-gain-transfer/independent.py
python3 -I -O -Werror -B research/p112-sparse-gain-transfer/mixed_controls.py
python3 -B scripts/research_package.py --package research/p112-sparse-gain-transfer
```

The two geometry checkers authenticate their scientific inputs directly.
The mixed-control checker uses only declared literal fixtures. All three are
standalone, compare committed receipts without writing, and need no network,
project imports or scratch files. `--write-receipt` is explicit maintenance.
The checks cover:

- All 111,556 literal and symbolic I334 expansion positions, including 28 free
  physical group pairs and 420 free scalar entries.
- All 57 target marks, their `3 H3 + 53 H6 + H7` invoice, the singletons and
  residual-bearing mark `{9,39,55}` with its 6+1 sparse refinement.
- Exact GF4 gauge/unit/cycle controls, a failed common-reader intersection,
  changed-free strict fits, and complete bridge reader-kernel identities.
- A replicated-gain balanced square, a preserved unbalanced repeated-gain
  cycle, a mixed I3 example with forbidden cancellations across orientation
  classes, and an F4 three-diagonal tree with consistent row scaling and
  endpoint-preserving reader-column normalization.

The quantified transfer arguments are written proofs reviewed by separate AI
agents. The finite scripts check their premises and failure modes; they are
not a proof-assistant formalization or independent human review. In particular,
the mixed controls do not replace the universal repeated-gain proof.

The transfer may change free entries and fitting rank. It does not preserve
a chosen exact endpoint except in the stated companion results. No native
routing, dirty-state restoration, storage, precision, all-size compiler or
complete multiplication supplier is supplied.

## Provenance, overlap and credit

Scientific base: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority revision 7. The donor's assigned decoder goal takes precedence over
a new task draw; `TASK.json` records the changed scope. An earlier 20 October
public API snapshot covered 354 open PRs. Discussion coverage remained
unavailable after persistent HTTP406; this is not a novelty certificate.

Nearby retained work has different premises: `p112-regular-query-floor` treats
projectively totally-unimodular queries for a fixed canonical plane target;
`p112-graphic-query-transfer` treats finite two-terminal replacements at one
query interface; and `p112-two-port-transfer-classification` classifies 30
non-Fano placements and coherent boundary maps. This package permits the
strict fit's free entries and rank to change, and allows the sparse factor
orientation to vary from term to term. No prior result is claimed as a new
deduction here.

The cover, canonical targets and original invoice are retained from
flyingviper's [p112-rational-decoder-gate](../p112-rational-decoder-gate/README.md),
including Cinna Davis's P112 cover lineage, Sagar Thakrar's scalar-mask and
full-group audits, Adam Gall's mask obstruction, ctoth and Philippe Van
Velzen's endpoint/pricing framework, and Hanson Sun's projection work.
Physical labels retain the attribution in the adaptive-kernel-demotion source.

Signed-incidence ranks, switching and circuits are standard; see Thomas
Zaslavsky, [Signed Graphs and Geometry](https://people.math.binghamton.edu/zaslav/Tpapers/sggm.pdf),
Theorems 3.1 and 3.5-3.6. The package proves the required arbitrary-gain facts
directly; it does not attribute its mixed or uniform strict-mask transfer
theorems to that signed-only survey. The strict-mask relaxation, mixed
orientation argument, common vertex gauge, support-intersection transfer,
and invoice applications are deductions in this investigation. Prepared by
flyingviper with substantial OpenAI Codex assistance and separate AI-agent
mathematical checks. Apache-2.0.

## Open next questions

- Can a term dense on both sides support a verified full-group saving?
  Merely mixing a dense query from one term with a dense reader from another
  cannot do so. Start with one exact mechanism containing a term with at least
  three ports on each side, then price all terms and check the common-gauge
  obstruction. If all queries lie in the canonical span, the coefficient
  companion additionally requires a term using at least three marks and
  three reader ports. No such saving is supplied here.
- Can the mixed splitting inequality reject a proposed dense decoder cheaply?
  Give one source and one reader partition per term and sum the cheaper
  overheads. A total below 334-C excludes that candidate; a large overhead is
  only a necessary condition and does not construct a decoder.
- Can one common within-group similarity make every term sparse on some side?
  A positive certificate would preserve all physical tariffs and activate the
  mixed floor. The same similarity must serve every term; independent per-term
  gauges do not satisfy the hypothesis.
