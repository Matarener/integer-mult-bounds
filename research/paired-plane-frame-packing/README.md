# Thirteen disjoint P112 binary orthonormal frames

The literal 112 P112 labels admit **thirteen disjoint orthonormal 8-frames**,
covering 104 ports. This answers [PR3335 open question 1](https://github.com/CrocSwap/integer-mult-bounds/pull/3335)
by refuting the proposed maximum of twelve. That predecessor reported a best
packing of twelve and left maximality open. The packing number is now between
13 and 14. A partition into fourteen frames remains open.

This improves a finite packing bound. It does not improve the reported scalar
fitting-rank upper bound of 34, supply a native COPY invoice, or certify a new
multiplication exponent. All results below are exact finite checks plus the
written linear-algebra arguments. No human or proof-assistant review is claimed.

## Exact model and source

Port `i` has the nine-bit label `q_i` in the `recipes` array of
`research/adaptive-kernel-demotion/inputs/DATA-PHASES.json`. The committed input
has SHA256 `c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`.
These are the same bytes that PR2484 authenticates as the selected1094 replay's
`candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json` member.
The source is already on canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
No pending Git object, predecessor checker, or network access is needed for replay.

The pairing is `dot(q,r) = popcount(q & r) mod 2`. A binary orthonormal frame
`F` satisfies `dot(q_i,q_j) = 1` exactly when `i=j`, for all `i,j` in `F`.
This is binary label orthonormality, not Euclidean orthogonality of E8 roots.

The first thirteen `orthonormal_groups` in `CERTIFICATE.json` are the frame
witness. The four remaining groups are pairs. The verifier checks every Gram
entry and that the groups partition ports 0 through 111 exactly once. Therefore
all thirteen frames are disjoint. Conversely, any disjoint packing has at most
`floor(112/8)=14` frames. The latter is only the cardinality bound.

## Scalar fitting consequence and its limit

The eight uncovered ports are
`{16,24,29,65,68,70,80,108}`. Their binary orthogonality graph has thirteen
edges and no four-clique. Every remaining even orthonormal group therefore
has size two. One finishing matching is `{16,108}`, `{24,80}`, `{29,65}`,
`{68,70}`. Retaining the thirteen full frame groups thus leaves four pair
groups. It does not yield a smaller colouring fit merely by finishing this
remainder. The verifier checks all seventy four-subsets of the remainder.

Pair consecutive ports within each group. This gives 56 Gram-I2 planes. Write
`E(i)` for the plane containing port `i`. The strict scalar fitting mask is

```text
K[i,i] = 1
K[i,j] = 0 for i != j whenever E(i) and E(j) are not orthogonal.
```

For each even orthonormal group, make two supports by taking its even and odd
positions. Let `v_s` be the 0/1 indicator column of support `s`, and set
`K = sum_s v_s v_s^T`. These 34 nonempty supports partition the ports. Hence
`K` has rank exactly 34 over every field: the factors give rank at most 34,
and selecting one representative from each support gives a principal `I_34`.

The diagonal entries are one. The two ports of a plane lie in different
supports. Two distinct planes can share a support only within an orthonormal
group, where every cross-pairing vanishes. Thus every forced off-diagonal
entry is zero. Both checkers inspect the resulting full 112-by-112 matrix;
there are 11,360 forced entries for this matching.

The certificate also gives sixteen pairwise nonorthogonal planes. Both ports
from every such plane force a principal `I_32` in **every** scalar fit, including
nonsymmetric fits. Thus this new matching's minimum fitting rank lies between
32 and 34 over every field. The rank-34 matrix above is a particular fit;
its rank does not prove minimum rank 34. PR3335's exact minimum 34 concerns
its different matching. No claim is made that 32 is attainable here.

## Reproduction

Python 3.12 or later and the standard library suffice for all proof checks:

```sh
python3 -I -O -B research/paired-plane-frame-packing/verify.py
python3 -I -O -B research/paired-plane-frame-packing/independent_check.py
python3.12 -B scripts/research_package.py --package research/paired-plane-frame-packing
```

The primary check authenticates the source, checks the frames, strict scalar
mask and clique, and rejects duplicate/omitted ports, a false frame count,
a repeated clique vertex, a partition-preserving nonorthogonal swap and changed
source bytes. The independent check imports no predecessor or primary verifier.
It expands the labels into nine coordinates, constructs the dense scalar matrix,
checks all required entries, and computes rank 34 modulo 2, 3 and 1,000,003.
It rejects a dense-matrix mutation that replaces a forced same-plane zero by one.
The written disjoint-support argument supplies the all-field conclusion.

`RESULT.json` is the exact receipt. `SOURCES.json` binds the live label input
and the historical task context. `VERIFY.json` registers both bounded checks.
The selected supplier's full cold replay and the native plane implementation
are outside this contribution and were not run.

### Optional discovery

`discover.py` enumerates the 4,032 possible 8-frames and sends their disjoint
packing problem to SciPy's MILP interface. The discovery environment was
Python 3.12.15, numpy 2.5.4, scipy 1.18.1, HiGHS 1.12.0 on macOS arm64.
After 180 seconds it returned a thirteen-frame candidate and an unresolved
fourteen-frame bound. Numerical search is not part of the proof.

```sh
python3.12 -B research/paired-plane-frame-packing/discover.py --output /path/outside/package/packing.json
```

The optional search needs the stated numpy/scipy versions, may return a different
candidate, and refuses to overwrite a file. Check every returned candidate
exactly before interpreting it. A timeout is not an impossibility certificate.

## Scope, overlap and credit

Card `coverage-law-change`, priority revision 6, scope changed to the explicit
finite packing question in PR3335. This is an algebraic prerequisite of the
changed two-coordinate plane contract, not a completion of the card's physical
acceptance gate. The source-bound task and stopping rule are in `TASK.json`.
The card's first ceiling replay passed as an orientation check.

Entry overlap checked 259 open PRs and 2,188 Discussion records with complete
pagination, plus current handoffs. The concurrent audits of PR3335's literal
34-support copy tariff and vector/block extension were left to their claimants.
This contribution changes the matching and answers the frame-packing question.

PR3335 at `1d46df8b5aeac49d165cae58c1dd1036666bb789`, contributed by
Matarener/Mark, supplied the question, previous packing and rank-34 result.
The retained plane model, rank and mask lineage includes ywz65/PR2471,
thakrarsagar/PR2484, Cinna Davis/PR1825/PR2118/PR2126, Adam Gall/PR1889,
ctoth and the Discussion #1587 collaborators. Native-payload and tariff boundaries
retain Jeremy Diviney and Philippe Van Velzen's credit. The literal label source
retains its own attribution and notices. No predecessor package is changed.
Apache-2.0.

## Open next questions

Can fourteen disjoint frames partition all 112 labels? The exact-cover input
is small and explicit, but this session supplies no infeasibility certificate.
An attaining partition would give fourteen groups and a rank-28 colouring fit.

Can a changed matching or a genuine scalar completion lower the rank-34 upper
bound? This matching has a 32-to-34 bracket. A useful follow-up must check the
strict scalar mask and distinguish query dimension from copied-information rank,
payload arrays, physical transport and restoration. Those implementation costs
remain unpriced. Further construction expansion needs the repository's complete
boundary and cost checkpoint.
