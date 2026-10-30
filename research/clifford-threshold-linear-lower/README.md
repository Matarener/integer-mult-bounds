# The full Clifford tensor threshold grows at least like 2n+1

For every n >= 2, the projective tensor Gram matrix of the full n-qubit
Gaussian-dyadic Clifford group is **singular at every width f <= 2n**.
Its pointwise tensor-independence threshold therefore satisfies

    2n + 1 <= T(n) <= 4n + 4,

where the upper bound is Ali Romman's
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526).
In particular **7 <= T(3) <= 16**. Before this, the only exact values were
T(1)=5 (MatShep, #5549) and T(2)=9 (MatShep,
[#5675](https://github.com/CrocSwap/integer-mult-bounds/pull/5675)), and there
was no lower bound for general n. With cited code lemmas, T(n) >= 2n+3 for
n = 1 (mod 4), n >= 5 (#5635), and T(n) >= 2n+2 for n = 2 (mod 4) (#5902).

This partially answers the Open next question of #5675 ("does 4n+1 continue
at three or more qubits?"). It proves linear growth and leaves the exact
three-qubit value open. It is a scoped proof with finite corroboration, not
a κ, supplier or selected-frontier change.

## The argument

[PROOF.md](PROOF.md) has the details. The Hadamard-free affine/quadratic
monomial native group of #5369/#5529 is a subgroup of the Clifford group with
the same scalars, so its Gram matrix is a principal submatrix of the Clifford
Gram, and any null vector of it is a null vector of the full Gram. Ali
Romman's cuspidal residual from
[PR #5635](https://github.com/CrocSwap/integer-mult-bounds/pull/5635),
projected to zero phase, is a fixed nonzero group-algebra element. A
self-orthogonal-code argument valid for every n shows that it vanishes at
every width f <= 2n. It is nonzero because an explicit full-span zero-phase
tuple of length 4n+1 sees it.

The new parts are the principal-submatrix transfer from the monomial grammar
to the full Clifford Gram, and the all-n code step (#5635 states its code step
only for n = 1 mod 4).

## Evidence and reproduction

Use the repository CPython 3.12 interpreter from the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/clifford-threshold-linear-lower
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/check_research_commit.py --package research/clifford-threshold-linear-lower --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/clifford-threshold-linear-lower/verify.py
```

On another machine, substitute any CPython 3.12. Only the standard library is
used. The direct verifier prints `PASS_CLIFFORD_THRESHOLD_LINEAR_LOWER` in
about three seconds, in normal and `-O` modes. It checks, exactly:

- the code step exhaustively at n = 2, 3, 4 (7, 34 and 458 zero-phase
  multisets of size at most 2n, none with full affine span), plus the explicit
  length-(4n+1) full-span tuple for n = 2..64;
- the cuspidal coset identity on GL(2,2) and GL(3,2) at 1,194
  (g, hyperplane) pairs;
- at two qubits, literally: all 3,072 monomial matrices normalize the Pauli
  group and form 768 projective classes. At each width f = 1..4 the residual's
  class vector is nonzero and the exact class Gram (tr(U_a^* U_b))^f
  annihilates it. The same residual has diagonal entry 128 at widths 9..12;
- three rejection controls (trivial character, sign with its order-three
  values negated, one perturbed coefficient), each of which fails H_4 v = 0.

No predecessor executable is run. The cited proofs are pinned in
[SOURCES.json](SOURCES.json).

## Limits

Green's character theorem enters through #5635's cuspidal lemma and is cited,
not proof-kernel checked; the n = 2, 3 coset checks only corroborate it. The
bound 2n+1 is not sharp at n = 2 (T = 9), and the theorem does not decide
T(3) = 13. Spectral constants, physical callers, invoices, compiler,
precision, tape, stock and κ are outside this result. Independent human and
formal proof-kernel review are unclaimed. All five framework assumptions keep
their status.

The formal-interface card is explicitly narrowed to this written
native-interface side result (see [TASK.json](TASK.json)). Base main is
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221825).
Overlap was checked against open PRs, Discussion claims, merged PR titles
(`cuspidal`, `axis cutoff`, Clifford threshold) and `research/*` README and
PROOF text on main. A search with no hit does not prove novelty.

## Open next questions

- **Exact T(3), now in [7,16].** This decides whether 4n+1 continues. First
  step: compute the centre action of the three-qubit Clifford group on class
  functions at widths 7..13, as #5675 did at two qubits. Blocker: the group has
  order 4 x 92,897,280 and no class or character table is in the repository.
- **A full-group residual.** The residual here lives in the Hadamard-free
  subgroup, whose own threshold is only about 2n+3. Raising the all-n bound
  toward 4n+1 needs a null vector that uses Hadamard-type elements. First
  step: find an all-n analogue of #5675's width-8 determinant witness. The
  determinant itself is trivial for n >= 3.

## Credit

This contribution was produced by Nick Petalas. MatShep posed the question in #5675 and proved the
n = 1, 2 thresholds (#5549, #5675). Ali Romman proved the 4n+4 upper bound
(#5526), the native grammar and Fourier framework (#5369, #5529) and the
cuspidal residual (#5635). Joseph Anglada (#5542) introduced the coset method.
The n = 2 (mod 4) refinement uses #5902. Self-orthogonal codes, Schur products
and Green's character theorem are classical. New work is Apache-2.0.
