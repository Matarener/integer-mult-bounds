# Odd cyclotomic Clifford response gate

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
For every odd n>1, an actual Gaussian-rational M-qubit Clifford U satisfying
Phi_n(U)=0 on the whole bank necessarily obeys

```text
phi(n)=2^a,  1<=a<=M
n is a squarefree product of distinct Fermat primes
Tr(U)=mu(n) 2^(M-a)
rank_F2(S_U-I)=2a
native B-rank <= min(M,2a).
```

The degree-four cap is sharp: a complete four-qubit Clifford W satisfies
Phi5(W)=0 and has native B-rank four. Its construction adds two identity
spectators to an explicit two-qubit order-five Clifford and conjugates by
Bell preparation. For fixed odd n, the primitive relation cannot carry
unbounded native rank. This is an interface obstruction, with no new kappa.

[PROOF.md](PROOF.md) gives the all-parameter argument and the explicit
sharpness construction. The new step extends Ross Richardson's
[PR4081](https://github.com/CrocSwap/integer-mult-bounds/pull/4081)
whole-bank cubic gate to every odd cyclotomic polynomial. His cubic result
and fixed-Pauli character argument retain their credit. Classical cyclotomic
irreducibility, totient arithmetic and Clifford/Bell gates retain their
classical status. Global literature priority is unclaimed. No predecessor
verifier is imported or replayed.

## Evidence and reproduction

The standalone standard-library verifier uses exact integer Gaussian
numerators, common positive denominators and binary elimination. It checks:

- All 2,047 odd n in 3..4095. Totients from explicit coprime enumeration
  equal the independently factored formula, and the degree condition equals
  the squarefree Fermat-prime condition. Eleven n in this interval pass the
  necessary degree test. This is not an existence census.
- The complete two-qubit degree-four matrix and four-qubit sharp example,
  including their polynomial identities, unitarity, all Pauli generators,
  every fixed-Pauli sign, both ranks and the adjoint trace identity.
- An order-five tensor control with symplectic defect eight that fails
  Phi5=0; a wrong global phase; a passing primitive-power control; a
  nonunitary companion matrix satisfying Phi5; and four invalid domains.

Run from the repository root with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/odd-cyclotomic-response/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/odd-cyclotomic-response/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/odd-cyclotomic-response
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/odd-cyclotomic-response --check-source-history --check-modes
```

Other installations may substitute their CPython 3.12 path. Expected markers
are `PASS_ODD_CYCLOTOMIC_RESPONSE`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Each direct check takes less than one second
locally and has a registered 30-second limit. Normal and optimized runs
generate the same six-file SHA256-bound receipt on stdout. No receipt is
hand-written or stored in the package. Direct replay also works in a
read-only Git-free export.

[SOURCES.json](SOURCES.json) pins the catalogue, selected record and source
proof as historical provenance. They are not executable inputs. The
scientific base is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. The selected source-binding first command passed as metadata
orientation only. The `joint-query-controller` card is explicitly changed
to this algebraic response-interface result; it does not solve the installed
QQ16 caller task. [TASK.json](TASK.json) records the overlap limits and
structured next questions.

## Limits

The universal result is the written proof. Finite checks corroborate the
identities and bounded arithmetic, and do not prove the all-n statement.
The necessary condition on n is not a sufficient existence classification.
Order n alone, non-Gaussian coefficient fields, non-Clifford operators,
several cyclotomic factors and restricted-input identities are outside the
theorem. A sparse reader relation of unbounded degree is also outside the
fixed-degree consequence.

No actual selected caller, physical native program, complete signed invoice,
dirty restoration, ownership, hosting, precision, stock, tape execution or
supplier admission is supplied. No selected scientific replay, Lean or
Docker run was performed. All five selected framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed. No complete
multiplication theorem or selected-frontier change follows.

## Open next questions

- Determine which degree-permitted n admit Gaussian-rational Clifford
  responses. Begin with a complete primitive order-seventeen example and
  its Pauli action; the necessary degree condition alone supplies no such
  construction.
- Bound native rank when a fixed product of several odd cyclotomic factors
  annihilates U. Begin with the exact multiplicity and trace equations for
  Phi3*Phi5; cancellation can make the adjoint trace vanish, so the present
  nonzero-character argument does not automatically apply.

These are follow-on questions. Any favorable physical caller still needs
its complete producer/consumer contract and paid bill before expansion.

## Verification implementation bounds

There is no recursion or dynamic code loading. Every matrix has dimension
at most 16, every scalar numerator and denominator is bounded by 2^256,
matrix powers use at most 32 factors, polynomials have at most 33 bounded
integer coefficients, and the factor domain ends at 4095. Pauli loops have
at most 256 labels and eight generators. Every function is below 60 lines.
Explicit invariant failures remain active under optimized Python.

Power of Ten rule 3 has a managed-runtime deviation at verify.py: Python
allocates integer, tuple and dictionary objects during exact arithmetic.
Fixed dimensions, bit capacities, factor bounds and sequential fixtures
bound live collections. No asynchronous resources or retained output files
exist. Rule 8 uses the standard dataclass decorator for one fixed four-field
immutable record; it loads no external schema or executable input. Rule 9
uses reduce with the single built-in gcd target over at most 512 integers.
Warning-strict normal and optimized runs plus AST compilation supply the
available Python diagnostics. A static type-checking configuration is not
introduced for this isolated research package. A future larger replay must
reassess these capacities before raising them.

New work is Apache-2.0. Exact predecessor pins and credit are in
[SOURCES.json](SOURCES.json) and [PROOF.md](PROOF.md).
