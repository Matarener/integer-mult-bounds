# A restored third bank does not add an unpaid coordinate

**Scoped obstruction. No new κ. The selected record is unchanged.**

Original card: `coverage-law-change`. The actual question is the third-bank cycle left open by
[multipair-schedule-bound](../multipair-schedule-bound/README.md): can a cycle `X → Y → Z` leave
more than one unpaid coordinate per family? Scope status is **refined**. The full card, the reason
for the refinement, and the bottleneck link are in [TASK.json](TASK.json).

## What is certified

The selected nested contract in
[INHERITED-COMPLEX-GEOMETRY.txt](../split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt)
starts at `X_(-1)=C_q` and ends at the Y endpoint `C_all C_q^(-1)`, with `m=73`. That note states
that a nested transition has Fourier rank equal to the dimension difference of the Lagrangian
preimages. On binary frames this package uses that dimension rule directly:

- a frame is nested when every initial vector lies in the final span;
- the unpaid count is the initial rank;
- the acquired count is the final rank minus the initial rank.

The selected initial direction inside the full 73-dimensional frame has unpaid count 1 and acquired
count 72. That is the `72W` term in the coverage identity `mass = 72W + 64N`. The selected word
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` then has local mass 5586, idle mass 1646, and deficit
`320/9` at centre charge 64.

Four explicit frames, each checked by Gaussian elimination:

| Schedule | Initial frame | Final frame | Nested | Unpaid | Acquired |
|---|---|---|---|---:|---:|
| Selected family | one coordinate | full `F_2^73` | yes | 1 | 72 |
| Restored dirty bank | a 2-dimensional bank subspace | the same subspace | yes | bank rank 2, family still 1 | 0 |
| Datum copied into a second bank | the family coordinate | that coordinate plus the copy | yes | 1 | 1 |
| Cleared source, new bank written | the family coordinate | a different coordinate | no | — | — |
| Plane-port initial frame | two coordinates | full `F_2^73` | yes | 2 | 71 |

A restored bank returns to the subspace it entered, so it acquires no data direction. The family's
initial frame is still the single coordinate `C_q`, and the family unpaid count stays 1. Copying
that datum into a second bank acquires one direction. That direction is paid mass. Two unpaid
coordinates appear when the initial frame itself has rank 2. That is the plane-port contract
already screened in [plane-port-copy-budgets](../plane-port-copy-budgets/README.md), whose
complex break-even copy charge is about 160–164 per call. This package does not reprice it.

## Excursion prices

The ceiling engine is the pinned
[complex-local-word-ceiling](../complex-local-word-ceiling/ceiling.py), grid `1/10^12`, idle cap
`R=51`, `w=896/9`. The selected saving is
`a = κ/(1-κ) = 836330098538459/499163669901461541`
for `κ = 836330098538459/500000000000000000`.

| Profile | Idle mass | Deficit | Ceiling high endpoint |
|---|---:|---:|---:|
| Selected word, unpaid 1 | 1646 | 320/9 | 169005411/100000000000 |
| One extra rank-1 child per live family, unpaid 1 | 13918/9 | 320/9 | 1659158299/1000000000000 |
| Two extra rank-1 children per live family, unpaid 1 | 13022/9 | 320/9 | 1629372687/1000000000000 |
| Same word, unpaid 2 | 13918/9 | 1216/9 | 6377984109/1000000000000 |

The one-step and two-step ceilings are about 0.982 and 0.964 times the selected ceiling. At the
selected saving, ideal idle packing of the selected word has relaxation strictly below 1. The same
packing of either excursion has relaxation strictly above 1 (floating orientation about 1.000048
and 1.000139; the certificate is the inequality). Paying the third-bank copy on the selected word
therefore misses the current saving.

The unpaid-2 ceiling is `708664901/187783790` times the selected ceiling, which prints as 3.77×,
the lever in [levers.py](../complex-local-word-ceiling/levers.py). Its idle mass equals the
one-step idle mass `13918/9`, because one extra unpaid coordinate and one extra rank-1 child per
family move the same amount of mass. They move it in opposite directions: unpaid 2 enlarges the
deficit and leaves the word's children idle-cheap, while the excursion spends that mass as rank-1
children and keeps the deficit at `320/9`. The shared idle figure is the integrality obstruction
recorded by PR #3757 for a two-unpaid histogram. This package uses it only to separate those two
schedules.

## Domain and limitations

The frames are the binary preimages of the `C_q` products. The verifier authenticates the geometry
note, the multipair question, the selected word, and the selected κ, then counts ranks. It does
not replay Clifford phases, the 946 local frames, or a native tape.

A cleared source has intersection zero with its replacement bank, so the nested unpaid rule does
not apply to it. A schedule that erases an initial direction and still leaves two unpaid
coordinates would need a different contract. No such schedule is supplied here.

The ceiling calls are ideal idle packings of one changed histogram. They are planning bounds.
They do not exhibit a circuit, and they do not change the selected frontier.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/three-bank-restored-unpaid/verify.py
python3 scripts/research_package.py --package research/three-bank-restored-unpaid --check-only
python3.12 scripts/research_package.py --package research/three-bank-restored-unpaid
```

