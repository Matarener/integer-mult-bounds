# Independent P104 caller audit with explicit owned lifetimes

The selected PR5599 independent caller adapter assumes every public label is
productive, eight owned lifetimes, and one reusable scratch field. Newer P104
constructions use retired public labels and overlapping owned lifetimes. This
package supplies the missing inventory and scheduling adapter and checks it on
[PR5713](https://github.com/CrocSwap/integer-mult-bounds/pull/5713), head
`a5348f7143f95fe0046b92b96172e30763c7d731`.

The source's recursive invoice is unchanged. **This is a scoped independent
forward-caller audit: no new construction, kappa gain, selected-frontier update or
complete supplier admission.** The old adapter's inventory restriction is an
evidence gap for the newer interface, not a demonstrated flaw in the source's
primary verifier.

## Checked result

| Obligation | Exact coverage |
|---|---|
| Unchanged original positive control | Complete PR5550 scientific output reproduced byte-for-byte |
| Physical caller | 7,488 contacts; all eighteen forward LOCALs; exact 32-bank free-Laurent endpoint |
| Native target binding | 535 helper normalizers and 208 intrinsic main adapters; 302 distinct signed-Pauli/independent-phase comparisons |
| Productive inventory | 743 independent local inputs; 9,630 fresh caller helpers; 12,958 total productive fields |
| Owned storage | Nine local owned labels, eleven lifetimes, peak two; explicit global interval schedule including thin queries |
| Complete invoice | 66,348 paid jobs and 12,958 targets, equal to the pinned source |
| Ordinary allowance | 124,284,844 abstract address/phase/scalar passes < retained 184,647,552 allowance |
| Fault rejection | All ten original controls plus six inventory/lifetime/scratch controls |

The actual source is compact. A separate exact role-permutation fixture swaps
helper 573 with owned 743 to create a retired public hole while preserving every
chart, coefficient, input count and lifetime. It verifies that the hole gets no
productive ID, the relocated helper does, and all 1,758 local/query owned
intervals remain nonoverlapping on their assigned scratch fields. This tests
the general adapter without importing another construction or changing the
candidate's scientific result.

The exact candidate output is stored as `expected/candidate.json.gz`; replay
compares its **complete decompressed bytes**. SHA256:
`9fe876e5e74e878e691b0f9277ebbc39ce4610262526632db489816a4dd741ac`.
Its inherited `reviewed_head` and `canonical_main` keys identify the original
PR5550 checker capsule. The current candidate is separately and explicitly
bound by `candidate_input.declared_source_head` to PR5713; those legacy keys
are not its source revision.
The original positive-control output remains the canonical PR5550 artifact,
with SHA256
`b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009`.

## What changed in the checker

[The explicit adapter patch](source/selected-adapter.patch) retains the selected
checker's route, Laurent, signed-phase, native-normalizer and original fault
equations. [The interface checker](code/interface.py) replaces numeric inventory
assumptions with a disjoint independent/owned partition, literal INIT/CLEAR
intervals and actual lifetime recount. It records two scratch fields above the
productive inventory and proves query reuse is sequential by expanding their
addresses as `(physical event, port, local instruction)`.

The new controls modify real inventories or schedules: promote an owned label
to an independent input, remove an independent field, stale the source's
lifetime receipt, INIT a reused label before its prior CLEAR, alias simultaneous
local lifetimes, and place a thin query inside a live local interval. Each fails.
See [PROOF.md](PROOF.md) for the exact boundary and accounting argument.

## Prerequisites and limits

The primary PR5713 verifier is a separate prerequisite. A fresh parent-side
replay passed its complete 752-column scalar/transpose obligations, 2,917 native
maps/phases, primary physical caller and complete pricing; the short output is
retained in `evidence/primary-prerequisite.log`. This package does not rerun that
primary science or turn its log into an independent proof. Its own native checks
cover helper/main normalizers, not every paid native map.

The five selected framework assumptions remain: native all-width semantics,
owned erasure, compiler closure, precision/tape realization and analytic
recovery. COPY is an ADD into an ideally initialized owned zero, with numerical
residuals retained; overwrite of noisy state is not justified. The result keeps
`paid_native_maps_replayed: false` and `machine_and_precision_admitted: false`.
The ordinary count is a finite descriptor-pass allowance under the retained
tape contract, not a new machine-runtime, precision or storage theorem.

## Reproduction and source custody

Python 3.12, standard library, no network. From an integrated checkout:

```sh
python3 -B scripts/research_package.py --package research/p104-caller-owned-interface --check-only
python3 -B scripts/research_package.py --package research/p104-caller-owned-interface
python3 -B scripts/check_research_commit.py --package research/p104-caller-owned-interface --check-source-history
```

Expected marker: `PASS_P104_EXPLICIT_OWNED_CALLER_AUDIT`.
Each registered normal/optimized command runs the original and candidate
serially, with separate 120-second and sampled 512-MiB child caps. Normal and
optimized equality is reproducibility, not two independent implementations.
The untouched original positive control passed in 25.625 seconds. The current
candidate passed in 26.313 seconds with a sampled RSS peak of 76,578,816 bytes;
portable registered replay and publication checks are reported separately.
The earlier PR5684 compact receipt and binding are retained in `evidence/` as
historical evidence; they are not substituted for the PR5713 replay.

Main provenance is `df0137efd35e11b4445734bf612bdd4c7ebc330c`. Canonical PR5550
capsule inputs and the selected PR5599 adapter are declared live inputs in
`SOURCES.json` and `VERIFY.json`; their bytes are authenticated before imports.
The original capsule is reused in place. Only the current pending word, result,
notice, exact adaptation and new evidence are packaged here. Pending PR5713
bytes have explicit hashes in `source/EXPORT.json`; their archival custody does
not claim that its head is in main's ancestry. Fresh child bytecode namespaces
prevent stale caches from replacing authenticated source.

## Scope and overlap

This is an explicit user-authorized independent verification checkpoint. It
changes the historical `supplier-boundary-audit` card's subject from PR4088 to
the current P104 caller, retaining the card's gate: pin one exact obligation and
preserve rejection predicates. It does not claim the original complete
ordinary/outer admission task is finished. The parent coordinates current PR
and discussion overlap and any publication; unknown unpublished coverage is
not evidence of novelty.

## Open next questions

- Rebind this adapter to a successor only after pinning its primary all-input
  and native evidence and comparing its actual controller and helper ABI.
- Independently map the full pending supplier to all selected compiler,
  precision, storage and analytic premises before any frontier admission.

Concrete first steps and blockers are recorded in `TASK.json`. No broader
search or recurring run is started by this package.

## Credit

Chris R/Clear1nsight's PR5550 supplies the independent caller, spectral,
Laurent and native-normalizer checker. The maintainer PR5599 review supplies
the selected inventory adapter and admission analysis. Ali Romman supplies
PR5713 with OpenAI Codex assistance, building on Joel Pulikkan/GamingPuzzled's
PR5684 with Claude assistance and Ali Romman's PR5678. The predecessor
attribution is retained verbatim in
`source/NOTICE-PR5713`. This includes the work of flyingviper, Scratch-net,
Pierre-Loic Doulcet, Joel Pulikkan, DreamingOfClouds, thu-nmrc, Gareth Davidson,
David Arias, Cinna Davis, Jacob Alan Sussman, zxv and Cao Yifan.

New explicit ownership adaptation, independent replay and package prepared for
flyingviper with substantial OpenAI Codex assistance. Agent checks are not
independent human or formal mathematical acceptance. Apache-2.0.
