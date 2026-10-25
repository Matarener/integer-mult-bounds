# Conditional κ = 0.00300105: fresh helper retiming on query-thinned controllers

This builds on the stronger [PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440)
found during the requested 20-minute frontier check. After auditing its exact
head, replace all 19 full complex native calls by the verified fresh-helper
unit of `research/fresh-helper-boundary`. The main controller, 16 paid query
shears and stronger ordinary BIT supplier stay those of PR4440. The proposed
conditional bound is

```
T(n) = O(n (log n)^(1 - 0.00300105)).
```

The gain is **0.00004105 (about 1.39%) over PR4440's 0.00296**,
**about 11.71% over PR4416's 0.00268647**, and **30.48% over the pinned
selected 0.0023**. The new result is author-checked and awaits review; it
retains the conditional source implementation and transfer contracts.

| Complete complex raw invoice | PR4440 | Combined construction |
| --- | ---: | ---: |
| Full native calls / paid query shears | 19 / 16 | 19 / 16 |
| Independent productive fields | 11,560 | 11,560 |
| Paid calls | 72,902 | **69,273** |
| Productive / paid rank mass | 258,271 / 257,471 | 260,798 / 259,998 |
| Rank-one surplus | 800 | 800 |
| Proposed conditional κ | 0.00296 | **0.00300105** |

The native retiming removes **3,629 paid calls**. It changes 117 helper
entrances, 42 exits and 395 scalar frames in each full invocation, with exactly
the same main operator and complete owned-center program. Thus substitution
is a native operator equivalence, not merely replacement of a histogram.
Every helper is still a distinct arbitrary original input; query copies and
centers receive no productive credit. [PROOF.md](PROOF.md) gives the join.

The exact changed-profile root is enclosed by

```
0.0030010541830 < root < 0.0030010541834.
```

An interval proof covers every real `0<C<1`, giving a fixed-profile ceiling.
Only about `4.18e-9` headroom remains; further substantial progress needs another
profile. At tested saving `0.003001052`, tensor power 1024, cutoff `20^1024`
and target floor `21^1024` pay both tails. The changed profile needs the
explicit gamma limit `97/100`; copying PR4440's `31/32` limit would fail.
PR4433's general logarithmic compiler supplies an explicit sufficient rank
recorded in RESULT.json. Its enormous word is specified algorithmically and
has not been materialized. The unchanged stronger BIT supplier, atom power
0.004, all nine outer rows, 54 predicates and four functional guards are retained.

## Replay and source pins

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/fresh-helper-thinned
```

Normal replay freshly runs **both complete source verifiers**, then independently
counts every full/query/idle event and checks the combined moment, root ceiling,
charged tails, finite rank, scalar/route bound and entire consumer. The `--write`
authoring option assembles only the new receipt from previously audited source
receipts; normal replay never uses that shortcut and does not write.

The exact predecessor heads are `40e22a83ed660d3d6074c4f2dbf14bfb621eee51`
(PR4440) and `ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9` (the first version of
this helper-retiming PR). SOURCES.json pins all transitive live inputs against
those commits or canonical `3a23e9d9d`. Both predecessor commits are actual
ancestors of the submission. Their source files are unchanged. See
[AUDIT-4440.md](AUDIT-4440.md) and [VALIDATION.md](VALIDATION.md).

## Scope and credit

The native/all-column, permitted physical movement and whole-job matching,
owned-erasure, precision, finite-template, analytic, fixed-tape, prime and
exact-recovery premises remain conditional. No selected-record change, formal
verification, independent human proof review, global optimum or practical
runtime claim is made.

Credit: PR4440's query thinning, stronger BIT and owned-query construction;
zxv's native controllers and higher-moment/logarithmic compiler work;
Jacob Alan Sussman's mixed integer flow; the PR4416 paid-completion construction;
and the retained native, Clifford, BIT, precision and outer contributors.
The helper boundary retiming and combined construction were prepared for
1337isnot1337 with substantial OpenAI Codex assistance, Apache-2.0.
All predecessor notices remain intact. No subagents were used.

## Open next questions

TASK.json specifies independent all-column/owned-query review and a changed
multi-frame or controller topology as the next useful work. Neither the finite
path screen nor the fixed-profile ceiling proves global optimality.
