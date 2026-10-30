# Full side rank for the four-subset decoder

For every odd n >= 5, the complementary four-subset kernel
K(S,T)=binomial(|S intersection T|/2,2) has invertible side map I-K over Q.
At n=9 its ranks are rank(K)=36 and rank(I-K)=126. The
[proof](PROOF.md) gives the complete spectrum for every n and a sharp
algebraic consequence: implementing the whole side response through scalar
linear intermediates, with no direct source-to-output bypass, needs at least
binomial(n,4) intermediates. This is a scoped proof, not a physical tariff or
a new kappa.

This takes a partial step on Cinna Davis / 1337isnot1337's
[PR #2225](https://github.com/CrocSwap/integer-mult-bounds/pull/2225), which
leaves the side map open. It derives a new side-map obstruction from that
kernel's definition. It does not audit the predecessor's fitting theorem,
feature supports or numbers. A direct identity contribution plus a compressed
-K correction remains outside this obstruction and may still help a circuit.

Ali Romman's merged [PR #5458](https://github.com/CrocSwap/integer-mult-bounds/pull/5458)
studies the cube restriction of the same kernel and separate binary endpoint
hulls. Here the port set is the entire constant-weight shell, with 126 ports
at n=9, and the conclusion is its full side-map spectrum. Full-rank
compensation in other geometries is also prior work, including Dominik
Scholz's [PR #606](https://github.com/CrocSwap/integer-mult-bounds/pull/606)
on E8 squared. This package claims the four-subset result, not the general
idea of a compensation-rank obstruction.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/four-subset-side-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/four-subset-side-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-subset-side-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-subset-side-spectrum --check-source-history
```

Another CPython 3.12 path can be substituted. The direct success marker is
`PASS_FOUR_SUBSET_SIDE_SPECTRUM`. The registered launcher must print
`PASS_REGISTERED_RESEARCH_PACKAGE`; the publication check must print
`PASS_RESEARCH_COMMIT_BYTES`.

The read-only verifier reconstructs all 17,126 matrix entries at n=5,7,9
directly from intersections. Exact fraction-free elimination checks all ten
eigenspace dimensions, the three full side ranks and their complete
determinants. Literal incidence counting checks 1,737 pair-Gram entries.
The bounded formula check covers 499 odd n through 1001; it is not the proof
of the unbounded statement. Three malformed spectra are rejected, and an
actual smaller compression has the expected deficient rank. A generated
stdout receipt records results, interpreter version and all six package-file
hashes. No receipt or replay output is written into the checkout.

## Scope and implementation limits

The result is over characteristic zero. It covers k=4, not every even k.
It proves no bound on circuits with retained source access, general dirty
workspace, native queries or paid recursive work. The rank-36 kernel at n=9
does not supply a 36-feature dyadic circuit. Its predecessor's 45-feature
incidence expansion remains credited and unchanged. Physical side construction,
restoration, both native orientations, hosting, precision and the complete
supplier invoice remain open. The selected frontier and its five framework
assumptions are unchanged. No selected cold replay, Lean, Docker, independent
human review or formal proof-kernel review is claimed.

The verifier uses no external runtime inputs. `SOURCES.json` pins the source
definition and task/selected-record provenance through ancestor Git blobs.
The bounded checker uses dynamic Python allocation, a managed-runtime
deviation from Power of Ten's fixed-allocation rule. Its largest dense matrix
is 126 by 126, its incidence list has 36 pairs, and every loop has a finite
bound from the explicit replay domain. Elimination checks every exact division;
exceptions propagate. Warning-strict normal and optimized execution retain
all acceptance checks. There is no recursive or generated executable code.

## Open next questions

- Can a legal direct identity route plus a compressed -K correction implement
  the n=9 side map cheaply? Begin with explicit input/output frames and charge
  arbitrary dirty restoration. This theorem does not exclude that route.
- For another even k, when is one an eigenvalue of the complementary-subset
  kernel? Derive its incidence action before inferring any physical invoice.

## Credit and coordination

This contribution was produced by Nick Petalas. Cinna Davis supplies the
kernel definition, dyadic fitting construction, support theorem and open
side-map question in PR #2225. The source retains the Zhihao Chen subset and
compiler ancestry. Incidence decomposition and rank bounds for products are
classical; the contribution is this exact spectrum and its scoped side-map
consequence.

Base: `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228386)
records the scope. The initial P104-oriented selection changed to this
specific decoder-side obligation. Main, merged PRs, open PRs, this account's
recent contributions and active claims were searched. The cached open snapshot
covered 393 PRs and complete Discussion pagination; sparse local note coverage
was incomplete. The relevant source was materialized and main was searched
through Git. No matching side-spectrum result was found in that coverage;
unpublished work remains outside it.
