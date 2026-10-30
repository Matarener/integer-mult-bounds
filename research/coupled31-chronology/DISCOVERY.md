# Search record and limits

The assigned target was 31 leaves, two coupled ports, and five rank-two thin
connectors. Main and active claims were refreshed first. PR5681 had supplied
static maps for this target; no new static construction was needed. PR5701
had separately qualified two characteristic-zero lift contracts.

The first new calculation used the thin row-space basis in the mixed
chronology relation. Left multiplication by one stage projection isolates
the prefix of every other stage. Untouched stages force the affine row map
to lose a dimension whenever a prefix determinant becomes too large.
Iteration gives the proof in PROOF.md. Thus the requested endpoint is
impossible, before any larger synthesis or native compilation.

The complete source tariff with the new rank lower bound then rejects every
one- or two-port paired-star caller at saving .00256. The proof uses an exact
tangent, so it does not leave an unsearched large-leaf range.

Two bounded seed searches tested larger coupling as a possible next route.
Both used g=3,d=4, arbitrary compatible rank-two full query halves, and all
eleven call positions as solver variables. The fixed five rank-two thin maps
use the PR5681 F/G/E formula. Their leaf signatures are `(0,1,1)` in one run
and `(1,2,3)` in the other. The sum and square-zero identities hold in both.
Each run checks the full first mixed coefficient and the pairwise pure stage
coefficient. Any SAT model is then passed to the retained complete polynomial
replay, which keeps all stage exponents. Both runs reached their 60-second
solver limit without a model. They are **unknown**, not obstructions.

```sh
python3.12 -m venv /tmp/coupled31-discovery
/tmp/coupled31-discovery/bin/python -m pip install z3-solver==5.3.2.0
/tmp/coupled31-discovery/bin/python -B research/coupled31-chronology/discovery/coupled_seed.py --pattern pair --timeout 60000 --models 8 --output /tmp/coupled31-pair.json
/tmp/coupled31-discovery/bin/python -B research/coupled31-chronology/discovery/coupled_seed.py --pattern triangle --timeout 60000 --models 8 --output /tmp/coupled31-triangle.json
```

The actual environment was Python 3.12.13 on macOS arm64, with Z3 5.3.2.
The two saved JSON files retain the precise version, pattern, timeout and
unknown reason. Timings and solver progress can vary. The default verifier
does not import the solver or treat a timeout as mathematical evidence.

A smaller projected-chronology census shows why a dimension bound alone is
not a sufficient endpoint test. Of 19,440 ordered three-stage rank-one flags
over F2, 9864 admit a one-extra-row representation of the extracted S_jk
differences. They are necessary-condition candidates only. The census covers
six flags per stage and all 90 words with two occurrences of each label.
It does not specify thin matrices, their call order, or a full endpoint.

```sh
python3.12 -B research/coupled31-chronology/discovery/row_signature_census.py
```

Its saved JSON contains four examples. Compare the counts and examples;
elapsed seconds are not a correctness criterion. No claim of a new caller
comes from this census.

The next investigation of a cheap five-map target must use larger port
coupling and noncommuting full projectors. The commuting-projector count
proof in COMMUTING.md excludes five maps at both 13 and 31 leaves. It also
supplies a complete word at the larger map-count bound. WORD31.json and its
negative complete recursive price are retained as a control.

No changed native supplier, practical runtime gain, or kappa improvement
was found. All failed or incomplete searches keep their stated scopes.
Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
