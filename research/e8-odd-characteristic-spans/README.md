# E8 span inputs have no exceptional odd prime

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with an exhaustive finite integer certificate. No new kappa.**
The E8 facts S1, S2, S3prime and W2 used by DreamingOfClouds's
[PR2819](https://github.com/CrocSwap/integer-mult-bounds/pull/2819) hold over
**every field of characteristic different from two**. This supplies a new
field range for the span inputs that its section 7 leaves open. The existing
characteristic-zero classification and SAT work are cited, not audited.

[PROOF.md](PROOF.md) states the exact domains. Orthogonal roots span the
seven-, six- and five-dimensional complements of the specified one-, two-
and three-root anchor sets. The 56 nonorthogonal neighbors of any root
project to 28 distinct directions, with every three independent. No odd
prime changes those conclusions.

The new verifier constructs 6539 integer minors with absolute determinants
in {2,4,8,16,32,64,128,256}. Each remains nonzero over every odd-characteristic
field. Its complete fixed-anchor domain consists of one S1 matrix, 119 S2
matrices and their 119 anchor pairs, 1512 S3prime matrices and their 1512
anchor triples, and all 3276 projected-direction triples. It checks all
14400 root images under the 120 integral reflections and verifies a
120-line orbit to transport the result to every anchor.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/e8-odd-characteristic-spans/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e8-odd-characteristic-spans
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e8-odd-characteristic-spans --check-source-history
```

Local checks used CPython 3.12.15 on macOS 27.0.1 arm64. The two registered
commands took 0.13 and 0.14 seconds locally, below their 60-second limits.

The principal marker is `PASS_E8_ODD_CHARACTERISTIC_SPANS`. The verifier
writes a JSON receipt to stdout, binding its certificate digest to SHA256
hashes of the package and declared input files. Redirect outputs outside the
checkout. It writes no files and executes no predecessor program.

Modular elimination only selects minors. Exact fraction-free determinants
supply the proof certificates. The checks include 673 comparisons with an
independent Leibniz determinant formula, rejection of a singular matrix and
odd-torsion matrices at three and five, and two dyadic-unit/power controls.
All checks remain active under `-O`.

## Limitations

This does not extend the complete rank-nine classification to positive
characteristic. Its remaining sign logic, pinning implications, other finite
facts, SAT encodings and refutations were not assessed or replayed here.
There is no decoder floor, native supplier, caller, signed invoice or
selected-frontier change. The five selected framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed.

The executable uses bounded exact integer arithmetic, without recursion.
Every matrix has at most 63 rows and eight columns; every determinant has
order at most seven. Managed Python allocation is a documented deviation
from fixed-capacity allocation. Finite inventories bound live data. The
certificate digest is generated, not a hand-written receipt. Historical
source checks are byte bindings only.

## Open next questions

- Which remaining PR2819 classification implications require a further
  characteristic restriction? Start by listing those implications and their
  denominators. This matters because the new span inputs alone cannot admit
  the classification in a new field; those implications remain the blocker.
- Does an explicitly missing span input for P112 or P104 admit dyadic-unit
  minors? First identify its exact incidence domain in a source package.
  This could help the supplier geometries, but is blocked by that distinct
  target specification. No punctured-unit result is claimed here.

The same questions are structured in [TASK.json](TASK.json).

## Credit and related work

DreamingOfClouds retains PR2819's classification, naming and characteristic-zero
span inputs, with its PR2784 lineage. The standard E8 root coordinates are
also retained there. No predecessor source or credit line is changed.
CubeJerry's [PR3095](https://github.com/CrocSwap/integer-mult-bounds/pull/3095)
and conorholds's [PR3755](https://github.com/CrocSwap/integer-mult-bounds/pull/3755)
use power-of-two minors and integral reflection transport for different
root/character span questions. Those methods are established background.
The new contribution is the all-odd-field S1/S2/S3prime/W2 input set and its
complete bounded certificate. No literature-priority claim is made.

The overlap check covered all 310 open PR bodies and complete Discussion
pagination at the recorded snapshot, targeted merged-PR searches, and
canonical-main README searches for the facts, their field range and more
general formulations. The sparse local-note corpus was incomplete. No
matching open PR was found. Unpublished work remains outside that coverage.
