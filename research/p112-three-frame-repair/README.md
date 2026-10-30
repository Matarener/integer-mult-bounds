# Three-frame repairs cannot attain fifteen P112 groups

**Sixteen even orthonormal groups are necessary and sufficient when at least
ten of PR3356's thirteen original eight-frames remain complete groups.**
A fifteen-group partition must disturb at least four original frames.
Unrestricted fifteen-group attainment remains open.

This strengthens [PR3387](https://github.com/CrocSwap/integer-mult-bounds/pull/3387),
whose proved restriction retained eleven originals and whose three-frame pilots
included unknown cases and unproved solver reports. Here all 286 triples are
exhaustively rejected by two separately implemented exact algorithms, without
budget exhaustion. [PR3370](https://github.com/CrocSwap/integer-mult-bounds/pull/3370)'s
unchanged sixteen-group witness supplies the upper bound and retains its
construction credit. [PROOF.md](PROOF.md) gives the reduction and completeness
argument.

The result closes a finite query-interface question. Under the two-support
recipe it excludes thirty queries in this retained-frame domain. It supplies
no arbitrary fitting-rank lower bound, native saving, new kappa or selected
frontier. The full-plane tariff remains 224 for these group constructions;
the general recoding obstruction in
[PR3383](https://github.com/CrocSwap/integer-mult-bounds/pull/3383) is respected.

## Reproduce

Base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
Python 3.12 or later, standard library only. From the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p112-three-frame-repair
```

The three registered commands check the source-bound result, the separate
implementation and behavioral controls. Direct Git-free replay uses:

```sh
python3 -I -Werror -B research/p112-three-frame-repair/verify.py
python3 -I -Werror -B research/p112-three-frame-repair/independent.py
python3 -I -Werror -B research/p112-three-frame-repair/test_controls.py
```

Set `TMPDIR` to an existing external directory to contain the controls' disposable
exports. Normal checks do not rewrite evidence; `--write` deliberately regenerates
each mathematical receipt. [RESULT.json](RESULT.json) and
[INDEPENDENT.json](INDEPENDENT.json) preserve every case, including complete
group-inventory digests and separate state counts. [VALIDATION.md](VALIDATION.md)
records environments, controls and limits.

[SOURCES.json](SOURCES.json) authenticates the selected live label input.
[SOURCE-EXPORT.json](SOURCE-EXPORT.json) pins the two retained predecessor
certificates to exact public commit bytes. Replay does not require unmerged
Git objects, a SAT solver, native compilation or network access.

## Open next questions

The unrestricted fifteen-group question remains open, including every partition
that disturbs at least four originals and every non-colouring fitting matrix.
Another repair census needs a separate research decision. A more useful physical
advance would specify a changed row space or source/reader contract and reduce
its fully charged bill. Fewer orthogonal groups alone cannot evade tariff 224.
The first steps and blockers are recorded in [TASK.json](TASK.json). This package
starts no deeper repair or supplier expansion.

## Credit

Nick Petalas's PR3356 supplies the thirteen-frame certificate; Tekalign's PR3370
supplies the retained sixteen-group construction and earlier repair pilots.
PR3387 supplies the preceding two-frame obstruction, and PR3383 explains the
fixed-row-space tariff boundary. Credit also stays with Matarener/Mark/PR3335,
ctoth, ywz65, Sagar Thakrar, Cinna Davis, Adam Gall, Jeremy Diviney,
Philippe Van Velzen and the retained E8/P112/compiler/supplier lineage.
Prepared by Nick Petalas. New work is Apache-2.0; assistance is disclosed in
TASK.json. No independent human or proof-kernel review is claimed.
