# The last16/32 buffers cannot merge by neutral whole-bin transport

Proved for exact [PR3388](https://github.com/CrocSwap/integer-mult-bounds/pull/3388)
`684d347c0e6e578b8ab600d2e680ad6701cf7fa0`: at its fixed final chronology,
neutral equal-capacity whole-bin transports followed by splitting one full48
bundle cannot realize `-H16-H32+H48`. This answers a restricted version of its
explicit remaining16/32-buffer consolidation question.

The relaxed rank16-buffer closure has896 locations. Every original full48
bundle offers at most9 width eligible for any such location, below the
required 16. The proof permits arbitrarily long transport histories, repeated
visits and whole evacuation of partially occupied bins. It ignores all family
conflicts and grants the rank32 buffer unrestricted placement. A positive
result in the relaxation would require further physical validation.

[PROOF.md](PROOF.md) defines the strategy and proves the all-length implication.
[RESULT.json](RESULT.json) contains the source-bound finite receipt. This is a
scoped negative result with no new kappa or selected-frontier change.
Nonneutral or partial-bin rearrangements and chronology changes remain open.

## Reproduction and evidence

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/t16-buffer-transport-cut
```

Direct primary, independent and behavioral checks are also available:

```sh
python3.12 -I -Werror -B research/t16-buffer-transport-cut/verify.py
python3.12 -I -Werror -B research/t16-buffer-transport-cut/independent.py
python3.12 -I -Werror -B research/t16-buffer-transport-cut/test_package.py
```

The primary reconstructs all sixteen PR3388 maps and audits their exact whole
helper capacities, source windows and family identities. Its closure uses
integer bit masks. The separate checker imports no project code and rebuilds
the actual event windows with explicit sets. It agrees on all 896 locations,
four eligibility classes and the full 2,288-bundle histogram. Eight behavioral
groups include576 complete tiny systems and five actual CLI rejections.

Default verification writes no evidence. Set TMPDIR to an external owned cache
for disposable test copies. `--write` explicitly regenerates RESULT.json.
All retained inputs are authenticated; no pending Git object, network or solver
is needed. [RETAINED.json](RETAINED.json) records original source paths, Git
blobs and byte hashes for the unchanged 20-file PR3388 source package.
OWNERS.json.gz and PLAN.json are normalized reconstruction fixtures, compared
in full with that source. [SOURCES.json](SOURCES.json) pins canonical-main live
inputs and historical task provenance. [VALIDATION.md](VALIDATION.md) records
actual checks and implementation limits.

This checks the specific transport obstruction. It does not rerun PR3388's
strict physical admission or supplier/outer prices, prove packing optimality,
or discharge any inherited all-size or multiplication theorem assumptions.

## Open next questions

Can a literal nonneutral or partial-bin exchange concentrate the same buffers
at fixed chronology? Begin with one simultaneous redistribution from exact
PR3388 and require unchanged complete admission. No witness is supplied here.

Can a changed causal paired order move a full48 bundle into the rank16 window?
First recompute its actual source-event windows, then audit the literal owner
map, chart stock and complete physical invoice. Neither chronology feasibility
nor a new kappa follows from this obstruction. [TASK.json](TASK.json) gives the
success and stop tests.

## Credit and scope

Nick Petalas. Pierre (hexapode) supplied PR3388 and its retained PR3381 source
chain. Hao Yan supplied the T16 controller and independent audit; Philippe Van
Velzen supplied strict admission. PR3308/3338/3354/3359/3366/3375/3381 and their
compiler, owner, bit, geometry and moment contributors retain the source-specific
credit in the unchanged source documents. New work is Apache-2.0. Assistance is
disclosed in TASK.json. No independent human or formal review is claimed.

Canonical investigation is [the scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3355#discussioncomment-19008660).
