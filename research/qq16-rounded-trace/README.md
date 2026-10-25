# QQ16 rounded trace transfer across streaming storage reuse

PR4015 changes where the future query lives and interleaves its scalar work with
native calls. It preserves all **3,392 value-producing operation dependencies**
of PR3985, their occurrence counts, all224 final output roots, the inverse-B1
checkpoint, and the ordered224 native input/recipe sequence.

Under explicitly identical deterministic finite primitives, formats and isolated
workspace, the two words therefore produce identical bits. A valid materialized
decoder range/error certificate transfers without a new rescheduling error term.
This is a relative result: PR3985 has no supplied numerical certificate, and
PR3303/3652's exact producer grid does not bound this decoder's interiors.
No new decoder precision constant, physical tariff, supplier or kappa is claimed.

The new interpreter reads only authenticated source data/text, imports no
predecessor code and performs no arithmetic simplification. It compares exact
structural tuples, verifies access/initialization/zero-return discipline and
retains the full event bijection in RESULT.json. PROOF.md states the quantified
finite-primitive theorem and the first missing actual format premise.

Two source-site fixtures separate the premise from a universal assertion:
old privateF0 at events2140/2141 and new hostedZ1 at1716/1764 diverge if width4
becomes width3 on query values3,1; the actual-1/4 response at old2563/new2537
separates signed floor from truncation. These are boundary fixtures, not claimed
reachable full-producer inputs. A wrong source order and eight other semantic
mutations are rejected. All tested uniform-format arithmetic decisions are
checked against exact rational/two's-complement conventions.

Reproduce from the repository root, standard-library Python3.12:

```
python3 -I -O -Werror -B research/qq16-rounded-trace/verify.py
python3 -I -O -Werror -B research/qq16-rounded-trace/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-rounded-trace
```

Default replay is read-only; --write exclusively creates an absent RESULT.
Runtime inputs are the two canonical scope sources in SOURCES/VERIFY and three
narrow retained data/text sources in PREDECESSORS. Pending Git history or
network fetches are not required. The actual native/cover semantics and original
frame proofs are inherited; this package does not reexecute producer payloads.

## Open next questions

Pin an actual decoder scalar/native/store implementation and prove the shared
DAG's range/error certificate once. The first missing assignment is matching
private F accumulators to persistent Q/output-bank widths, rounding and storage
semantics. Then bind disjoint native workspace and actual caller output ownership,
movement and numerical entry format. TASK.json gives the first step and blockers.
Global chronology and physical tape work are not preserved by this theorem.

Credit Chris R/Clear1nsight PR3985/4015, ywz65 PR2707, Arham Tahir PR2681,
Ali Romman and retained QQ16/native/geometry lineage; Nick Petalas PR3303/2965;
ToikY PR3652. Original retained proof notice is unchanged. Substantial OpenAI
Codex assistance, no human or proof-kernel acceptance claimed. Apache-2.0.
