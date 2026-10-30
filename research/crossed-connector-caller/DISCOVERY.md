# Discovery record

The new theorem replaces these bounded searches. It does not derive an
unbounded claim from their counts. `discovery/RESULTS.json.gz` retains the
JSON outputs under their original file names. The archive uses fixed gzip
metadata. It is data, not instructions or a registered proof dependency.

| Experiment | Coverage and result |
| --- | --- |
| Different C,D forward/reverse splits | All 75,600 relative orders: 71,880 degree-two and 3,720 degree-three contradictions |
| Four arbitrary minimum-rank aggregate connectors | All 3,150 relative orders: 2,995 degree-two and 155 degree-three contradictions |
| Arbitrary aggregate map in every gap | Fifteen paired-stage orders; each has a degree-three contradiction |
| Three calls per stage, arbitrary aggregate gaps | All 280 orders: 279 degree-three contradictions; word reduction gives a degree-four certificate for the remaining cyclic sweep |
| Four calls per stage | The cyclic sweep only; a bounded word-reduction certificate. This is not an order census |
| Three-way, zero-B matrix frames | 168 binary frames, 24 pair-compatible frames, 144 complete stage words; no compatible aggregate chronology found |
| Six arbitrary thin queries, three paired stages | Twenty orders; solver reports 17 unsat and 3 unknown. This first screen did not impose the separate stage-word conditions |
| Eight arbitrary thin queries | Sixty orders; 23 sat, 19 unsat, 18 unknown. Sat means necessary conditions only. The full word rejects some sat candidates |
| At most seven active queries in eight thin slots | Seventy orders; 22 unsat and 48 unknown |
| Grow a complete escape word by two leaves | Four fixed-source extension tests reported unsat: case11 with identical and independent new signatures, and cases13/20 with identical signatures. All retain eight thin factors and the old call order |
| Coupled ports, five rank-two thin queries | Eight orders at three leaves: two unsat and six unknown; no positive word |
| Three-stage cycle, two thin queries | Fifty basis-parameterized orders: 42 unsat, 8 unknown. Fifty direct-projector orders: 43 unsat, 7 unknown |

`ESCAPE-WORD.json` selects case 11 of the eight-query search. Its complete
word is checked again by the separate default checker. All fields and all
independent stage exponents are retained. Case 8 in that same search is an
example that passes the pure stage word and first mixed coefficients but
fails higher mixed coefficients. `MIXED-ONLY-CANDIDATE.json` preserves it, and
the separate checker rejects it.

## Discovery commands

The algebra searches use the standard library. Run them from the package
folder or give the full path. They write new JSON files beside their scripts;
the archived results remain unchanged.

```sh
python3 -B discovery/order_search.py --degree 2
python3 -B discovery/aggregate_search.py --degree 2
python3 -B discovery/gap_search.py
python3 -B discovery/multisplit_search.py --splits 3 --degree 3
python3 -B discovery/ideal_completion.py --splits 3 --degree 4
python3 -B discovery/m3_frame_search.py
python3 -B discovery/tournament_search.py
```

The original degree-four dense monomial expansion was interrupted before a
result because it was too large. `ideal_completion.py` uses bounded word
reduction and literal certificate expansion instead. It produced the retained
three- and four-way cyclic-sweep certificates. It is discovery code; it is
not a general decision procedure.

The finite matrix searches used Python 3.12.13 and `z3-solver==5.3.2.0`.
The default verifier needs neither Z3 nor the search code. The published
cycle tool uses the direct-projector parameterization; the earlier
basis-parameterized results are historical discovery data. The current
six-query tool includes stage-word constraints added after its first run.
These changes are stated so that a different replay is not treated as the
same frozen experiment.

```sh
python3 -B discovery/leaf_echo_search.py --thin 8 --cases 60 --timeout 4000 --seed 3
python3 -B discovery/leaf_echo_search.py --thin 8 --budget 7 --cases 70 --timeout 4000 --seed 3
python3 -B discovery/cycle_search.py --g 3 --thin 2 --cases 50 --timeout 5000 --seed 91
python3 -B discovery/coupled_five_search.py --cases 8 --timeout 10000
python3 -B discovery/grow_escape.py --case 11 --distinct --timeout 30000
python3 -B discovery/grow_escape.py --case 13 --timeout 30000
python3 -B discovery/grow_escape.py --case 20 --timeout 30000
```

The growth model retains every old query factor on the old coordinates and
the old call order. New full calls can enter any gap. It allows either equal
or independent signatures for the two new leaves. Its four negative results
do not exclude changing an old query or order, or other source words.

Time limits are milliseconds per solver call. A timeout is unknown. The
solver models and timing-dependent statuses are not independent theorem
certificates. A rerun can choose a different model. Use `check.py` to verify
the frozen full positive word, rather than expect a solver to emit identical
bytes.

## Orientation and boundaries

Canonical main was refreshed before selection and before the aggregate and
cycle pivots. Its base was `df0137efd35e11b4445734bf612bdd4c7ebc330c`, with
selected kappa .00310045 and priority revision seven. The complete remote
overlap refresh at 03:10 UTC covered 344 PRs and 4,952 Discussion records;
7,655 local HEAD note paths were not searched by the sparse overlap scan.
Targeted historical controller notes were then read. No claim of exhaustive
novelty is made. Active P104, Cao and G20 native-word claims were kept separate.

The scoped claim and changes are in Discussion5593, starting with
[the claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19187529).
PR5650 and PR5440 were comparison points, not source upgrades to the bill.
The pinned PR5599 tariff stays fixed. The stronger open BIT admission in
PR5653 does not itself supply a compatible complex caller.
