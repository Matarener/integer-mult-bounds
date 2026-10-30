# Validation and limits

Environment: Linux x86_64, CPython **3.12.14** (bundled runtime). Initial
factor discovery also ran on CPython 3.14.8. Standard library only. No
subagents, Lean build, Docker run or full historical suite.

Completed on 2026-10-21:

- `python3.12 -B scripts/research_package.py --package research/query-thinned-controllers --check-only`
  passes metadata and all 17 input pins.
- `python3.12 -B scripts/research_package.py --package research/query-thinned-controllers`
  passes the complete registered replay.
- `python3.12 -O -B research/query-thinned-controllers/verify.py` passes
  from a separate **Git-free export** containing this package and exactly the
  declared input files. Its RESULT.json agrees with the normal replay.
- The two external rejection controls also run in that Git-free export under
  optimized Python. Appending a comment to the pinned interval source rejects
  with `Changed source`. Changing an emitted QUERY_SHEAR to LOCAL rejects the
  physical-event equality check. Both altered export files were restored;
  no canonical predecessor file was changed.
- Internal controls execute omitted-clear and omitted-erase query words,
  reverse a query's actual orientation, change a Laurent coefficient, retain
  the old BIT cap or atom, close the complex/epsilon gap, omit layout, and
  request the unfunded outer endpoint. Their intended gates reject.

The exact native contacts include 896 complex forward/inverse checks and
111 rational binary charts. Both complete physical event lists are replayed.
Two rational interval implementations agree on the strict native moments.
The complete charged tensor tails, effective compiler ranks, ordinary BIT
cover/conversion and nine-row outer ledger pass. All 54 strict outer
predicates, three inherited functional predicates and the added stock guard
are retained.

The actual local full-native words and their all-column implementation are
reused from the pinned reviewed lineage. Their entire historical physical
stack was not rerun. New winning tensor/uniform words are specified by
finite algorithms; their enormous instruction lists have not been emitted.
No finite pass establishes an unconditional theorem or formal verification.

The committed-byte preflight and source-history check both pass after
committing the package, with all 28 package/input files matching and the pinned
canonical base in publication ancestry. Hosted CI is reported separately.
All reports retain the inherited native, whole-job, owned-erasure, fixed-tape,
precision, analytic, prime-supply and exact-recovery proof boundaries.
