# A shape-sensitive bound for mixed negative Q8 targets

For t_i inverse-i targets and t_j inverse-j targets, every exact positive-Q8
word in the retained dirty-register model satisfies

```text
2n_i+n_j >= 4t_i-t_j,   n_i+2n_j >= 4t_j-t_i,
2n >= 5t_i+2t_j,       2n >= 2t_i+5t_j.
```

This is a scoped proof with finite corroboration. It strengthens the inherited
11t/5 total-call bound when one target multiplicity exceeds four times the
other. At shape (7,1), the previous necessary-count region allowed 18 calls;
the new lower bound is 20. No 20-call construction is supplied. Direct
execution costs 24, so the actual minimum remains in {20,22,24}.

The exact minimum of the strengthened INTEGER COUNT RELAXATION is

```text
N(t_i,t_j) = t_i+t_j
          + 2 max(ceil(3(t_i+t_j)/5), ceil(3t_i/4), ceil(3t_j/4)).
```

This projects the block floors, trace parities, inherited cubic count
inequalities and the two new quadratic inequalities. It is not an attainable
word classification. For example the relaxation permits seven at shape
(2,1), whose actual minimum nine is already established in PR3536.

[PROOF.md](PROOF.md) gives the new mixed quadratic rank charge, the uniform
proof, the exact integer projection and the infinite excluded family
(t_i,t_j;n_i,n_j)=(7k,k;7k,11k). The argument permits any finite number
of arbitrary restored dirty spectators and arbitrary binary scalar GL mixing.
Paid calls are positive i/j rank-one idempotent calls in the full formal
F2[Q8] algebra. Extra call types, clean workspace and physical costs are
outside this model.

## Evidence and reproduction

From the repository root, use CPython 3.12:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/q8-negative-shape-bound/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/q8-negative-shape-bound
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/q8-negative-shape-bound --check-source-history
```

The registered normal and optimized commands enumerate every candidate
nonnegative surplus split through total target count 64, compare its exact
minimum with the formula, and construct an arithmetic witness for each shape.
They also check the new rank inference on small binary matrices, exact full
Q8 direct words with two arbitrary dirty spectators, every regular basis
column of those words, and failure controls. These finite checks corroborate
the written proof; they do not independently re-certify the predecessor
chronological identities. The verifier prints a deterministic receipt bound
to all package files and declared source bytes, and writes no files.

[SOURCES.json](SOURCES.json) pins the inherited proofs and historical catalogue
and selected record at main `12fa8c5c844be21bfefb38a19503fbd867a11244`.
[TASK.json](TASK.json) records the changed card scope. This is a mathematical
side result for `bit-new-register-model`, not a new legal native construction.

## Limitations

The exact word minimum at shape (7,1), realizability of the count fixtures,
all physical scalar/routing/restoration/hosting/precision costs and supplier
admission remain unresolved. Unknown costs are not zero. No multiplication
theorem, kappa improvement or selected-frontier change is claimed. The selected
full cold replay, Lean and Docker builds are unrelated and were not run.
Independent human and formal proof-kernel review are unclaimed.

The verifier uses Python-managed allocations, bounded by its fixed target,
binary-width and ten-role limits. This is the documented Power of Ten rule-3
deviation: Python allocates tuples and integers during enumeration. Results
are aggregated rather than retaining candidate splits. If the bounds grow,
review the live-memory bound before widening them. Every loop has a finite
input or fixed-range bound; functions stay below 60 physical lines. Explicit
ValueError contracts remain active under optimized Python. No recursion,
dynamic code, external solver, subprocess or dependency is used by the verifier.
Warnings are treated as errors in both registered scientific commands.

## Related open work

- [PR3906](https://github.com/CrocSwap/integer-mult-bounds/pull/3906) checks
  arbitrary-dirty restoration of the one/two-target direct construction. It
  does not derive the mixed shape bound. The overlapping one/two-target
  counts are exactly 3 and 6 here, matching that package and PR3697.
- [PR2444](https://github.com/CrocSwap/integer-mult-bounds/pull/2444) supplies
  generic noncommutative exact-search tooling and a different GL2/S3 census.
  It does not study this inverse-Q8 target-count projection; no numerical
  quantity is shared.

## Open next questions

- Is there a full 20-call word for seven zi and one zj targets? Start with
  the legal splits at n=20 and the complete eight-coefficient endpoint
  equations. This decides whether the new floor is attained, but no endpoint
  search or physical caller is supplied here.
- Can simultaneous equality in the new quadratic and inherited cubic rank
  charges be realized at t_i=4t_j? Keep one chronological L in both
  orientations. Further count fixtures cannot establish realizability.
- Can an actual caller benefit from an improved formal word after its complete
  physical bill? First name that caller and its permitted layout and reads.
  No such caller or full invoice is currently supplied by this package.

## Credit

This contribution was produced by Nick Petalas. PR3578 supplies the homogeneous
quadratic method, PR3589 the mixed cubic boundary ranks, and PR3736 the old
necessary-count comparison. All are used as credited premises, not offered
as a new verification deliverable. Their PR3570/PR3536/PR3558/PR3517,
Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna Davis,
steph4n-gh and Q8/register predecessor attribution is retained in PROOF.md.
The mixed-target correction and its exact integer projection are new here.
New work is Apache-2.0.
