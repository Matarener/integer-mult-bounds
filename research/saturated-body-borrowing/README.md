# Saturated setup for least BIT borrowing

Stock-capped trial powers preserve the exact least covering borrowing and
reduce the conditional setup bound to O(h^3+w^2 h^4) tape operations and
O(wh) cells, where h=1+ceil(log2(e+1)). Only the final accepted plan constructs
exact q^k. Minimality proves q^k<q S_D(floor(e/w)), so that final construction
also fits the smaller space bound. [PROOF.md](PROOF.md) gives the full argument.

Hiroki Kumazaki's [PR3502](https://github.com/CrocSwap/integer-mult-bounds/pull/3502)
left this saturation question open. Its full-power setup bound is
O(h^3+h^2(e+wh)^2), with O(e+wh) cells. The new contribution removes the e
term caused by rejected-trial powers when the fixed width exponent is below
one. It preserves the R=q^k>=S covering predicate and fixed original width.
Nick Petalas's PR3486 supplied the earlier threshold result. PR3503's wider
strict-volume padding rule is a separate contract.

The opt-in [selector.py](selector.py) uses the inherited literal Count tapes.
No input-dependent integer is decoded during selection. It returns the same
seven exact plan Counts, or the documented no-fit sentinel. No default backend
or frozen source changes. All changes are inside this package.

## Evidence and replay

Python 3.12 and the standard library suffice, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/saturated-body-borrowing
python3.12 -W error -B scripts/check_research_commit.py --package research/saturated-body-borrowing --check-source-history
```

Use an existing private external TMPDIR for the source exports and caches.
The direct commands also work in a complete committed Git-free package export:

```sh
python3.12 -I -W error -B research/saturated-body-borrowing/verify.py
python3.12 -I -O -W error -B research/saturated-body-borrowing/verify.py
python3.12 -I -O -W error -B research/saturated-body-borrowing/independent.py
python3.12 -I -O -W error -B research/saturated-body-borrowing/controls.py
```

[RESULT.json](RESULT.json) binds 900 literal complete Count plans, 120 capped
powers, 1920 direct integer cases and ten boundary/failure controls. A separate
no-import inverse-depth/slab implementation reconstructs the complete census.
Seven actual optimized CLI corruptions reject bad powers, lost final radix
rows, omitted compatibility, source/comparison drift and a Boolean receipt.

At reduced parameters e=1000000, q=2, m=2, r=1, W=Q=1 and w=1, the actual
selector returns k=50 and records a maximum runtime Count extent of 63 cells.
The old upper trial's power would have 500000 bits by arithmetic; it was not
executed or timed. The observer covers all runtime Count allocation bindings.
An earlier incomplete observer failure is preserved in the session evidence.
These are resource observations, not a runtime speed factor or all-input proof.

## Sources, credit and limits

Canonical base is 6f100d4bb5083f8c35d96fd95a539811c62f245c, priority revision 6.
[SOURCES.json](SOURCES.json) pins the exact canonical Count arithmetic,
ordinary proof and complete frozen source closure. The two retained PR3502
files are byte-authenticated comparisons at public head
232b3916e6331222278f6edd5a4b9d56731667d9. They require no foreign Git object
or noncanonical ancestry claim. Frozen historical notices remain unchanged.

Credit Hiroki Kumazaki/PR3502, Nick Petalas/PR3486/3246, Jose Manuel/PR2899/
2786/2808, Tekalign/PR3264, David Arias/PR2753, Ross Richardson/PR2420 and
their retained BIT, geometry, hosting and compiler lineage. count_math.py
adapts Jose Manuel's exact arithmetic definitions only by removing physical
source activation and the unrelated old selector. Nick Petalas. Apache-2.0.

The setup proof is conditional on the retained tape arithmetic/refinement.
There is no payload callback, selected GL64 execution, physical C0 admission,
new stock coefficient, supplier, cutoff, kappa or selected-frontier change.
Full-cover, completed leaves, source access, fresh fields, pointwise restoration,
precision/tape, physical costs and outer transfer remain separate obligations.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Bind the least plan to one real reduced ordinary invocation and check both
   padded returns, genuine high-field spectators, restrictions and fallback.
   Start with the existing execute_plan hook. The completed-callee and physical
   C0 source obligations remain the blocker; a matching setup plan is insufficient.
2. Apply capped comparison to PR3503's strict-volume predicate only after an
   exact successor contract and final-materialization bound are proved. The
   present covering result does not establish that different selector.
