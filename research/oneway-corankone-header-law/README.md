# Exact full-guard law for a one-way coupled pair

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: **scoped counting proof with finite corroboration**. Let U,V
be rank-one idempotents over F_q^m with UV nonzero and VU=0. Both
corank-one requests P=I-U and Q=I-V use one equally weighted complete
GL_m header. A request passes when every leading principal minor through
its rank is nonzero. These requests do not commute.

[PROOF.md](PROOF.md) proves an exact all-field transfer with
q^2(q-1)^2 states. Over F2, for every m>=2, its closed form is

```text
Pr(P and Q pass) = (9^(m-1)-5^(m-1))
                  / [4(2^m-1)(2^m-2)2^(2m-4)].
```

The fractions at m=2,3,4 are 1/6, 1/12 and 151/3360. This strictly
exceeds the orthogonal-kernel density of
[#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261) in every
dimension, by (7^(m-1)-5^(m-1))/(2D), with
D=(2^m-1)(2^m-2)2^(2m-4). Both passing events are still strictly
negatively correlated. Their joint fraction is asymptotic to
(1/4)(9/16)^(m-1); its ratio to the product of marginals tends to one.

The changed premise is one-way coupling of the kernel projectors. This
answers a higher-rank subcase of the nonorthogonal full-guard question in
[#4240](https://github.com/CrocSwap/integer-mult-bounds/pull/4240).
The new step normalizes the partial-Gram endpoint to [[1,1],[0,1]] and
extracts the changed binary walk endpoint. It is original counting work,
not an audit of the cited packages. No new kappa or supplier admission.

## Reproduction and evidence

From the repository root, with any CPython 3.12 replacing this local path:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/oneway-corankone-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/oneway-corankone-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/oneway-corankone-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/oneway-corankone-header-law --check-source-history
```

The scientific marker is `PASS_ONEWAY_CORANKONE_HEADER_LAW`. Its generated
stdout JSON records each exact count and SHA256 bindings for every package
file and both live inputs. No stored or handwritten receipt is used. The
verifier authenticates inputs before enumeration and writes no files.

The complete bounded replay checks:

- **32,094 complete GL headers** over F2 at m=2,3,4; F3 at m=2,3;
  and F5 at m=2. Generic matrix conjugation and literal no-pivot
  elimination test both full guard chains. Every normalized-pair fiber
  is counted and checked to have the same size.
- **1,946,574 normalized pairs X,Y with YX=[[1,1],[0,1]]**, separately
  enumerated over F2 at m=2..6, F3 at m=2..4 and F5 at m=2,3. Every
  joint fraction matches the transfer and every marginal matches the
  cited #4227/#4228 corank-one formula.
- **84 transfer cases**, over F2 at m=2..64 and F3,F5,F7 at m=2..8.
  All 63 binary counts match the closed form and strict gain/correlation
  identities. Rank-one factor multiplicities are independently enumerated
  over all four fields.
- Five controls distinguish the orthogonal endpoint, wrong binary parity,
  a lost zero-factor multiplicity, independent marginals and first-pivot-only
  admission. At q=2,m=3, first-only admission accepts 66 headers while
  full admission accepts 14, out of 168.

Both normal and optimized Python execute explicit checks, so `-O` does not
remove them. The finite counts corroborate the written all-parameter proof.

## Scope and remaining obligations

The transfer applies to every finite field. Executed arithmetic uses only
F2,F3,F5,F7; extension-field execution is unrun. Only F2 has a closed form
here. The theorem requires fixed one-way coupled kernels and complete,
equally weighted headers. It says nothing about arbitrary restricted covers,
local rings, coincident image/kernel types or pairs with both products nonzero.

Binary guards extend beyond the retained normalizer's odd-prime executable
domain. Even in odd characteristic, no real producer, header selection or
emission, dispatch, dirty return, stock, precision or complete physical invoice
is supplied. Those costs are unknown. No selected cold replay, GL64 scan,
Lean or Docker run was performed. No complete multiplication theorem is
claimed. Independent human and formal proof-kernel review are unclaimed.

The executable loops have bounded domains, with no recursion. The largest
transfer has 1,764 states and at most 679,140 candidate transitions; each
normalized census uses at most 125 vectors, at most 125^2 candidate X
choices and at most 125 candidate rows per X. Accepted row-fiber pairs
have at most 16^2 combinations. Direct GL censuses visit at most 65,536
candidate matrices, of dimension at most four; factor vectors have length
at most six.
CPython's dynamic integers and containers are a managed-runtime deviation
from fixed allocation, constrained here by these explicit finite domains.
All functions stay below 60 lines. Registered diagnostics use warnings as
errors in normal and optimized modes. No standalone Ruff executable was
available; local AST inspection checks syntax and function sizes.

## Related open work and credit

- [#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261), head
  `4728fc766b3084f3ab2f5c8543a5e74e4a12b126`, supplies the orthogonal-kernel
  partial-Gram method. The new numerator is strictly larger in all 63 binary
  replay dimensions. Its m=3 density 1/84 differs from the new 1/12, as the
  changed premise predicts; no same-type joint number is shared.
- [#4240](https://github.com/CrocSwap/integer-mult-bounds/pull/4240), head
  `9f9c89ed75e9fdae6b6762925b080fb308824858`, supplies the one-sided
  rank-one classification. At m=2 our requests have that type. Its joint
  fractions for q=2,3,5,7 agree numerically with this transfer, respectively
  1/6, 1/4, 13/30 and 31/56. This adds the full chain at m>2.
- [#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227), head
  `3d793eade8de2ba49ec08f8d004c1b2f566a78e6`, supplies the determinant
  reduction and marginal law. All ten marginal census fractions agree
  numerically; the joint one-way law is new.
- [#4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228), head
  `bb25dcedb5bbbacd3c35359eb6b5488b087bcde6`, supplies all-rank marginal
  densities. Its corank-one specialization agrees on those same ten cases;
  no intermediate-rank recurrence is imported.
- [#4239](https://github.com/CrocSwap/integer-mult-bounds/pull/4239), head
  `5e24dfb5463d540721687d92c369609da5589523`, counts orthogonal rank-one
  requests. The one-way requests here share no joint type with that theorem,
  including at m=2, so no overlapping joint number is asserted.
- [#4246](https://github.com/CrocSwap/integer-mult-bounds/pull/4246), head
  `a2d99d73bf21b39fbb0a9a88917424ff26c2e63c`, counts orthogonal full chains.
  Our noncommuting pair is outside that hypothesis; no joint number is shared.
- [#4259](https://github.com/CrocSwap/integer-mult-bounds/pull/4259), head
  `2a582d8f66d1900b22ee2cd0062ee5dca94e8f85`, counts laminar full chains.
  Our pair is neither contained nor orthogonal; no joint number is shared.
- [#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) supplies
  the BIT request and complete-header context. Its actual caller costs and
  multiplication claim are outside this package; no recursive bill is compared.

All the preceding counting packages were produced by Nick Petalas. Source527,
commdata2338 and Jose Manuel retain the normalizer and recursive-closure
credit. Cinna Davis supplies BIT.md. Chris R / Clear1nsight's #3950 is earlier
deterministic counting context. The proof and enumerators are self-contained;
no unmerged source code or unavailable Git-history object is imported.
SOURCES.json pins the two retained main-branch contract files, base and card.

## Open next questions

1. What is the full-guard law when both UV and VU are nonzero? Start with
   endpoint [[1,a],[b,1]], separating invertible endpoints from ab=1.
   The singular endpoint needs extra image/covector-rank filters to identify
   the intended simultaneous-conjugacy orbit.
2. Can an actual odd-field producer use a fully charged one-way shared-header
   caller? Pin its kernel lines and charge selection, emission, dispatch,
   dirty restoration and stock. No producer or complete invoice is supplied.

The active ternary orthogonal-pair and three-orthogonal-kernel claims in the
[handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
change the field or number of orthogonal kernels. They are separate from this
changed-coupling question. [TASK.json](TASK.json) records scope and provenance.
