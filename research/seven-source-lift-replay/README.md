# Second native replay of the length-20 triple-four exclusion

This independently implements PR4207 open question1, using the five-source/two-lift route explicitly suggested by **Nick Petalas**. The new result is an independent implementation and full replay, not a new mathematical method or a new connector alphabet. The predecessor is frozen at5da1b72f18915820618d14905ad01422ec0a8246.

For restored seven-source words with profile(4,4,4,2,2,2,2), no word covers all98 nonzero masks of weight at most4 in the unchanged one-root dirty F2 query contract. The projection proof reduces any hypothetical full cover to the enumerated candidates. **95 is the maximum only among lifts of full56 six-source projections.** Other words are rejected by a necessary projection condition; this package does not claim their global maximum is95. A nonfull six-source projection yields at most55+42=97, which already excludes98. The940 maximum hits count raw filtered insertions, not canonical seven-source classes.

## Evidence and reproduction

- Native:51975 five-source classes;1257 full30 seeds;2287740 six-source insertions;17152 raw full56 covers;8576 unique, each appearing exactly twice. Every one of41550720 final candidate lifts is evaluated: zero full98, candidate maximum95 at940 raw lifts. Complete histograms and the sorted six-source list are retained in NATIVE.json.
- Independent Python oracle: choose the unique four-position block and match the other8 positions. Literal interval masks and prefix-pair masks agree on every one of51975 words. The complete five-source histogram agrees with the native result. The four-use label may appear at any first-appearance index.
- Integration: every8576 retained six-source word is literally checked, with both of its fourfold-label projections (17152 total). Four corrupted receipt/source controls reject. Python checks authenticate the large native histogram; they do not re-enumerate its41550720 lifts.
- Written projection/quotient completeness and separate proof/code review accompany the exact finite computation. This is not a formal-kernel proof or independent human acceptance.

Python3.12, stdlib only, generic registered checks:

```sh
python3.12 -B scripts/research_package.py --package research/seven-source-lift-replay
```

The actual **complete native replay additionally requires a C++17 compiler named c++** (no library dependencies):

```sh
python3.12 -I -B research/seven-source-lift-replay/native_replay.py
python3.12 -I -O -W error -B research/seven-source-lift-replay/native_replay.py
```

The launcher builds in a fresh temporary directory, waits for the full child, fails on compiler/runtime/output mismatch, and checks exact output bytes against NATIVE.json. It never substitutes quick controls for a missing native run. The focused seven-source-lift-native workflow runs both complete commands; generic Python CI only runs the four registered checks. Native source/provenance and the initial4.586s Apple clang21 single-thread run are retained separately. Compiler time and hosted status are separate receipts in the handoff.

## Scope and remaining obligations

This supplies the previously missing second implementation of one L20 exclusion. L16/L18 billion-class rows, the full218-call theorem, downstream uses of the older216 floor, physical compiler/caller costs, changed alphabets, ordinary/outer transfer and multiplication bounds are not recertified. No new supplier or kappa, merge or selected-frontier change. James Reed's earlier cheap-census and sealed-row audit is separate and explicitly left this native step open.

## Open next questions

Independently check one still-unreplayed L16/L18 row under a separate budget, or locate one actual downstream use of216 and inspect its caller. No absence-of-use claim follows from this session. Mechanisms outside this fixed alphabet require their own priced contract; the present exclusion does not apply automatically.

## Sources and credit

Nick Petalas/PR4207 supplies the original exclusion, explicit second-replay request and suggested five-source/two-lift route. Retain nightangelflowerwin-ops/PR4079/3780, commdata2338/PR2397, Cinna Davis/PR2229/2236 and Ross Richardson/PR943 for connector/projection/readout-cost lineage. James Reed/rcfc-jreed supplies the separate cheap-census/receipt review (PR4207 issuecomment6294899460). The two minimal unchanged PR4207 exports retain original source paths/hashes in SOURCE-PINS.json and an own-branch ancestor. Substantial OpenAI Codex assistance includes coordinating integration, primary C++ implementation, separately frozen matching-based oracle and separate proof/code review. Apache-2.0; no independent human/formal acceptance.
