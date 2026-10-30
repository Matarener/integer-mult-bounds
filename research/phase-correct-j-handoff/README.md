# Phase-correct J caller and a fixed-core joint cleanup bound

**Scoped exact result; no new κ or selected-frontier change.**

For `q>=2`, put `n=2q+2`, `k=2q+1`, `m=4q+4` and let each native
fresh plane have arity `2f`. This package completes the original-input
joint H/L cleanup for the specified J caller and proves a lower bound
for every cleanup of its fixed scalar core and diagonal continuation.
It retains the complete operator, its actual `F_k J` target and endpoint
gauges, every independent original field, and all public readers.

## Joint cleanup theorem

Write `F_s=N_s...N_1` and suppose `J^2=-I` and the actual target
`T=F_k J` has full native support: every row has `2^(m f)` entries.
The physical source stage uses a separately admitted query
`K_s=F_(s-1) J F_(s-1)^-1`, scalar delivery, an arbitrary physical
source monomial `S_s`, and fresh `N_s` progress on every other bank.
The `S_s` need not be causal, Clifford or tensor products. The stated
scalar core, scalar retraction and diagonal continuation remain fixed.

Its required original-t/current-V inverse coefficient `C` obeys the
exact noncommutative identity

```
C R = T,
R = S_k N_(k-1) S_(k-2) ... S5 N4 N3 S2 S1.
```

There are exactly `q` native factors in R. No source monomial is
commuted through a frame. Each row of R has at most `2^(2q f)`
entries, so every row of C has at least `2^((2q+4)f)` entries.
Every native/monomial/binary-bank-ADD implementation of the complete
joint tail therefore satisfies

```
total actual native arity + binary ADD count >= (2q+4) f.
```

This includes joint public-reader fusion, physical monomial routing,
and arbitrary dirty helpers within the stated complete-state model.
The [all-q proof](source/joint-native/GENERAL-SOURCE-PROOF.md) separates
the symbolic identity from its exact free-word checks q=2..25.
An [independent literal audit](source/joint-native/literal_inverse_binding.py)
reconstructs the physical q2/q3 source prefix and original-input inverse
coefficient, including the f-dependent target-J unit.

## Explicit cost premise

The support inequality alone is a statement about arities and ADDs.
If every counted ADD costs a full scan of at least a fixed positive
fraction of volume V, a linear arity shortfall requires `Omega(V f)`
work. With fixed m and `f=floor(e/m)`, this is `Omega(V e)` and cannot
fit the retained `O(V e^lambda)` local toll for `lambda<1`.
An admissible fixed native tail profile consequently has mass at least
`2q+4`.

To compare this unweighted mass with the proper-child moment, additionally
assume **equal-volume full-bank native-child normalization**, including
every queried dirty helper: one unit in H and prescribed child volume
`V/W` for each counted native operation. At the separately exposed native
query sites the prefix has mass at least `n m-2q`; the completed mass is
therefore at least `n m+4`, above stock `n m`. For every `0<b<1` and
proper ranks `0<r<m`,

```
sum H[r] (r/m)^(1-b) >= sum H[r] r/m > n.
```

The [transfer proof and canonical sources](source/root-joint/FULL-SCAN-TRANSFER.md)
state these premises explicitly. Unequal queried-bank volumes require
their actual volume-weighted bridge and are outside this moment corollary.

## Complete exact caller witness

The [all-q caller derivation](source/caller-joint/JOINT-HL.md) gives the
full original-input H/L map and a conservative cleanup. Every public
L-reader uses scalar ADDs from completed public banks; no extra native
query is hidden in a reader, and no nonunit operator inverse is a primitive.
The complete physical word has

```
H[2]=n^2+1, H[4]=2, H[6]=1,
mass=stock+16, D=-16.
```

It is an exact negative invoice, not a saving. The written proof establishes
the all-q formula and tariff. The retained q2/q3 fixtures check all original
field columns, both literal inverse orders, all four Gaussian f residues,
actual bank slots and gauges, and selected-native realizations of every
native query. Omitting original-t restoration or the final public-reader
extraction rejects.

The producer generated the fixed selected-native recipes. The registered
verifier checks those witnesses independently instead of repeating expensive
synthesis. It reconstructs every recipe, compares complete signed Pauli
images, and separately compares an exact source column computed by integer
Walsh arithmetic with the physical recipe expansion. Together these fix
the whole Clifford operator including global phase. Every forward/inverse
event's recipe ID, embedding, actual rank and all-f unit tag is checked.
A compensated phase gauge is accepted; a wrong global phase, wrong rank
and the preserved pre-fix inverse-pointer receipt reject. The
[source-to-check map](REPLAY-MAP.md) gives the exact coverage and limits.

## Retained resource and factor-first gates

