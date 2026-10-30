# Historical follow-up supplier saving binding audit

The historical PR49 arithmetic checker accepts a candidate whose complex
supplier moment contracts at `717/20000000`, while its assembly still consumes
`a_complex = 717/10000000`. For the same supplied child counts, an independent
exact rational lower bound proves that the moment at the consumed saving is
**greater than `1 + 4/10^10`**. The missing implication is equality between the
checked supplier saving and the assembly parameter.

This is a scoped audit of standalone arithmetic acceptance. The unmodified
original certificate passes its original fixed receipt. The existing
`--check docs/research/community-followup-arithmetic.json` check **already rejects
the mutant** because the receipt binds the certificate bytes. This finding is
not a CI bypass, a counterexample to the original witness, a validated finite
construction, or a change to the selected result or multiplication theorem.

## Concrete counterexample and controls

`verify.py` reads the exact historical checker, arithmetic dependency,
certificate and saved receipt from the Git commit recorded in `SOURCES.json`.
It authenticates their Git blob IDs and SHA256 values before reconstructing
those files in a disposable directory. All seven source rows are historical
provenance; no evolving root helper is a live input. Full Git history containing
the base commit is required. Future repairs of the root helper do not invalidate
this historical reproduction.

Starting with the pinned `research/climbed-48/certificate.json`, the complex
counterexample changes exactly two JSON values:

| Field | Original | Mutant |
|---|---:|---:|
| Last `complex.child_width_multiplicities` row | `[756, 516232080]` | `[756, 516232085]` |
| `complex.saving` | `717/10000000` | `717/20000000` |

The assembly parameter stays `717/10000000`. The complex denominator constants
stay `m = 784`, `W = 537696432`. Counts are positive integers and all child ranks
satisfy `0 < r < m`; this establishes the arithmetic domain only. The counts
are supplied inputs, **not claimed to arise from the retained finite producer**.
Other cached certificate fields are left unchanged and are not claimed to be
producer-consistent.

The historical CLI prints its ordinary PASS for the mutant. Its recomputed
upper bound at the weaker saving is below one (approximately
`0.9999931500318783`). The independent consumed-saving lower bound is above one
(approximately `1.0000000004398843`). Approximate decimals are explanatory;
`EXPECTED.json` contains the exact rational evidence and is checked on replay.

The bounded replay executes these controls as real Python CLI processes:

- Original historical checker with its fixed receipt passes and produces the
  same parsed receipt; the optional guard also passes.
- Mutant historical checker without `--check` passes, but the fixed receipt
  check rejects it with `receipt mismatch`; the guard rejects `a_complex` mismatch.
- An original certificate with only `assembly.parameters.a_bit = 1/100000`
  still passes the historical arithmetic checker; the guard rejects the mismatch.
- Equivalent rational spellings for both assembly savings pass the guard.
- Restoring equality in the complex mutant makes the guard pass, while the
  historical checker rejects `complex moment does not contract`. Equality is a
  necessary binding check, not sufficient arithmetic validation.

`guard.py` is an **opt-in** check of exactly the two rational equalities
`bit.saving == assembly.parameters.a_bit` and
`complex.saving == assembly.parameters.a_complex`. Its success marker is
`PASS_SUPPLIER_SAVING_BINDING_ONLY`. It does not run the arithmetic checker or
validate finite counts, all assembly parameters, or transfer hypotheses.
Production entry points remain unchanged. A direct helper edit would invalidate
live byte pins in `mixed-demotions-t37` and `mixed-fusions-x54-t37`; their frozen
files are preserved.

## Independent lower-bound argument

For the supplied positive counts `c_r`, define

\[
M(a)=\sum_r\frac{c_r}{W}\left(\frac r m\right)^{1-a}
=\sum_r\frac{r c_r}{mW}\exp\left(a\log\frac m r\right).
\]

The verifier checks positive integer `m,W,c_r`, `0 < r < m`, and `0 < a < 1`.
For each `x=m/r`, divide by powers of two to obtain `x=2^k y` with
`1 <= y <= 2`. For `t=(y-1)/(y+1)` we have `0 <= t <= 1/3`, and

