# The native product commitment and its execution-log boundary

**Independent finite boundary audit of PR #4180; no new κ or supplier admission.**

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

This package audits the unchanged `native_outputs.authenticate_native` gate in
[PR #4180](https://github.com/CrocSwap/integer-mult-bounds/pull/4180), using the
actual retained PR #4085 `gauge44` and `extra` native product trees. The
independent normalizer reconstructs their 22 committed product digests. The
mutation sweep partitions every root field and exercises the actual gate,
including edits whose dependent raw references are all coherently rebound.
[RESULT.json](RESULT.json) is the complete deterministic case receipt.

The resulting scope distinction is precise: **scientific products are committed;
stage history is projected to five ordered names and integer-zero exit codes.**
The gate accepts a minimal stage list with all timing fields removed, and also
accepts negative or nonfinite stage timings and invented stage metadata. These
are witnesses to information outside this gate's contract, not invalid native
operators, a new admission defect, or evidence that the selected result fails.
The two product-level `seconds` fields, in contrast, must pass explicit numeric,
finiteness and nonnegativity checks before being discarded.

The current selected record at the scientific base is #5413. This audit concerns
the retained #4180 integration named by the revision-7 supplier-boundary card;
it does not replay #5413 or reinterpret #4180's historical selected-status prose.

## Exact boundary

Each provider contains eleven product objects with 117 root fields, partitioned
as 109 ordinary fields, six serialized-reference fields and two timing fields.
The oracle derives new normalized objects using an independently enumerated
reference graph. It neither imports the predecessor's normalizer nor uses its
reference table or digest function. A separately implemented structural encoder
reconstructs canonical JSON; SHA-256 and JSON scalar escaping use the Python
standard library. The unmodified audited source is then executed directly from
its authenticated bytes, bypassing bytecode caches, to check the same fixtures.

| Parent product | Reference field | Referenced product |
| --- | --- | --- |
| `CLIFFORD-REVIEW.json` | `canonical_word_sha256` | `CANONICAL-WORD.json.gz` |
| `CLIFFORD-REVIEW.json` | `recipe_sha256` | `CLIFFORD-RECIPES.json` |
| `INDEPENDENT-LOCAL-REPLAY.json` | `canonical_word_sha256` | `CANONICAL-WORD.json.gz` |
| `INDEPENDENT-LOCAL-REPLAY.json` | `local_programs_sha256` | `LOCAL-PROGRAMS.json.gz` |
| `WARP-RECIPE-CHECKS.json` | `canonical_word_sha256` | `CANONICAL-WORD.json.gz` |
| `WARP-RECIPE-CHECKS.json` | `recipe_sha256` | `CLIFFORD-RECIPES.json` |

Every target is a leaf of this reference graph: none contains a root reference
field or one of the two discarded timing fields. The oracle explicitly checks
this property, rather than assuming recursive reference normalization.

The two timed objects are `CLIFFORD-REVIEW.json` and
`SCALAR-FRAME-AUDIT.json`. Only their **root** `seconds` key is removed.
A newly added nested `seconds` field remains committed. The other nine product
objects have no timing exception.

## Source-relative normalization argument

Let `J(f)` be the Python JSON value obtained after optional gzip decompression,
`C` its canonical serialization, and `H` SHA-256. For a product `f`, define
`N(f)` by the following operations on its root object:

1. For either timed product, require the literal source predicate
   `type(t) in (int, float) and math.isfinite(t) and t >= 0`, then remove `seconds`.
2. At each of the six edges `f --k--> g`, require `J(f)[k] = H(bytes(g))`,
   then replace that value by `H(C(J(g)))`.
3. Retain every other key and its complete value, including nested data and
   any additional fields.

The audited gate compares the product-name dictionary
`{f: H(C(N(f)))}` with its fixed provider commitment. It separately checks the
word commitment, ordered stage-name/exit-code projection, regular local files,
and the complete regular-file inventory. It does not regenerate the expected
product dictionary from the submitted cache.

For the pinned graph, the three target objects are themselves committed without
normalization. Consequently, a simultaneous serialization change and correct
rebinding of all six raw references leaves every `N(f)` unchanged. The same is
true of valid changes to the two discarded timing values. Conversely, every
other product field survives literally into some `N(f)`. Changing a target's
parsed content and updating all references cannot erase that change: the
target's own committed object changes, as do any affected normalized references.
Product names remain part of the dictionary. Missing, added or renamed products
cannot be hidden by changing their internal references.

This is a structural argument about normalized values, not a proof of SHA-256
collision resistance. Inferring identity from equal digests retains the ordinary
cryptographic integrity assumption and the fixed commitment file as a trust
anchor. Python parsing is the boundary: JSON key ordering, whitespace and gzip
transport are irrelevant; this package does not claim a duplicate-key rejection
policy or enumerate all possible JSON parser inputs. All retained scientific
numeric leaves are integers; floating-point root timing values are discarded.

`STEPS.json` has a different rule. Only the ordered list of `step` values and
strict integer-zero `exit_code` values is inspected. Its other fields never
enter the scientific product dictionary. Thus this gate alone certifies neither
elapsed time, executor identity nor the occurrence of an execution. In the real
caller, [`replay.py`](../mixed-provider-admission/replay.py) checks additional
source/result bindings and assigns execution labels from its own control flow.
That caller has not been replaced or fully replayed here.

## Bounded evidence and reproduction

The coverage is one deterministic leaf edit inside **each** ordinary root field,
not an exhaustive search over every nested leaf or every malformed file. Edits
retain the leaf's type when possible; empty containers receive an inserted
member, and null is replaced by false. Dependent raw references are rebound so
these cases cannot be dismissed as stale-reference failures. All 218 edits reject
at `native scientific output commitment`, rather than at a stale-reference or
parsing check; the exact reason is part of the fixed receipt.

Across the two actual product trees the receipt records:

| Case family | Accepted | Rejected |
| --- | ---: | ---: |
| All 109 ordinary root fields per provider | 0 | 218 |
| Six stale references per provider | 0 | 12 |
| Re-serialization with correctly rebound references | 12 | 0 |
| Added fields and missing products | 0 | 44 |
| Valid product timing changes | 12 | 0 |
| Invalid/missing timing and nested `seconds` additions | 0 | 32 |
| Each stage omitted, renamed or given nonzero/non-integer exit; reorder/duplicate | 0 | 54 |
| Uncommitted stage metadata | 8 | 0 |
| Extra files or same-byte product symlink | 0 | 6 |
| Combined JSON/gzip/timing change | 2 | 0 |
| Cross-provider products and wrong word commitment | 0 | 8 |
| **Total** | **34** | **374** |

The independent oracle and unchanged gate agree on every ordinary fixture.
The cross-provider and word-binding controls separately challenge the gate's
provider lookup. Both THREE trees reject against each of the other three fixed
provider commitments, including the two FOUR entries. That is not a replay of
the actual FOUR output trees.

From the repository root, standard-library CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/mixed-native-normalization-audit --check-only
python3 -B scripts/research_package.py --package research/mixed-native-normalization-audit
```

The registered command uses isolated, optimized Python. Its direct equivalent is:

```sh
python3 -I -O -B research/mixed-native-normalization-audit/verify.py
```

Expected final line:

```text
PASS_MIXED_NATIVE_NORMALIZATION_AUDIT providers=2 products=22 cases=408 accepted=34 rejected=374 no_new_kappa
```

Normal receipt generation and the optimized registered replay both passed on
CPython 3.12.3 / Linux, as did package metadata and source-pin validation.

The direct verifier checks every live source digest and compares the entire case
receipt. Its inputs are read-only; mutations use a temporary directory. Optional
`--write-result PATH` writes a candidate receipt for review; it is not the normal
verification command. The normal replay never rewrites `RESULT.json`.

## Scope, existing coverage and remaining obligations

The claim is in [discussion #5511](https://github.com/CrocSwap/integer-mult-bounds/discussions/5511).
The source base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
[SOURCES.json](SOURCES.json) pins 34 live inputs and the historical catalogue and
selected record. [TASK.json](TASK.json) records the refined card, exact predecessor
heads and next questions. The package changes no shared or predecessor code.

PR #4180 already exercised phase corruption, omitted phase execution, a false
private-erasure claim, and equivalent serialization/timing. Its full author
replay and owner ledger are not new results here. James Reed's independent
[#1166 owner-ledger review](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19074124)
and [source/binding review](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19082260)
are also predecessors. This package adds the complete root-field partition,
independent normalizer/graph reconstruction, systematic real-gate coverage and
explicit stage-metadata boundary. This account's #2040 concerned PR #1824's
different payload comparator, not this native gate.

Not checked here: actual FOUR native products, new native operator execution,
source/compiler correctness, word endpoints, owner rows, full ordinary/outer
admission, selected #5413 replay, Windows behavior, formal-kernel proof or any
all-size generation, precision, tape, ownership or analytic assumption. A
commitment match preserves retained evidence; it does not create new evidence
that its mathematics is true. No independent human review is claimed.

## Open next questions

1. Apply the same independently reconstructed graph and case families to both
   **actual FOUR output trees** from an authenticated #4180 replay/export. This
   closes the remaining provider coverage without rerunning the unchanged
   ordinary/outer engine. The actual FOUR directories are not present among this
   package's live inputs; obtaining them requires a separate source-bound replay
   or authenticated export.
2. If a downstream claim needs execution history, trace that precise claim
   through `replay.bind_cache` and its caller before adding another seal. The
   current gate intentionally binds scientific products and a completion
   projection. No stronger history contract is assumed by this audit.

## Credit

PR #4180, **yssite**, supplied the audited integration, product commitments,
normalization implementation and original adversarial controls (retained head
`15a4153e734a8d1d485c6d3bea9b1a8201328a4c`). **zxv**, PR #4085
(`c5854c77620723aae6914c32122870519a6f820d`), supplied the retained THREE products
and repaired operator release. **Cinna Davis**, PR #4088
(`72d7efc181edb21806a878f174847c96dd410ab0`), supplied the mixed construction;
**unpaidmoon**, PR #4165 (`430072ee4130b58c1dd952cb37fd81759675a118`), identified
the mixed-idle rebind obligation. Credit **Rohan Arun** (#4076), **David Ganz
(Dugongue)** (#3945), **Tekalign** and the retained native/Clifford/geometry lineage; the
original notices remain in their packages. **James Reed / rcfc-jreed** supplied
the distinct independent bounded reviews linked above.

The new normalizer, coverage argument, harness and writing were prepared with
substantial OpenAI Codex assistance. Apache-2.0. Separate code does not imply
independent human or formal review.
