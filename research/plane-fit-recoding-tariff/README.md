# Recoding the fixed plane fit still costs 224

Proved, under the full-plane one-total tariff: every spanning scalar query list
in the literal orthogonal-group fitting matrix's row space costs at least 224,
over every field. The disjoint indicator basis attains 224. Thus every
rank-minimal factorization of this same matrix has sharp tariff 224, including
arbitrary dense changes of query basis.

The theorem applies to any even orthonormal partition of P112. The concrete
replay binds PR3370's rank 32 partition, with eleven size-eight, two size-six and
three size-four groups. It does not construct a new partition. PR3345 and
PR3370 already priced their literal indicator factors at 224; the new result
excludes an arbitrary scalar recoding as a way to lower that tariff.

[PROOF.md](PROOF.md) gives the weighted spanning lemma and its application.
[RESULT.json](RESULT.json) contains the exact concrete receipt. This is a scoped
negative cost result, with no new kappa or selected-frontier change.

## Evidence and reproduction

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/plane-fit-recoding-tariff
```

Direct source-export checks also work without Git:

```sh
python3.12 -I -Werror -B research/plane-fit-recoding-tariff/verify.py
python3.12 -I -O -Werror -B research/plane-fit-recoding-tariff/verify.py
python3.12 -I -Werror -B research/plane-fit-recoding-tariff/independent.py
python3.12 -I -Werror -B research/plane-fit-recoding-tariff/test_package.py
```

The primary replay checks all 65,535 nonempty group closures, 11,392 forced mask
entries, and 37,632 exact factorization entries over F2, F5 and F1000003. The literal
basis costs 224; a dense basis costs 288. The separate checker imports no primary
code, uses explicit coordinate vectors and dense elimination, and checks 137
geometric sets plus 264,864 invertible two-query recodings over F2, F3 and F5. These
are deterministic exact counts. The all-field theorem comes from the written
proof, rather than extrapolation from the finite tests.

Seven behavioral groups include four actual CLI mutations. They reject changed
selected bytes, changed retained bytes, a false 223 receipt, a duplicate port
even after repinning, a singular query family and a query outside the row space.
Default verification writes no evidence. The test suite uses private disposable
copies and honors TMPDIR; set it to a session-owned external directory when
running in a shared research worktree. See [VALIDATION.md](VALIDATION.md) for
actual checks, bounded-code deviations and verification limits.

## Scope and sources

The binary tariff is defined by the complete-plane closure's source/reader Gram
rank. It ignores further coefficient implementation costs. The theorem fixes
both this tariff and the literal matrix K. It does not bound another fitting
matrix, overcomplete queries outside K's row space, a changed reader contract,
nonlinear production or shared native operations. Source access, frames,
restoration, hosting, precision and a full physical consumer remain open. The
selected conditional kappa remains 0.001672660197076918.

[SOURCES.json](SOURCES.json) pins canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6, and the selected
DATA-PHASES payload. [RETAINED-RANK32.json](RETAINED-RANK32.json) preserves
PR3370's certificate byte-for-byte from
`4cae85b18712b85a39905e51bde17346ccc5b805`. The checker authenticates its SHA256
and Git blob locally; it never needs that pending Git object or imports pending
code. The selected record and task catalogue are historical provenance.

Canonical investigation:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19008393.
Worker 2's fifteen-group local-repair investigation and the mixed566 common-cut equality work
are separate scopes. No partition search or native implementation was run here.

## Open next questions

Can a different fitting row space or a larger query space achieve tariff below 224?
Start with one exact K=UQ and check its complete strict mask and every query's
full-plane closure before a native construction. No lower-tariff alternative is
supplied here.

Can a changed reader or shared consumer avoid this additive tariff? First state
one real cut's source availability, coefficients, dirty restoration and consumer
outputs, then price the complete path. The physical bill is still missing.
[TASK.json](TASK.json) records the corresponding blockers and stop rule.

## Credit

Nick Petalas. PR3370's partition and finite interface are due to Tekalign.
The predecessor literal-tariff audit is PR3345 by Nick Petalas; the rank 34
rematching is PR3335 by Matarener/Mark, with the retained work of ywz65,
thakrarsagar, Cinna Davis, Adam Gall, ctoth, Philippe Van Velzen, Jeremy Diviney
and the selected E8/P112 lineage. PR3356 supplies predecessor frame-packing
context. Their constructions and source-specific credit are preserved.
New work is Apache-2.0. Assistance is disclosed in TASK.json; no independent
human or formal-kernel review is claimed.
