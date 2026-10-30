# A direct root-2 stage deletion needs more than receiver-only compensation

This contribution was produced by Nick Petalas. It builds on
[DreamingOfClouds's PR #6144](https://github.com/CrocSwap/integer-mult-bounds/pull/6144),
Ali Romman and the retained P104 construction lineage.

**Scoped proof with an exact finite certificate; no new kappa.** One explicit
attempt to remove owned register 772's frame-520 stage moves helper 497's root
read to frame 737 and removes its earlier register-48 read. The missing form is
`V = x_48 + x_32 + x_98 + x_85`. At the next 145/161 consumer, the resulting
differences are exactly `-V` in 497 and `V/2` in 161; all other rows agree.

Receiver-only compensation cannot preserve that consumer contract. The input
`x_32=1, x_5=-1`, with all other independent inputs zero, gives zero in receiver
161 and every field it can read throughout the stated repair window. Its
required consumer value is `-1/2`. Arbitrary homogeneous linear compensation
in that window therefore fails, even with unrestricted constant coefficients
and repeated reads. [PROOF.md](PROOF.md) gives the exact edit, window and proof.

This is a new obstruction to an attempted changed read/trajectory contract.
It does not audit the predecessor or exclude its general open lead. A useful
next construction must change another source, trajectory, earlier prefix or
consumer contract. Frame 737 is unattempted. No new paid invoice, supplier,
native tariff, selected-frontier change or complete multiplication theorem is
claimed. The five inherited framework assumptions remain.

## Reproduction and evidence

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p104-root2-receiver-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/p104-root2-receiver-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-root2-receiver-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-root2-receiver-obstruction --check-source-history
```

Other systems may substitute their CPython 3.12 interpreter. Expected direct
status is `PASS_ROOT2_RECEIVER_OBSTRUCTION`; the registered runner reports
`PASS_REGISTERED_RESEARCH_PACKAGE`. Every registered check is bounded at 120
seconds. The receipt is generated, binds its verifier and input hashes, and is
compared byte for byte. Regenerate it only to an external path with
`verify.py --output /absolute/scratch/RESULT.json`.

The verifier checks all 2,712 cuts in the compensation window and 241,377
coframed donor occurrences. A separate full symbolic interpreter checks the
attempted edit's effect on every one of the 799 input coordinates at the
consumer cut. Five false-claim controls run in normal and optimized mode.
These are finite exact checks supporting the induction proof; they are not
formal proof-kernel or independent human review. No full predecessor, selected
supplier, native, compiler, outer or rounded-multiplier replay is performed.

The predecessor word is retained byte for byte in `inputs/`. `UPSTREAM.json`
records its author, original head, path, Git blob, size and SHA256. Replay needs
no network or unmerged Git object. Its original compressed bytes were obtained
through GitHub's contents API and checked against the API's Git blob and size.
The task and selected-record provenance are pinned at canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419` in `SOURCES.json`.

## Related open work

- PR #6144 poses the root-2 stage-removal lead and supplies the input word;
  it supersedes the closed predecessor PR #6143.
- PR #6145 independently descends the 772/731 relay on top of #6143. This
  certificate is bound to #6144's different word and claims no transfer to it.
- PR #6136 studies chart-only changes on PR6030. This attempted edit changes
  which register 497 reads and where it reads it.
- PR #6084 excludes an endpoint-recoding approach to helper 469. The helper,
  read graph and quantified repair class here differ.
- PR #6154 coalesces the 791/770 owned lifetime on PR6144. This certificate
  uses the uncoalesced predecessor and concerns the separate 772/497 path.

The broader P104 scalar and helper-split packages have different contracts.
Their results and credits remain with their authors. The overlap search checks
metadata and scoped main-branch notes; it is not a global novelty certificate.

## Open next questions

Can another source or consumer contract remove root 772's frame-520 stage?
A paid complex improvement would matter at the binding supplier. First change
one source trajectory or the 145/161 consumer cut, track both the separating
input and the full missing form, then charge all additional moves and target
changes. No legal all-input construction or favorable complete invoice is
supplied here. The structured question is in `TASK.json`.

## Credit and license

The input word, root-relay descent and open lead are by DreamingOfClouds.
PR6030/PR5907 supply the previous rung-removal words; Ali Romman's PR5827
supplies their checking conventions, following Mason Hale's PR5811 and the
retained lineage through Pierre-Loic Doulcet's PR5565. This package contributes
only the explicit attempted edit, its separating certificate and the scoped
receiver-only theorem. The available-span obstruction method is classical;
Jonathan Capalbo's PR6069 and JoyboyBrian's PR6084 provide related P104 uses.
New material is Apache-2.0.

Independent human and formal proof-kernel review are unclaimed.
