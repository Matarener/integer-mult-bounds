# Joint binary bases do not lower the two-plane invoice

**Negative result; no kappa improvement claimed.** For the fixed certified
matching of the selected 112 ports into 56 orthogonal planes, every invertible
four-message binary basis on every pair of planes costs exactly as much as
decoding the two planes separately. The exact minimum is 8 copy units for all
1,540 pairs. No strict improvement occurs in this finite subfamily.

This tests one concrete route toward leaving two coordinates unpaid per live
family: let a joint decoder mix two matched planes. It does not prove that such
an interface change is impossible. The original `coverage-law-change` card
asks for a changed coverage identity and a fully charged endpoint contract;
this package deliberately narrows that target to an exact decoder screen. The
scope change and bottleneck connection are recorded in [TASK.json](TASK.json).

## Exact object and invoice

The inputs are the pinned 112-label selected record and the 56-edge matching
in `paired-plane-port-matching-seed6c563a/CERTIFICATE.json`. Each edge spans a
Gram-\(I_2\) plane under the binary dot pairing. A candidate selects any two
matched planes, giving four source coordinates and four reader coordinates.

For each invertible \(P\in\{0,1\}^{4\times4}\), the four messages are the
columns of \(P\), and the exact decoder is \(P^{-1}=\operatorname{adj}(P)/\det
(P)\). A message's source support is the set of input planes used by its
column; its reader support is the set of output planes used by the matching
row of the adjugate. The charge for one message is the rank over \(\mathbb F_2\)
of the original binary pairing matrix restricted to those complete source and
reader plane spans. Summing the four charges gives the copy invoice. This uses
the inherited pairing-rank tariff; it is not the rank of the rational encoder
or decoder coefficient matrix.

The baseline is four separate messages, two per plane, each charged two, for
total charge of \(2+2+2+2=8\). There are 22,560 invertible binary matrices,
which induce 391 distinct source/reader support patterns after quotienting by
the invoice-relevant supports. We price every pattern against every unordered
pair among the 56 planes: 602,140 exact cases. Each pair's minimum is 8.
`RESULT.json` records the histogram, a representative minimizer, source pins,
and a digest of all per-pair minima.

The verifier computes determinants and adjugates over the integers, checks
both adjugate identities, and computes pairing ranks using independent row-
and column-elimination routines. It binds the receipt to the archive member
and matching certificate by SHA256. Positive identity/permutation controls,
singularity rejection and a nontrivial-basis control guard the enumeration.

## Scope boundary

This is a complete negative result only for the finite family above. It does
not cover arbitrary rational or complex encoder entries, more than four scalar
messages, mixing three or more planes, a different matching, multi-array
native operations, physical routing/restoration, or a replacement coverage
law. The 0/1 restriction is on the encoder columns; the exact inverse may have
rational coefficients. No complete supplier, endpoint contract, construction
round, or change to the selected kappa follows.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/joint-plane-basis-screen/verify.py
python3.12 -I -O -B research/joint-plane-basis-screen/verify.py
python3.12 scripts/research_package.py --package research/joint-plane-basis-screen --check-only
python3.12 scripts/research_package.py --package research/joint-plane-basis-screen
```

The replay is read-only and must reproduce [RESULT.json](RESULT.json) byte for
byte. `VERIFY.json` registers the two pinned live inputs and bounded command.
Source commits and file digests are recorded in [SOURCES.json](SOURCES.json).
The scientific base is canonical main at `20ecf2891d80b5acf18d980b2164fb44ea7faa90`,
priority revision 6. Frozen source evidence is unchanged.

## Open next questions

Can arbitrary rational coefficients or overcomplete factorizations lower the
same two-plane pairing-rank invoice? A first step is to formulate a finite
relaxation for a fixed pair and prove that its objective matches or lower
bounds the native copy tariff. Even a cheaper relaxation would still need an
implementable multi-output primitive, restoration schedule and complete
endpoint cost before it could affect kappa. Three-plane mixing is a separate
extension and should follow only if the two-plane decoder model yields a
credible route to admission.

## Credit

The selected labels and matching follow the pinned selected-provider lineage.
Credit the paired-plane endpoint and scalar identity in [Discussion #1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587)
and [PR #2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126), and
the exact one-array payload accounting in
[paired-plane-native-payload](../paired-plane-native-payload/README.md). That
work prices independent blocks and explicitly leaves joint mixing across
planes open; this package tests only the four-message binary-basis subfamily
of that gap. Prepared for Gonzalo Mier with substantial OpenAI Codex
assistance in research framing, exact enumeration, verifier implementation,
checking and writing; no independent human review. Frozen predecessor evidence
remains unchanged. New work is Apache-2.0.
