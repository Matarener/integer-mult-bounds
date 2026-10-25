# Selected forward recipe dispatch in Lean

This package reduces `RecipesExact` for the complete existing
`K8.Forward.events` word to **2,888 explicit child-operator identities**.
It binds all 5,064 relabel occurrences to their original recipe descriptors
and handles the tag, endpoint, identity, and residual-wrapper cases by algebra.
The child identities remain hypotheses. This is a conditional formal
refinement, with no new numerical recipe-exactness result or κ claim.

**Verification status:** the fresh Lean 4.21.0 replay passed in **793.1 seconds**
on x86_64 Linux, compiling 34 proof modules in a new temporary directory.
All 97 block checks passed, and four false claims were rejected. The 20 theorem
and control roots use only `propext`, `Classical.choice`, and `Quot.sound`;
`used_child_count` uses no axioms. The eight Python control groups also pass
under isolated, optimized CPython 3.12.15. [KERNEL.json](KERNEL.json) retains
the exact input/source hashes, dependency revisions and per-root axiom report.

## Exact conditional theorem

For any rational module `M`, `Model Rat M` independently assigns linear
equivalences to frame IDs, monomial IDs, and core ranks. For every used child
record `c : old → new`, `ChildExact tables model` requires, for every `v`,

```text
L_c (C_rank(c) (R_c v)) = T_new (T_old⁻¹ v).
```

The concrete conclusion in [ForwardRecipeResult.lean](ForwardRecipeResult.lean)
is:

```lean
theorem forward_recipes_exact
    (model : Model Rat M) (hc : ChildExact tables model) :
    LemmaG.Stream.RecipesExact
      (tagOp tables model) (dispatch tables model) K8.Forward.events
```

Here `dispatch` executes the selected descriptor; it is not defined to be
`T_B ∘ T_A⁻¹`. The proof shows that equality for every admitted relabel.
`forward_dispatch_bound` additionally identifies the complete ordered list of
registers, labels, and selected descriptors with the generated raw-record list.
`used_child_count` states that the retained child table has 2,888 entries.
The original 97 blocks and all 24,757 semantic events from PR2944 are retained.

Composition below applies the rightmost operator first. The tag interpretation
and executed descriptor agree with PR1964's extended-label convention:

| Transition | Extended-label operator | Executed descriptor |
| --- | --- | --- |
| Source entry, `pre → plain` | `T_pre = M_i⁻¹ ∘ T_F` | `M_i` |
| Target exit, `plain → post` | `T_post = N_t⁻¹ ∘ T_F` | `N_t⁻¹` |
| Helper entrance, `prew → plain` | `T_prew = R_EU ∘ T_E` | `R_EU⁻¹` |
| Helper exit, `plain → done` | `T_done = L_EU⁻¹ ∘ T_U` | `L_EU⁻¹` |
| Same plain label | `T_F` on both sides | Identity |
| Different plain frames | `T_old`, `T_new` | `L_c ∘ C_rank(c) ∘ R_c` |

Only the last case needs `ChildExact`. The matrix/control witnesses make
inverse direction and noncommuting composition order explicit.

## Source binding and finite coverage

[source.py](source.py) authenticates the selected replay archive, reuses
PR2944's unchanged translator, and independently reads recipe choices from the
literal raw opcodes. Its Nat-label dispatcher must agree with that raw reader
at every occurrence. The original source indices, exact rational word, and
all 14 retained forward Lean source hashes are checked. The generated Lean
checks bind each complete block to these source-derived descriptors.

| Descriptor | Forward occurrences |
| --- | ---: |
| Child transport | 3,494 |
| Source entry | 112 |
| Target exit | 112 |
| Residual pre-wrapper | 240 |
| Residual post-wrapper | 240 |
| Identity adapter | 866 |
| **Total** | **5,064** |

The 3,494 child transports comprise 3,486 climbs and eight centre operations.
They use 2,888 distinct directed records from the original 2,896-record table.
The eight unused records are `0 → 415` through `0 → 422`, each rank eight;
the forward centres use the reverse directions. They are not identity records.
The Python artifact retains all original record metadata and the 3,474
deduplicated monomial literals; the generated Lean child table contains only
the used records. Exact token IDs and raw record bytes are source-bound, while
their operator denotations remain parameters of `Model`.

The Nat codec has frame radix **1,004** and owner/tag stride **712**, inherited
unchanged from PR2944. The register type remains `Fin 1024`; 1,024 is not the
codec stride. Private centres are registers 704–711. For helper450, the
literal wrapper key is **`2:999`**, with its right operator at entrance and
left operator at exit. The existing FULL-terminal key `2` is a different
recipe. Independent address witnesses distinguish them at right input 0
(`511` versus `241`) and left input 2 (`12` versus `18`).

[test_dispatch.py](test_dispatch.py) independently rereads the raw archive and
checks all descriptor literals. Its eight control groups cover the 712/1024
confusion, omitted centre/identity events, duplicate events, reversed
transitions, wrong wrapper keys, child rank and left/right token changes,
source-byte corruption, and noncommuting matrix witnesses. Those small matrix
examples specify the required algebra; separate Lean controls exercise the
production definitions.

