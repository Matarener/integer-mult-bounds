# A signed R429 lift: lower range, mixed error sensitivity

Changing 23 of the 47 quotient ADD coefficients in the published R429 word
preserves its complete binary map, arbitrary integer helper restoration and
paid rank mass 4989. It changes the integer lift. The selected scalar controller
has a smaller normalized range bound, but forward additive-error sensitivity
increases. This is a fixed witness and conditional scalar-network calculation,
not a precision-admitted supplier.

The immediate parent is [PR3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645),
head `99b901c9b5ac70cf441b3d7e585cc7b8744b5359`. Parent gzip SHA256 is
`1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870`;
the signed witness is
`e802611104c61fc8477837b4ab41abc4f13cf41fbca6ef3de60d0b5e768fb949`.
The unchanged `parent_word_gzip_sha256` field inside both artifacts names
their earlier support-code ancestor, not this immediate sign-variant parent.

## Exact local contract

There are 111 source fields, 111 target fields, 429 arbitrary dirty helpers
and one private field initially zero. Both words have 16,102 records,
2,873 MOVEs, 13,223 ADDs and three immutable COPY/ERASE pairs.
The independent integer checker covers every public input column in both
directions and both integer roundtrips. It derives the binary source matrix
from the original R438 word, rather than assuming the saved matrix.

The binary interface is `(x,y,h) -> (Ax,y+Ax,h)`. Over the integers the
interface is `(A_Z x, y+T_Z x+E_Z h, h)`, with its literal inverse and exact
private return. The even dirty block need not vanish. For the signed witness,
`A_Z[0,0]=-23`, `T_Z[0,0]=-125` and `E_Z[0,4]=2`; it is not an integer
pure shear. All native frame and copied-source lifetimes are retained.

The fixed prefix–quotient–suffix factorization explains the whole sign family.
Its nine-dimensional changed block cannot change integer helper leakage;
forward target changes are confined to three rows. The current forward witness
has source delta rank 9 and target delta rank 3. The universal bounds and their exact
premises are proved in [PROOF-INTEGER.md](PROOF-INTEGER.md).

## Range and error are different comparisons

| Quantity | Parent | Signed witness |
| --- | ---: | ---: |
| Exact forward scalar prefix row norm | 34,285 | 80,639 |
| Exact inverse scalar prefix row norm | 5,839,860 | 239,014 |
| Selected controller scalar upper-bound bit length | 458 | 401 |
| With the specified terminal scalar code sweeps | 601 | 519 |
| Historical 64-bit block allowance for controller range | 512 | 448 |
| Corresponding allowance with terminal scalar sweeps | 640 | 576 |

The local scalar maxima have explicit attaining unit-box inputs. The global
numbers are sufficient upper bounds, not exact maxima or minimal word widths.
They include all 63 selected source-code factors, all nine local calls,
all 18 ordinary bank shears and the current encoded helper magnitudes.
Sign storage, initial input scale, native child interiors and physical access
are separate obligations.

The controller artifact also contains an older 6,372-gate code. Its binary
endpoint differs from the selected 1,499-ADD source code. This package uses
only its ordered abstract schedule, instantiating every sweep with the actual
selected code or its literal inverse. An independent calculation in the free
noncommuting polynomial algebra over GF(2) checks the schedule identity.
Its interpretation here uses the selected invertible stage codes.
No claim is made that the artifact's older code listing is the new integer word.

For a scalar defect of magnitude at most one at the destination immediately
after each eligible atomic event, the exact completed-output constant is
`J=max_j sum_i |(S_i e_dst(i))_j|`, where `S_i` is the suffix after that event.
Every event and all output coordinates are covered. Independent dual-row and
forward executions attain the reported constants.

| Eligible defect locations; exact scalar J | Parent | Signed witness |
| --- | ---: | ---: |
| Forward, all events except exact ERASE | 880,068 | 1,081,994 |
| Inverse, all events except exact ERASE | 34,848,225 | 1,255,309 |
| Forward, MOVE and COPY only | 383,045 | 479,557 |
| Inverse, MOVE and COPY only | 1,239 | 1,239 |

Thus the inverse all-event improvement comes from ADD sensitivity; the inverse
MOVE/COPY aggregate is unchanged. The forward bounds worsen. These are exact
constants of the stated normalized scalar assignment model, not an analysis
of arbitrary native child defects. COPY and ERASE use their exact abstract
assignments; physical copied-workspace cleanup under perturbations is not
proved by an assignment that simply clears a coordinate.

The earlier saved suffix receipt concerned a different 660-input, six-copy
word. Its values are not transferred here. Both actual 651-input words are
recomputed in [PROOF-RANGE.md](PROOF-RANGE.md) and the new complete receipt.

## Verification

Use CPython 3.12 from the repository root:

```sh
python3.12 -B scripts/check_research_commit.py --package research/r429-signed-range --check-source-history
python3.12 -B scripts/research_package.py --package research/r429-signed-range
```

[VERIFY.json](VERIFY.json) registers the bounded checks.
[EVIDENCE-INDEX.md](EVIDENCE-INDEX.md) separates the retained original functions,
two independent implementations, written proofs and acceptance controls.
No sign search is repeated. The fixed historical signed receipts and all new
receipts are compared completely, preserving JSON scalar types and list order.

Original bytes are pinned in [ORIGINS.json](ORIGINS.json) and
[FROZEN-SHA256.json](FROZEN-SHA256.json). Large unchanged JSON inputs and full
receipts are gzip-compressed for storage; decompressed original hashes are
checked separately. Retained functions are selected from authenticated ASTs;
their imports and original entrypoints are not executed. Complete independent
checkers are also compiled from authenticated bytes, with assertions enabled
under optimized parent Python.

[REVIEW-INTEGER.md](REVIEW-INTEGER.md), [REVIEW-RANGE.md](REVIEW-RANGE.md)
and [REVIEW-VERIFICATION.md](REVIEW-VERIFICATION.md) are separate AI reviews,
not independent human acceptance or formal-kernel proofs.

## Open next questions

No optimality of the 23-sign witness or of any width allowance is claimed.
The paid rank profile is unchanged. The scalar controller bounds do not
repair the terminal/owner deficit in
[PR4185](https://github.com/CrocSwap/integer-mult-bounds/pull/4185).
No selected frontier file is changed and no new kappa is claimed.

The next precision obligation must specify the input lattice, native child
interiors, permitted defects, internal storage and exact copied-state return.
The completed-word atomic constants do not bound all perturbed prefixes or
state-relative feedback. A favorable range calculation alone cannot discharge
those obligations.

## Sources and credit

The R438 word lineage is due to Ali Romman/PR1043, with transport and rehosting
from Sagar Thakrar/PR2423 and the prior PR1307 geometry ancestry.
The source-code word is Ross Richardson's PR3645; original source headers,
notices and exact bytes are retained. The fixed signed witness, independent
mathematical checks, added proofs and publication were prepared by Ross
Richardson with substantial OpenAI Codex assistance. Apache-2.0.

Scientific source artifacts retain their original
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` context; publication guidance and
catalogue revision 7 are pinned at
`12fa8c5c844be21bfefb38a19503fbd867a11244`.
[RELATED-WORK.json](RELATED-WORK.json) records overlap scope and exact heads.
