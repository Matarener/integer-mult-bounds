# Source gauges cannot help before the third use

**Claim type: scoped proof with exact finite corroboration. No new κ.**
This contribution was produced by Nick Petalas.

In the restored dyadic ADD-once bipartite model of [PROOF.md](PROOF.md),
temporarily scaling sources cannot reduce the optimum if every source is
used at most twice. This holds with arbitrary simultaneous target gauges,
ADD order, integer gauge excursions and arbitrary dirty initial fields.
The optimum reduces to Dugongue's target-only interval formula from
[PR #4518](https://github.com/CrocSwap/integer-mult-bounds/pull/4518).

Three uses are the first possible strict gain. For one source feeding d
distinct targets with coefficient o 2^v, o signed odd, the exact optimum is

```text
d c(o) + 2 min(d,2)|v|,
c(o) = 2(2 + bit_length(|o|) + popcount(|o|)).
```

The target-only optimum is d c(o)+2d|v|. At d=3, o=1, v=-1, a restored
source scaling gives cost 28, versus the exact target-only minimum 30.
The inverse-dual word has the same cost and full dirty-state correctness.
The star construction is elementary shared-factor extraction. The new
contribution is the elimination theorem, its exact coupled optimum and
sharp source-use threshold under this schedule contract.

The proof erases a source's gauges, saving at least four times its maximum
absolute gauge. Each incident ADD can lose at most twice that maximum.
At two uses the saving covers the entire possible loss. This supplies a
pruning rule for the coupled source/target question in #4518 Open next
question 2. A single row with distinct sources is an immediate special case.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -B research/low-use-source-gauges/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -O -B research/low-use-source-gauges/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/low-use-source-gauges
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/low-use-source-gauges --check-source-history
```

Another CPython 3.12 path may replace the one shown. Direct replay prints
`PASS_LOW_USE_SOURCE_GAUGES no_new_kappa` and a freshly generated stdout
receipt binding the package files by SHA256. It writes no files. Registered
replay runs both normal and optimized modes with warnings treated as errors.

The exact finite checks enumerate:

- All 256 two-source/two-target lists with each of four pairs absent or
  carrying valuation -1, 0 or 1, and fixed alternating odd parts 1 and -3.
  A separate Dijkstra oracle searches every ADD order and gauge state in
  {-1,0,1}. Coupled and source-fixed minima equal the interval formula.
- 81 prescribed gauge-path fixtures at levels -2, 0, 2, comparing each
  original and source-erased program on all arbitrary-input coefficients.
- 18 star shortest-path problems and their 18 reversed-incidence versions,
  with one to three leaves, valuations -1, 0, 1 and odd parts -3 or 1;
  51 additional degree-three witnesses with valuations -8 through 8 and
  odd parts -3, 1, 5. Reversed stars exercise profitable target gauges while
  all sources remain low-use.
- Full physical and inverse-transpose endpoints and tariff equality for
  every checked word. Six invalid contracts are rejected. Two further
  controls detect wrong coefficient compensation and failure of the
  low-use premise at degree three.

The finite gauge box corroborates the new theorem; it does not prove the
unbounded optimum by enumeration. The written proof carries that quantifier.
The predecessor's native program, counts and scientific suite are not replayed.

## Scope and sources

Base `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the retained #4518 model, tariff, interval
theorem and dualization statement at head
`2b71c89a7ca0ad41f12149d7971e73f16f320e81`. The catalogue and selected
record are historical provenance. Both predecessor files are authenticated
before direct replay. Its mathematical results are cited inputs.

The scope requires disjoint source/target roles, each listed contribution
once, only positive power-of-two gauge scales, and every gauge returned to
zero. Repeated entries count as repeated uses. Role mixing, factoring the
ADD list, borrowing, source writes, target reads, different prices and
unreturned gauges are outside the result. No actual P104 word is changed.
No paid recursive gain, physical implementation, precision/tape saving,
supplier admission or complete multiplication theorem is claimed. All five
selected framework assumptions remain. Selected cold replay, Lean, Docker,
independent human review and proof-kernel review are unrun.

Before reservation, live open PRs, recent account PRs, handoff comments,
active Discussions, local locks and main/merged-work searches were checked.
The overlap helper reported complete pagination of 379 open PRs and 5,780
Discussion records, but only 60 of 8,348 local notes. Searches of main's
README objects and relevant merged PRs supplemented that sparse cache.
These searches do not establish global literature priority.

Ali Romman's [#5824](https://github.com/CrocSwap/integer-mult-bounds/pull/5824)
and [#5830](https://github.com/CrocSwap/integer-mult-bounds/pull/5830) already
optimize different fixed P104 representation graphs with exact flow duals;
[#5783](https://github.com/CrocSwap/integer-mult-bounds/pull/5783) supplies
related exact binary-cut tooling. Richard Hoekstra's
[#1235](https://github.com/CrocSwap/integer-mult-bounds/pull/1235) normalizes
endpoint gauge tours in a different rank-priced phase model. None is an
audit target or an executable dependency here. No new general gauge,
shared-factor, shortest-path or flow algorithm is claimed.

## Open next questions

Which sources with at least three uses in a named complete native window
admit a profitable restored gauge after all surrounding interfaces are
charged? Start by extracting one ADD-once bipartite window and its existing
target-only optimum, then remove low-use source variables with this theorem.
The remaining emitted-window, caller, native and precision/tape contracts
block physical adoption. The present package stops at the sharp threshold.

## Verification design

The verifier is a separate standard-library implementation and imports no
predecessor code. Its finite domain enforces at most four roles, four ADDs,
valuation magnitude eight and 1,000 events. The oracle has at most 1,296
states and 15,553 heap pops, with parent reconstruction bounded by the state
count. Other enumerations have literal finite products. Functions have
fewer than 60 lines. Explicit exception-based invariants remain active under
`-O`; all arithmetic is exact. No recursion, runtime code generation or
external solver is used.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py`: CPython,
Fraction and heap/dictionary operations allocate during execution. The
enforced capacities bound live state and rational sizes; no retained
external resources or output files exist. Static input sizes and the finite
loop bounds compensate for the lack of allocation-free Python operation.
A fixed-storage implementation would be needed for an allocation-free
runtime; that is outside this scientific check. Warning-strict normal and
optimized runs are the available local diagnostics.

## Credit

Credit David Ganz / Dugongue for #4518's native dyadic tariff, target-only
interval theorem, emitted interfaces and coupled-path question. Its
PR #4502/#4505 borrowed-adapter and native lineage retain their attribution.
The Levi inverse-transpose identity is classical and used as in #4518.
Credit Ali Romman and Richard Hoekstra for the related gauge work above.
New work is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
