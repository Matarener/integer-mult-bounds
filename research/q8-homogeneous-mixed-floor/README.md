# A stronger homogeneous mixed-Q8 bound

For t identical inverse-i targets in full formal F2[Q8], with both
positive i and j calls permitted, every exact word satisfies

```text
2 n_i+n_j >= 4t,       2 n_i+3 n_j >= 6t,
therefore n_i+n_j >= 5t/2.
```

The [proof](PROOF.md) permits free binary scalar GL mixing and any finite
restored dirty workspace. Exchange i and j for the homogeneous inverse-j
endpoint. This raises PR3570's homogeneous lower bound from 2t to 5t/2.
Four identical negative-generator targets therefore require **ten or
twelve** calls. At ten the only necessary paid counts are six calls of
the target's positive generator and four of the opposite generator.
Neither a ten-call word nor its exclusion is supplied.

The new step charges both boundary ranks through the homogeneous
zero-product relation X_jY_j=0. Two triangular quadratic identities and
the two label orientations of PR3570's cubic identity give the count
inequalities. The necessary region is not claimed attainable or sharp.
This is an author-written proof with finite corroboration. Independent
human and formal proof-kernel acceptance are unclaimed. No physical
caller, complete supplier, new kappa or selected-frontier change follows.

## Reproduce

Use CPython 3.12 and a private external writable TMPDIR. No third-party
dependency is needed. From the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-homogeneous-mixed-floor
python3.12 -B scripts/check_research_commit.py --package research/q8-homogeneous-mixed-floor --check-source-history
```

The exact commands also work in the same directory structure without
Git, network or foreign objects:

```sh
python3.12 -I -Werror -B research/q8-homogeneous-mixed-floor/verify.py
python3.12 -I -O -Werror -B research/q8-homogeneous-mixed-floor/verify.py
python3.12 -I -O -Werror -B research/q8-homogeneous-mixed-floor/test_package.py
```

[RESULT.json](RESULT.json) authenticates the scientific/runtime sources
and exact deterministic evidence. Replay checks the 256-element basis,
64 Hamilton products, cubic/fourth reductions, 390 fixed generic words
in both label orientations on 9,360 faithful dirty-input columns,
1,593 triangular Sylvester fixtures including 399 equality cases,
186 zero-product rank pairs, and 36 direct homogeneous endpoints on
1,296 dirty columns with 378 omitted-factor controls. A bounded integer
check covers t=1 through 32. Four optimized behavioral groups reject
actual arithmetic/chronology/action/count faults, missing hypotheses,
invalid domains, changed source/proof/receipt bytes and output overwrite.
These are correctness fixtures, not an endpoint search or minimum census.

`--write PATH` generates a candidate receipt exclusively and refuses an
existing file. [VALIDATION.md](VALIDATION.md) states bounds, deviations
and unrun obligations. The proof supplies the universal quantifiers.

## Sources and credit

Canonical baseline is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. SOURCES.json pins the canonical catalogue and selected record.
Exact used PR3570/3536/3558 proof bytes are retained under inputs/;
[RETENTION.json](inputs/RETENTION.json) records origin commits, paths,
blobs, SHA256 and actual mathematical use. No premise is comparison-only,
and scientific replay needs no foreign Git object or network. The finite
three-role exclusion in PR3536 and cyclic determinant in PR3558 are not
premises of this result; the required arguments are rederived here.

Nick Petalas/PR3570 retains the mixed cubic identity, PR3536 the quadratic
chronology and PR3558 the subspace method. PR3517, Tuafo/PR2900,
ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna Davis, steph4n-gh and the
retained register-model lineage keep their credit. Arham Tahir/PR3137
and PR3461 concern separate physical/scalar obligations. New material is
Apache-2.0. Nick Petalas.

[Canonical investigation and original scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19012819).
TASK.json preserves the initial hypothesis, scope, evidence and limits.
The selected full cold replay, Lean, Docker and independent acceptance
are unrun. No solver or expanded endpoint census ran.

## Open next questions

- Decide the homogeneous ten-call four-target case at counts 6/4.
- Decide the untouched mixed 2/2 eight-call boundary with its nonzero
  opposite-label target block.
- Bind a concrete formal saving to an actual caller and complete paid
  physical bill before claiming supplier or exponent improvement.

TASK.json gives each question's relevance, first step and blockers.
