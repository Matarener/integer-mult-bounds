# A mixed-negative Q8 boundary-rank bound

For t_i inverse-i and t_j inverse-j targets in full formal F2[Q8], every
word of positive i/j rank-one idempotent calls satisfies

```text
t=t_i+t_j>0, n=n_i+n_j,
2n+n_i >= 6t-t_i,       2n+n_j >= 6t-t_j,
therefore n >= 11t/5.
```

The [proof](PROOF.md) permits free binary scalar GL mixing and any finite
restored dirty workspace. It closes PR3570/PR3578's remaining balanced
2/2 eight-call handoff. Every four-target inverse-generator endpoint now
has exact minimum ten or twelve calls. Neither length ten nor the sharp
uniform constant is decided. The homogeneous 5t/2 bound in PR3578 remains
stronger in its own domain.

The new step replaces the homogeneous zero-product argument by
rank(X_g)+rank(Y_g)<=n_g+t_g, then uses both inherited cubic orientations
to lower-bound all four boundary ranks. This is a mathematical side
result for the nonabelian bit-register model. No selected-frontier,
physical supplier or kappa improvement is claimed.

## Reproduce

Use CPython 3.12 from a repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-mixed-boundary-rank
python3.12 -B scripts/check_research_commit.py --package research/q8-mixed-boundary-rank --check-source-history
```

The second command must run after committing the package. Direct scientific
and control replay also work from an export without Git or network:

```sh
python3.12 -I -Werror -B research/q8-mixed-boundary-rank/verify.py
python3.12 -I -O -Werror -B research/q8-mixed-boundary-rank/verify.py
python3.12 -I -O -Werror -B research/q8-mixed-boundary-rank/test_package.py
```

Keep the package directory intact. Use an external writable TMPDIR for the
controls. No third-party dependency is needed. [RESULT.json](RESULT.json)
is the exact finite receipt; [VALIDATION.md](VALIDATION.md) states coverage
and code constraints. [TASK.json](TASK.json) preserves the original card,
actual scope, hypothesis, public claim and structured next questions.

Finite corroboration covers both algebra bases and cubic orientations,
216 fixed generic words on 6,048 independent dirty columns, 4,452
rectangular boundary pairs including 3,770 nonzero products, 578 cubic
subspace equality fixtures, 42 direct endpoints on 1,296 dirty columns,
and 6,157 admitted integer-count pairs through t=16. Eight optimized
behavioral tests reject actual algebra/action/correction faults, missing
rank hypotheses, bad domains, source corruption and receipt corruption.
These checks support the author-written universal proof. They are not
a word-length census or a formal proof-kernel verification.

## Sources and limits

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19013623)
preserves the original claim and current status. Nick Petalas/PR3570
supplies the exact mixed cubic identity and subspace lemma; PR3578
supplies the two-orientation homogeneous boundary-rank method. PR3536
and PR3558 supply the sign-sensitive quadratic chronology and cyclic
subspace argument. Their unchanged actual proof premises are retained
with origin commits, paths, blobs and SHA256 in
[inputs/RETENTION.json](inputs/RETENTION.json). Scientific replay needs
no pending branch, foreign Git object or network. Canonical ancestry
pins in SOURCES.json concern the selected record and originating card.

The retained lineage includes Nick Petalas/PR3517, Tuafo/PR2900,
ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna Davis, steph4n-gh and
the credited Q8/register sources. Arham Tahir/PR3137 and PR3461 concern
separate physical/scalar costs. Frozen notices stay unchanged in inputs/.

Independent human/formal acceptance, a ten-call decision, a sharp
constant, physical caller, full scalar/routing/restoration/hosting/
precision/recursive invoice, complete supplier and multiplication theorem
remain unclaimed. The selected full cold replay, Lean and Docker are
unrun. No dependent construction round or minimum-length search ran.

## Open next questions

- Decide the balanced 2/2 ten-call case from the complete eight-coefficient
  endpoint equations. Necessary counts alone cannot settle it.
- Inspect simultaneous equality in the cubic subspace and nonzero-product
  boundary bounds to test sharpness of 11t/5. Finite rank fixtures are not
  endpoint realizations.
- Bind an actual formal saving to a physical caller and a complete paid
  invoice before making a supplier or exponent claim.
