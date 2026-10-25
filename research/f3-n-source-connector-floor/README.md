# Unsigned F3 connector: the three-call floor for n sources

For n immutable sources and all 2^n − 1 nonzero binary-mask outputs over F3,
every legal word needs at least 3(n + 2^n − 1) complete calls. This package
shows:

- **Attained for n ≤ 6** (finite certificate): explicit restored source paths
  give words of 6, 15, 30, 57, 108 and 207 calls, each operator called exactly
  three times.
- **Deletion lemma** (proof): if the floor is attained for n sources, it is
  attained for n − 1. The attaining set is therefore an initial segment
  {1, …, N}.
- **Fails for every n ≥ 14** (proof): at most C(3n+3, 3) readout triples
  exist, and C(45, 3) = 14,190 < 16,383 = 2^14 − 1.
- **Seven sources, upper bound 405** (finite certificate): one 21-event path
  serves 126 of 127 masks with three readouts; the all-ones mask takes six.
  The seven-source optimum is 402 or 405.

So 6 ≤ N ≤ 13. Whether N = 6 is open (see Open next questions). The claims are a
scoped proof plus a finite certificate. There is no new κ, no selected-frontier
change and no multiplication theorem.

This extends the five-source result of
[#4225](https://github.com/CrocSwap/integer-mult-bounds/pull/4225) (head
`397025101d23195a5193c7912e6cd384eccdbf1c`) and the one-source alphabet and
handoff of Riquelme Soares's
[#4189](https://github.com/CrocSwap/integer-mult-bounds/pull/4189) (head
`5fb3936dfc8082f438f21c72dd6ca49ff4366ae7`). The interface and the
prefix-boundary readout criterion follow Ross Richardson's
[#943](../universal-connector-boundary/README.md), whose characteristic-two floor
fails at five sources.

## 1. Interface

The rows are n read-only sources x_j, 2^n − 1 outputs y_m and one borrowed dirty
connector z. For arbitrary F3-linear maps B_j and A_m of compatible
dimension, the word must implement

```text
y_m += sum_(j: bit_j(m)=1) A_m B_j x_j   for m = 1, ..., 2^n - 1;
x_j and z unchanged.
```

The only calls are unsigned `B_j: z += B_j x_j` and `A_m: y_m += A_m z`, with
the complete-call contract of #4225. Signed calls, extra connectors, scaling,
source mutation, frame changes and free copies are not admitted. The maps may
be singular and need not commute.

## 2. Lower bound for every n

This is #4225's argument applied to general n. Specialise to scalar identity
maps. If B_j occurs b_j times, restoring z forces 3 | b_j. If A_m occurs a_m
times, output m receives a_m·z0, so 3 | a_m. Every count is positive, so
each is at least three and the total is at least 3(n + 2^n − 1). Every count is
a multiple of three, so a word that misses the floor has at least
3(n + 2^n − 1) + 3 calls.

## 3. Floor words are source paths with triple readouts

A floor word has a source path w of length 3n that uses each source three
times. Let q_t ∈ F3^n count source events modulo three after t steps. Three
A_m readouts at boundaries a ≤ b ≤ c add A_m(3z0 + Σ_j (q_a + q_b + q_c)_j
B_j x_j). The word is correct exactly when every nonzero binary mask equals
some q_a + q_b + q_c. Readouts at one boundary commute.

**Window form.** For source j, let n2 and n3 count its events in the windows
[a, b) and [b, c). Then (q_a + q_b + q_c)_j ≡ n3 − n2 (mod 3). Mask m is
served when, for every j, n3 − n2 ≡ m_j and never ≡ 2.

**Deletion lemma.** Remove the three events of source j from a floor path. Each
old boundary maps to a new boundary with the same counts on the other sources.
A mask with bit j zero keeps its triple, so every mask of the n − 1 remaining
sources is served. The verifier checks all 20 single-source deletions of the
certified paths as a control.

**Counting.** A path of length 3n has 3n + 1 boundaries and C(3n+3, 3) readout
triples with repetition. That number is at least 2^n − 1 for n ≤ 13
(C(42, 3) = 11,480 ≥ 8,191) and smaller for n = 14. The deletion lemma extends
the failure to all n ≥ 14. The verifier also checks the table directly up to
n = 64.

## 4. Certificate

[CERTIFICATE.json](CERTIFICATE.json) lists one path for each n = 1..6. For
example, the six-source path is

```text
0 1 2 3 1 1 3 3 2 4 2 4 4 5 0 5 5 0
```

The verifier regenerates the lexicographically first triple for every mask,
builds the literal word, and simulates it with generic coefficients: z is held
as a formal sum over z0 and the B_j x_j terms. Every output must receive
exactly its mask row with no z0 term, and z must restore. This identity uses
no commutation of A_m with B_j.

For seven sources, the path

```text
6 0 5 5 4 0 0 3 4 4 2 3 3 1 2 2 6 1 1 5 6
```

serves all masks except 127 with three readouts. Mask 127 uses six readouts
at boundaries (0, 0, 1, 2, 8, 14). The literal word has 21 + 3·126 + 6 = 405
calls, the next multiple of three above the floor of 402.

## 5. Search evidence for n = 7 (local only, not a proof)

These runs are search failures, not exclusions. Simulated annealing over
restored 21-event paths reached at most 126 of 127 masks in eight runs. For
n = 8, 9 and 10 the best runs reached 224/255, 366/511 and 430/1023. A direct
SAT encoding found floor paths for n = 5 and 6 in under a second. For n = 7 it
did not finish within its time limit. These scripts and logs are not
committed, and no unsatisfiability certificate exists.

## 6. Reproduction

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f3-n-source-connector-floor/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f3-n-source-connector-floor
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f3-n-source-connector-floor --check-source-history
```

Expected marker:
`PASS_F3_N_SOURCE_CONNECTOR_FLOOR attained_n=1..6 counting_excludes_n>=14 n7_upper=405`.
The verifier is standard-library only and prints a receipt hash bound to all
six package files. Five mutation controls must be rejected: a dropped call,
two doubled call counts, a relabelled source call, and a sorted four-source
path that misses some masks.

## 7. Limitations

The result covers only the unsigned, immutable-source, complete-call interface
over F3. Fixed call prices must include their full implementation. Input
admission, coefficient preparation, dispatch and physical costs are additional
and unknown. No consumer is instantiated. Proof-kernel checks and independent
human review are not claimed.

## Open next questions

These are recorded with first steps in [TASK.json](TASK.json).

1. Is the floor attained for n = 7, so that the seven-source optimum is 402
   rather than 405? By the deletion lemma this decides whether N = 6.
2. What is the exact optimum for each n ≥ 7 once the floor fails?
3. Does any concrete consumer use an n-source unsigned F3 batch with a
   favourable complete invoice?

## Credit

Produced by Nick Petalas. The F3 alphabet and one-source handoff are Riquelme
Soares's #4189. The mod-three count argument and five-source word come from
#4225. The connector interface and prefix-readout criterion come from Ross
Richardson's #943. Apache-2.0.
