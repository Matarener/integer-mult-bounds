# Forward helper450 unit row in Lean

This package supplies the scalar unit-row hypothesis `hS` for helper450 in the
complete retained `K8.Forward.events` word. Its strongest theorem states that,
for every initial scalar state `x : Fin 1024 → Rat`,

```lean
scalRun K8.Forward.events x (450 : Fin 1024) = x (450 : Fin 1024)
```

Consequently, for every one of the 1,024 typed columns `j`,

```lean
S K8.Forward.events (450 : Fin 1024) j = if j = 450 then 1 else 0
```

The concrete roots are `Helper450Concrete.helper450_restored`,
`helper450_unit_row`, and `helper450_hS`. The last has the premise orientation
used by `Stream.row_unit` and the hyperplane-ended helper consumers. No initial
coordinate, including a private centre, is assumed zero.

A fresh Lean 4.21.0 kernel run passed in 591.5 seconds; its exact root-axiom
reports are retained in [KERNEL.json](KERNEL.json). The registered Python 3.12.15
source replay and seven control groups also passed. [VERIFY.md](VERIFY.md)
records the commands and distinguishes this fresh evidence from the archived
predecessor receipt. This scoped formal-interface contribution does not change
the selected frontier or claim a new multiplication bound.

## Exact word and proof

[source.py](source.py) authenticates the selected replay archive and reuses
Nick Petalas's unchanged PR2944 translator and Lean generator. It compares the
complete translation, source-index map, and all 14 generated forward source
files with the retained PR2944 receipts. The original `Fin 1024` register
type and register numbering are preserved.

The 24,767 serialized events become 24,757 semantic events after omitting the
ten phase markers. The typed word retains 18,962 ADDs, 707 SCALEs, eight COPYs,
16 CLEARs, and 5,064 relabels. Local coordinates occupy 0–703; the eight private
centres occupy 704–711. The theorem also quantifies over all other coordinates
of the original finite type. Phase markers are metadata in this scalar-shadow
translation; relabels remain in the word and act as scalar identities.

Exactly two scalar operations write helper450. All indices below are
zero-based, and block intervals are half-open.

| Part | Semantic indices | Length | Scalar targets excluded |
| --- | --- | ---: | --- |
| Prefix | `[0, 13944)` | 13,944 | 450 |
| First ADD | `13944` | 1 | `450 += 230` |
| Middle | `[13945, 16501)` | 2,556 | 450 and 230 |
| Second ADD | `16501` | 1 | `450 -= 230` |
| Suffix | `[16502, 24757)` | 8,255 | 450 |

The two ADDs correspond to serialized indices 13,949 and 16,507. The prefix
may change coordinate230: only its value between the two ADDs must be fixed.
The generic proof checks target preservation for ADD, SCALE, COPY, and CLEAR;
relabels preserve every scalar coordinate. It then cancels the two ADDs over
an arbitrary ring and module. The concrete proof uses the original 97 generated
blocks, each containing at most 256 events. Small append/flatten identities
preserve the complete word and its four avoidance predicates. The active ADDs
are in block54 at offset120 and block64 at offset117; `div_one` normalizes the
original rational literals `(±1)/1`. The full kernel run succeeds with the
default stack. Cinna Davis's PR3331 supplies `scalRun_append`.

## Scope boundary

This establishes an **output row**, not isolation of input column450. Other
outputs may depend on its initial value even when output450 is restored. A
positive kernel control deliberately exhibits that distinction. It also does
not establish physical recipe correctness, bank ownership, label semantics,
the backward helper row, every helper row, full selected cold replay, or a
complete supplier theorem. Those consumers retain their other hypotheses.

The Python/JSON-to-Lean adapter is outside the kernel. Exact byte pins and
byte-identical regeneration bind the stated theorem to the existing typed
word; they do not formalize a general serializer-correctness theorem. The
read-only Mathlib cache is a further explicit reproduction dependency.

## Reproduce

From the repository root, the registered Python 3.12 checks require only the
standard library:

```sh
python3 scripts/research_package.py --package research/k8-helper450-lean-row --check-only
python3.12 scripts/research_package.py --package research/k8-helper450-lean-row
```

These authenticate the source closure, regenerate the retained Lean source,
check the exact schedule and archived receipts, and run seven independent
source/arithmetic control groups. They do **not** invoke Lean. For a fresh
kernel run using an existing matching dependency cache:

```sh
python3.12 -I -O -Werror -B research/k8-helper450-lean-row/check_lean.py \
  --lake-project /path/to/matching/lean/project
```

The driver checks Lean 4.21.0 and the pinned Mathlib/dependency revisions,
compiles into private temporary storage, and removes that storage on exit.
It does not update or build the supplied Lake project. See [VERIFY.md](VERIFY.md)
for the cache contract, receipt comparison, controls, and verification status.

## Sources and credit

[SOURCES.json](SOURCES.json) records exact Git objects and SHA256 pins at base
`6f100d4bb5083f8c35d96fd95a539811c62f245c`.
The immediate predecessors are:

- Hanson Sun (@bbMisk), [PR1611](https://github.com/CrocSwap/integer-mult-bounds/pull/1611),
  head `156cc788b5a8122b19686f015e5654b117e4389d`: numeric helper450 binding,
  complete source-word hashes, and regeneration lineage.
- Nick Petalas, [PR2944](https://github.com/CrocSwap/integer-mult-bounds/pull/2944),
  head `2c97782a83da48230f1cffca73c5a7ad58ada31e`: the existing complete typed
  words, exact translator/generator, label proofs, and kernel-driver pattern.
- Cinna Davis (@1337isnot1337),
  [PR3331](https://github.com/CrocSwap/integer-mult-bounds/pull/3331),
  head `499c02bcd6febeada7f3f9db21ed4431c901d9b5`: scalar composition and
  one-event row-update lemmas.

The scalar semantics and conditional row consumer are DreamingOfClouds's
Lemma G work. Jeremy Kothe's HPE/k8 lineage, icekylinx's compiler, Rohan Arun's
packing, and the retained word and realization contributors keep their
existing attribution. Earlier numerical row/column checks, including PR1710
and PR1843, are not new claims here.

New work: Sagar Thakrar, with substantial OpenAI Codex assistance in proof
development, implementation, independent agent checks, and writing. Separate
agent review is not independent human review. New work is Apache-2.0;
predecessor notices are unchanged.

## Open next questions

The canonical investigation is
[Discussion2703, claim19007184](https://github.com/CrocSwap/integer-mult-bounds/discussions/2703#discussioncomment-19007184).
[TASK.md](TASK.md) and [TASK.json](TASK.json) record the task and its bounded
scope. Concrete next questions are:

- **Backward helper450 row:** derive a block decomposition of the retained
  `K8.Backward.events` word and prove its unit row. Start from the existing
  PR2944 backward generator; the forward decomposition alone does not supply it.
- **Column isolation:** prove that other output coordinates do not depend on
  initial helper450. Start with a formal forward column propagation lemma and
  compare the existing numeric audit. A unit-row theorem cannot discharge this.
- **Physical consumer:** instantiate the helper theorem with the remaining
  label, exact-recipe, and ownership hypotheses. Start with one actual consumer
  and list each premise separately; the scalar theorem supplies only `hS`.