`verify.py` prints

`PASS_THREE_BANK_RESTORED_UNPAID restored_adds_unpaid=false one_step_exceeds_selected=true no_new_kappa`

and checks [RESULT.json](RESULT.json) against a fresh execution. Pins are in
[SOURCES.json](SOURCES.json). The selected record and the task catalogue are historical
provenance at base `bb4bccbf42844d2801487450727c2f63e10d1d0f`. Live inputs are the five paths in
[VERIFY.json](VERIFY.json).

Rejection controls inside the same run: a restored bank with positive acquired rank, a copied
second bank counted as unpaid 2, and a one-step excursion whose relaxation still meets the
selected saving.

## Open next questions

1. **Can a non-nested three-bank schedule, one that erases an initial direction and rewrites it, leave two unpaid coordinates without becoming a plane port?**
   The nested contract is what makes the unpaid count equal the initial dimension. An erasure could in principle be paired with a second surviving direction. First step: write one explicit erasure and rewrite on three coordinates and count `dim(initial ∩ final)` after every paid climb. Blocker: no candidate schedule is supplied. The cleared-source example in this package drops the intersection to zero.

2. **If the third bank is identified with a second initial direction, does any scalar endpoint pass the paired-plane obstruction while staying inside the plane-port copy budget?**
   That identification is the actual two-unpaid contract. The 3.77 multiplier is the ideal screen. First step: recheck [paired-plane-scalar-mask-obstruction](../paired-plane-scalar-mask-obstruction/README.md) on one concrete endpoint whose copy charge is at most the certified complex budget near 160 per call. Blocker: this package does not contain a scalar endpoint or a native copy program.

## Credit

- The third-bank question and Theorem S are from themilkman216,
  [multipair-schedule-bound](../multipair-schedule-bound/README.md).
- The ceiling and the 3.77× lever are Douglas Colkitt's
  [complex-local-word-ceiling](../complex-local-word-ceiling/README.md), with Claude (Anthropic)
  assistance, Apache-2.0.
- The nested Fourier-rank rule, `m=73`, and the `C_q` endpoints are the inherited complex
  geometry note above. Its predecessor attribution stays in that file.
- PR #3561 (jwr404) caps a line-port replica offset at one unpaid coordinate per family
  (896). PR #3757 records that the two-unpaid idle mass `13918/9` is not an integer histogram
  on one call. Plane-port copy budgets are a separate contract and are not recomputed here.
- The selected κ is the repository's selected record. This package does not replace it.

Prepared by unpaidmoon with substantial Cursor Grok assistance for the proof check, the ceiling
calls, and the package text. New work is Apache-2.0.
