# Independent audit of the updated PR4441 frontier

At **2026-10-21 20:42:34 UTC**, the 30 most recently updated PRs, the 30 most recently created PRs and canonical main were refreshed. The strongest newly observed claim remained PR4441 at **kappa 0.00300105**, head `5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39`. No claim above the proposed `0.003001053` was found in those bounded lists. Canonical main remained `2a13eb1827784206202db90e5dc8327cf8a250db`. This is bounded retrieval coverage, not an exhaustive claim about all historical PRs.

## Checked

The independently constructed retimed p17 case and the published combined profile agree exactly. They contain 11560 productive fields, 69273 paid requests, and productive/paid rank masses 260798/259998.

A newly written interval engine uses only integer arithmetic, outward rounding in units of 10^-60, an atanh series with an exact logarithm remainder, and an exponential series with an exact geometric remainder. It imports no source interval implementation. Optimized execution succeeds with `python3 -I -O -B research/kappa-hybrid-controller/frontier/audit.py`.

At tested saving 0.003001052, the new engine independently encloses every published alpha, gamma and delta interval. It proves alpha < 1-10^-9, gamma < 97/100 and delta < 19/20; the earlier gamma limit 31/32 fails. Both decay-block inequalities and the complete paid-tail bound `2097152001953127/2097154147483648 < 1` hold exactly.

The two signs bracketing the fixed-profile root at 0.0030010541830 and 0.0030010541834 hold independently. Sixteen derivative interval cells prove strict decrease through C=1/20. Another 128 interval cells keep the moment negative from C=1/20 through 1. This establishes the stated ceiling for this one profile throughout 0<C<1. It does not establish an optimum over other controllers.

The logarithmic compiler checks hold with the source active ambient 153, theta=63/64 and logarithm power 1000. The exact sufficient uniform height is 165315500000000. Its integer inequality passes, while the immediately preceding grid point fails. The source BIT conversion is exactly `8590884599/2500000000000`, above the admitted 0.0034. Re-evaluating the retained outer-ledger implementation reproduces the entire published receipt, including all 54 strict predicates and four functional guards.

The parent's refined tested saving 0.003001054 also has alpha < 1-10^-10; an independent enclosure is recorded in AUDIT.json. This is approximately 0.99999999981197332875426410809243316.

## Scope

The original helper native sources are unchanged from the already audited retiming. The written substitution preserves the main interfaces, arbitrary independent helper fields and complete paid invoices, under the retained all-column lifting and physical matching contracts. No additional full native verifier was run during this delta audit.

The 153-dimensional active-space implementation is a source premise for the compiler comparison here; this audit does not independently reconstruct that reduction. The parent's own certificate retains conservative ambient 281 and derives its own sufficient constants. No objection to the source reduction is asserted.

Analytic, precision, ownership/erasure, fixed-tape, prime and exact-recovery premises remain conditional. Arithmetic agreement is not formal verification or independent human acceptance of the multiplication theorem.

## Files and reproducibility

`AUDIT.json` records source hashes, all new interval enclosures and the exact checks. `FRONTIER.json` records the bounded PR snapshot. `audit.py` is now portable and registered as the second package command. Its default run compares the complete saved receipt without modifying it. Its external reads are the four immutable updated-frontier input files, the independently constructed P17-DIRECT-CASE.json, and the existing compiler-refill endpoint.py. The source input hashes are bound in the parent package's manifests. Runtime was a few seconds, without a stopwatch measurement.
