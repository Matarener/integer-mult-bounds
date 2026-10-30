# Sharp sparse cyclic quotient obstructions

Scoped algebraic proof with exact finite corroboration. No new kappa.

For a two-point exponent support {u,v}, let h be the positive gcd of the
coordinates of v-u. With the ambient integer lattice fixed, its smallest
faithful cyclic quotient has size

    mu(h) = min { q >= 2 : q does not divide h }.

Every such minimum is a prime power, and every prime power occurs. Thus even
two points in one dimension can require arbitrarily large moduli. For maximum
coordinate difference H, the sharp worst-case minimum is the first m with
`lcm(1,...,m)>H`. These statements optimize over every integer weight vector.

A separate exact fixture shows the simultaneous constraint. The support

    {(0,0), (1,0), (0,1), (1,1), (2,2)}

has optimum modulus **six**, versus its mixed-radix box bound **nine**.
Weights (1,3) give residues (0,1,3,4,2) modulo six. Modulus five fails for every
weight, although all ten pairs can be separated individually modulo five.
The first four points are the subset sums of (1,0),(0,1), and the last is a
target exponent. No true register identity is asserted from that support alone.

[PROOF.md](PROOF.md) proves the unbounded laws and the exact fixture minimum.
The result answers the short-quotient question in woklerx's
[PR #1440](https://github.com/CrocSwap/integer-mult-bounds/pull/1440).
It gives a smaller finite representation on a new support and two exact
obstructions to support-size or pairwise-only compression rules. The source's
mixed-radix theorem remains valid and is not audited here.

## Reproduce

From the repository root, using the local CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sparse-cyclic-quotient-obstructions/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sparse-cyclic-quotient-obstructions/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sparse-cyclic-quotient-obstructions
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sparse-cyclic-quotient-obstructions --check-source-history
```

Another CPython 3.12 path can replace the absolute interpreter path. Only the
standard library is needed. The verifier writes no files and has no executable
predecessor dependency. Both registered commands produce
`PASS_SPARSE_CYCLIC_QUOTIENT_OBSTRUCTIONS no_new_kappa`; the runner also reports
`PASS_REGISTERED_RESEARCH_PACKAGE`. A generated stdout receipt binds all six
package files by SHA256. No handwritten receipt is used.

The declared finite corroboration is:

- All 4,096 scalar heights through 4,096, with the exact minimax envelope at
  every height, and all 27 prime-power realizations through 64.
- All 1,176 vector/modulus cases for nonzero differences in [-6,6]^2 and
  moduli 2 through 8, enumerating 34,104 weight vectors.
- All 91 weight vectors modulo 1 through 6 on the new support. The numbers
  of injective projections are (0,0,0,0,0,8).
- All 32 binary support polynomials at every such projection, comparing
  14,112 regular-action columns against direct integer-exponent translations.
  Every unfaithful projection gets an explicit nonzero two-term kernel witness.
- All ten pairs modulo five, four rejected unsafe projections and three
  semantic controls for an omitted target, prime-only search and a modulus
  bound based solely on support size.

Finite enumeration is evidence for the implementation. The written proof,
not extrapolation from those counts, establishes the general statements.

## Scope and limitations

This is a verification side result under a changed task-card scope. It does
not satisfy the card's complete decoder/supplier acceptance gate. The modulus
is a certificate representation size; a smaller modulus is not a runtime
speedup or a legal physical address realization. No larger-register candidate,
selected paid/target profile, complete native/ordinary invoice, all-size
compiler, precision, tape/stock bound or multiplication theorem is supplied.
No selected cold replay, proof kernel or independent human review was run.

The two-point obstruction assumes integer weights on the supplied ambient
lattice. A frontend may evade it by first rebasing the subgroup generated
by the differences: {0,h} inside hZ then needs only modulus two. That is a
different domain for the homomorphism. The five-point support generates
all of Z^2, so its optimum six survives such a change of group basis.

[SOURCES.json](SOURCES.json) pins the source README, original catalogue and
selected record as historical provenance at canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. They are not executable inputs.
The package itself can replay without Git or a network. Predecessor code,
frozen evidence and the selected frontier are unchanged.

The Python checker uses bounded finite loops and functions below 60 lines.
Managed-runtime allocation is the Power of Ten deviation: live collections
are limited to 32 polynomial images, six fixture success counts and a fixed
six-file hash receipt, plus fixed-size vectors. Integer values are bounded
by the displayed scalar and prime-power domains. It has no recursive calls,
code generation, subprocesses or hidden runtime dispatch.

## Open next questions

Can one compress the full support of an actual larger-register candidate
below its mixed-radix box bound? First retain every subset sum and target
exponent, test arithmetic pair obstructions, then certify one simultaneous
injective weight vector. A specified candidate and an explicit representation
cost allowance are missing. [TASK.json](TASK.json) records this handoff.

## Credit

The sharp sparse-support analysis, new five-point fixture, proof and checker
were produced by Nick Petalas. Credit woklerx's PR #1440 for posing the
short-quotient question, its sufficient mixed-radix injection and faithful
regular-action criterion, and its retained eumemic PR #288 / huxint PR #203
register-model lineage. Gcd, least-common-multiple and regular-representation
facts are classical; no general literature-priority claim is made.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
