# One-column completion without enlarging cyclotomic alphabets

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. Let A
be an n-by-(n-1) matrix over the mth roots of unity, with A* A=nI.
Its normalized missing column is explicitly

```text
w = (nI-AA*) e_1,          w_1=1.
```

The completed matrix [A w] has orthogonal columns and retains the original
alphabet whenever m is even, for every n>=2. It also retains the alphabet
when m is an odd prime power and n>=3. For arbitrary odd m it always uses
at most the 2mth roots. Matrix order and alphabet order need not agree.
This extends the prime-order case of David Ganz's
[atlas B097](../pure-math-atlas-400/volumes/02-geometry.md#b097), PR2849,
and the prime pilot interface in his PR2855. Neither predecessor is audited
or replayed here.

[PROOF.md](PROOF.md) proves the universal statement. The missing entries
are integral sums of roots and have modulus one. Classical Kronecker and
cyclotomic field arguments put them in the original even alphabet. For
an odd prime-power alphabet p^a, orthogonality implies p divides n;
reduction at zeta=1 then excludes the extra minus sign.

The n>=3 restriction for odd prime powers is necessary. For any odd m,
A=(1,1)^T has missing column (1,-1)^T, even up to global phase. Thus
alphabet doubling is unavoidable in the unrestricted odd-alphabet problem.
For odd composite m and n>=3, this package gives the doubled bound and
leaves original-alphabet completion open.

## Exact finite evidence

The standard-library verifier uses integer polynomial arithmetic modulo
cyclotomic polynomials. It imports no predecessor executable and uses no
floating-point comparisons. It reconstructs each missing column, checks
literal column and row Gram identities, checks input preservation and
checks same-alphabet membership where the theorem requires it.

It checks all 314 dephased partial matrices in these ten domains:

```text
shape    alphabet orders m         numbers of valid inputs, in that order
3x2      3, 6, 9, 15              2, 2, 2, 2
4x3      2, 4, 6, 8, 10, 12       6, 24, 42, 60, 78, 96
```

Dephased means first row and first column have phase zero. The census
enumerates 3,879 candidate nonconstant columns and 2,582 candidate input
matrices. It does not identify gauge/permutation equivalents with each
other. Each count above is directly enumerated.

An additional 189 gauged tensor-Fourier erasures, at orders 4,6,8,9,12,15,
compare the recovered column with the independently retained erased column.
They include m=3,n=9 and m=9,n=9. Another 32 erasures of the 4-by-4
one-parameter family over mu_8 test a changed non-Fourier phase. Four
odd-alphabet two-row examples check the necessary sign boundary.
In total the verifier completes 539 cases and recovers 3,325 entries;
488 cases fall under the same-alphabet theorem. The other cases test the
general doubled-alphabet conclusion without claiming a counterexample
at n>=3. Nine malformed inputs reject. Three changed output entries fail
the Gram check. These finite fixtures corroborate the proof rather than
prove its unbounded quantifiers.

## Reproduction

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cyclotomic-column-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/cyclotomic-column-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cyclotomic-column-completion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cyclotomic-column-completion --check-source-history
```

Another CPython 3.12 path may replace the local path. Both direct modes
write nothing and emit `PASS_CYCLOTOMIC_COLUMN_COMPLETION`, the enumerated
counts and a generated SHA256 receipt for the six package files. The
registered commands each have a 60-second timeout. Source history,
metadata and committed-byte checks are separate from mathematical review.

The selected-baseline orientation passed with distinct complex, ordinary
BIT, admitted BIT and outer budgets. Its scope is source-binding metadata,
not a selected scientific replay. No selected cold replay was run.

## Scope and credit

This is an exact algebraic completion theorem and finite verifier. More
than one missing column, approximate observations, physical preparation,
paid consumption, dirty restoration, precision, tape costs and supplier
admission remain unproved. No new kappa or selected-frontier change is
claimed. Independent human and formal proof-kernel review, and global
literature priority, are unclaimed. Lean and Docker were not run.

Credit David Ganz's PR2849 for B082/B097 and the explicit composite-alphabet
boundary, and his PR2855 for the exact pilot recovery application. Their
proofs, implementation and original attribution remain unchanged.
Kronecker's theorem, cyclotomic irreducibility and field degrees, prime-power
reduction, Fourier tensors and the four-dimensional one-parameter Hadamard
family are classical. The new contribution is the stated extension of
this project's completion interface. Exact repository provenance is in
[SOURCES.json](SOURCES.json); classical primary-source links are in the proof.

The `formal-interface-lemma` card is explicitly changed to this algebraic
side result. It removes a prime-only alphabet restriction, without
constructing or pricing a multiplication supplier. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214393)
and [TASK.json](TASK.json) record the exact scope and overlap limitations.

## Open next questions

1. For odd composite m and n>=3, must every such partial matrix complete
   over mu_m? Start with m=15 and a dimension permitting mixed 3-cycle and
   5-cycle vanishing sums. The sign exclusion used for a single prime power
   has no direct replacement. A counterexample must be a complete partial
   matrix, not just a sum of n-1 roots with the right modulus.
2. Can this exact alphabet theorem support a robust completion method for
   noisy composite-phase inputs? Start by bounding the perturbation of
   (nI-AA*)e_1 and proving a separation radius for root rounding. Exact
   orthogonality and integrality are used here, so no noise guarantee or
   paid physical implementation follows.

## Verifier bounds

Only `verify.py` is executable. It has nonrecursive control flow and no
subprocess, network, generated code or dynamic imports. Functions are below
60 physical lines. Alphabets have order at most 15, cyclotomic conductors
at most 30, and matrices at most 16 rows. The largest census scans at most
12^3 candidate columns and at most 1,000^2 candidate pairs. Tensor fixtures
have at most four factors, three gauges and sixteen erasure positions.
All mathematical checks use explicit exceptions and remain active under -O.
Six package reads are each bounded by 1 MiB. Warning-strict execution and
syntax/function-size inspection are the available diagnostics; no external
static analyzer is installed or claimed.

Power of Ten rules 3 and 9 need managed-runtime deviations. Python integer,
tuple, iterator and JSON operations allocate and use runtime dispatch.
The fixed capacities above bound live data and call targets; this command
has no steady service loop or external mutable resource. Both registered
modes exercise these limits and controls. Reassess storage and validation
before accepting external inputs or larger search domains.
