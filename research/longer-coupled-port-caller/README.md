# An all-order obstruction for coupled star callers

The constant-loss star frame cannot be repaired by port coupling or by a
longer order. In the binary normalized model, this package excludes every
odd leaf count g>=3, every coupled channel dimension and every order of
its calls. It keeps the star query frame and four complementary connector
queries fixed. **No new kappa is claimed.**

[PROOF.md](PROOF.md) gives the complete contract and the three-stage
reduction. There are only 75,600 relative order types after that reduction.
For each type, an exact identity in a free noncommutative algebra proves
0=I. The identities apply to matrices of every size. This is stronger than
a bounded search over matrix entries or port counts.

[RESULT.json](RESULT.json) records the independent replay. The compressed
[certificates](ORDER-CERTIFICATES.json.gz) contain every witness. The
[checker](check_certificates.py) expands them without importing the search
code or using a solver. There are 72,020 witnesses of degree at most two
and 3,580 of degree at most three. None has more than 77 terms.

The package also checks actual coupled matrices, the mixed coefficient
formula, a complete one-leaf positive word, and corrupted data. The pinned
PR5599 bill gives a positive relaxed moment at saving 1/320 for g=1023;
the theorem shows why that price screen cannot become a caller in this
frame. The selected record advanced upstream to .00310045 during this
work. It was not changed by this contribution.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3 scripts/research_package.py --package research/longer-coupled-port-caller --check-only
python3.12 scripts/research_package.py --package research/longer-coupled-port-caller
python3.12 -I -O -B research/longer-coupled-port-caller/verify.py
```

The registered check uses the saved exact witnesses. To rebuild witnesses:

```sh
python3.12 -B research/longer-coupled-port-caller/build_certificates.py
```

The optional discovery searches and their complete receipts are described
in [DISCOVERY.md](DISCOVERY.md). Their Z3 results are not proof inputs.
Exact source commits, Git blobs and SHA256 hashes are in
[SOURCES.json](SOURCES.json). The package began at canonical main
6cf7a683f447b9f1e2333791907fd92be5009a63; the refresh at
df0137efd35e11b4445734bf612bdd4c7ebc330c changed the selected record but
not the priority or working instructions.

## Open next questions

- Change the query Gram frame. Test its chronological matrix equations
  before any full native construction or favorable price claim.
- Change the connector maps or add interleaved paid queries. Recompute
  every equation and keep the complete bill.
- Establish a valid characteristic-zero statement for a concrete caller.
  General dyadic coefficients cannot be reduced modulo two.

Other frames, connector contracts, nonfull stage ranks, noninvolutive
stages, changed targets and productive helper feedback remain outside the
theorem. No native replay, proof-assistant proof, independent human review
or global obstruction to improving kappa is claimed.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. Credit Cinna Davis / 1337isnot1337 for the controller and simplex
lineage, PR5617 for the stage/intersection cuts, PR5631 for the star frame
and mixed chronology condition, and all P104/helper/native/compiler/outer
source authors retained by those packages. Free-algebra identities and
finite linear algebra are standard tools. The new work is the coupled
parameterization, the all-order reduction and its exact certificates.
