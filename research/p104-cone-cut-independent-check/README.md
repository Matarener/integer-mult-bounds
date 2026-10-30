# An independent recomputation of the frozen P104 forward/backward cone cut

**Independent check. No new exponent.**

The merged package `research/p104-cone-cut` reports that X102's dimension-5
forward cone and Y71's dimension-8-to-6 backward cone do not meet: 1,725
forward edges, a backward cone that grows `12 → 22 → 37`, and an empty
intersection at 4,992 required pairs. A second, separately written checker
reproduces every published value of that receipt from the same frozen inputs,
and adds two things the merged receipt does not report.

## What reproduces

| Published value | Merged receipt | Independent run |
|---|---|---|
| forward cone at dimension 5 | 1,725 edges | 1,725 edges |
| backward seeds (dimension-8 writers of Y71) | 12 | 12 |
| backward growth over dimensions 8, 7, 6 | `12, 22, 37` | `12, 22, 37` |
| backward departure-slot histogram | 37 edges over 12 slots | identical |
| writer arrivals | `142:2, 143:10` | identical |
| intersection | 0 | 0 |
| 37-edge sha256 | `9f44aa43…` | `9f44aa43…` |

Two further inherited quantities also reproduce: the marker counts at
dimensions 2 to 5 are `25, 52, 365, 1725`, and the dimension-2 incoming state
is the departure-slot histogram `165:9, 204:7, 205:9`.

## What is added

1. **Schedule sensitivity of the emptiness.** The frozen transfer applies
   exactly one expansion step per dimension. Iterating the *same* relation to
   its fixed point at the same dimension instead — a strictly larger closure —
   the backward closure grows to 99 edges and 26 of them lie in the one-step
   forward cone; the settled forward propagation reaches all 2,309 edges by
   dimension 3 and contains all 37 one-step backward edges. The emptiness is
   therefore a property of the frozen one-step-per-dimension schedule, not of
   the adjacency relation alone. This does not contradict the merged receipt;
   it says a relation-level or closure-level strengthening of this cut is
   unavailable.
2. **Structural guards and counts.** The derived relation is checked for
   reflexivity and symmetry in the verifier itself, and the count of comparable
   index pairs with disjoint lower bounds is reported (zero on this input,
   where the frozen checker's integer division would otherwise fail).

## What was executed

`verify.py` re-derives, from the pinned witness and certificate and without
importing the merged checker: the transport chains, the 208 departure spans,
the 208 arrival hyperplanes, the 2,309 compatible edges, the span relation at
each dimension used, the X102 marker propagation over dimensions 1–5, and the
backward expansion from Y71's dimension-8 writers over dimensions 8, 7 and 6.
It then compares its own values against the merged `RESULT.json` field by
field, and against the frozen `RESULT.json` of this package. `test_verify.py`
holds four behavioural controls: the stored receipt, a weakened relation that
must change the adjacency, a changed target label, and a changed source label.

The merged package's checker is not imported and not executed here; only its
published receipt is read. The relation rule and the transfer schedule are the
frozen model's definitions; they are restated in separate code. A one-off diff
of the restated relation against the published rule was used while developing
this package and is not shipped.

## Reproduce

From the repository root with CPython 3.12:

```sh
python3.12 -B research/p104-cone-cut-independent-check/verify.py
python3.12 -B -O research/p104-cone-cut-independent-check/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-cone-cut-independent-check
python3.12 -B scripts/check_research_commit.py --package research/p104-cone-cut-independent-check --check-source-history
```

The scientific replay takes about 20 seconds and the controls about 35 seconds
on a laptop; both are registered with a 300-second per-command budget.

## Sources and limits

- Live inputs: `research/p104-native-channel/inputs/LOWRANK-WITNESS.json` and
  `research/p104-joint-unit-flags/CERTIFICATE.json` (hashed in `SOURCES.json`),
  plus the merged `research/p104-cone-cut/RESULT.json` as the comparison target.
- The related `research/p104-missing-pair` and `research/p104-literal-missing`
  readings (interval and literal recurrences each reaching 4,991 of 4,992
  required pairs) are **not** re-derived here. The 4,992-pair accumulation, the
  backward-cone licence and the fixed-cover consumer contract are out of scope.
- This is an independent finite check of one published receipt, not a proof of
  the underlying transfer model, not a construction, and not a supplier
  admission. It does not close the fixed-cover contract.
- The saturation comparison is a statement about iterated closures of the same
  relation, not about any executable schedule in the frozen word.
- No κ, packing, physical invoice, consumer or selected-frontier change.
- Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Does the one-step emptiness survive a *scheduled* variant with two expansion
  steps at one dimension and none at another? The saturation result above says
  an unbounded closure at one dimension does not; the intermediate schedules
  are unexamined.
- Do the 26 meeting edges carry any required pair, or only non-required
  positions? The merged package does not accumulate the other required pairs,
  and this package does not either.

## Credit

The merged package `research/p104-cone-cut` (author jwr, with the assistance it
records) supplies the receipt being checked; it in turn credits Nick
Petalas/PR3124's pooled-cut checker for the archived relation rule and the
frozen channel witness's own predecessor credit. The frozen witness and
certificate are used unchanged. Only the separate recomputation, the
saturation comparison and the structural guards are new here. Produced by Nick
Petalas with AI assistance. Independent human and formal proof-kernel review
are unclaimed.
