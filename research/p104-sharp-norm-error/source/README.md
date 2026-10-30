# Accumulated native updates

Three owned buffers collect pending additions before the destination is read.
Each buffer pays one native conversion, delivers the sum and is cleared.
These three queries replace five source queries. The complete conditional
kappa increases from PR5786's **0.00312265044** to **0.00312336057**.
The gain is **0.00000071013**, or **0.0227413%**. This is a small gain.

The exact source is [PR5786](https://github.com/CrocSwap/integer-mult-bounds/pull/5786)
at `6b936acd68a7e0f9062037900f0fe9bc4b6fdd25`. The construction extends
[PR5774's retained copies](https://github.com/CrocSwap/integer-mult-bounds/pull/5774)
with destination accumulation. Source copies share one conversion among reads
of a fixed value. The new buffers share one conversion among additions to an
unread destination. The whole physical caller stays fixed.

The package includes the [proof](PROOF.md), [fixed plan](PLAN.json),
[complete result](RESULT.json), [source pins](SOURCES.json),
[validation scope](VALIDATION.md) and [search limits](DISCOVERY.md).
The verifier checks all 798 public and dirty owned input columns, native maps
and phases, the actual caller, the complete invoice and compiler predicates.
It checks the unchanged protected contact subsequences and every exact COPY
value. The standard library and Python 3.12 suffice:

```sh
python3.12 -B scripts/research_package.py --package research/p104-accumulated-native-updates
```

Expected final markers:

```text
PASS_P104_ACCUMULATED_NATIVE_UPDATES
PASS_REGISTERED_RESEARCH_PACKAGE
```

The complete caller has 13444 productive targets and 66870 paid calls.
All scalar work, native maps, adapters, thin queries, idles, owned storage,
clearing, restoration and routes are included. The signed-moment gain is
strict for every exponent 0<t<1. Exact interval engines check the claimed
kappa and its finite compiler completion.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19202609)
records the scope. The R22 composition in
[PR5795](https://github.com/CrocSwap/integer-mult-bounds/pull/5795) and the second
block in [PR5796](https://github.com/CrocSwap/integer-mult-bounds/pull/5796)
remain separate. Their source contact regions are unchanged here.
The claim exceeds PR5795's 0.00312277313 by 0.00000058744. It does not claim
that the independent constructions have already been composed.

The five inherited framework assumptions remain. The large uniform word and
rounded multiplier are not materialized. Author checks are not independent
acceptance. The selected frontier is unchanged. Hosted verification and
publication evidence are reported in VALIDATION.md and the PR.

## Open next questions

- Can two pending sums share a native conversion? Start with an exact relation
  between their decoded values before either destination is read. Charge
  common-frame delivery and all restoration. A relation alone is insufficient.
- Can a fixed plan with two replacement frames beat the one-frame steps?
  Price all copies, sums and helper targets first. Then check the complete word.
  The finite searches in DISCOVERY.md do not prove a global optimum.

Prepared by Ali Romman with substantial OpenAI Codex assistance. No subagents.
Apache-2.0. [NOTICE](NOTICE) retains all predecessor credit.