## Reproduce

The Python source controls are independently runnable with the standard library:

```sh
python3.12 -I -O -Werror -B research/k8-lean-recipe-dispatch/test_dispatch.py
```

The registered replay authenticates and regenerates the source artifacts,
checks the retained kernel receipt, and runs the controls. It does not invoke
Lean; receipt validation is cheaper than a fresh proof check:

```sh
python3 scripts/research_package.py --package research/k8-lean-recipe-dispatch --check-only
python3.12 scripts/research_package.py --package research/k8-lean-recipe-dispatch
```

For an independent fresh kernel run, use an existing cache matching the pinned
Lean 4.21.0 toolchain and Lake manifest, and a new receipt path:

```sh
python3.12 -I -O -Werror -B research/k8-lean-recipe-dispatch/check_lean.py \
  --lake-project /path/to/matching/lean/project \
  --write-receipt /path/to/new-kernel-receipt.json
```

The driver checks the dependency revisions, reads that cache without changing
it, and compiles generated and local proof sources into a private temporary
directory that is deleted on exit. Omitting `--write-receipt` performs a fresh
run and compares it with the retained receipt. Compiler binaries and cached
dependency proof objects remain trusted environment inputs; they are not
rebuilt here. Exact commands and input declarations are in [VERIFY.json](VERIFY.json).

The publication run used the command above with the read-only dependency cache
at `/root/projects/integer-mult-bound-ci-performance/formal/lean`,
`--work-dir .scratch/iteration-13`, and the package's new `KERNEL.json` as
the receipt destination. No dependency build ran in that shared checkout.

## Remaining boundaries

This does not discharge the 2,888 child identities in Lean. PR1781 already
checked every child record numerically with global phase, and PR2048 already
rechecked the 2,888 used records and endpoint adapters. Their numerical work is
not new evidence claimed by this package.

The model's frame, monomial, and core maps are independent parameters. The
proof does not identify them with serialized Clifford operators, the native
executor, or a complete physical program. It also leaves the Python/JSON-to-Lean
adapter, common-chart interpretation, ownership, precision, full selected cold
replay, and the complete supplier theorem explicit. The forward scope does
not automatically include the backward word. No selected frontier changes.

## Credit and coordination

The canonical investigation is
[Discussion2703#19007895](https://github.com/CrocSwap/integer-mult-bounds/discussions/2703#discussioncomment-19007895).
[TASK.json](TASK.json) records the refined `formal-interface-lemma` task.
[SOURCES.json](SOURCES.json) pins consumed bytes at base
`6f100d4bb5083f8c35d96fd95a539811c62f245c`. Relevant predecessor heads are:

- Sagar Thakrar, [PR1781](https://github.com/CrocSwap/integer-mult-bounds/pull/1781),
  `dafbaadeb423b3bc80fbf6fcd6f415400dc0ffbf`: independent numerical child and endpoint recipe checks.
- Sagar Thakrar, [PR1964](https://github.com/CrocSwap/integer-mult-bounds/pull/1964),
  `6f34af34efa178cc2dbe0612c094a1bda591d332`: extended labels and the written dispatcher interpretation.
- commdata2338, [PR2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048),
  `a0e55f357344f1742f72942f94ae2a6f13ff7065`: native centre lift and recheck of all used child recipes.
- AAAmirinu, [PR2378](https://github.com/CrocSwap/integer-mult-bounds/pull/2378),
  `5816f94741709e8082e06a2cc9a114ff87411f3d`, and Gareth Davidson,
  [PR2422](https://github.com/CrocSwap/integer-mult-bounds/pull/2422),
  `0df268def5a3ce9e7e077ed8166eec545c3b8c25`: complementary formal refinements
  for residual `0:1000.right`, with completed physical primitives explicit.
- Nick Petalas, [PR2944](https://github.com/CrocSwap/integer-mult-bounds/pull/2944),
  `2c97782a83da48230f1cffca73c5a7ad58ada31e`: the complete typed words, codec,
  source generator, and concrete label proofs reused here.

Hanson Sun's PR1611 supplies the selected numeric binding. DreamingOfClouds
supplies the Lemma G semantics and generic conjugation theorem; Jeremy Kothe,
icekylinx, Rohan Arun, and the retained construction and realization contributors
keep their existing attribution. PR3357's forward scalar unit row is a separate
result. New work is by Sagar Thakrar with substantial OpenAI Codex assistance in
implementation, formalization, independent agent review, and writing. No
independent human review is claimed. Apache-2.0; predecessor notices are unchanged.

## Open next questions

- **Discharge the used child identities in Lean.** Bind one retained record's
  left/core/right operators to an exact Clifford denotation, including global
  phase, then prove its identity. A formal serialized evaluator is still needed.
- **Connect the physical executor to this dispatcher.** Start with one actual
  completed invocation and its ownership/restoration contract. The model and
  source selection alone do not prove physical execution or common-chart semantics.
- **Bind the backward dispatcher separately.** Derive its exact raw occurrence
  and used-record inventory before reusing the generic proof; the forward
  2,888-record table must not be assumed to cover that orientation.
