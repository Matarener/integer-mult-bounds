# Encoded axis guard for the many-axis prime band

Independent review of the encoded `TensorPlan.production_axis` contract that
PR #4029 asks to be lowered onto the actual caller. No new κ and no
selected-frontier change. Selected κ stays `0.001672660197076918`.

The guard is three strict predicates on Counts that `__init__` has already
loaded. It does not read, write or rewind a prime-queue tape. On PR #4029's
band `I(t,d) = (t(1-1/(3d)), t(1-1/(4d))]`, every real point satisfies both
ratio predicates, and for `d >= 2` it also satisfies the near-one gate
`s < t < 2s`. Oddness is separate: `s = 14`, `t = 16`, `d = 2` is in the band
and even. If `K = target_halo + 2w <= 2^(ell-3)`, every band integer beats the
encoded period `s > 2K`. The witness `s = 939`, `t = 1024`, `d = 4`,
`target_halo = 470` passes `s > K` and fails `s > 2K`.

The argument is in [PROOF.md](PROOF.md). The imported prime-number estimate is
not reproved. `production_common`, numerical recovery and a literal encoded
tape scheduler stay open.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/many-axis-encoded-axis-guard/verify.py
python3.12 -B scripts/research_package.py --package research/many-axis-encoded-axis-guard
```

`verify.py` checks the vendored plan's SHA-256, the AST contract, the rational
endpoint and Bernoulli identities, every band integer for `ell = 3..12` and
`d = 2..8` on both target scales, and the even and factor-2 witnesses.
`-O` runs the same checks. Expected first line:

```text
PASS_MANY_AXIS_ENCODED_AXIS_GUARD
```

## Open next questions

1. Can the prime queue be written as the odd `read_fixed` source tape that
   `__init__` loads before `production_axis`, with head return included?
   The predicate review does not supply that scheduler. The blocker is an
   encoded Count runtime, which this package does not execute.
2. Does the imported prime-count cutoff still leave at least `D` primes in
   each band after the oddness gate removes composite and even integers?
   PR #4029 treats odd primes as the selection. A band integer need not be an
   odd prime, as `14` shows. The blocker is the analytic estimate, which is
   not reproved here.

## Credit

The tensor plan is Jose Manuel's PR #3935. The prime-band statement, the
`d = D+1` reading and the period premise are ToikY's PR #4029, following
PR #4024 and the source08 prime-interval lineage named there. This package
re-derives the encoded predicates and the band inclusions from that vendored
file and does not import PR #4029's checker.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
