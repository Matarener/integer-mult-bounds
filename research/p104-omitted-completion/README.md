# Rank-eight completion of the omitted P104 endpoint effects

The 4,027-event PR3446 projection omits 696 outgoing ADD effects on 93 banks.
This package computes its difference from the full 5,398-event PR2586 word on
all 358 public normalized payloads. The final difference is a Y-to-X shear
with 52 nonzero rows and exact rank eight. The other 41 omitted banks restore
identically in normalized coordinates.

The explicit integer factorization is `R=C A/2`. Its eight queries can run
sequentially through one arbitrary dirty helper, restoring that helper after
every query. The completion alone preserves a Gaussian module `M` when Y is in
`2M`; the predecessor's sufficient `4M` Y entrance meets that condition.
A fixed 8 by 8 minor has determinant `-1/128`. The factorization and this minor
prove rank eight, including over fields of characteristic other than two.
The bound concerns linear query dimension, not simultaneous workspace or native
cost. The written argument is in [PROOF.md](PROOF.md).

All 93 omitted banks still have unfilled physical frame changes, including the
41 zero normalized rows. This is an algebraic endpoint completion, conditional
on native covariance for its interpretation in the physical word. It is not a
paid native implementation, supplier admission or improved kappa. The selected
frontier and unchanged-profile stopping rule remain unchanged.

## Evidence and replay

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -I -Werror -B research/p104-omitted-completion/verify.py
python3.12 -I -O -Werror -B research/p104-omitted-completion/verify.py
python3.12 -I -O -Werror -B research/p104-omitted-completion/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-omitted-completion
python3.12 -B scripts/check_research_commit.py --package research/p104-omitted-completion --check-source-history
```

The verifier uses forward provenance bitsets to reconstruct the projection and
exact rational state rows to compute both endpoint maps. Reverse covectors
separately check all 716 public output rows. It checks all 5,408 factorization
entries, eight original private erasures, native class/occurrence frame bindings,
93 physical frame gaps, six full-map fixtures and six rejecting controls.
The tests also execute all 104 source columns with three dirty helper values and
exercise the real optimized CLI with Git unavailable, altered/missing source
bytes and altered certificate data. No predecessor executable is imported.

`CERTIFICATE.json` contains the complete `A,C` matrices, basis minor, residual
matrix digest, omitted outgoing event IDs, all omitted frame gaps and exact
counts. Default verification compares every receipt field. `--out NEW_PATH`
writes a fresh receipt and refuses overwrite. It does not regenerate frozen
inputs. These are exact structural counts, not runtime measurements.

## Source and overlap

Canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The input bytes already on main are PR2586's word and compressed native archive,
retained by the rounded-collector package. `SOURCES.json` pins their hashes,
blobs and the original card. PR3446 at
`886222c1d3e2c2d878b263dc8d165ef03d5bac7f` supplies the projection definition,
its published event-list hash and the released omitted-effects question.
Runtime reconstructs that projection directly from the two canonical inputs;
it needs neither PR3446 files nor an unmerged commit in the object store.

The advance claim is [in the existing P104 investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009903).
Entry overlap covered 368 open PRs and 2,285 Discussions with complete pagination.
Targeted omitted-effects/residual/PR3446 search found the credited predecessor
and its handoff. Unpublished work, every historical diff and omitted sparse
local notes are outside that coverage. No match is a novelty guarantee.
Submission refresh covered 374 open PRs and 2,299 Discussions with complete
pagination and no warnings; the relevant matches were this claim and PR3446.
Canonical main, guidance and the PR3446 head were unchanged. Concurrent
correlated-entrance work changes a different obligation.

## Open next questions

- Can an actual physical caller realize `A,C` with legal frame access and
  restore the one borrowed dirty helper? Start by binding the certificate's
  93 target frame gaps and retained dimension-eight Y outputs to exact native
  adapter recipes. Adapter availability, source restoration and payment block
  a physical completion; a normalized zero row does not remove its adapter.
- Can a complete changed profile pay for those adapters and the summary circuit?
  First specify a full invoice, including scalar expansion, physical owners,
  source/target movement, idle and cleanup costs, precision and recursive calls.
  Unknowns are not zero. Stop before further construction if a fully charged
  favorable screen fails. This package does not license an unchanged-profile
  optimization campaign.

## Credit

Nick Petalas. Apache-2.0. Hiroki Kumazaki/PR3446 supplies the recipient-history
closure and omitted-effects handoff; Clear1nsight/PR3423 and PR3382 supply the
open-port/first-collector predecessors. ywz65/PR2586 and PR2497 supply the
physical dual and logical word. Arham Tahir's rounded-collector package retains
the canonical source bytes. Retain the contributions of Tekalign/PR3025,
Ross Richardson/PR3068, Jose Manuel, Vasek, Philippe Van Velzen, Chafik Boukhalfa,
Rohan Arun, Adam Gall, Josie Elliston, Ali Romman, icekylinx and the credited
geometry/native/compiler lineage. PR3406, PR3416, PR3426 and PR3448 retain their
separate source-domain, native-covariance and tensor-domain credit. No frozen
predecessor bytes or notices were changed.
