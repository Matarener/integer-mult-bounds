# Unsigned F3 connector: the floor fails at seven sources

For seven immutable sources, all 127 nonzero binary-mask outputs and one
arbitrarily dirty restored connector over F3, no word attains the 402-call
floor. Combined with the 405-call word of
[#4232](https://github.com/CrocSwap/integer-mult-bounds/pull/4232), the exact
seven-source optimum is **405 calls**. By #4232's deletion lemma, the floor
3(n + 2^n − 1) is attained **exactly for n ≤ 6** and fails for every n ≥ 7.

This answers #4232's open question 1. The claim is a scoped proof whose
exhaustive step is a finite computer census, run by two separately written
enumerators that use different arithmetic and different symmetry reductions.
There is no new κ, no selected-frontier change and no multiplication theorem.

## 1. Interface and reduction (from predecessors)

The interface is #4232's: rows are n read-only sources x_j, 2^n − 1 outputs
y_m and one borrowed dirty connector z. The only calls are unsigned
`B_j: z += B_j x_j` and `A_m: y_m += A_m z` with arbitrary F3-linear maps. The
word must add `sum_(j in m) A_m B_j x_j` to every y_m and restore x and z.

Two facts are taken from #4232 (head `86ad339efc9f817846479431d8cc0f04edf95fb9`),
which extends #4225's mod-three count argument:

- every call count is a positive multiple of three, so the floor is
  3(n + 2^n − 1) and any word that misses it has at least three more calls;
- a floor word is a restored source path of length 3n, each source three times,
  with three readouts per mask, and it is correct exactly when every binary
  mask equals q_a + q_b + q_c for prefix boundaries a ≤ b ≤ c. Here q_t ∈ F3^n
  counts source events modulo three after t steps.

#4232 also supplies the seven-source 405-call word (masks 1..126 by readout
triples, mask 127 by six readouts) and the deletion lemma. This package
re-runs the 405-word check as a cheap self-contained step. The new content is
the exclusion in section 2.

## 2. No seven-source floor path exists

**Rotation invariance.** Because each source occurs three times, q_{3n} = 0 =
q_0, so the boundaries form a cycle of 3n points. Rotating the path to start
at position r replaces every q_t by q_{t+r} − q_r. A readout triple sum changes
by −3q_r = 0. The set of served masks is therefore invariant under cyclic
rotation, and also under relabelling the sources, since the mask set is
closed under coordinate permutations.

**Census.** A floor path for n = 7 exists exactly when some path in either
reduced family below serves all 127 masks:

| Engine | Reduction | Paths checked | Floor paths |
|---|---|---:|---:|
| `engine/reduced.c` | labels by first occurrence; rotated so position 0 is an event whose gap to the same source's next event is the path's minimum cyclic gap | 4,130,223,840 | 0 |
| `engine/independent.c` | labels by first occurrence; rotated so the last event differs from the first | 32,590,958,400 | 0 |

Each family meets every rotation-and-relabelling orbit. For the first, rotate
any minimum-gap event to position 0. For the second, pick r with
s_(r−1) ≠ s_r, which exists because n ≥ 2. The engines also differ in
arithmetic. The first packs F3 vectors as two bit masks and uses a bitwise
adder. The second uses base-3 integers and digit-wise tables. Both mark the
pair sums q_a + q_b and accept mask m when m − q_c is a marked pair for some c.

**Calibration.** For n = 1..6 both engines find floor paths, and their counts
are recorded in [CERTIFICATE.json](CERTIFICATE.json). For n ≤ 4 a pure-Python
brute force over every path, with no symmetry and a direct triple-sum test,
matches both engines. It confirms that each reduced solution list meets every
solution orbit and contains only solutions.

## 3. Consequences

- The seven-source optimum is 405: no 402-call word exists, and every call
  count is a multiple of three, so 405 is the next possible value, attained
  by #4232's word.
- The floor-attaining set is exactly {1, …, 6}. The deletion lemma says a
  floor word at n gives one at n − 1, so failure at 7 propagates to every
  n ≥ 7. This replaces #4232's interval 6 ≤ N ≤ 13 with N = 6.
- For every n ≥ 7 the optimum is at least 3(n + 2^n − 1) + 3. Exact values for
  n ≥ 8 remain open.
- Open PR [#4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248)
  (head `e7df122403cfc2febfb6799abb821487d8d1ee49`) reaches the unsigned floor
  for k ≤ 2c sources in characteristic c. At c = 3 that gives k ≤ 6, so with
  this exclusion its range is exactly the attaining set in characteristic three.

## 4. Reproduction

From the repository root (a C11 compiler `cc` is required):

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/f3-seven-source-connector-floor/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/f3-seven-source-connector-floor/verify.py --n7-shards 0,1
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/f3-seven-source-connector-floor/verify.py --n7-all
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/f3-seven-source-connector-floor/verify.py --n7-independent
```

The default mode runs the calibration (reduced engine n ≤ 6, independent
engine n ≤ 5), brute-force cross-checks, the 405-word check and controls (marker `PASS_F3_SEVEN_SOURCE_CALIBRATION`). `--n7-shards`
replays named shards of the reduced census and compares their leaf counts with
the certificate (marker `PASS_F3_SEVEN_SOURCE_SHARDS`). `--n7-all` and
`--n7-independent` replay the whole census for one engine (marker
`PASS_F3_SEVEN_SOURCE_CENSUS`); `--n7-independent` also replays the
independent engine's n = 6 calibration. They use every available core. Measured
locally on an 18-core Apple machine: about 25 CPU minutes (2.5 minutes wall) for the
reduced engine and about 12.5 minutes wall, all 18 cores busy, for the
independent one. The independent leaf count equals the closed form
((3n)!/6^n − n(3n−2)!/6^(n−1))/n!, which the default mode checks for n = 2..7.
[VERIFY.json](VERIFY.json) registers the calibration and six of the 18
reduced shards (0, 1, 8, 9, 16, 17), the most the 1200 s package replay cap
holds. The complete reduced census (`--n7-all`) and the independent census
(`--n7-independent`) are opt-in. Their per-shard leaf counts are in the
certificate.

## 5. Limitations

- The exclusion is a computer census, not a written proof. CI replays only six
  of the 18 reduced shards; the full censuses of both engines were run locally
  and are reproducible with the opt-in commands. No proof-kernel
  check, SAT certificate or independent human review is claimed. The two
  engines share the reduction to boundary triples from #4232, so a flaw in
  that reduction would affect both.
- The result covers only the unsigned, immutable-source, complete-call
  interface over F3. Admission, coefficient preparation, dispatch and physical
  costs are additional and unknown. No consumer is instantiated.

## Open next questions

1. What is the exact optimum for n = 8..13? The floor fails, so each optimum
   is at least the floor plus three. Is it exactly the floor plus three, as for
   n = 7?
2. What is the largest number of masks a 21-event seven-source path serves with
   triples? #4232's annealing reached 126; the census here could also record
   the maximum, which would bound how many masks need longer readout lists.
3. Can the n = 7 exclusion be given a short written argument, for example from
   the window form of #4232 applied to the all-ones mask and the weight-six
   masks?

## Credit

Produced by Nick Petalas. The interface, readout criterion, deletion lemma and
405-call seven-source word are from #4232. The mod-three count argument and the
five-source word come from #4225. The F3 alphabet and one-source handoff are
Riquelme Soares's #4189. The connector interface and prefix-readout criterion
originate in Ross Richardson's #943. Apache-2.0.
