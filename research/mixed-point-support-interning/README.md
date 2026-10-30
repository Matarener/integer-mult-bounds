# Faster exact support interning for mixed-point construction

An opt-in compact interner reduces the complete fresh-process time for the
frozen `build(50,3,3,1,common=True)` workload by **24.2%** on the recorded host.
The median is 4.538 s before and 3.440 s after, including unchanged output
verification and complete structural hashing. Construction itself falls from
3.384 s to 2.246 s, a **1.507x** speedup. Five alternating fresh-process pairs
retain every sample and produce the same structural digest.

Claim type: an engineering improvement with a written exact-equivalence proof
and finite correctness evidence. No new supplier, kappa or selected-frontier
change is claimed. This answers Open next question 1 of Victor Li's
[PR #2150](https://github.com/CrocSwap/integer-mult-bounds/pull/2150), which asks
whether mixed-point `Circuit.add` and construction can be sped up without
changing the DAG. Its output-verifier improvement is a cited predecessor.

## Change

The original builder interns the complete integer bitmask of each support.
Repeated dictionary probes hash those large integers again. The new interner
assigns a fixed 64-bit key to each input and XORs the two operand keys when
forming a disjoint sum. A dictionary key selects candidate node IDs. It accepts
an existing node only after comparing its **complete integer support**. Unequal
supports with the same key share a bucket; they remain separate nodes.

The [proof](PROOF.md) shows that every successful valid addition sequence
retains node IDs, support sequence and the first argument pair of every node.
The summation trees, planner, caches, traversal, output masks and pruning are
unchanged. Hash consing and XOR-linear fingerprints are standard methods;
the contribution is this exact adapter and its measured construction gain.

The adapter is isolated here. `baseline/` retains four original source files
byte for byte. `candidate/` contains the new interner and two adapted source
files. The verifier checks their complete diff against declared replacements.
Shared scripts, historical certificate pins and predecessor credit are untouched.
The internal `lookup` representation changes, so this is not a promise to preserve
direct external uses of that private dictionary.

## Evidence

The default verifier checks:

- 28 interner fixtures and 41,212 exact union calls against a separate
  set-of-inputs oracle. Key widths 0, 1, 8 and 64 include a complete-collision
  case. Different decompositions of equal supports keep their first node.
- Exact complete structure equality for 15 builder pairs, including direct,
  common-point, split, vector, transpose, paired-kernel and factored paths.
- One fresh large builder pair covering 509,195 nodes, 489,594 active additions
  and 509,194 active nodes. Every support, argument, input, target, output and
  active-node entry contributes to its matching SHA256 digest.
- Eight controls for key-only equality, first-decomposition retention, overlap,
  invalid key widths, malformed inputs, input capacity and source corruption.
- Exact source and adapter bindings, benchmark-source hashes, all retained
  work counts and recomputed timing summaries. `RESULT.json` is generated and
  binds the code, benchmark and source-map files by SHA256.

The large comparison uses a complete structural digest; the small comparisons
compare the actual structures. The written invariant supplies the general
equivalence statement. No finite test is presented as a proof of a multiplication
theorem or of predecessor mathematics.

[BENCHMARK.json](BENCHMARK.json) records the ten samples, exact source hashes,
environment, zero errors and the separate timed regions. Construction ranges
are 3.336..3.490 s before and 1.932..2.345 s after. Complete-process ranges are
4.470..4.691 s before and 3.105..3.541 s after. The median gain exceeds each
arm's full range. No sample was omitted or rerun. Peak RSS medians are 1.897
and 1.992 GiB; the compact keys cost about 0.095 GiB more memory.

The host is macOS 27.0.1 arm64, CPython 3.12.15, with 18 logical CPUs. Load was
2.70/2.49/2.13 at entry and 3.75/3.53/2.72 at the end. Runs were serial. These
measurements describe this host and workload. Hosted correctness replay does
not establish another host's speedup.

[PROFILE.txt](PROFILE.txt) is the untimed diagnostic profile. `add` accounts
for 2.087 s of 5.202 s profiled construction; circuit initialization accounts
for another 0.398 s. The source maps these costs to support operations and
large-integer dictionary keys. Profiling overhead is excluded from the reported
timings. Full support operations, traversal and planning remain payable.

## Reproduce

From the repository root, with a CPython 3.12 installation and standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/mixed-point-support-interning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/mixed-point-support-interning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-point-support-interning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mixed-point-support-interning --check-source-history
```

Replace the interpreter path with the local CPython 3.12 path on another host.
The two registered checks are read-only and time out after 180 seconds each.
They perform correctness checks, not timing acceptance. A fresh performance
experiment writes exclusively to a new path outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/mixed-point-support-interning/benchmark.py --rounds 5 --output /tmp/new-mixed-point-benchmark.json
```

`run_builder.py candidate` is the standalone opt-in construction. Its JSON
includes work counts, verification status, timing and structural digest.
The CLI supports valid `n <= 50`, `k,l <= 3` cases and caps full JSON at `n <= 14`.
The interner separately caps inputs at 25,000 and nodes at 4,000,000.

## Limits

This is a frozen historical builder, not the selected supplier's complete
caller. No mathematical predecessor verifier, Lean proof, Docker job or
selected cold replay is run. The native, ownership, compiler, precision/tape,
analytic recovery and complete supplier obligations remain open. The new
overlap guard remains active under optimized Python; inherited assertions
retain their original behavior. Memory grows with stored supports; worst-case
collisions can slow the bucket scan without affecting correctness. The runner
uses POSIX resource accounting and has not been qualified on Windows.

## Open next questions

These are also structured in [TASK.json](TASK.json):

- Can the shared mixed-point audit adopt this interner under its source-pin
  and consumer contracts? First inventory direct `lookup` consumers and pins,
  then compare its complete receipt with all existing checks retained.
- Does the gain persist on Linux CPython 3.12? Run the fixed five-pair benchmark
  on that host. No second-host timing is claimed here.

The construction improvement, proof and verifier were **produced by Nick Petalas**.
Credit Douglas R. Colkitt for the original mixed-point and exclusion builders,
and Victor Li / VictorLiwentao for PR #2150's question and faster output verifier.
Their original source bytes and attribution are preserved. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
