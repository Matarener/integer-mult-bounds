# An actual P104 residual consumer and its return cost

**Partial source-bound construction and conditional budget decision. No new kappa.** This package follows PR [#3882](https://github.com/CrocSwap/integer-mult-bounds/pull/3882), but does not repeat its tail, eight-replacement theorem, or original channel construction as new work. It identifies an actual consumer of the eight encoded `q` fields, rather than inventing an unused readout.

The consumer is the frozen native word's final query cleanup, zero-based events 3642 through 4057. Its 416 updates `Q += D x` factor exactly through `q = x_J + B x_N`. Moving the existing correction tail immediately before that cleanup and replacing the original reads by `Q += T q` preserves the complete 280-field endpoint, including all 72 arbitrary dirty helpers. There are 32 nonzero coefficients in T instead of 416 in D. Under the specified read-only-donor lowering, this replaces 832 unit Gaussian ADDs by 64, saving 768 array ADDs, or 786,432 real component ADDs for 512 complex words per array. This is not an optimal scalar circuit claim.

The second result prices the old source-preserving return contract. An explicit adapter returns every `X_i=x_i` in FULL and every corrected `Y_i=x_i+y_i` in its target hyperplane. It costs 192 formal rank-one transports, 960 unit array ADDs, 104 exact halves, and 104 restoring doubles. A chart-occupancy argument proves that 192 is sharp in the stated nested-transport, fixed-occupancy model. It adapts the retained terminal-floor proof method, with a different starting boundary and 96 necessary information exports.

The recursive rank profile does not improve. A conditional paired-chain screen, explicitly granting this same profile and full net endpoint credit to every stage, still rejects all odd stage counts and every finite number of fully paid auxiliary banks. The decision remains **NARROW**. Keep the useful scalar consumer and exact return adapter; do not treat scalar savings as a new recursive supplier.

## Sources and the actual chronological join

Canonical main is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. PR3882 is pinned at `9d56eeedbed5e3e9bbbc8c189d66f14cf15b6067`. Its geometry and result are retained byte for byte under `inputs/`, with original origins and a source-retention ancestor in SOURCES.json. The actual 4,058-event word and full geometry are authenticated from the unchanged main files. No predecessor executable is imported.

Use the predecessor pivot indices `J=[0,1,3,6,22,31,93,103]`, with N their 96-port complement. With `A=G/2` and `B=A[J,N]`, the exact root geometry gives

```
A = [[I, B], [B^t, B^t B]],     q = x_J + B x_N.
```

All 384 nonzero B entries are signed halves. At the actual cut before event 3642, X holds x in FULL, Y holds `v=y+A x` in its final hyperplanes, and `Q=h_Q-Dx` in FULL. The other 64 dirty helpers are already restored. Every private lifetime is closed. The actual suffix gives `D=T[I B]`; its 32-entry matrix T is printed in PROOF.md and the frozen RESULT.json.

Execute the PR3882 tail at that cut. It neither reads nor writes Q. It leaves the corrected sums w on `X_N,Y_J`, q on `X_J` in FULL, and v_N on `Y_N` in FULL. The 64 unit cleanup ADDs then read only X_J and target only Q. They restore Q to its arbitrary original dirt while leaving the other outputs unchanged. This closes an actual missing consumer implication. It does not restore the original X bank or make residual erasure legal.

The inherited prefix has 3,642 events. The new suffix has 1,728 literal events, including the unchanged 1,664-event tail, so the joined representation has 5,370 events. Counting each signed-double cleanup as one weighted ADD instead gives 5,338 events. The two conventions are kept distinct. The 208 new frame conversions are still formal uses of the inherited hyperplane/FULL pairs, not a newly replayed native implementation.

## Cost and coverage decision

| Quantity | Encoded exit and actual cleanup | With old source-preserving return |
| --- | ---: | ---: |
| Combined local native rank mass | 2,576 | 2,768 |
| Additional return-adapter rank mass | 0 | 192 |
| Optimistically creditable net frame progress per call | 2,312 | 2,312 |
| Local rank mass above that progress | 264 | 456 |
| Nine-stage paid-mass lower bound | 62,280 | 64,008 |
| Nine-stage capacity | 60,736 | 60,736 |
| Nine-stage deficit | 1,544 | 3,272 |

These are native-rank and conditional coverage quantities. They do not include a scalar-to-recursive tariff conversion. The scalar cleanup has no additional native calls, banks, divisions, source writes, or frame changes. Consequently it leaves the PR3882 profile `(1282,58,86,104,48,24,8,8)` unchanged. The return adapter increases it to `(1474,58,86,104,48,24,8,8)`.

The budget uses `s=2p+1`, `m=8s+1`, and `W=104(s-1)` per replica, with one unpaid coordinate per original family. Grant all s calls the same local profile and net credit above; a compatible dual orientation is not constructed. Grant zero other scalar, control, precision, or hosting cost. For b fully paid auxiliary banks and `0<=a<1`, the resulting necessary screens are

```
M(a) >= 1 + (160s+104)/(m(W+b)) > 1,
M_return(a) >= 1 + (352s+104)/(m(W+b)) > 1.
```

This is a proof for that explicitly hypothetical equal-profile template. It does not establish an actual owner embedding, cover arbitrary cheaper opposite orientations, or reject every changed consumer. The old bare width-nine `46/45` screen and PR3620's different 358-bank dual threshold are not substituted for this calculation. At nine stages, even reaching strict contraction at saving zero requires total net savings plus genuine extra credit, after added charges, exceeding 1,544 or 3,272 respectively. Passing that necessary test would still not prove a positive-saving supplier.

## Verification and evidence status

From a complete checkout, with Python 3.12 and the standard library,

```sh
python3.12 -B scripts/research_package.py --package research/p104-residual-consumer
python3.12 -B scripts/check_research_commit.py --package research/p104-residual-consumer --check-source-history
```

The registered commands run the primary checker normally and under `-O`, the separately implemented integer-matrix checker, and 16 semantic/control test groups. Default verification is read-only. Each source-bound checker executes the actual 3,642-event prefix, authenticates the literal cleanup matrix, and checks the new full 280-column endpoint. The primary checks exact binary nesting and all original cut frames. The second checker uses dense scaled integers, different root enumeration, and a different block schedule. Both compare the entire endpoint against the exact predecessor digest. The primary additionally tests every one of the 96 information-export witnesses for the written return floor.

The portable algebra-only commands are deliberately weaker,

```sh
python3 -I -O -B research/p104-residual-consumer/verify.py --algebra-only
python3 -I -O -B research/p104-residual-consumer/independent.py --algebra-only
python3 -I -O -B research/p104-residual-consumer/test_verify.py
```

Those commands passed locally on CPython 3.13.5. They do not authenticate the complete native source or actual prefix. Subsequent source-bound hosted results belong in the PR handoff with exact head and run identifiers. The frozen canonical result digest is `cdf6210cb348566f7647722f05c695d268b220909fb12997d12255817985f43f`; normal replay never regenerates it. `--write-result` is an explicit authoring operation.

Controls reject missing, early, sign-flipped, and duplicated cleanup, wrong donors, missing restoring doubles, wrong output locations, and missing return transports. Actual isolated CLI copies reject typed-result corruption, changed geometry bytes, and missing main sources. Tests remain active under `-O`. They corroborate, rather than replace, the arbitrary-length written occupancy proof and all-stage conditional budget proof.

No native phase/compiler replay, physical signed-floor execution, complete physical width bound, selected cold replay, all-size theorem, independent human acceptance, or proof-kernel verification is claimed. The inherited prefix retains its owned live-copy discard semantics; it is not relabelled as a reversible zero erasure. Formal chart execution and an actual physical recursive supplier remain separate claims.

## Credit and overlap

Credit Rohan Arun / PR1972 and Chafik Boukhalfa / PR1991 for the channel, Adam Gall / PR1940 for its schedule, and the retained geometry/native lineage. PR3882 supplies the correction tail and residual coordinates. The retained `p104-terminal-correction-floor` package, prepared for Adam Gall with OpenAI assistance, supplies the occupancy proof method and the prior source-preserving complete-coverage warning. Dominik Scholz's larger-gain model, Sagar Thakrar / PR1012, and Douglas Colkitt supply the paired-chain and coverage context. Their bounds and constructions are not claimed as new.

PR3609 is related in-place pivot work on a different dual entrance. PR3620 and Sagar Thakrar's PR3782 concern different profiles. PR3810 has a different fixed-cover/preconditioner contract. New PR3894 constructs a direct source-preserving end-cut correction; PR3907 reviews a monotone lifetime bound, and PR3915 checks one flag coefficient. None is used as a theorem dependency for this splice. The recorded bounded overlap is not an exhaustive novelty certificate.

Prepared by Clear1nsight with substantial OpenAI assistance in mathematics, implementation, verification, and documentation. The two implementations share this assisted session and the same frozen sources, and are not independent human review. New work is Apache-2.0. Predecessor bytes, attribution, and notices are retained.

## Open next questions

A next consumer must exploit more than this scalar cleanup saving. First name its actual required outputs and opposite orientation, derive the changed full coverage law, and determine which native operations or net boundary obligations disappear. Stop when even a favourable complete lower bill remains above capacity. Neither decoded source recovery nor residual disposal is free.

A bounded native audit is possible without supplier expansion. First bind one changed-role hyperplane/FULL map and its physical entrance to the literal signed-floor implementation, with phase and arbitrary dirt. The present package does not establish that admission. A larger construction should proceed only after an affordable consumer and full cost allowance are demonstrated.
