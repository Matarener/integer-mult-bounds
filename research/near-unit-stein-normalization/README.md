# Near-unit rational Stein generators

**Scoped proof with exact finite corroboration; no new kappa.** For a
Gaussian-rational matrix E of rank r and any integer p>=1, the new exact
producer retains r outer products E=sum_j g_j a_j and guarantees

    ||g_j||_2 <= 1,       ||a_j||_2 < (1+2^-p)||E||_2.

At p=3 this replaces the factor two in Jose Manuel's
[PR4198](https://github.com/CrocSwap/integer-mult-bounds/pull/4198) by 9/8.
The orthogonal residuals, reconstruction and coefficient-row convention
remain credited to that package. The change replaces a power-of-two scale
by a dyadic scale with a bounded mantissa. It uses exact integer square
root and squared comparisons. Each emitted rational component gains at
most p+2 bits of height relative to the old normalization.

Exact factor one cannot always be achieved over Q(i) with r terms. For the
rank-one matrix with first column (1,1,1)^T and all other columns zero, it
would require a Gaussian rational with squared norm three. The classical
modulo-three norm obstruction excludes that. Extra terms change the
contract, so this is not an obstruction to overcomplete factorizations.

[PROOF.md](PROOF.md) proves both statements. The universal claims are
written proofs; the finite replay corroborates their implementations.
No predecessor scientific result or executable is audited or replayed.

## Exact example and evidence

On the same rank-one input, p=3 gives

    c=7/4,    g=(4/7,4/7,4/7)^T,    a=(7/4,0,0).

The squared column norm is 48/49. The squared row norm is 49/16, compared
with four from the old scale c_0=2. These values are checked directly from
the displayed formulas.

The standard-library checker passes 4,800 independent small normalizer
comparisons on 960 distinct positive rational squared norms, plus 84
wide-exponent/precision fixtures. It constructs 717 new real/complex
matrices and checks all 2,151 factorizations at p=1,3,9, containing 3,645
terms. A separate Gaussian elimination checks exact ranks. Every matrix
entry is reconstructed. Exact Hermitian Schur tests check the stronger
row inequality a_j* a_j <= (c_j^2/n_j) E* E. Eighteen domain and semantic
controls cover invalid inputs, zero and negative PSD pivots, strict rounding,
capacity limits and the modulo-three obstruction. The complex and tiny-pivot
fixtures separately exercise conjugation and exact nonzero rank decisions.

The small normalization oracle scans bounded exponents and mantissas,
independently of the producer's integer square root. The complete two by
two domain uses entries in {0,1,-1,i,-i}; other fixtures include zero rank,
large exact denominators, a 2^-200 independent direction and dimensions
three, four and eight. No numerical singular values or rank tolerance
are used. A generated stdout receipt binds the six package files and
the retained proof input by SHA256. No receipt is handwritten.

## Reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/near-unit-stein-normalization/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/near-unit-stein-normalization/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/near-unit-stein-normalization
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/near-unit-stein-normalization --check-source-history
```

Substitute another CPython 3.12 path on another machine. Expected markers
are `PASS_NEAR_UNIT_STEIN_NORMALIZATION`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The optional `--receipt PATH` creates a new receipt outside the package
and refuses to overwrite an existing file. Default execution is read-only
and needs no Git or network.

## Scope, provenance and implementation bounds

Canonical base is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. [TASK.json](TASK.json) explicitly changes the
`uniform-transfer-audit` card to this coefficient-generation side result.
The selected record resolves to conditional kappa .003125804. Its five
framework assumptions remain. [SOURCES.json](SOURCES.json) pins the
retained PR4198 proof at its incorporated bytes; it originated at
`e457d5e912a27307d725827aeca7198169320b84`. No predecessor engine is imported.

The proof allows arbitrary finite dimension and requested precision. The
supplied implementation enforces dimension at most eight, input component
height at most 512, requested precision 1..128, and normalizer numerator
and denominator at most 65,536 bits. An intermediate norm exceeding that
capacity is rejected. These are implementation limits, not mathematical
exceptions. All loops range over bounded dimensions, fixed fixtures or
explicit finite oracle domains. No recursion is used. Functions are below
60 lines. Managed Python and Fraction allocations are a Power of Ten
rule-3 deviation; live state is bounded by these finite capacities. The
fixed test callbacks are a rule-9 deviation with explicitly listed targets.
Warning-strict normal and optimized checks supply the interpreted-code
diagnostics. No repository analyzer configuration is changed.

The published scale c is dyadic, but dividing v by c can introduce odd
denominators. Gaussian-rational coefficients were already the source
contract. This package does not claim a Gaussian-dyadic native realization.
It supplies no rounded child execution, coefficient-page format, physical
delivery, full dirty-state error ledger, actual precision saving, complete
caller invoice, compiler admission or multiplication theorem. Exact
factorization and height estimates do not settle those obligations.
Independent human and formal proof-kernel review are unclaimed.

Initial overlap covered live claims and local reservations, 337 open PRs
and 5,953 Discussion records in the cached complete remote pagination,
targeted merged PR searches, recent account work and main README searches.
The sparse local-note scan omitted 8,525 notes; the separate Git searches
covered the main README inventory. Neither search covers unpublished work
or proves literature novelty. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279686)
states the exact target. Classical normalization and arithmetic remain
background; the contribution is this implemented normalization refinement,
its encoding bound and minimal-term endpoint obstruction.

## Open next questions

Can an actual rounded Gaussian child exploit the smaller coefficient norms
in its error allocation? Start with one emitted row and its normalizer,
bind the coefficient/data errors to the child's literal rounding protocol,
and charge coefficient delivery. This would make the local magnitude
improvement useful to the caller. The rounded child and its physical cost
interfaces remain missing. The structured question is in TASK.json.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0. Credit Jose
Manuel / jmbarrancoml for PR4198's exact rational residual factorization,
row convention, bounded coefficient producer and Gaussian interface;
Vlado Vojdanovski / PR1673 for the underlying dirty-shear compiler;
Cinna Davis for its retained caller; and the predecessor's credited
structured-matrix and phase contributors. Gram-Schmidt, rank-one norms,
integer square root and the Gaussian-rational norm obstruction are
classical. All predecessor files and credit lines are preserved.
