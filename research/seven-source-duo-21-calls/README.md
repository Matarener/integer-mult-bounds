# Seven-source singleton+DUO connectors: 21 calls at 24 adds, and 20 calls

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: finite certificate (explicit construction).** No search
exclusion, no optimality proof, no new κ, no supplier change.

In the seven-source restored connector of Ross Richardson's
[#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943), extended by
the charged pair-source DUO call `z += B_j x_j + B_k x_k` of
`research/duo-toggle-connector`, Aaron Wang's
[#2396](https://github.com/CrocSwap/integer-mult-bounds/pull/2396)
(`research/connector-seven-source-duo`) gives a universal word with
`(k, W) = (22, 24)`: 22 source calls and 24 toggle-adds. Its first open
question asks whether `(22, 24)` is the Pareto profile. It is not. This package
gives two universal words:

| Word | Calls `k` | DUO calls | Adds `W` | Batch queries | Batch adds |
|---|---:|---:|---:|---:|---:|
| #2396 (cited) | 22 | 2 | 24 | 276 | 278 |
| **this package** | **21** | 3 | **24** | **275** | **278** |
| **this package** | **20** | 6 | 26 | **274** | 280 |

The batch is the all-127-row batch of #2396 with two paired readouts per row
(254 readouts). The `(21, 24)` word strictly dominates `(22, 24)`: one fewer
call at the same adds, so in #2396's tariff `c_B = o + p`, `c_DUO = o + 2p`,
`c_A = o + p` the batch saves `o` for every `o > 0`, and `3o` against the
24-call singleton Gray word. The `(20, 26)` word saves one more call at two
more adds; it beats `(21, 24)` exactly when `o > 2p`. It also answers
#2396's `(20, d)` question at `d = 6`, where #2396's search reached 126/128.

## The words

Prefix states, with bit `j` for source `j`. Each word closes back to `0`.
A step of weight one is a singleton call, a step of weight two a DUO call.

```text
(21,24): 0 1 33 36 38 102 100 96 98 114 82 83 115 123 120 88 89 9 41 40 8
(20,26): 0 2 16 112 120 88 92 60 61 29 21 85 81 115 123 59 58 26 14 12
```

Universality is the paired-readout criterion used by #943 and #2396:
the prefix-state set `P` satisfies `P + P = F2^7`.

## Evidence

[verify.py](verify.py) uses only the Python standard library and no search.
For each word it rebuilds the steps from the prefix states and checks:

- every step has weight one or two, the word restores the connector, and every
  source label has positive even multiplicity;
- all 128 masks lie in `P + P`, and a separate dual test (mask `m` is covered
  when `p xor m` is in `P` for some `p` in `P`) finds no missing mask;
- `k`, the DUO count, `W` and the batch bill match [CERTIFICATE.json](CERTIFICATE.json);
- four mutations per word are rejected: a deleted call, a DUO shrunk to a
  singleton, a retargeted call and a dropped call.

It also reads #2396's pinned certificate, confirms that word is universal at
`(22, 24)`, and checks the dominance relations above. Assertions are explicit
checks, so `-O` does not skip them.

## Reproduce

From the repository root with CPython 3.12 (the recorded local interpreter was
`~/git/integer-mult-bounds/.venv/bin/python3.12`):

```sh
python3.12 -B research/seven-source-duo-21-calls/verify.py
python3.12 -B scripts/research_package.py --package research/seven-source-duo-21-calls
```

Expected marker:
`PASS_SEVEN_SOURCE_DUO_21_CALLS k21_W24_queries=275 k20_W26_queries=274 pred_queries=276 universal=128/128 mutations_rejected=8`.

The words came from the simulated-annealing program [search/sa.c](search/sa.c)
(`cc -O2 -o sa sa.c -lm`; arguments `K WMAX seed iterations restarts`).
`./sa 21 24 1 5000000 20` and `./sa 20 26 7 5000000 20` printed these words
on an Apple arm64 host. The search is provenance only; the verifier does not
depend on it.

## Limitations

- **No lower bound.** Runs at `(20, W <= 24)`, `(19, W <= 34)`, `(18, W <= 36)`
  and `W = 22` at `k = 21, 22` found nothing. These are bounded search
  failures listed in CERTIFICATE.json, not exclusions.
- The counting bound `C(k,2) + 1 >= 128` gives only `k >= 17`.
- Inherited from #2396 and `research/duo-toggle-connector`: no physical
  supplier instance of this connector exists, so no recursive moment, frame,
  compiler or κ consequence follows. With `o = 0` the `(21, 24)` word gains
  nothing over `(22, 24)`.

## Open next questions

1. **Is 20 the minimum number of calls?** A universal 19-call word would cut
   the batch to 273 queries. First step: an exact census of 19-point sets `P`
   with `P + P = F2^7`, then a Hamiltonian-cycle test with edges of weight at
   most two. Blocker: no exclusion argument beyond the counting bound
   `k >= 17` and the parity rule `d = k mod 2`.
2. **Is 24 the minimum number of adds?** `f(7) = 24` (#3058) settles the
   singleton case, but a word with DUO calls and `W = 22` is not excluded.
   First step: adapt #3058's deletion argument to steps of weight two.
3. **Is `(20, 24)` attainable?** It would dominate both new words. The local
   search reached no such word.

## Credit

Ross Richardson (#943) supplied the connector model and paired-readout
criterion. The DUO family and its pricing come from `research/duo-toggle-connector`.
Aaron Wang / navinor (#2396) supplied the `(22, 24)` word, the batch bill,
the tariff and the open Pareto question answered here. Douglas Colkitt (#1185)
supplied the Gray baseline, and conorholds (#3058) the singleton value
`f(7) = 24`. Their results are cited, not re-audited. The two new words, the
verifier and the search program are new.
