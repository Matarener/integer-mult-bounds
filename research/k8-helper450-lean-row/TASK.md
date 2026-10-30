# Task: bind forward helper450's scalar row to the existing typed word

The `formal-interface-lemma` card asks for one small interface lemma with its
actual hypotheses. This investigation refines that request to a missing
concrete `hS` premise, after checking the selected result and the existing
numeric and Lean bindings. It does not construct another event translator or
repeat the already available numeric row calculation as its contribution.

The canonical scoped claim is
[Discussion2703#19007184](https://github.com/CrocSwap/integer-mult-bounds/discussions/2703#discussioncomment-19007184).
PR2944 already formalized the complete typed words and their labels; PR3331
provided the composition/row-update lemmas and released the concrete scalar
row as a follow-up. The exact task is to prove, for every `x : Fin 1024 → Rat`,

```lean
scalRun K8.Forward.events x (450 : Fin 1024) = x (450 : Fin 1024)
```

The resulting unit-row equation has exactly the orientation required for the
scalar `hS` argument of the existing helper consumers. Arbitrary initial values
include the eight private centres and unused coordinates of the original
finite type; no cold-input assumption is introduced.

## Bounded method and acceptance gate

Use the unchanged PR2944 translator and generator on the authenticated selected
forward word. Retain all 24,757 semantic events, original register identifiers,
COPY/CLEAR events, and relabels. Bind the regenerated Lean sources to the
predecessor's recorded hashes. Split the word around semantic ADD indices
13,944 and 16,501, corresponding to serialized indices 13,949 and 16,507.

Prove coordinate preservation for a block whose scalar targets avoid that
coordinate. The prefix and suffix avoid450; the middle avoids450 and230.
Their lengths are 13,944, 2,556, and 8,255. The intervening operations are
`450 += 230` and `450 -= 230`. The prefix may write230. The proof needs no
condition on scalar reads or relabel events.

Use the retained generator's 97 blocks of at most 256 events, with the active
ADDs at block54 offset120 and block64 offset117. Exact append/flatten identities
recover the complete word and its avoidance predicates; `div_one` normalizes
the original rational literals. The complete source-authenticated driver run
passed with the default stack in 591.5 seconds, checking five theorem roots
and the kernel controls. The registered Python replay and seven source-control
groups also passed; exact commands and receipts are in [VERIFY.md](VERIFY.md).

Acceptance requires a fresh Lean kernel check of both the generic cancellation
lemma and the concrete full-word roots, with a recorded axiom report. Source
replay and independent rational controls are separate evidence. Archived
predecessor kernel receipts establish provenance and generated-source equality;
they are not fresh checks of this package's theorem.

Stop after this one forward row, source binding, and meaningful failure
controls. Do not expand into the backward word, all helper rows, physical
recipes, column isolation, or a full selected replay. The nominal session
budget is 60 minutes. Current verification details are in [VERIFY.md](VERIFY.md);
the machine-readable task and source records are [TASK.json](TASK.json) and
[SOURCES.json](SOURCES.json).

## Why it matters and what remains

This removes one explicit finite scalar premise from a formal helper consumer.
It is useful even though it does not change κ: a numerical identity for a
selected stream and a generic conditional Lean lemma are different artifacts,
and this result connects them at the already retained typed word.

The source adapter remains outside Lean. The theorem proves an output row and
does not isolate its input column. Physical recipes, labels, bank ownership,
and the remaining consumer premises must be handled separately. No whole-state
restoration or complete multiplication theorem follows from this package.

## Open next questions

| Question | Why it matters | First bounded step | Present blocker |
| --- | --- | --- | --- |
| Does the backward typed word have the same formal helper450 unit row? | Both orientations occur in the selected supplier. | Derive its exact protected blocks using the existing PR2944 generator. | The present proof binds only the forward word. |
| Is input column450 isolated from other outputs? | Row restoration permits dirt leakage to other registers. | Formalize column propagation and compare the frozen numeric column audit. | A unit-row equation is insufficient. |
| Which remaining premises admit a physical helper instantiation? | `hS` is only one argument of the conditional theorem. | Enumerate one actual consumer's label, recipe, and ownership obligations. | Those obligations are outside scalar-shadow semantics. |

Attribution and immediate predecessor heads are recorded in [README.md](README.md).
Prepared by Sagar Thakrar with substantial OpenAI Codex assistance; separate
agent checks do not constitute independent human review.
