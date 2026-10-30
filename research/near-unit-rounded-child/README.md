# A near-unit Stein row in the retained rounded child

PR6228's p=3 producer can feed the unchanged PR4205 compensated rounded
generator child through an explicit source-bound adapter. On the padded
rank-one example, the smaller coefficient row changes P from3I/2 to23I/16,
but increases the scaled-G envelope from6 to48/7. Both versions use Gamma4
and the same allocator inputs. Their child/phase/multiplier/leaf/data widths
remain25/77/71/69/49 bits, with98 executed layers and264 gates each.
This is one concrete producer-to-child binding and parameter comparison,
not a precision saving, full Gaussian caller or physical delivery result.

## Object and evidence

Take v=(1,1,1,0), T=L(v), E=v e0^t. The original terms are g=v/2,a=2e0^t;
the actual new producer emits g=4v/7,a=7e0^t/4. The receiver requires a
power-of-two dimension, so the three-coordinate source example is explicitly
padded to4. Keep rank1, displacement bound3, radius2, target12 and incoming1.
`PROOF.md` derives the exact factor, scale and envelope comparison.

The wrapper loads the original producer unchanged, invokes the actual PR6228
producer, verifies its adapter contract, then runs the original rounded child
for both. Scientific modules are compiled with assertions enabled. All eight
caller code/data inputs equal the pinned PR4205 bytes on current main; the
single vendored PR6228 executable is byte-exact and separately authenticated.
Pending source history is retained for clean full-clone provenance checks.

Predeclared inputs per program are eight real basis inputs, eight imaginary
basis inputs and one mixed complex dirty-bank input of Euclidean norm 2
(squared norm 4). `CERTIFICATE.json`
contains the finite observations and `VALIDATION.json` records executed checks.
Each observation separately measures coefficient error, arithmetic rounding,
total error, source-return error and temporary height. Basis observations do
not imply a universal rounded-error theorem, because rounding is nonlinear.

The initial draft declared incoming0 for the mixed half-integer input. Source
review caught that invalid input contract before registered acceptance. The
17-input corpus is retained; both arms use incoming1 and an explicit grid
guard rejects the old incompatible declaration. The data49 allocation remains
unchanged. This correction is also recorded in the canonical Discussion claim.

Registered Windows11 / CPython3.12.11 normal and optimized executions pass
with identical complete receipts:34 observations and6 rejecting controls.
Maximum observed temporary height is212 bits for both children. This finite
height observation remains distinct from the inherited universal height bound.

## Reproduce

From the repository root, with standard-library CPython3.12:

```sh
python3.12 scripts/research_package.py --package research/near-unit-rounded-child
python3 scripts/check_research_commit.py --package research/near-unit-rounded-child --check-source-history
```

The normal and optimized registered runs emit deterministic JSON and a PASS
marker. No source files are regenerated. `SOURCES.json` identifies source
commits/blobs/hashes; `PREDECESSORS.json` identifies the executable vendor copy.

## Limits

The exact producer uses Gaussian-rational coefficients; denominator7 is
retained, not silently replaced by a dyadic native representation. This wrapper
does not replace the original frozen loader. The receiver is a compensated
Toeplitz-generator child used by the Gaussian pipeline; the chosen lower
Toeplitz matrix is not claimed to be an actual Gaussian kernel. No Full,
normalized/raw Gaussian or finite-core program is executed. Unrounded source
return is exact; rounded source return is checked only against its allowance.

The allocation is intentionally frozen. Its unchanged bits/gate counts are a
result for this declared example, not a general impossibility of exploiting
near-unit generators. Setup, coefficient pages, physical delivery, tape and
complete caller costs remain unpriced. No selected assumption, new kappa,
hosted CI, independent human review or formal proof-kernel acceptance is claimed.

## Open next questions

Can a separately proved norm-aware allocation exploit the new row in an actual
full caller after coefficient delivery is charged? First derive the changed
coefficient, prefix and rounding bounds, including the larger scaled-G factor.
Then bind a named caller and complete setup/delivery invoice. Neither that
proof nor a physical cost allowance is supplied here; see `TASK.json`.

## Credit

Nick Petalas owns PR6228's near-unit normalizer and rounded-child handoff. Jose
Manuel / jmbarrancoml owns PR4198's rational producer and PR4205's rounded
generator connection. The retained program credits Vlado Vojdanovski/PR1673's
dirty-shear compiler, Chafik Boukhalfa/PR628's certified phases, Cinna Davis and
the original structured-matrix/caller lineage. Their scientific sources and
credit lines remain unchanged. New adapter, finite comparison and write-up:
AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
