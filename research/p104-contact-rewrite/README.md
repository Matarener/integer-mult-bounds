# Conditional kappa 0.00310676333 from a four-gate rewrite

This package raises the complete conditional kappa from PR5651's
**0.00310644469 to 0.00310676333**. The increase is **0.00000031864**.
It is a small gain. The selected record stays unchanged.

The package reconstructs the PR5644 helper cleanup and zxv's PR5643 paid
A2 change. PR5650 already publishes this composition; PR5651 checks it again.
A new four-gate schedule then uses an earlier helper value
and changes two paid H1 requests into one H2 request. Every independent input,
productive target and owned instruction is retained.

| Complete quantity | PR5651 | This package |
| --- | ---: | ---: |
| Paid requests | 66,492 | 66,474 |
| Productive fields | 12,958 | 12,958 |
| Rank-mass surplus | 760 | 760 |
| Claimed conditional kappa | 0.00310644469 | 0.00310676333 |

The exact raw crossing is `(0.00310676334487,0.00310676334488)`. The new
four-gate component contributes `18*(2-2^t)` to the signed moment. Relative to PR5644, the
published A2 component also contributes `18*(3^t+5^t-2^t-6^t)`. Both are strictly
positive for `0<t<1`. See [PROOF.md](PROOF.md), [WITNESS.json](WITNESS.json)
and [RESULT.json](RESULT.json).

## Replay

Use Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-contact-rewrite
```

In an official Git-free export, run:

```sh
python3 -I -O -B research/p104-contact-rewrite/verify.py
```

Expected marker: `PASS_P104_CONTACT_REWRITE_KAPPA_00310676333`.
The verifier authenticates all retained bytes before source imports. It
checks the four-column identity, 565,504 complete endpoint coefficients,
native maps and phases, the full physical caller, two interval engines,
compiler costs and all 58 outer predicates. Corruption controls test the
source version, early value, frame, erasure, target credit and paid bill.
[VALIDATION.md](VALIDATION.md) records the completed checks and their limits.

The five selected assumptions remain: native all-column realization, owned
erasure, uniform compiler closure, precision and fixed-tape execution, and
analytic recovery. The helper endpoint contract is also retained. The huge
uniform word and complete rounded multiplier are not materialized. No global
optimum, independent human acceptance or proof-kernel theorem is claimed.

## Sources and credit

The exact consumed source is
[PR5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627) at
`ed4dc88a09a7d201971f6603b8c2074e95dd9c32`.
The released inputs are
[PR5644](https://github.com/CrocSwap/integer-mult-bounds/pull/5644) at
`c5871955d89bf73506fd68b0a5bf1cf2b3153c02` and
[PR5643](https://github.com/CrocSwap/integer-mult-bounds/pull/5643) at
`a3ff5c628bfc8825553d62d913f3e91f75d6825f`.
The composition word is also retained from
[PR5650](https://github.com/CrocSwap/integer-mult-bounds/pull/5650) at
`7916490124ac946704339a6a332bb76f06e5db5c`. The stronger rounded comparison is
[PR5651](https://github.com/CrocSwap/integer-mult-bounds/pull/5651) at
`853192167b27d44aea0d4bc2b0d52d695fadc7c6`. The checker matches the published
composition after it orders independent public MOVEs in the same way.
The archive retains its complete source closure. Copied inputs match their
published Git objects. [SOURCES.json](SOURCES.json) records both locations.

Credit zxv for the paid A2 witness and PR5650 composition; Ali Romman for PR5644 and the prior
complete P104 caller; Chris R/Clear1nsight and ToikY for the prior A2 method;
and Cinna Davis for the compensated triangle and scalar compression method.
Retain flyingviper's relay, Scratch-net's preparation, Pierre-Loic Doulcet's
cascade, and all David Arias, Gareth Davidson, Cinna Davis, Jacob Alan Sussman,
Cao Yifan, zxv, geometry, native, BIT, compiler and analytic source notices.
[NOTICE](NOTICE) retains the detailed source credit.

The new four-gate placement and author checks were prepared by
Ali Romman with substantial OpenAI Codex assistance. No subagents were used.
Apache-2.0. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19183208)
records the scope and the prior failed screens. Those screens are not inputs
to the positive verifier.

## Open next questions

1. Independently check the four-gate source version and native frame placement,
   then replay the complete package at its publication commit.
2. Test a different dependency pattern, a longer sequence or a changed caller.
   The stated finite search is at a fixed point; it does not exclude those
   constructions. A new claim must include its complete paid profile.
3. Resolve the retained framework assumptions. A finite source-bound replay
   does not supply a complete rounded multiplier or formal multiplication proof.

[TASK.json](TASK.json) states the first step and limit for each question.
