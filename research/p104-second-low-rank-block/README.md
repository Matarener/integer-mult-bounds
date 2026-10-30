# Second rank-four block: conditional kappa 0.00311325989

This package gives a complete conditional kappa of **0.00311325989**. It improves
[PR #5756](https://github.com/CrocSwap/integer-mult-bounds/pull/5756)'s claim by
**0.00000012194**. The exact raw crossing lies in
**(0.00311325991155, 0.00311325991156)**. This is a small gain. It does not meet
the donor's request for a much larger improvement.

[PROOF.md](PROOF.md) gives the argument. [RESULT.json](RESULT.json) records the
complete bill and checks. [SOURCES.json](SOURCES.json) pins all retained bytes.
The base is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority
revision 8. The selected frontier is unchanged.

Later [PR #5786](https://github.com/CrocSwap/integer-mult-bounds/pull/5786)
claims the larger bound 0.00312265044 through retained copies and asynchronous
hubs. This package does not supersede that result. Its new block is released
for the separate [source-composition investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19202093); no gain is obtained by adding the published decimal values.

## Change and scope

The exact source is PR #5756 at
`a1b338e5d9271b541f2a198f4fc19cefc565feed`. It contains the paid-meeting changes
from [PR #5751](https://github.com/CrocSwap/integer-mult-bounds/pull/5751) and
Joel Pulikkan's R22 block from
[PR #5739](https://github.com/CrocSwap/integer-mult-bounds/pull/5739).
This package changes a different block on roles
57, 81, 92, 224, 225, 227, 229, 234 and 742.

[PLAN.json](PLAN.json) pins two scalar runs by index, length and SHA256. All 102
operations move from chart 267 of rank eight to `span[11,21,38,448]` of rank
four. Helper 742 starts there; helper 225 ends there. Every scalar coefficient,
scalar order, owned event, main endpoint and port is unchanged. The constructor
rebuilds every native MOVE, including entry and final routes.

Per local call, the paid change is `H1 + H4 - H5`. The helper target change is
`-H1 + H4 + H5 - H8`. Here `Hr` denotes a recursive job of rank r, not an
array-volume exponent. The complete caller has 13,390 productive fields,
66,870 paid calls and rank-mass surplus 760. A count reduction alone is not the
source of the gain: the complete signed moment improves.

The exact raw ceiling applies only to this fixed full target/paid profile.
It leaves between `2.155e-11` and `2.156e-11` above the claim. Further useful
progress must change that profile. No optimum over other words is claimed.

## Replay

Python 3.12 and the standard library are sufficient. From a checkout:

```sh
python3.12 -B scripts/research_package.py --package research/p104-second-low-rank-block
```

The registered commands use ordinary Python and `-O`, in sequence. Each ends:

```text
PASS_P104_SECOND_RANK4_BLOCK_KAPPA_00311325989
```

A source export needs no Git, network or solver. In its package directory:

```sh
python3.12 -I -B verify.py
python3.12 -I -O -B verify.py
```

The source word is frozen, not regenerated from the PR #5756 search. The new
word is regenerated from that frozen word. All 602,176 scalar coefficients and
a separate dense transpose replay are checked. The replay also checks 2,934
native maps with their absolute phases, 208 main adapters, 1,118 helper
normalizers, 7,488 physical contacts and 53,248 central-square columns. Two
rational moment engines check completion and the full bill. All ordinary
COPY/CLEAR, scalar, restoration and route charges remain in the inherited
compiler proof. See [VALIDATION.md](VALIDATION.md) for the run record.

## Conditions and limits

The five inherited framework assumptions remain: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery`.
This is a complete conditional price in that framework. The uniform word and
rounded integer multiplier are not materialized. No independent human review,
proof-kernel acceptance or selected-frontier change is claimed.

## Open next questions

[TASK.json](TASK.json) gives the next questions and their first checks. A larger
gain needs a new full profile. Independent review must still assess this exact
source closure, word and price. Check current Discussions before taking a new
scalar, helper or caller scope.

## Credit

Ali Romman with substantial OpenAI Codex assistance supplied this second block,
its constructor and this replay package. No subagents were used. Apache-2.0.
Joel Pulikkan (GamingPuzzled), with Claude Opus 5.5 assistance, supplied the R22
reframe mechanism and the different block retained from PR #5756. We do not
claim that mechanism as new.

The retained PR #5751 source supplies the exact local, native, caller and price
checks. Its source chain includes flyingviper's distinct-boundary work in
[PR #5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718), the earlier
P104 helper work, and the controller, compiler and analytic work.
[NOTICE](NOTICE) preserves their notices. Exact source commits, blob IDs and
SHA256 hashes are in SOURCES.json. The nested archives are unchanged.
