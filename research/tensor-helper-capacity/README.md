# Sharp tensor composition of dyadic helper capacity

For dyadic pairing matrices K_i, the exact simultaneous unit-channel count is

```text
c(tensor_i K_i) = min_{odd primes p} product_i rank_Fp(K_i mod p).
```

If factor i has rational rank r_i and positive capacity c_i, the sharp bounds are

```text
product_i c_i <= c(tensor_i K_i) <= min_i c_i product_{j != i} r_j.
```

Both endpoints are attainable for every prescribed rank/capacity tuple. Thus t
rank-n factors, each with capacity one, can have tensor capacity n^(t-1).
Repeated equal factors retain exactly the product capacity. Different odd-prime
rank losses are what permit a strict gain.

Claim type: scoped algebraic proof with exact finite corroboration. No new kappa
or physical supplier is claimed. [PROOF.md](PROOF.md) gives the theorem, equality
criterion and explicit X K Y = I_2 witness for
`diag(1,3) tensor diag(1,5) = diag(1,5,3,15)`.

Ali Romman's [#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
supplies the cited single-cut unit-block theorem. The new step is its sharp
composition envelope and the failure of individual capacities to determine
tensor capacity. No predecessor executable is imported or replayed. The
predecessor's direct-sum example `diag(3,5)` is credited and is not our result.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/tensor-helper-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/tensor-helper-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/tensor-helper-capacity --check-source-history
```

Use any CPython 3.12 interpreter in place of that local absolute path. Both
registered normal and optimized commands must print `PASS_TENSOR_HELPER_CAPACITY`;
the launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier emits
a generated JSON receipt with counts and SHA256 of all six package source files.
It writes no files and needs no Git, network or predecessor package at runtime.

The complete ordered-pair census uses all 2-by-2 matrices over entry alphabets
{0,1,3} and {0,1,5}. A determinant-ideal oracle independently computes capacity
of every 4-by-4 tensor; field elimination computes the predicted profile. The
extremizer checks construct actual unit blocks for both sharp bounds. Separate
rectangular, oblique dyadic, zero-capacity and deliberately false rules test
the boundary. Exact executed counts and local timings are recorded in the PR.
The all-size theorem rests on the written proof, not finite extrapolation.

## Scope and relevance

This is a changed-scope side result under `scalar-to-moment`, prompted by the
current legal-helper-splitting priority and #5615. It identifies an algebraic
condition to examine before multiplying capacities of separately normalized
cuts. A physical tensor cut, simultaneous timing, saturated eligible modules,
common charts and sufficient carriers are additional hypotheses. Basis work,
coefficient growth, native execution, dirty restoration, storage and complete
paid/target invoices remain unpriced. No selected replay, compiler/outer
admission or complete multiplication theorem is supplied. Independent human
and formal proof-kernel review are unclaimed.

Base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The selected source-binding orientation passed. The live open PR/discussion
cache had complete remote pagination, but its sparse local note inventory was
incomplete. Separate all-main README and merged-PR searches addressed the
composition terms; this bounded overlap check does not establish global novelty.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214979).

## Implementation bounds

The minor oracle accepts at most 4-by-4 matrices. Field elimination and tensor
helpers have at most 32 rows/columns at their checked entry points. Executed
extremizers have at most 12 diagonal entries and at most three factors. All
censuses are fixed finite products. The Euclidean routine has a 1,024-step cap
and a checked Bezout identity. Every mathematical check remains active under
`-O`; malformed inputs and corrupted endpoints must reject.

Power of Ten rule 3 deviation: CPython and Fraction allocate during evaluation.
This finite verifier uses fixed census sizes, matrices of bounded dimension and
bounded input bit sizes; it has no service loop or external resource ownership.
Rules 8 and 9 use ordinary Python iteration and standard-library arithmetic,
with no dynamic evaluation or generated code. Warning-strict normal/optimized
replays are the recurring diagnostics. Reassess capacities before widening a
census; the finite implementation does not implement arbitrary-size Smith form.

## Open next questions

1. Can a named physical pair of helper cuts realize the tensor eligible modules
   with complementary odd-prime losses? First exhibit its complete prefix,
   suffix, saturated bases and carrier/timing contract. A static tensor matrix
   is insufficient; physical delivery and restoration are blockers.
2. What is the least complete basis-operation bill for the displayed two-channel
   example in an admissible caller? First compile its explicit X,Y with bounded
   coefficients and include all inverse/restoration operations. No free basis
   change or independent-target credit is assumed here.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman #5615 for the
single-cut capacity theorem, #5602/#5609/#5611 for causal pairing and completion,
and #5599 with the retained helper/controller/native lineage. The predecessor
also credits Nick Petalas #5115 for a different Euclidean row preparation.
Smith normal form, Bezout identities and rank multiplicativity are classical.
The claimed addition is the sharp composition result in this interface, not a
new general Smith theorem. Apache-2.0.
