# Complete colored-graph audit of the common24 P112 theorem

An independent implementation audit of [PR3960](https://github.com/CrocSwap/integer-mult-bounds/pull/3960)
at `7e8d98e351ac153d81943218bf168dc8548b1cea` finds no defect in its common24
theorem or two literal caller transfers. The additional finite result is:
**the entire different-normal completion graph is a matching**, with2,884
edges and448 isolated vertices among6,216 vertices. A hypothetical three
qualifying directions under one24-site cut would force a triangle. This
replaces the target's specialized small-cut/candidate split with one complete
graph certificate.

The fresh verifier generates each two-dimensional annihilator by its unique
sorted pair `a<b<a xor b`, rather than either target implementation's RREF
or affine-space traversal. It checks all43,435 binary seven-spaces and all
5,212,200 root-normal/space pairs. Both complete target inventory digests
agree. Root labels are independently solved over rational numbers from the
canonical table and simple system. No predecessor executable is imported.
[PROOF.md](PROOF.md) gives the coverage proof, audits the characteristic-zero
bridge, explicitly derives distance53, and checks coefficient independence
in the quotient transfer. [RESULT.json](RESULT.json) contains the graph receipt
and a two-direction witness. [REVIEWED.json](REVIEWED.json) identifies exact
target bytes; it is provenance, with no pending-PR runtime dependency.

The transfer concerns exactly `2^4,3,5,7^5` and `2^4,4^2,7^5`: eleven independent
pieces, required code intersection dimension5, quotient dimension6, and one
common support union of size at most24. The first transfer uses Nick Petalas's
inherited rank5 support cap12, previously audited in PR3951. This audit does
not repeat that capacity census. Original filter membership is inherited
from PR3960/PR3154/3282. Caller arithmetic is executable; the general field
and coefficient implications are written mathematics.

## Reproduce

From the repository root, using Python3.12 and its standard library:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-common24-graph-audit
```

The two registered optimized commands take about20seconds total on the
contributor's workstation. They verify the graph and meaningful adversarial
controls, including a triangle that does not correspond to a common cut,
repeated-color suppression, complete small annihilator orbits, and actual
CLI rejection of changed result, missing edges and changed input bytes.
Direct commands also work in a Git-free declared-input export.

## Scope and status

This is a fresh computational and written audit within the same donor/AI
assistant context as the target. It is not independent human acceptance or
formal verification. No full C5 result, closure of the whole(5,6) cell,
cut-threshold sharpness, decoder floor, supplier admission, full multiplication
theorem or changed selected kappa is claimed. Frozen predecessors remain
unchanged. The exact assigned acceptance gap and current overlap coverage
are recorded in [TASK.json](TASK.json).

## Open next questions

- Review the chamber, rational-kernel and quotient proof independently; start
  with PROOF.md sections3-4. Finite certificate success does not itself accept
  those written implications.
- A different literal caller needs a common30 bound or additional coefficient
  structure. Follow the separate current investigation after overlap checking;
  the common24 matching is not permission to extend its cutoff.

Structured first steps, relevance and blockers are in TASK.json.

## Credit

Nick Petalas retains credit for global capacities, root geometry, shortening
and shared-cut predecessors. DreamingOfClouds supplied PR3154/TWOSIDE/C5;
David Arias supplied the quadratic model; joaqcoo and the retained E8/P112
lineage retain their credit. This donor's PR3931, PR3951 and PR3960 supply
the earlier common-cut and dependency results. The new contribution is the
fresh complete-graph certificate and explicit application audit.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
