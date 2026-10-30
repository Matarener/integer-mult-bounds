# Exact COPY error from constant-weight phase histories

This contribution was produced by Nick Petalas. It proves the exact best COPY
approximation from one explicit family of Gaussian-dyadic Clifford histories.
The claim is a scoped written mathematical proof with exact finite corroboration.
There is no new kappa or selected-frontier change.

Let S=diag(1,i), and let U_A apply S on exactly the k axes in A among n axes.
Available source-preserving operations add c_A U_A^(tensor f) x to an arbitrary
initial accumulator y and return x unchanged. For every n>=1, 1<=k<=n and
integer f>=1, define

    L = sum_{j=0}^{min(k,n-k)} binom(k,j) binom(n-k,j) 2^(-fj).

The exact minimum normalized squared response error is

    min_c ||I - sum_{|A|=k} c_A U_A^(tensor f)||_HS^2
      = 1 - binom(n,k) 2^(-fk)/L > 0.

Its unique attaining coefficients are c_A=((1-i)/2)^(kf)/L. This permits
arbitrary complex, width-dependent exterior coefficients. For k=1 the error
is `(2^f-1)/(2^f+n-1)`. For n=8,k=4 it is `251/321` at f=1 and `1851/1921`
at f=2. No exact COPY can be synthesized within this fixed history contract.

[PROOF.md](PROOF.md) derives the phase-sensitive kernel, constant Gram row sum
and global optimum, then records every independent source and accumulator
column. The error normalization uses response dimension 2^(nf); for the full
two-register matrix normalized by twice that dimension the minimum is half
the displayed value. The source and dirty accumulator returns are exact.

## Evidence and reproduction

The standard-library verifier constructs literal tensor diagonals independently
of the formula, solves the exact normal equations, and executes a phase/ADD/
inverse-phase word on both registers. Its complete small domain is
`1<=n<=6`, `1<=k<=n`, `1<=f<=min(8,floor(10/n))`.

- 51 literal interfaces, 49,538 source diagonal entries and 1,653 Gram entries.
- 398 real/imaginary normal equations and 23,484 independent endpoint columns.
- 160 larger formula evaluations, nine semantic controls and ten input controls.

The larger evaluations reach n=128 and f=256; their matrices are not enumerated.
The universal statement relies on the written proof. Semantic controls change
the trace conjugation, coefficient power, intersection exponent, diagonal term,
history alphabet, coefficient field, dirty-state handling and source restoration.
The verifier generates a stdout receipt bound to SHA256 of all six package files.
No receipt is handwritten and no output is written into the package.

From the repository root, using CPython 3.12 and no third-party dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/constant-weight-phase-copy-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/constant-weight-phase-copy-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/constant-weight-phase-copy-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/constant-weight-phase-copy-error --check-source-history
```

The direct commands emit `PASS_CONSTANT_WEIGHT_PHASE_COPY_ERROR` in JSON.
The direct verifier also runs from a Git-free export using a local Python 3.12.
The committed-byte preflight requires a committed package and full Git history.
Hosted CI is separate from the local evidence.

## Scope, sources and implementation limits

This is a new explicit application of the finite-span follow-up in Ali Romman's
[PR #5727](https://github.com/CrocSwap/integer-mult-bounds/pull/5727), head
`8b74ecd0eea26d95b400e56435d35fbd261dc49b`. Its exact projection contract is
cited, not audited or replayed. No predecessor executable is imported or copied.
Normal equations, Hilbert-space projection, tensor-basis independence and subset
intersection counts are classical. The new contribution is the closed optimum
and attaining coefficients for this history family, with its complete endpoint.
Retain the broader Clifford/native/controller credit recorded by #5727.

[SOURCES.json](SOURCES.json) pins the predecessor proof and question, the
revision-8 catalogue and selected record as historical provenance at canonical
main `de5ec2e7a6074068452f45b1a191b5c72832df4a`. There are no live scientific
inputs outside this package. [TASK.json](TASK.json) preserves the original
helper-inventory card and explicitly changes its scope to an algebraic side
result. The selected source-binding orientation passed; it was not a replay.
The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216139)
states this same target.

The coefficients can have odd denominators. Native realization, coefficient
preparation, physical source restoration, precision, movement, ownership, stock,
storage and the complete recursive invoice are unproved and unpriced. The result
is not a physical supplier or a complete multiplication theorem. Adding other
history weights, source feedback or an identity history changes the theorem's
premise. Independent human and formal proof-kernel review are unclaimed.

The Python evaluator is bounded to n<=128,f<=256, and the literal enumeration
to n<=6,nf<=10. Loops have explicit finite bounds; the largest literal layer
has 20 histories and its largest diagonal has 1,024 entries. All functions
are below 60 lines, there is no recursion or dynamic code generation, and
checks use explicit exceptions that remain enabled with `-O`. Warning-strict
runs provide the available language diagnostics; no static type checker is
required here.

Rule 3 deviation applies to `verify.py` for its entire standalone run.
Python/Fraction requires dynamic allocation. Enforced domains bound live
collections and integer sizes; each interface is processed and released before
the next. Literal domain and rejection controls verify the caps. Before widening
them, derive and check the new live collection and integer-size limits. Runtime
and library allocation internals are not independently inspected.

## Open next questions

- What changes when two positive history weights are available together? Start
  with the phase-sensitive two-layer Gram blocks and their invariant normal
  equations. No multi-layer optimum is supplied. This can distinguish a real
  caller with a larger history alphabet from the fixed-layer obstruction.
- Can one attaining coefficient vector be implemented with a fully charged
  Gaussian-dyadic caller? Start with one explicit n,k,f and price coefficient
  approximation and restoration. Native delivery, precision, movement and the
  complete recursive bill are blockers; the algebraic optimum alone admits none.

New proof and verifier are Apache-2.0. Predecessor files and credit are unchanged.
