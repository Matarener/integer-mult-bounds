# The f(7) records agree; a second engine at length 22

**Navigation index plus a complete second-engine replay of the length-22 census. No new bound, no κ, no
supplier or frontier change.** The model throughout is Ross Richardson's PR943
abstract singleton prefix-walk model. Seven immutable sources, singleton
additions, paired readouts, eventual restoration. A restored word is universal
iff its prefix set `P` satisfies `P + P = F2^7`.

## The question

Item 5 of petalas's [consolidation handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19230473)
says the records disagree on f(7). The two records are #3058, titled "f(7) = 24",
and `research/f7-independent-full-replay` (#3333), which says `{22,24}` and does
not cite #3058.

**They do not disagree.** #3333 is a length-20 replay. It says it "does not
decide whether length 22 is attainable". Its `{22,24}` is a scope limit, not
a contrary finding. Length 22 is excluded on main by two routes that share no
search code. Every record below is `partially_reviewed` in
`docs/research/pr-ledger.json` at the base commit. Archival merge is not
scientific approval.

## Record map

| Step | Route | Records on main | Independent coverage | Still open |
|---|---|---|---|---|
| L ≤ 20 excluded, so f(7) ≥ 22 | census | #2973 (Nicholas Stone), corrected census | #3005 (Nick Petalas, separate C++ engine), #3333 (1337isnot1337, separate C engine) | none at this step; #2542/#2634/#2691 used the bit-0 prune and are retired (#4946, JoyboyBrian) |
| L ≤ 20 excluded | covering code | #3058 (conorholds) §1–2: `ell(7,2)=19` gives a 20-point cover floor, and the published 19-point classification gives L ≥ 24 for a 20-point cover | #3728 re-checks the `\|P\|=20` step. #3732 (James Reed) excludes two of its five representatives by a multiplicity count. | the two published results are imported, not re-derived |
| L = 22 excluded | covering code | #3058 §3 (21 distinct prefixes), §4 (patterns A and B via f(6)=16, f(5)=12), §5 (complete small-path search) | engine audits: capacity #3224, propagation #3244, domain #3261, search #3276, caller #3287. SAT proofs for 4 of the 77 B cases (#3360). | §3 is checked by #3058's own two implementations, but no separate audit package covers it on main. #3360 lists it as out of scope. Pattern A has #3058's own Python port and solver checks. The other 73 B cases rest on the single native search. |
| L = 22 excluded | census | split domain #3708, independently #3712; probes #3731 and #3818; closure #4221; receipt binding #4871 | before this package, every split ran on one engine (#3818's `union_census.c`). **This package adds a second engine for the splits below.** | #3899 (tiny-domain audit of the union prune) is open. Both engines share #3005's union-support bound and #3708's domain and symmetry. |
| L = 24 attained | witness | #1185 (Douglas Colkitt) Gray cycle; #2973's `UPPER-WITNESS.json` | `verify.py` checks `010201030102010345464546` directly | none |

Consumers cite only #3058 for f(7) = 24: `research/eight-source-singleton-floor`
(#5234), `research/eight-source-lift-obstruction` (#5430) and
`research/seven-source-duo-21-calls` (#6005). They use only the value, so the
census route serves as well. It avoids the two imported literature results, but
it needs #3708's split domain and the pruning proofs of #2973, #3005 and #3818.

#4221's second open question (re-derive the domain inside the verifier) is
already answered by #4871. Its first open question, a second engine at length
22, is what the next section addresses.

## Second engine at length 22

`research/f7-union-support-audit/census.cpp` (#3005, Nick Petalas) is gated at
`L <= 20` only through `max_length`. `verify.py` rebuilds it from the pinned
bytes with exactly two changed lines: `max_length = 22` and the matching error
message. It uses #3005's compiler flags.

The two engines are separately written but not mathematically independent.
#3818's `union_census.c` is #2973's `corrected_census.c` with #3005's
union-support bound ported in. That bound's proof (in #3005) is therefore a
premise of both engines, and a flaw in it would affect both. What the second
engine removes is the single implementation: state representation, traversal,
the other prunes and the sharding. The proof in #3005 is written for general
even L. Its small-domain oracle checks (L ≤ 12) do not touch the changed
constant.

Controls, all rerun by the default `verify.py`:

- **Unchanged at L ≤ 20.** On L=18 `(9,9)` and L=20 `(10,7)`, `(10,8)`,
  `(9,9)`, every summary field equals #3005's `FULL.json`.
- **Depth-22 leaves work.** A capped n=6, L=22 `(11,11)` run finds hits. Every
  hit is checked by direct XOR coverage as a simple restored universal word.
- **Fails closed.** A capped n=7 run exits 2 with `complete=false`.

Results at n=7, L=22 (LOCAL-ONLY; full receipts in [RESULT.json](RESULT.json)):

| Split | This engine: entered nodes | Hits | Status | Prior engine (nodes) |
|---|---:|---:|---|---|
| `(11,11)` | 37,567,052,539 | 0 | complete, exit 0 (3751 s wall) | #4221 cover sum 55,385,607,437 |
| `(11,10)` | 40,743,043,536 | 0 | complete, exit 0 (4188 s wall) | #4221 cover sum 52,957,641,635 |
| `(11,9)` | 11,942,611,230 | 0 | complete, exit 0 (1537 s wall) | #4221 cover sum 14,058,107,415 |
| `(10,10)` | 37,400,857,165 | 0 | complete, exit 0 (4117 s wall) | #4221 cover sum 44,378,511,529 |
| `(11,8)` | 973,631,241 | 0 | complete, exit 0 (130 s wall) | #3731 1,349,702,650 |
| `(10,9)` | 6,624,261,154 | 0 | complete, exit 0 (830 s wall) | #4221 cover sum 7,027,617,655 |
| `(11,7)` | 8,613,944 | 0 | complete, exit 0 (1 s wall) | #3731 8,784,744 |
| `(10,8)` | 238,010,457 | 0 | complete, exit 0 (32 s wall) | #3731 597,933,297 |
| `(9,9)` | 386,427,869 | 0 | complete, exit 0 (50 s wall) | #3818 388,563,293 |
| `(11,6)` | 1,020 | 0 | complete, exit 0 (0 s wall) | #4221 cover sum 2,247 |
| `(10,7)` | 699,412 | 0 | complete, exit 0 (0 s wall) | #4221 cover sum 700,909 |

Entered-node counts track the #3731/#3818 node counts closely. `(9,9)` gives
386,427,869 here against 388,563,293. `(11,7)` gives 8,613,944 against
8,784,744. Throughput was about 7.5 M entered nodes per second per core on a
shared 10-core machine.

**All eleven splits close on the second engine with zero hits.** Every census-route length-22 exclusion now rests on two separately written engines. The engines still share #3708's domain and symmetry premises.

The census route still imports #3708's rotation symmetry, so only `s >= t`
runs. It also imports its four necessary conditions, as #4221 does.

## Reproduce

Requires Python 3.10+ and a C++20 compiler; no Python packages.

```sh
python3 -I -B research/f7-record-map/verify.py                       # ~5 s
python3 -I -B research/f7-record-map/verify.py --splits 9:9,10:8      # ~1 min
python3 -I -B research/f7-record-map/verify.py --full --workers 8     # every completed split
python3 scripts/research_package.py --package research/f7-record-map --check-only
```

The default run authenticates every live input and checks each quoted sentence
of the record map against its pinned README. It also checks the witness and
the #4221 receipt closure (7 + 4 = 11 splits), then runs the controls above
and replays `(11,6)`, `(10,7)` and `(11,7)` exactly.

## Open next questions

1. **A tiny-domain audit of the union prune.** #3899 (open) does this at `(n,L)=(4,8)`. Both engines depend on that bound, so it is the main shared premise left. First step: review #3899. Blocked by: none.
2. **Audit #3058 §3, the 21-distinct-prefix case, separately.** #3058 checks it
   with two implementations of its own. No separate audit package covers it
   on main, and #3360 lists it as out of scope. First step: re-derive the
   degree-four/degree-two walk structure and the 16 surviving classes from
   `table6.json` without reading #3058's checkers. Blocked by: none.
3. **The remaining 73 pattern-B cases.** #3058 says its B exhaustion "rests
   on this single native implementation". #3360's SAT translation covers 4 of
   the 77. First step: run that translation on the next named template.
   Blocked by: solver and proof-checking budget.

## Credit

Item 5 and the question are petalas's. The engine is Nick Petalas's (#3005),
unchanged except for the length gate. The routes belong to conorholds (#3058),
Nicholas Stone (#2973), Nick Petalas (#3708, #3728, #3731, #3818, #4221, engine
audits), James Reed (jwr404, #3712, #3732), codyw912 (#4871), 1337isnot1337 (#3333, #3899),
commdata2338 (#3224), krzysztofwojt (#3261), JoyboyBrian (#4946), Douglas
Colkitt (#1185) and Ross Richardson (#943). Prepared by Claude Opus 5.5 for
JosieElliston; see TASK.json for the AI-assistance disclosure. Apache-2.0.
