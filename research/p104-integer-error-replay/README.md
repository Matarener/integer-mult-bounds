# Exact integer replay for the complete P104 precision contract

The complete PR5826 precision replay now has an exact integer backend for its
ideal input, signed error and transposed passes. A proved common dyadic scale
replaces Fraction operations in the inner loops. Every division is checked;
no floating or modular result decides acceptance. The word, full799-coordinate
endpoint, all25,984 events, signed coefficients, guards and six source rejection
controls remain unchanged. See [PROOF.md](PROOF.md).

The local complete-process median falls **24.091 to 4.301 seconds**
(**5.60x**, 82.1% less wall time). The host was not reserved:
baseline runs range from 19.791 to 31.149 seconds; candidate runs range
from 3.259 to 9.810 seconds. `BENCHMARK.json` records six serial fresh-process runs of the complete baseline
and candidate, with code hashes, all receipts and the local timing limits.
The candidate still authenticates and extracts the frozen source, executes the
literal attaining oracles, and compares the full source result. It has no
persistent cache. Qualification is a separate cost and is not hidden in the
claimed runtime.

Run the fast complete replay:

```sh
python3 -I -B research/p104-integer-error-replay/verify.py
```

Run the full independent arithmetic qualification:

```sh
python3 -B scripts/research_package.py --package research/p104-integer-error-replay
```

Qualification compares the entire original/candidate result, every actual
signed witness row, the ideal metadata and all local weights. It also checks120
separate dyadic words with4,240 events, varied defect sites, reset, COPY and
cancellation, plus three integer-contract rejection controls. The source's six
controls remain active in every normal replay. `RESULT.json` records this scope.

To repeat timings with Python3.12, run `benchmark.py --output /tmp/p104-error-times.json`
from this package directory. Six complete processes run in sequence. Local
macOS timings do not establish Linux or hosted CI performance. Python3.12 and
the standard library suffice. The source export and source NOTICE files are
retained unchanged. Registered, source-corruption and read-only Git-free
optimized checks are separate from timing.

`contract.py` adds four explicit parameter edits to the source runner and removes
its old CLI. `CONTRACT-EDITS.json` authenticates that adaptation. The backend is
passed as an ordinary argument. No runtime monkeypatch or import hook is used.
The candidate keeps the original literal scalar and reverse-cut oracles.

## Open next questions

- Reproduce the complete six-process measurement on an idle Linux runner. Keep
  all endpoint, error and failure checks, and report qualification cost separately.
- If a later word needs new operations or nondyadic coefficients, prove a new
  representation contract before using this backend. This package rejects them.
- Bind actual native/rounded child and reset implementations to the retained
  precision theorem. A faster replay does not discharge those assumptions.

Source PR5826 at58f93cf41751920f3d6766a39caccc2974ce18b0. Credit PR5819,
Adam Gall, ywz65, PR2878, Mason Hale/PR5811 and all retained P104/native/compiler
sources. New backend and qualification by Ali Romman with substantial OpenAI
Codex assistance; no subagents. Apache-2.0. No new kappa, frontier change,
physical supplier admission or independent human acceptance is claimed.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
