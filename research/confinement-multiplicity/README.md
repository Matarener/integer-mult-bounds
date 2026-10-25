# Two 20-point representatives fall short of 18 edges

**Partial. No new exponent.**

A closed walk on a 20-point set needs at least 18 edges to have at most two
components. Each basis direction contributes only one difference class, so the
number of edges is at most the sum of the seven largest difference
multiplicities.

The five imported 19-point representatives, each extended by zero, are covers
of the seven-bit space. Representatives 1, 2 and 3 have largest multiplicities
`3,3,3,3,3,3,3`, summing to 21. Representatives 4 and 5 have `2,2,2,2,2,2,2`,
summing to 14. The sum 14 is below 18, so those two representatives are
excluded for every basis. The sum 21 does not exclude the other three.

The same count leaves two even multiplicity patterns for a simple length-22
cycle: `(6,4,4,2,2,2,2)` and `(4,4,4,4,2,2,2)`.

## What was executed

The checker reads the imported table and recomputes the histograms. It does
not sample bases, it does not exclude the 21-point or 22-point cases, and it
does not claim `f(7)`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the confinement arithmetic in PR
3728, head `0f000bb4aac86fa667906d8092eb36e49a76944a`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to these
sums. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the imported table.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/confinement-multiplicity/verify.py
python3.12 -B research/confinement-multiplicity/test_verify.py
python3.12 -B scripts/research_package.py --package research/confinement-multiplicity
```

## Open next questions

These sums are the arithmetic exclusion. A basis sample would leave them.

## Credit

Alexander A. Davydov, Stefano Marcugini and Fernanda Pambianco classified the
sets in Table 6 of arXiv:1802.04214. petalas compared the seven largest
multiplicities with the 18-edge count.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
