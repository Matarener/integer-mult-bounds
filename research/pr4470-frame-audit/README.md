# Independent chronological frame and invoice audit of PR4470

**Scoped independent check; no new kappa.** Both native orientations of
[PR4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470) at
`b9a13c1673e0e9697de410de16e8bbf3207a7363` reproduce the claimed local paid
and productive-helper profiles. The check reconstructs the chronological frame
requirements from pinned inputs, then compares them with the original
constructor's emitted word. It does not call the original proof engines.

This takes the local native-word part of
[#4478's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19111584).
The canonical investigation is [Discussion #4500](https://github.com/CrocSwap/integer-mult-bounds/discussions/4500).
The `independent-moment` card is refined to this actual changed ledger; see
[TASK.json](TASK.json). Canonical main is
`2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7. The selected
record remains conditional kappa `23/10000`.

## Result and exact coverage

All 499 patch locations bind to their predecessor: 38 helper entrances,
47 helper exits, and 414 scalar contacts (A: 21, B: 238, cleanup tail: 155).
The 224 main boundaries remain fixed. All 408 helper fields have a strictly
nested positive endpoint. In **each** orientation:

| Checked quantity | PR4447 predecessor | PR4470 |
|---|---:|---:|
| Persistent frame transports | 3,355 | 3,302 |
| Owned center jobs, all rank 8 | 8 | 8 |
| Total paid jobs | 3,363 | 3,310 |
| Paid rank mass | 5,290 | 5,327 |
| Productive-helper rank mass | 3,434 | 3,471 |
| Scalar events | 17,453 | 17,453 |
| Warp events | 240 | 240 |

The independently reconstructed new profiles are:

```text
helpers = {4:28, 7:7, 8:47, 9:326}
paid    = {1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}
```

Thus the change removes 53 paid jobs per local call while increasing **both**
rank masses by 37. These are local bills, not a runtime comparison between the
different p16 and p17 controllers. Every actual transport is checked at its
chronological position, including its source state, subspace inclusion and
rank; an aggregate rank histogram alone cannot pass. All scalar coefficients,
warp labels, main adapters and owned operations match the pinned source word.
All eight rank-eight center operations remain paid, and the owned field ends
with an explicit clear. [RESULT.json](RESULT.json) records both full receipts.

## Method and implication

`verify.py` independently applies the PR4441 boundary/contact edits, PR4447's
B/480 patch and PR4470's patch. Binary row elimination supplies subspace equality,
containment and rank. It deliberately assigns different frame IDs from the
constructor; comparisons use reduced subspaces. The expected demand path is
built separately for each persistent field from scalar operands, warp
entrances/exits and final boundaries. Its charged transitions must match the
entire emitted stream, position by position.

`emit_source.py` runs only the pinned `native_joint.construct()` in a temporary
source tree. Its output is the **object under test**, not a verification oracle.
No source `span`, `synthesize`, literal interpreter, rank checker or proof result
is called by the independent checking code. The source constructor necessarily
uses its own helpers to generate the candidate. The old word is checked through
the same independent path as a positive calibration case.

The limited frame-coordinate implication is as follows. Assign one fixed
invertible operator `C_F` to each frame subspace F. A checked transition
F -> G implements `C_G C_F^-1`; a scalar operation whose operands all have
frame F commutes with this common coordinate change. The unchanged native warp
at its unchanged entrance/exit has its inherited logical action. Induction
through the checked event word therefore preserves the predecessor's logical
word, with the new helper endpoints. This implication assumes the proposed
physical transitions and normalizers actually implement those operators.
The executable check establishes the frame and event premises, not that
physical-operator assumption or the predecessor's complete identity theorem.

Eleven negative controls reject nonnested rank-only transitions, dependent
bases, a false emitted rank, a changed scalar coefficient, a changed warp label,
a borrowed clear, an omitted paid climb, an omitted center job, duplicate
patch locations, main-field productive credit and a false predecessor basis.
Equivalent binary bases are an additional positive control. Failures use
explicit exceptions and remain active with optimized Python.

## Reproduce and source availability

Python 3.12, standard library only. From the repository root:

```sh
python -B scripts/research_package.py --package research/pr4470-frame-audit
```

The registered command authenticates snapshots, checks both old/new words and
all controls, then compares the complete result to the committed receipt.
The same mathematical check works without Git or network access:

```sh
python -I -O -B research/pr4470-frame-audit/verify.py
```

`--write` is an explicit authoring mode to regenerate the receipt; ordinary
verification does not rewrite evidence. [VERIFY.json](VERIFY.json) lists the
inputs. [UPSTREAM.json](UPSTREAM.json) records all nine byte-exact snapshots,
source paths, public head, Git blob IDs and SHA256 hashes. These retained files
make the pending PR available without fetching foreign commits. The source
constructor, its parent implementation and its proof retain their notices.
[SOURCES.json](SOURCES.json) separately pins the base catalogue and selected
record as historical provenance. No historical package is edited.

## Limitations and overlap

This is an independently implemented check of the source schedule and bill,
author-checked in this session. It is not maintainer acceptance or a new
physical supplier. Exact Clifford operators and absolute phases, whole-helper
normalizers, the full arbitrary-input-column identity, controller ownership,
p16 queries, precision/stock, compiler, analytic and outer obligations remain
separate. No new moment root or kappa is claimed.

PR4470 already has author checks of these objects. This contribution adds
separate elimination and per-field chronological verification against the
actual constructor. PR4478 checks arithmetic; its latest verifier also checks
uniform local gain, despite the older grid-only PR description. PR4457 checks
the predecessor native/lift layer. PR4479 and the later compiler refinements
retain PR4470's local word. These predecessors are credited rather than counted
as new work here. Live overlap and local-note coverage are recorded in TASK.json.

## Open next questions

- Independently lower PR4470's 423 changed transport/helper pairs in both
  orientations, comparing absolute phases as well as rank. This would check
  the physical premise left by the frame-coordinate argument. Start from the
  exact source head and its native receipt; an independent Clifford lowering
  and a separate resource budget are needed.
- Check the p16 controller's actual query/owner protocol using the audited
  local call. Start by adapting the PR4457 lift audit to PR4470's
  `CONTROLLER.json`, retaining every query and owner charge. This is outside
  the local-word scope; coordinate on the PR4478 handoff before starting.

The structured questions and blockers are also in TASK.json. This package
does not authorize expanding the construction family or selecting a frontier.

## Credit and license

Prepared by mihir-s-05 with substantial OpenAI Codex assistance, Apache-2.0.
The construction and native constructor are Cinna Davis / 1337isnot1337's
PR4470, extending PR4447 and PR4441. Credit zxv's native/controller work,
Jacob Alan Sussman's mixed-flow work, the retained scalar/Clifford/geometry
contributors, and Ryanson Jonathan / pinterbanget's PR4478 audit and handoff.
The retained source PROOF.md and Python notices give predecessor credit.
The package scaffold and replay infrastructure retain Douglas Colkitt's
attribution. This independent audit claims no ownership of the construction.
