# One-query endpoint obstruction with a paid scan lower bound

**Scoped caller result; no new κ or selected-frontier change.**

## Result

For the fixed triangular cut
`C_f=[[Q_f-I,N_f],[Q_f,0]]`, two arbitrary independent carrier banks,
and one unary query on an M-dimensional bank, fixed finite uniform-tensor
physical-monomial endpoint dictionaries cannot implement C for every f.
The proof allows arbitrary f-dependent scalar coefficients and arbitrary
query U. It uses tensor-ray separation, not false matrix independence at f=1.

An independent support argument allows growing, nonuniform physical
monomial controllers. The actual N and all 18 admitted primal/dual Q base
operators are unitary, four-flat in every physical column, with maximum
entry modulus 1/2. Their tensor recipes therefore force endpoint column
supports `K_G K_F>=4^f`, and hence at least `a_G+a_F>=2f` scalar bank ADDs.
A paid O(f) ADD word is allowed by this bound.

The same-size restored dirty-helper extension retains the dimension
contradiction. The separately stated variable-width extension requires
queried width `w<=M`. An arbitrarily wider queried helper is outside it.

## Proof and exact coverage

The [proof](source/q4-pauli-fusion/ONE-QUERY-ENDPOINT-OBSTRUCTION.md)
retains the untouched-column argument, a constructive tensor-separating
polynomial and Cauchy's support-uncertainty inequality. The actual base
checker computes every Gaussian entry of all 19 native matrices and the
monomial positive control, and checks orthonormality of all 64 columns.
The replay rejects a monomial relabelled as a four-flat native and checks
the exact helper-width boundary. These controls run in both Python modes.

The [archival search appendix](source/q4-pauli-fusion/EXTENSION-HANDOFF.md)
retains C36's repeated, varied-primal and primal/dual-routing screens,
their exact scripts and receipts: respectively `24^5`, `26^5`, `26^5`
declared five-query choices with the precise bank/route/endpoint alphabets.
All source and receipt bytes are checked, but these large searches are
**not reexecuted by the registered command**. Their historical exact
search coverage is separate from the fresh all-base Gaussian replay and
the written endpoint proofs. No general five-query impossibility is asserted.

## Limits

This concerns the displayed triangular C and endpoint contracts.
It does not exclude a changed carrier cut, balanced gate with a new
proof, growing paid ADD controllers, multi-bank queries, wider queried
helpers, nonmonomial free endpoints or cross-cut sharing. It is not a
full-caller stock lower bound or a new asymptotic bound.

## Reproduce

From the repository root, on Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/one-query-endpoint-scan
python3.12 -B scripts/check_research_commit.py --package research/one-query-endpoint-scan --check-source-history
```

The registered manifest runs `verify.py` normally and with `-O`. Its direct
portable equivalent is `python3 -B verify.py` (or `python3 -O -B verify.py`)
from this package. The direct command needs only standard-library Python,
no Git/network and no original Ross-specific directory. `--json` prints the
complete replay summary. It writes no package files.

[BINDINGS.json](BINDINGS.json) retains every consumed original source/data
byte hash and explicitly records the path-only adaptations. Original versions
of adapted scripts remain under `original/`. Other source bytes and historical
receipts remain unchanged. Those receipts retain their old absolute provenance
paths; they are data, not required filesystem locations. The replay adapter
resolves only the explicitly retained original source inventory. Original lane
notes are archival and keep their original scope and attribution.

The source loader hashes and compiles the **same bytes**, never loads `.pyc`,
and compiles historical implementations with `optimize=0` in both parent
Python modes, preserving inherited assertions. Mathematical receipt comparison
omits only the enumerated provenance fields in `verify.py`; all such retained
input bytes are checked separately. A changed-source control rejects. Hashes
provide integrity against the trusted publication, not external authentication
or mathematical correctness. Git/source-history, export integrity, finite
replay, written proof, hosted CI and supplier admission remain separate.

## Related work and credit

Ross Richardson with substantial OpenAI Codex assistance, including separate
mathematical checking contexts and this packaging adapter. No independent
human or formal-kernel review is claimed. New work is Apache-2.0.

The Gaussian-dyadic compiler is inherited unchanged from icekylinx's PR531
through Rohan Arun's kernel92 composition. The exact original notices and
source ancestry are retained in `source/vendor/credits/`; they preserve
DreamingOfClouds, Dugongue, eumemic and the geometry/compiler lineage.

Chris R / Clear1nsight's PR3987 and ToikY's PR4002 retain credit for generic
native-lift phase/cocycle normalization and the need for exact signed/global
phase witnesses. This package makes no generic normalization priority claim.
Chris R's PR3989 and PR4045 are related explicit interface/volume-cost results;
their different fixed sources and theorems are neither imported nor claimed
as new here. These named overlaps were read at exact heads:

| PR | Exact head | Contributor |
|---|---|---|
| [#3987](https://github.com/CrocSwap/integer-mult-bounds/pull/3987) | `fc536202fdaa924158789a5ef59ac079bbe21922` | Clear1nsight |
| [#4002](https://github.com/CrocSwap/integer-mult-bounds/pull/4002) | `d593941ea0a4926021cba9d01fe60500579e464f` | ToikY |
| [#4023](https://github.com/CrocSwap/integer-mult-bounds/pull/4023) | `9124007ea9029a9a3b88898bb4c350ddb27ffa58` | RossRichardson |
| [#3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989) | `7b6dda7ab6ed10d608ecba357ac2f6924166d38b` | Clear1nsight |
| [#4045](https://github.com/CrocSwap/integer-mult-bounds/pull/4045) | `91afbb643f7f4ccf6f34b685ecd959eb790a0f94` | Clear1nsight |

[RELATED-WORK.json](RELATED-WORK.json) separately inventories the already
published PRs 3630/3632/3645/3649/3655 and separate BIT PRs 4021/4023.
Their publication is not supplier admission. This contribution neither
constructs BIT nor duplicates those results. The recent-PR/live-discussion
overlap has explicit partial coverage, not a proof of novelty.

## Open next questions

Can an explicit growing paid endpoint word or a multi-query changed-cut word fit a complete caller budget? Write its physical operands, exact endpoint columns and scan lengths; compare with the 2f lower bound before any all-size pricing claim. The retained fixed alphabets found no favorable word; no general search, physical admission or compatible joint supplier is supplied.
The same question, relevance, feasible first step and blockers are in
[TASK.json](TASK.json).
