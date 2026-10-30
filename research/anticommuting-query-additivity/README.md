# Two anticommuting query types have an additive exact tariff

This contribution was produced by Nick Petalas. Claim type: scoped algebraic
proof with exact finite corroboration. No new κ or physical supplier is claimed.

For a faithful algebra with Q²=R²=I, RQ=-QR and ordinary coefficients
A=product_c Mat_(d_c)(K), char(K)≠2, the input-preserving shear

    y += (A0 + BQ + CR)x

has the exact query count

    max_c ceil(rank(B_c)/d_c) + max_c ceil(rank(C_c)/d_c).

Every word needs the first summand in Q calls and the second in R calls, even
with arbitrary linear feedback, retention, overwriting and restored borrowed
dirty fields. One source-preserving word attains both bounds and streams its
queries through one zero-return owned field. Positive unequal type prices give
the corresponding weighted sum. Ordinary routing is still charged separately.

[PROOF.md](PROOF.md) gives the complete model and argument. To lower-bound Q,
grant every R call for free, split the enlarged ordinary algebra into R's two
eigenspaces and factor the final Q coefficient through the Q outputs. Reverse
the roles for R. The two inequalities hold for the same original word.

The distinction matters even for A=K×K. Demands B=(1,0), C=(0,1) need two
queries globally, although each component needs only one. Taking the maximum
of each component's total would undercount. Noncommutative matrix blocks can
still pack several same-type demands; the explicit Mat_2 example needs one Q
and one R rather than four separately acquired responses.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/anticommuting-query-additivity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/anticommuting-query-additivity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/anticommuting-query-additivity --check-source-history
```

Use the last command after committing. On another machine substitute its
CPython 3.12 path. Both registered commands must finish with
`PASS_ANTICOMMUTING_QUERY_ADDITIVITY`; the launcher then reports
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The checker runs independently written formal-coefficient and literal-payload
interpreters on every original source, receiver and borrowed input column:

- All 6,561 pairs of scalar 2×2 response matrices over F_3.
- All 6,561 pairs of one-role Mat_2(F_3) response matrices.
- 216 rectangular/product-algebra fixtures over F_3,F_5,F_7, with nonzero
  ordinary response terms and dimensions up to three source/receiver fields.
- The explicit packed Mat_2 example and the two-component sector-conflict
  example, including arbitrary receiver/borrowed inputs and scratch restoration.
- All 1,555 words of length at most four in a six-instruction, two-role
  feedback alphabet. Their complete mixed coefficients satisfy both type cuts.
- Eight rejection controls for query deletion, wrong query type, dirty-owned
  leakage, borrowed-field corruption and invalid finite-model parameters.

The interpreters enumerate 149,742 input columns across the first three
fixture families. These are basis-column comparisons, not that many input
assignments. Their formal circuits contain 213,064 instructions in total.
The feedback enumeration corroborates lower bounds and is not an exhaustive
search over the theorem's arbitrary programs. Each run emits its counts and
SHA256 hashes of the six package files as a generated receipt to stdout; it
writes no files. No receipt is handwritten or retained as a frozen result.

## Scope and provenance

The target is the anticommuting-involution specialization of RQ09 in David
Ganz's [PR5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803), exact
head `0acda5ab421d28b98fdf916968696c8f9453376f`,
[volume-algebra.md](https://github.com/CrocSwap/integer-mult-bounds/blob/0acda5ab421d28b98fdf916968696c8f9453376f/research/frontier-mathematical-atlas/volume-algebra.md).
Credit its R03-R06 single-query inner-rank framework and explicit two-type
question, Ali Romman's [PR5626](https://github.com/CrocSwap/integer-mult-bounds/pull/5626)
faithful-sector compiler, Dugongue's PR5578 T6/T7, and the retained native,
phase, ownership, controller and compiler lineage, including Cao Yifan,
Cinna Davis, Ryanson Jonathan, zxv and Jacob Alan Sussman. Classical rank
factorization and Clifford algebra are not claimed as globally new.

The proof is self-contained. No predecessor verifier or numerical result is
replayed, and no pending source object or network service is needed to run the
checker. The cited atlas is bibliographic context, not a runtime input.
[SOURCES.json](SOURCES.json) pins the original catalogue and selected record
as historical provenance. [TASK.json](TASK.json) explicitly records the change
from the source-bound decoder card to this algebraic side result.

Live overlap checking included open PR metadata, this account's earlier PRs,
recent handoffs, active Discussions, merged-PR searches and all-main README
searches for the distinctive algebra and tariff. The overlap snapshot covered
426 open PRs and 5,328 Discussion records. Its sparse local search covered only
225 notes out of 7,845; the all-main Git searches cover omitted README paths,
not every package file or historical wording. These checks are not proof of
novelty.

The theorem excludes mixed QR target terms, characteristic two, nonfaithful
representations, extra ordinary operators, nonlinear instructions, queries on
multiple fields and choosing query type per component. Actual native Gaussian
realization, physical coefficient words, complete routing/precision/stock and
signed-moment funding remain unproved. No selected source or frontier changes.
Independent human and formal proof-kernel review are unclaimed.

## Verification design

The retained checker has no recursion, subprocesses, network access, external
dependencies or writes. Its fixed enumeration bounds, at most two components,
block size two, three source/receiver fields and 57 instructions bound all
work. Each matrix operation checks its dimensions; mathematical checks raise
explicit exceptions and survive optimized Python. Functions remain under 60
lines. Managed Python allocations are a Power of Ten deviation: these bounded
finite matrices allocate during evaluation; there is no fixed-memory runtime
claim. Warning-strict normal and optimized execution supplies the available
interpreter diagnostics. No separate static analyzer is installed.

## Open next questions

- Determine the exact minimum when a QR output coefficient is present. First
  compare the two type-specific projected ranks with explicit mixed words.
  The present proof supplies no attaining general constructor for that domain.
- Instantiate one faithful native caller with both query types and ordinary
  spectator matrix units. First pin the operators, phases and four-coefficient
  independence, then price the full producer/consumer. Its physical contract
  and complete paid/productive invoice are still missing.

New work is Apache-2.0. The predecessor notices remain with their sources.