\[
\log y=2\sum_{j=0}^{\infty}\frac{t^{2j+1}}{2j+1}
\ \ge\ 2\sum_{j=0}^{23}\frac{t^{2j+1}}{2j+1}.
\]

Every omitted term is nonnegative and the series converges because `t < 1`.
Use the same 24-term sum for `log 2`, multiply by `k`, and add. Rounding this
rational lower bound **down** on the `10^30` grid preserves a nonnegative lower
bound `L <= log(m/r)`. Hence `z=aL >= 0` and monotonicity plus the positive
exponential series gives

\[
\exp(a\log(m/r))\ge\exp(z)\ge 1+z+z^2/2+z^3/6+z^4/24.
\]

All weights `r c_r/(mW)` are positive, so their weighted polynomial sum is a
rigorous lower bound for `M(a)`. No floating point and no historical log/exp
function is used in this independent computation. In particular, this is a
positive-exponent expansion after the displayed identity, not a truncation of
an alternating series at `(1-a)log(r/m)`. Exact `Fraction` comparison proves
that the computed lower bound exceeds `1+4/10^10` for `a=717/10000000`.

## Reproduction

Python 3.12, Git, and the standard library are sufficient. From the repository
root with the source history available:

```sh
python3.12 -B research/followup-supplier-binding-audit/verify.py
python3.12 -O -B research/followup-supplier-binding-audit/verify.py
python3.12 -B scripts/research_package.py --package research/followup-supplier-binding-audit --check-only
python3.12 -B scripts/research_package.py --package research/followup-supplier-binding-audit
```

Both verifier modes require `PASS_FOLLOWUP_SUPPLIER_BINDING_AUDIT_ONLY` and compare
all evidence to `EXPECTED.json`. Explicit checks remain active under `-O`; the
historical child processes receive the same optimization level and private
bytecode-cache namespace. Replay only uses temporary fixtures. No finite-count
producer, historical all-package suite, Lean build, or selected cold replay is
run. To apply only the opt-in binding guard to a separate candidate:

```sh
python3.12 -B research/followup-supplier-binding-audit/guard.py path/to/certificate.json
```

## Task, overlap and attribution

Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
`TASK.json` retains the exact `portable-replay` card and declares **refined**
scope: its proof-relevant field-comparison method is applied to supplier and
assembly savings. This is a verifier side result, not an environment fix or a
new construction.

The pinned maintainer [PR49 review](../../docs/research/community-followup-review.md)
credits **Rohan Arun** and candidate head
`f95d2910e027495983b53cae1693cf535abf2569`, building on PR48. The historical
independent arithmetic checker and its PR39 rational enclosure dependency retain
**Douglas Colkitt's** attribution. The scope and original receipt are preserved.
[PR1329](https://github.com/CrocSwap/integer-mult-bounds/pull/1329) concerns retained
PR589 supplier identity and COPY deficit; it does not establish these PR49
saving equalities. The current handoff/PR overlap scan found no equivalent
PR49 arithmetic binding audit; absence of a match is not a universal novelty claim.

Audit and opt-in guard by **roger-sato**, with substantial **OpenAI Codex** assistance
in diagnosis, implementation, exact arithmetic, review and documentation.
Apache-2.0, retaining predecessor attribution.

## Open next questions

Structured questions and blockers are in `TASK.json`.

1. Integrate saving equality into a current arithmetic-checker entry point while
   preserving frozen consumers. Start by choosing a non-frozen entry point or
   source-preserving adapter, then replay the original-receipt and mismatch
   controls. Maintainer selection of the integration surface and review of
   dependent pins remain necessary; the optional guard is not production adoption.
2. Audit one other consumed assembly parameter against its supplier evidence.
   This matters because these two equalities do not prove complete binding.
   Begin with one explicit dependency trace and check overlap before expanding
   scope; finite-count production and the all-size transfer remain separate.
