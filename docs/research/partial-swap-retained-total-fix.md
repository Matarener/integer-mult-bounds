# Restore retained-total partial-swap verification

This is a verifier regression fix, with no new κ or runtime-speedup claim.
The reviewed starting tree is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

`partial_swap.graph.graph(h)` adds the local empty-exclusion output `()`.
`SharedPointCircuit` lifts that output to the singleton target `(common,)`,
representing a retained full pair-star total. The digest optimization introduced
in [PR2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039) unpacks
all targets as triples. Consequently even `graph(6).verify()` raises
`ValueError: not enough values to unpack (expected 3, got 1)`. The h25 producer
used by `make copied-fixed-reversed-producer` and `make verify` fails there too.
Existing equivalence tests constructed exclusion-only graphs, missing this case.

The repair joins the target's integer entries with commas inside the same JSON
array delimiters. For both singleton and triple targets these are exactly the
bytes emitted by the historical `json.dumps(..., separators=(',', ':'))`
verifier. Sorted traversal, newline boundaries, node encoding, topology,
disjointness, support, core and union assertions are unchanged.

New tests compare whole receipts to the pre-optimization verifier on retained-total
graphs of sizes 6, 8, 10 and 25, and compare h25 against the frozen
`research/copied-fixed-reversed/producer-input-25.json` scalar receipt. A negative
control replaces a full retained total with a proper excluded-pair sum and
requires both verifiers to reject it. Existing exclusion-only equivalence and
support-corruption controls remain in place.

The live partial-swap certificate is regenerated with its own generator. Exactly
one source hash changes; all mathematical values remain byte-identical. The two
existing optimization test suites and package verifiers bind the repaired source
hash. Their frozen baseline files, provenance manifests, performance receipts,
and historical source commits remain unchanged. No archived mathematical
certificate or expected circuit digest is edited.

## Reproduction

From the repository root, with Python 3.12 (the producer also needs a C++17 compiler):

```sh
python3.12 -B scripts/partial_swap_network.py
python3.12 -B -m unittest discover -s tests -p 'test_partial_swap*.py'
python3.12 -B scripts/research_package.py --package research/partial-swap-digest
python3.12 -B scripts/research_package.py --package research/partial-swap-init
make copied-fixed-reversed-producer
```

The package checks include h46 receipt equivalence, optimized-Python digest
checks and certificate pin-only comparisons. Production support assertions are
historically disabled by `python -O`; the negative controls run without `-O`.
This repair does not alter that inherited interface.

## Validation on the repaired source

- Python 3.14.7 focused suite: 16 tests pass, including the new negative control.
- Python 3.12.11 registered `partial-swap-digest` and `partial-swap-init`
  packages: both pass their complete normal/optimized verification and tests.
- `make copied-fixed-reversed-producer`: exit 0. Fresh h25 DAG, all 96,273
  distinct matrix profiles, five-prime reconstruction, positive labels,
  matching and the separate copied CRT audit pass.
- `make verify`: exit 2 after the repaired producer and full geometry checks
  pass. The next historical witness rejects its old source pin (see below).
- `git diff --check`: pass.

The unchanged h25 scalar digest is
`69283632099c012ae00cf1e9ab5b1f0757912944ff0708aa6cbf7633d841fd88`;
the exported DAG hash is
`ab28c3eba56b4b494f659b833c5aba4bb3e1e2225c3294411edf51a3999f1d03`.
The repaired source hash is
`5a0646a50b9f3e8ea55168620a78e8853b0ab810517cefc8cfb8696aedee278a`.

The broad historical sweep next fails in
`research/copied-fixed-reversed/witness.py:verify_sources`: its frozen manifest
requires `shared.py` hash `81e9af92cdf38243a540cdcff2062778e449467848d444da37a9553c12ca4c34`,
whereas pinned main already contains
`7290bd639600aecff11941d3faf95c9ce95589125cc6a7f7440fb86af7a0f17c`.
Comparing the manifest and source directly at the pinned main commit confirms
this mismatch predates this repair. The manifest remains unchanged; this PR does
not claim that the complete historical sweep passes. The selected cold replay,
Lean and unrelated historical sweeps were not rerun for this verifier-only change.

Open next question: separately reconcile historical witness provenance with live
tooling, retaining explicit equivalence evidence and immutable original pins.

## Scope and credit

Douglas R. Colkitt authored the shared-point and exclusion circuits; icekylinx
adapted the partial-swap producer; Wentao Li (VictorLiwentao) contributed the
PR2039 optimizations. The h25 producer credits the PR36/PR21 base-two graph,
PR32 structured profiler and Zhihao Chen's PR29 label audit. All existing license
and attribution notices are preserved. SovereignSteak prepared this repair with
OpenAI Codex assistance.

No asymptotic construction, conditional hypothesis or selected record changes.
Finite verification here does not prove the full conditional multiplication theorem.