The preceding-run C37 source is `J_f=i^(f+1) Z U`, of arity `2f`,
on an already-paid full native old source E. Its mandatory Gaussian phase
gives `J_f^2=-I`; a constant i fails for odd f. The
[resource proof](source/native-frames/EVEN-PARITY-SOURCE-PROOF.md) and
[handoff proof](source/native-frames/EVEN-PARITY-HANDOFF-GATE.md) retain
the dirty-bank boundary and scoped monomial drift floor `2f`; the displayed
drift is `4f`, without a universal `4f` optimality claim.

C38's [diagonal factory gate](source/native-frames/DIAGONAL-J-FACTORY-GATE.md)
and [independent star audit](source/q4-pauli-fusion/STAR-FACTORY-AUDIT.md)
remain useful local checks. The old separately factored completion costs
`(2q+8)f` against available `2qf`. The new joint theorem resolves the
previously open unfactored cleanup for the stated architecture. These
earlier resource/factory entrypoints are still replayed, not promoted to
a generic normalization theorem or a global caller obstruction.

## Boundaries

The theorem keeps the scalar core/retraction, diagonal continuation,
separately exposed query sites, original-input/output contract and full
target support. Its moment corollary also keeps the declared scan and
equal-volume premises. It does not exclude a changed core or delivery map,
cross-cut query fusion, a different target/owner contract, scans on vanishing
volume, or a different volume-weighted transfer. It supplies no physical
precision, owner allocation, fixed-tape realization, compatible BIT
construction, formal-kernel proof or κ improvement.

## Review the proof and fixed evidence

The authored argument is in `GENERAL-SOURCE-PROOF.md`, `JOINT-HL.md` and
`FULL-SCAN-TRANSFER.md` at the links above. `REPLAY-MAP.md`, `verify.py`
and `source/current-audit/fixed_native_recipes.py` explain and implement
the independent witness check. The large `JOINT-PREFIX.json` and
`JOINT-COMPLETE.json` files are generated fixed operator evidence, not
additional authored proof. They retain complete physical matrices, source
columns, literal events, inverse words and native-recipe pools.

The old inverse-pointer receipt is reconstructed byte for byte from
`BEFORE-ID-FIX-PATCH.json` and the corrected complete receipt; both complete
SHA-256 pins are checked before running its original rejection. This avoids
a duplicate 122,387-line receipt while retaining the exact negative input.
Unconsumed historical screen outputs are omitted and inventoried in
`BINDINGS.json`; shared imported source implementations remain unchanged.
Those unrelated screen entrypoints are outside this package's registered
commands. No registered proof or rejecting control was removed.

## Reproduce

From the repository root, on Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/phase-correct-j-handoff
python3.12 -B scripts/check_research_commit.py --package research/phase-correct-j-handoff --check-source-history
```

The manifest runs `verify.py` normally and with `-O`. The portable direct
commands are `python3 -B verify.py` and `python3 -O -B verify.py` from this
package; `--json` prints the replay summary. They use standard-library Python,
need no Git/network or original Ross-specific directory, and write no files.

[BINDINGS.json](BINDINGS.json) inventories every retained source/data hash,
original source locations, and explicit path/source-binding adapters.
The original general-source proof is also retained; its readable copy
only narrows the cost paragraph to the final explicit equal-volume premise.
Historical receipts retain their original paths as provenance data.

The loader hashes and compiles the same bytes, never loads `.pyc`, and
compiles historical sources with `optimize=0` in both parent modes to keep
their assertions. Receipt comparison omits only enumerated provenance keys;
the full retained bytes are independently hashed. Fixed selected-recipe
fields omitted from generation-mode comparison are checked by the separate
recipe verifier. A changed-source control rejects. Integrity, finite exact
checks, written proofs, hosted CI and mathematical admission are separate.

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
| [#3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989) | `7b6dda7ab6ed10d608ecba357ac2f6924166d38b` | Clear1nsight |
| [#4045](https://github.com/CrocSwap/integer-mult-bounds/pull/4045) | `91afbb643f7f4ccf6f34b685ecd959eb790a0f94` | Clear1nsight |

[RELATED-WORK.json](RELATED-WORK.json) separately inventories the already
published PRs 3630/3632/3645/3649/3655 and separate BIT PRs 4021/4023.
Their publication is not supplier admission. This contribution neither
constructs BIT nor duplicates those results. The recent-PR/live-discussion
overlap has explicit partial coverage, not a proof of novelty.

## Open next questions

Can a different scalar core/retraction or continuation avoid the required
inverse coefficient while preserving every arbitrary original input and
actual public target? First specify one changed complete bank map, derive
its inverse original-input columns before costing it, and give its actual
native/ADD/volume bill. The fixed-core theorem above does not certify the
changed model. [TASK.json](TASK.json) records this question and its blockers.
