# A smaller joint interval bound from protected boundaries

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new kappa.

For the unchanged balanced PR628 dirty word, put h=ceil(log2 n). The protected
source and unread target improve the general joint-error coefficient envelope:

```text
previous: (h+2)^2
new:      h^2+2h+3, for h>=1
gain:     2h+1
```

The one-factor case has the separate bound two. Every ordered pair of complete
leaf cuts and both word orientations are covered, with the same dirty scratch
register reused at each depth. For arbitrary contractive factors the new norm
bound is h^2+2h+3, without commutation. For commuting factors whose every subset
product has norm at most G, it is (h^2+2h+3)G.

For example, height four improves the upper bound from 36 to 27. This is an
upper-bound improvement, not a sharpness theorem. Arham Tahir's #1374 gives the
compatible lower family floor(h^2/2)+h+2 and explicitly leaves the sharp upper
constant open. [PROOF.md](PROOF.md) supplies the new block inequality. The
prefix-entry invariant and squarefree-interval theorem are cited dependencies,
not verification deliverables. No predecessor executable is imported or run.

## Evidence and reproduction

The standalone verifier checks eight generic formal block products and 10,000
strict-gain identities. Its own iterative word emitter checks 23,736 nonempty
free noncommutative intervals at n=1,2,3,5,8,11 in both directions, full arbitrary
dirty endpoints and literal inverse order. Fourteen controls cover invalid
arguments, removed source/target restrictions, an oversized entry and the
distinction between an upper bound and a sharp value. A generated receipt on
stdout binds all six package files by SHA256; no receipt is hand-written.

From the repository root with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error -X dev research/protected-boundary-interval-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error -X dev -O research/protected-boundary-interval-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/protected-boundary-interval-bound
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/protected-boundary-interval-bound --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path. Expected
markers are `PASS_PROTECTED_BOUNDARY_INTERVAL_BOUND`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The last command requires the publication commit and full source history.
Both registered commands have 120-second timeouts. Direct verification also
works in a Git-free export containing these six files.

## Scope and implementation limits

The all-size theorem rests on the written block proof and cited lemmas.
The finite verifier does not prove those premises. Its generic matrices have
independent formal entries and need not be prefixes of a common word; their
exact row counts do not prove sharpness for actual words.

The finite emitter accepts at most sixteen factors and height four. Generic
matrix checks use at most ten rows. Polynomial operations enforce at most
64 terms and word length 32. All loops have finite fixture or capacity bounds,
the emitter uses a bounded explicit stack, and no function exceeds sixty lines.
Python allocation is a managed-runtime deviation from fixed allocation; the
matrix and polynomial capacities bound live objects. The only indirect calls
are three fixed invalid-argument control variants. There is no recursion,
subprocess, network access, solver, dynamic code generation or external
dependency in the verifier. Diagnostics use warning-strict normal and optimized
execution.

Rounded-leaf execution, negative-leaf preimages, internal magnitude and
coefficient preparation, precision/tape integration, native realization, stock,
ownership and a complete supplier invoice remain unrun or unproved here.
The selected result and its five framework assumptions are unchanged.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Is floor(h^2/2)+h+2 the sharp universal joint interval envelope? Use actual
  chronological relations between the two prefixes in the six phase-pair
  formulas. Cancellation and shared scratch across unequal child sizes are
  the remaining obstacles.
- Can one exact rounded caller use the smaller envelope in a complete
  sufficient-precision and physical-cost substitution? First retain its
  destination support, negative-leaf preimages, preparation and internal
  magnitudes. No such caller or complete invoice is supplied here.

These questions and their first steps are also recorded in [TASK.json](TASK.json).
The scope is frozen after this first local improvement.

## Credit and provenance

Chafik Boukhalfa supplies the PR628/905 word and retained lineage. Hanson Sun
supplies PR1085's prefix-entry invariant. Charles Bethin supplies PR1278's
squarefree-interval theorem and PR1416's distinction between a column and a
joint-state bound. Arham Tahir supplies PR1374's quadratic lower family and
explicit open upper-bound question. Philippe Van Velzen's PR2177 settles the
different completed-leaf destination problem. Philipp/mightyOil, Gareth
Davidson and 0xkilgore retain the precision, perturbation and restoration
lineage credited in those sources.

[SOURCES.json](SOURCES.json) pins exact main-tree proof and context blobs at
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. They are historical proof premises,
not runtime imports. The current `uniform-transfer-audit` card is explicitly
changed to this original algebraic side result. Current selected-metadata
orientation passed; no selected scientific replay is claimed.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214460).
