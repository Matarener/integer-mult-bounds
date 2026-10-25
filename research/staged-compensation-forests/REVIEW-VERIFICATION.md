# Independent forest, source and acceptance review

**Verdict: PASS within the declared finite compensation model.**
This review independently derives the target-forest prices and verifies the
literal two-sided basis word, then audits the package's execution and receipt
bindings. It is separate AI review, not human acceptance or a formal-kernel
proof. Substantial OpenAI Codex assistance was used.

## Exact mathematical domain

The two inputs are pinned PR3605 words at
`3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. Their compensation matrices agree:
112 targets, 207 active helper columns and 5,736 nonzero entries. Each complete
word has 632 arbitrary live logical inputs. The independent panel interpreter
gives every live register its own input column, including arbitrary targets,
all active dirty helpers and all untouched spectators.

The required panel is `(y,h) -> (y+C h,h)`. The source's ZERO and FULL frames
are frame conditions, not assertions that a helper's entering data are zero.
The pinned transport's default `start` and `final` expressions were inspected
and matched as AST expressions without executing that producer. All 207
active helpers are present, absent from `removed`, and absent from both
override dictionaries `start_extra` and `helper_final`. They therefore have
the required ZERO entrance and FULL terminal conditions under that producer.

The independent checker uses sparse `Fraction` rows, without the builder's
common-eighth representation or any imported builder routines. Its tariff
counts a separately constructed binary-Horner work computation: initial
CLEAR, source accumulations, doublings, denominator halvings, signed target
ADD and final CLEAR. Its exact coefficient reconstruction is checked before
the count is used.

## Forest minimum and literal basis word

For a signed parent edge, the complete component cost is
`8 + sum_j p(C_tj - s C_pj)`; a root costs `sum_j p(C_tj)`.
The eight primitives include both unit basis directions. Sign invariance
makes each signed pair price independent of its eventual orientation.
Adding a superroot gives a cost-preserving bijection between the declared
single-parent forests and spanning trees.

The independent computation prices all 112 root edges and both signs of
all 6,216 target pairs: **12,544 edges**. It validates the selected tree,
reconstructs its rooted orientation and checks every cycle inequality.
A separate heap-based Prim traversal of the independently priced graph
returns **13,716**. The certificate has 17 roots, 95 target edges and maximum
target depth 15. This is a minimum only in the fixed signed-unit,
single-parent target-forest class with independent coefficient lowering.

The actual preparation list is checked for the prescribed parent/sign
incidences and leaf-before-parent chronology. Applying that literal list to
the source matrix independently yields `D=T C`; it equals the direct
immutable-parent formula. The restore list must be the literal reverse
inverse. This checks arbitrary target inputs as well as helper coefficients.

The checker separately recomputes all **85,284** ordered signed helper scores
from D. Exactly 951 are positive. The declared deterministic greedy rule
selects **88 disjoint pairs**, using 176 helpers and saving 3,083 component
primitives. Disjointness makes those scores additive. This verifies a
construction; it does not prove a maximum matching or a joint basis optimum.

For `h_a += s h_b`, right multiplication by `H^-1` changes column b to
`D_b-s D_a`. The actual residual injections are compared completely with
`E=T C H^-1`. The actual helper restore is `H^-1`, followed by `T^-1`.
Thus every arbitrary input returns
`T^-1(T y + T C H^-1 H h)=y+C h`, with h restored literally.

Both supplied providers pass all 632 input columns in the forward, literal
reverse-inverse and same-chronology inverse-transpose orientations. The dual
panel is `(y,h-C^T y)`: helpers change at this intermediate dual boundary.
The forward panel's restored-helper statement is not transferred to it.
Every complete candidate word is also checked to differ from its source
only in the compensation field.

The independent complete component bills are:

| Panel | Logical ADDs | Component primitives |
| --- | ---: | ---: |
| Original | 5,736 | 31,214 |
| Signed forest | 2,834 | 13,716 |
| Forest and disjoint helper basis | 2,288 | 10,633 |

The last bill includes 760 target-basis primitives, 704 helper-basis primitives
and 9,169 residual primitives. It does not omit restoration. The separate
same-matrix historical rank-basis comparator costs 17,334, as checked by the
package's literal-price and whole-word auditors.

## Defect-sensitive controls

The independent forest receipt records thirteen rejecting controls for each
provider. Actual mutations omit or change target preparation, helper
preparation, residual injections and either restore; reverse target
chronology; or violate the helper entrance/terminal conditions. Each
operator mutation has an explicit differing row and input-column coefficient.
The test requires the intended semantic error. Unexpected acceptance is
raised outside the exception handler.

Deleting only the complete endpoint requirement makes its negative control
fail, establishing sensitivity to that requirement. A positive control adds a
cancelling unit ADD pair: all three operator orientations still pass, and its
eight component primitives are charged. Omitting target preparation passes
the helper-only input projection while failing the full arbitrary-input map,
so checking only incoming helper columns would be insufficient.

Normal execution and an isolated optimized execution from a temporary script
path containing spaces produce byte-identical complete forest receipts.
`MST-VALIDATION.json` records that run. The source and candidate directories were
shared read-only; this is not described as a complete package export.

## Source execution and complete records

Three execution-layer gaps were found and corrected during review: the root
wrapper reopened authenticated script paths, its stage result could omit a
comparison without failing coverage, and the whole-word checker's nested
producer subprocesses reopened producer paths. Both execution levels now send
the captured authenticated bytes to isolated subprocesses and compile with
`dont_inherit=True, optimize=0`, preserving the declared `__file__` and
`sys.argv` values. No frozen module is loaded through importlib or a bytecode
cache. The nested historical producers' assertions remain active under an
optimized outer verifier.

The wrapper rejects duplicate JSON object keys and nonfinite constants,
unsafe paths, missing regular inputs, symlink escapes, changed frozen bytes,
origin-inventory mismatches and changed decompressed originals. Complete
canonical JSON comparison distinguishes integer, float and boolean values,
preserves list order and includes every nested field. Missing fixed records
are not regenerated.

The required stage sets contain thirteen construction/comparator records,
one independent forest record and one whole-word record. Exact set and
duplicate-count checks enforce all fifteen comparisons. Construction also
checks its complete generated-file inventory.

`CONTROLS.json` records compact normal and optimized runs against the final
wrapper and checkers: **70 intended rejections and three named-check deletion
tests per mode**, with all fifteen complete records checked. The control
driver itself also produces byte-identical receipts under outer normal and
optimized execution, recorded in `CONTROL-VALIDATION.json`.
These cover actual captured-source execution after a
disposable path change, both assertion layers, complete-record mutation and
omission, stage coverage, and a changed sign in the actual authenticated
target-basis word. Named record, coverage and endpoint checks are deliberately
deleted to verify that the corresponding controls then fail. The compact
suite replays the actual compensation panel; it does not repeat the complete
whole-word scalar audit or edge census for every mutation.

## Earlier work and remaining limits

The fixed PR1080 comparison was independently recalculated. Its prior matrix
has 216 active columns and quarter-grid coefficients; this one has 207 active
columns and 96 strict eighth-grid entries. Those invariants exclude signed
row/column permutation equivalence. Its frozen target forest costs 22,548 on
this matrix. Literal helper-ID transfer touches exactly four removed helpers,
fourteen nonzero entrances and sixteen non-FULL terminals. These are bounded
facts about that source and recipe, not a general basis-equivalence or paid
remapping obstruction.

The design proof and related-work note credit the prior target-forest,
helper-basis and broader bi-forest methods. The present contribution is a
source-specific restored circuit and its complete same-matrix comparison,
not priority for those mechanisms.

The companion whole-word audit owns the full free-operator identities,
literal emitter bindings and scalar-prefix replay. Its scalar numerical model
treats nonscalar events as identity and CLEAR as assignment. It therefore
does not by itself prove physical Clifford phases, reversible erasure,
native-child precision or recursive rounding. The panel proof also does not
establish COPY lifetimes, a new physical tape implementation, recursive
histogram improvement, a general supplier bound or a new kappa result.
Final package bytes are delimited by `CORE-SNAPSHOT.json`; committed and
Git-free package replay remain the parent's separate validation stages.
