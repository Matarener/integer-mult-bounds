# Exact extreme-rank BIT header densities

This package proves exact good-header fractions for rank-one and corank-one
projectors in every dimension m >= 2 over a finite field of order q. The
claim type is a scoped proof with a finite certificate, with no new kappa.

For the retained normalizer's leading-principal-minor criterion, the total
number of projectors in either family is

    T = q^(m-1)(q^m-1)/(q-1).

The good counts are

    rank one:   q^(m-2)((q-1)q^(m-1)+1),
    corank one: (q^2-q+1)^(m-1).

Divide by T for the good-header fraction. The exact rank-one bad fraction
is `(2q-1)(q^(m-1)-1)/(q(q^m-1)) < 2/q`. The [proof](PROOF.md) passes these
fractions to complete GL headers over Z/q^w, for prime q and every w >= 1.
They are deterministic complete-domain counts. An explicit wholly bad
header class prevents their use on arbitrary restricted header sets.

The distinction answers the extreme-rank part of #4215's bad-fraction
question with a new counting theorem. It does not repeat the predecessor's
normal-form proof. The current card concerns #4100; [TASK.json](TASK.json)
records the changed scope to the earlier retained normalizer and the reason.

## Evidence and reproduction

Use CPython 3.12, standard library only, from the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/projector-header-density/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projector-header-density
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projector-header-density --check-source-history
```

The replay enumerates canonical rank-one factorizations and their complements,
independently scans all matrices in small field/local-ring domains, enumerates
complete small GL header domains and compares actual source admission tests.
The generated [RESULT.json](RESULT.json) records every domain and counter,
controls and SHA256 of all package files except itself and both live inputs.
The all-matrix census visits 951,417 matrices and finds 2,162 nontrivial
idempotents, with 1,332 good. These aggregates agree numerically with #4215's
reported corpus. The complete-header census visits 315,648 invertible headers.
Normal and optimized registered commands compare that receipt exactly.
To regenerate a candidate outside the checkout, use
`verify.py --write-receipt /new/external/path.json`. It refuses overwrites.

Controls distinguish the wrong reversal, checking only the final minor,
dropping zero coordinate products and transferring the density to a bad
header subset. A separate direct pair-product dynamic program checks the
corank-one path count without using projector matrices.

## Limits

The universal statement rests on the written counting proof, without a formal
kernel or independent human review. The finite implementation uses prime fields.
It does not enumerate GL64, audit intermediate ranks, certify actual selected
residual counts, reprice fallback children or prove the full recursive machine.
No selected source or invoice changes.

## Open next questions

Can an exact intermediate-rank density replace the current union bound?
Start at rank two using a canonical image/kernel parametrization, and check
every required leading minor together. The obstacle is their joint distribution,
not another numerical evaluation of an existing root. Before changing an actual
bill, bind all request/header multiplicities and the complete fallback cost.
The structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

This result was produced by Nick Petalas. Source527 and commdata2338 retain
the normal-form algebra credit. Jose Manuel retains the recursive closure
and `controlled_normalizer.py` credit. The selected source lineage includes
DreamingOfClouds, eumemic and alephnan, as recorded in the unchanged source
notices. The small-ring normal-form audit in #4215 is a distinct predecessor.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
