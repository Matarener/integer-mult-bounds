# Independent audit of the exact Schur rank/dimension law

**Source-bound audit of PR6053 with a separate construction. No new kappa.**
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.

This follows [Nick Petalas's PR6031](https://github.com/CrocSwap/integer-mult-bounds/pull/6031),
Open next question 1, and [Krzysztof Wojt's PR5128](https://github.com/CrocSwap/integer-mult-bounds/pull/5128).
Their sector reduction, ordered maps, deficiency lifts and lower bounds are
credited and retained unchanged. This package uses a coordinate-minor chain
that attains the bound while preserving the three sector constraints.
This package is a local research result, separate from publication PR6046.

The final live overlap refresh found apoursh's [PR6053](https://github.com/CrocSwap/integer-mult-bounds/pull/6053),
opened at 03:27:51 UTC during this session. Its exact reviewed head is
12385ca23315181e3d15eb23a2d9ffec65d9a909. It proves the same dimension law
and an ordered closed formula for rho0. The final contribution is an
independent audit, including complete ternary d=2 corroboration and a
different attainment construction. It is not a competing new-theorem claim.
See AUDIT.md for the exact claim-to-evidence mapping and scope adjustment.

## Result

Let K be any field, d >= 1, A,B invertible d by d matrices, H arbitrary.
For commuting idempotents P,Q with leading blocks A,B and product leading
block H, let rho be the rank of the commutator of their Schur complements.
Use the quantities defined in PROOF.md:

    T00=I-A-B+H, T10=A-H, T01=B-H, T11=H,
    nu=sum nullity(Tj) for j=10,01,11,
    n0=rank(T00)+3d-nu, nmax=rank(T00)+3d+nu,
    rho0=rank(T G G' T), T=diag(T10,T01,T11).

For every integer rho from rho0 to 2d, the exact least ambient dimension is

    n_min(rho)=max(n0+rho-rho0, nmax-2(2d-rho)).

No smaller rank occurs. At n >= n0 the feasible ranks are exactly

    rho0 ... min(2d, rho0+n-n0, floor((n-nmax+4d)/2)).

The proof lifts sector kernels to a square defect pairing C. Retaining
coordinate rows R and columns J gives rank 2d-|R|-|J|+rank(C[R,J]).
First remove coordinates outside a maximal nonsingular minor. Then remove
row/column pairs at nonzero cofactors. These two phases meet the two lower
bounds exactly, without genericity assumptions over a finite field.

## Declared computational coverage

| Domain | Input cases actually constructed | Literal P,Q witnesses | Exhaustive admissible subspace pairs |
|---|---:|---:|---:|
| All A,B in GL2(F2), all H in M2(F2) | 576 | 2,496 | 21,690 |
| All GL2(F3) pairs and H, up to exact simultaneous conjugacy | 8,136 representatives | 26,148 | 113,768 |
| One fixed noncommuting d=3 binary pivot pair, all H | 512 | 2,546 | 35,801 |
| Structured inputs over Q,F2,F3,F5,F7,F11, d=1..4 | 165 | 861 | Not enumerated |
| Total | 9,389 labelled cases; **9,381 distinct triples** | **32,051** | **171,259** |

The ternary representatives cover all **186,624** raw input triples.
The finite action table, orbit disjointness, complete coverage and Burnside
count are checked. Simultaneous conjugation preserves the prescribed-block
problem and literal Schur complements as proved in PROOF.md. Witnesses are
constructed for representatives, not separately for every raw triple.

The d=3 binary pivots are A=((0,1,0),(0,0,1),(1,0,0)) and
B=((1,1,0),(0,1,1),(0,0,1)); this is not a census of all d=3 pivot pairs.
The structured rational/prime-field inputs are corroboration, not exhaustive
coverage of those fields or dimensions.

The verifier also compares all 576 binary profiles to the unchanged PR6031
program, checks every coordinate-subset pair for 609 small generic pairing
matrices (all 2x2 F2, 2x2 F3 and 3x3 F2 matrices), and rejects ten malformed
witness or false-formula controls. Nine actual source mutants test omitted
phases, principal-minor restriction, order/sign errors, sector mixing, a
wrong bound and a disabled independent rank check.
Two of these mutants additionally corrupt PR6053's ordered closed formula;
that formula is compared on all 9,389 labelled input cases.

## Reproduce

Python 3.12, standard library only. From this directory, including a Git-free
export:

    python -I -W error -B verify.py
    python -I -O -W error -B verify.py
    python -I -W error -B test_mutations.py

From the repository:

    python -B scripts/research_package.py --package research/schur-rank-attainment

A full replay takes about 2.5 minutes on the development machine; no timing
speedup is claimed. The registered commands allow 450 seconds per full replay
and 180 seconds for mutation checks. They read package-local files and create
no package output. The mutation harness uses temporary directories.

RESULT.json binds the declared result and all mathematical/code/metadata
inputs by SHA-256. Ordinary replay recomputes and compares it; missing bound
files and changed frozen references fail explicitly, including under -O.
The authoring option --emit-receipt prints a candidate receipt and deliberately
does not compare RESULT.json. It is not the normal verification command.
The quick option is a smoke test and is not evidence for the complete domains.

To inspect literal examples independently:

    python -I -B verify.py --emit-examples > examples.json
    python -I -B check_witnesses.py < examples.json

The second command imports no constructor code. This redirection syntax works
in a POSIX shell; on PowerShell pipe Get-Content -Raw examples.json to the
same checker. Fixture generation recomputes the full declared domains.

## Files and boundaries

- PROOF.md: field-independent argument and conjugacy coverage justification.
- AUDIT.md and reference6053.md: review map and exact concurrent-source proof.
- construct.py and linear.py: exact construction and arithmetic.
- oracle.py: separate finite subspace census, using explicit vector sets.
- check_witnesses.py: separate raw-matrix checker; no construction imports.
- ternary_orbits.py: complete finite group coverage.
- verify.py, test_mutations.py, RESULT.json: reproducible checks and fixed receipt.
- TASK.json, SOURCES.json, OVERLAP.json, VERIFY.json: scope, exact source pins,
  overlap coverage and registered commands.
- reference6031.py, reference6031.md, reference5128.md: unchanged attributed
  predecessor bytes. Source pins are checked before computation.
- VALIDATION.json: observed replay/export results; not a mathematical input.

The all-field conclusion comes from PROOF.md, not from extrapolating the tests.
"Independent" checks here means separate algorithms/code paths, all developed
by the same assistant. No independent human or formal-kernel review is claimed.

The hypotheses remain common deletion, invertible pivots, commuting idempotents
and coefficients in a field. No singular-pivot, coefficient-ring, physical
header, native delivery, restoration/ownership, precision, stock, outer-transfer
or selected-supplier claim is made. The selected frontier is unchanged.

## Open next questions

The next separate task would choose one concrete physical header and caller
contract, then translate and fully price a witness there. That contract is
not specified here; TASK.json records the blocker and first step.
