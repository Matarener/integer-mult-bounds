# Discovery record

These files preserve the searches that led to the rank cuts. They are not
part of the registered proof replay and do not establish a physical caller.
No positive kappa result was found. The proof does not depend on solver trust.

## Common advancing stage

The initial idea used U=S*H8, where S moves the next eight-axis block and
fixes the central query axis. Before wraparound, U^d can retain 8d transverse
axes. This can escape the fixed involution D^2=I. It does not supply the
scalar controller needed to extract independent outputs.

`simplex_search.cpp` enumerates compatible binary projectors on four fields
and five normalized query positions. It treats D as a formal variable.
`simplex-census.json` covers all 32 full/thin masks. For the all-full mask,
all 16^5=1,048,576 choices fail the central-query endpoint. Every mask with
three or more full calls fails the complete coefficient-factor test.

```sh
c++ -std=c++17 -O3 research/shortest-controller-stage-capacity/discovery/simplex_search.cpp -o /tmp/imb-simplex-search
/tmp/imb-simplex-search 31 0
```

The signed census tests the all-full mask with inverse masks 0 through 15.
It is not a recorded enumeration of all 32 inverse masks. Some words factor,
but their retained degrees lose the optimistic profile. The command takes
the full mask first and inverse mask second. Do not reinterpret a normalized
degree as free inverse-stage work.

The Python discovery programs used Python 3.12, z3-solver 5.3.2.0 and sympy
1.14.0. The exact environment and raw responses are in `receipts/`.
`pair_search.py` checks necessary pair equations for a common positive
formal D. At n=4,6,8 the solver returned `unsat`; at n=10 it timed out.
Leading-only and tangent-only controls are satisfiable. No solver proof
certificate was exported. The pair equations do not themselves construct
or diagonalize a full word.

```sh
python3 pair_search.py --n 6 --seconds 60 --output /tmp/pair6.json
python3 pair_search.py --n 6 --seconds 60 --constraint tangent --output /tmp/pair6-tangent.json
```

Run these commands from this directory with the optional dependencies
installed. `solve.py` instead expands the whole query polynomial. The
four-field query screen returned `unsat`; six-field query and balanced
endpoint screens timed out. `rational_pair_search.py` tests a rational
analogue: n=2 is satisfiable, n=4 returned `unsat`, and n=6 timed out.
These are bounded discovery statements, not characteristic-zero theorems.

## Relations and coordinate reuse

`relation_search.py` imposes involutive stage labels. The tested single
relation on three interior stages at n=4, and on five at n=6, returned
`unsat`. The saved `colour-query-search.json` contains all 52 set partitions
of five interior stage positions: 17 returned `sat` and 35 `unsat`, with
no unknown response in that run. Each partition used a three-second limit.
The positive responses are query-equation witnesses, not full endpoints.

In particular, label patterns `[0,1,1,1,0]` and `[0,1,1,1,2]` pass those
equations. They invalidate the tempting claim that adjacent equal-label
cancellation must reduce every successful query pattern to one letter.
This failure led to a rank-capacity proof instead of a word-reduction claim.

`search_cuts.py` tests a separate finite linear-subspace cut. With seed 5593,
100 random common stages and all 1,395 three-dimensional subspaces of F2^6
gave 139,500 tests and no positive separator for the balanced six-field
profile. This is a failed finite separator search, not a universal barrier.

```sh
python3 relation_search.py --n 6 --seconds 60 --output /tmp/relation6.json
python3 relation_search.py --n 6 --seconds 3 --labels 1,2,2,2,1 --output /tmp/colour-control.json
python3 search_cuts.py --half 3 --rounds 100 --seed 5593 --output /tmp/subspace-cut.json
```

The registered verifier uses neither these solver responses nor their
search bounds. The retained rigorous result is in `../PROOF.md`. The
advancing operator route remains open; the involutive-axis theorem does
not exclude it. New work is by Ali Romman with substantial OpenAI Codex
assistance, with Cinna Davis's simplex and query-frame lineage. Apache-2.0.
