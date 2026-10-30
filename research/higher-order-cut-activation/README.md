# Helper channels can require arbitrarily many parallel banks

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new kappa.** For every
q >= 2, q independent reversible scalar helper banks have zero dyadic unit
capacity in every proper nonempty subpool and capacity exactly one jointly.
The first new arity is three:

    every singleton and pair of [15], [21], [35]: capacity 0
    diag(15,21,35): capacity 1, since 15+21-35 = 1

The proof constructs d_i = product_{j != i} p_j for distinct odd primes.
An omitted prime obstructs each proper subpool. An integral Bezout identity
attains the full channel, and reduction modulo any chosen prime proves its
optimality. Each [d_i] is the full saturated pairing of an explicit
three-coordinate reversible scalar bank. The three-bank fixture restores
nine arbitrary dirty inputs in exactly 154 signed unit-coefficient ADDs.

[PROOF.md](PROOF.md) states the contract and all-size argument.
[activation.py](activation.py) constructs the finite witnesses and literal
scalar words. [verify.py](verify.py) uses a separate determinantal-divisor
oracle and exact dirty-input replay. It emits a computed stdout receipt
bound to SHA256 hashes of package files and the credited source input.

The practical implication is limited but concrete: bounded-arity grouping
cannot certify that arbitrary parallel helper banks have no algebraic unit
channel. A search needs either a source-specific restriction on joint banks
or their full prime obstruction data. This construction does not assert
that the selected P104 word contains these banks or can place them in one
legal common native chart.

## Reproduce

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/higher-order-cut-activation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/higher-order-cut-activation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/higher-order-cut-activation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/higher-order-cut-activation --check-source-history
```

Another CPython 3.12 path may replace the absolute path. Expected markers
are `PASS_HIGHER_ORDER_CUT_ACTIVATION`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`.

Finite coverage is 57 prime families, all 602 proper nonempty subpools,
57 attaining unit witnesses, 25 literal scalar cut fixtures, the 154-ADD
nine-coordinate forward/inverse identity, and 16 rejecting controls.
Normal and optimized commands must agree on every computed result.

## Scope, costs and remaining obligations

The changed contract is parallel pooling, with arbitrary cross-bank dyadic
row/column combinations at one scalar cut. There is no tensor multiplication.
Ali Romman's PR5615 single-cut capacity theorem and its diag(3,5) example
are credited premises. We add unbounded activation arity and its causal
scalar realization, not a new Smith theorem or a new two-bank phenomenon.
The new question was posed directly at the coverage-law-change bottleneck;
it was not selected from a predecessor's open next questions.

The scalar prefix/suffix and arbitrary-input restoration are proved and
implemented. Common native charts, physical carrier delivery, preparation
of joint bases, independent productive Gaussian targets, precision/growth,
stock, compiler and the complete paid/target invoice are **unproved**.
The scalar ADD invoice does not price those missing obligations. No selected
scientific replay, native supplier replay, Lean, Docker, rounded multiplier,
independent human review or formal proof-kernel review was performed.
All five selected framework assumptions remain. No frontier change is made.

Executable calibration bounds are at most eight banks, positive entries
through 10^9 and literal scalar fixtures through d=49. The written theorem
has no such bounds. Guard rejection is not a mathematical obstruction.
[CODE-BOUNDS.md](CODE-BOUNDS.md) records the managed-runtime deviations and
finite resource bounds.

## Sources and overlap

Base canonical main is a5bff3bf133e482541c09eba4e773884bdb2b1b7, priority 8.
The selected record resolves to conditional kappa .003125804; earlier values
in priority prose do not define this package's baseline. The source-bound
baseline passed without a selected scientific replay.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279640).
Live handoffs, active Discussions, open/merged PRs, recent account work and
local reservations were checked. Main README searches covered direct sums,
parallel pooling, complementary primes, higher-order activation, proper
subpools and the three diagonal entries. The cached overlap report covered
338 open PR records and 5,947 discussion records, but only 93 of 8,623 local
note paths; this is bounded overlap evidence, not proof of global novelty.
No matching arbitrary-arity parallel activation result appeared.

Credit Ali Romman's PR5615 single-cut capacity criterion, PR5602/5611 helper
handoff/completion, PR5599, and their retained P104/controller/native lineage.
The algebraic two-bank activation diag(3,5) is explicitly predecessor work.
Nick Petalas's PR5882 concerns tensor capacity, while zxv's product-module
result concerns factored tensor supports; those are context with a different
composition contract, not results rechecked or extended by this package.
Bezout, prime divisibility and Smith normal form are classical. Source bytes
are pinned in [SOURCES.json](SOURCES.json). No predecessor credit is changed.

## Open next questions

1. Does one actual source word have three compatible simultaneous banks with
   complementary prime obstructions and a legal shared native chart? Extract
   their full saturated modules first. Physical timing and carrier costs are
   the blockers; a positive algebraic pairing is insufficient.
2. Can the cross-bank unit witness be delivered as an independent productive
   target at a favorable complete signed bill? Start with the nine-coordinate
   fixture and charge both basis preparations, restoration and native maps.
   No favorable bound on those missing costs is claimed here.
