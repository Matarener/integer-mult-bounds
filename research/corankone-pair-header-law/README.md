# Exact full-guard law for an overlapping corank-one pair

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped counting proof with finite corroboration.** Let U,V
be orthogonal rank-one idempotents on F_q^m, m>=2. The requests P=I-U and
Q=I-V commute and have an image intersection of dimension m-2. A complete
header G passes a request when all leading principal minors through its
rank are nonzero. Both requests use the same G.

[PROOF.md](PROOF.md) gives an exact transfer recurrence over every finite
field, with q^2(q-1)^2 states, and this binary closed form for every m>=2:

```text
Pr(P and Q pass) = (9^(m-1) - 2*7^(m-1) + 5^(m-1))
                  / (4(2^m-1)(2^m-2)2^(2m-4)).
```

The binary passing events are strictly negatively correlated. A shared
passing header exists exactly when m>=3. At m=3 the fraction is 1/84,
while the product of the two marginals is (9/28)^2. At m=4 it is 1/80.
The joint fraction is asymptotic to (1/4)(9/16)^(m-1), and its ratio to
the product of the marginals tends to one from below.

This answers one subcase of the nonorthogonal full-guard question in
[#4240](https://github.com/CrocSwap/integer-mult-bounds/pull/4240) and
[#4246](https://github.com/CrocSwap/integer-mult-bounds/pull/4246). The new
part is the joint full-chain count for overlapping images. The rank-one
determinant identity and marginal density are credited to
[#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227).

## Reproduction and evidence

From the repository root, with any CPython 3.12 replacing this local path:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corankone-pair-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/corankone-pair-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-pair-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-pair-header-law --check-source-history
```

The scientific marker is `PASS_CORANKONE_PAIR_HEADER_LAW`. Its generated
JSON contains each census denominator, joint count and single count, plus
SHA-256 hashes of every package file and both declared source inputs.
The verifier checks the source pins before enumeration and writes no files.
There is no handwritten or stored result receipt.

The finite corroboration is:

- **32,274 complete GL headers**, over F_2 at m=2,3,4; F_3 at m=2,3;
  and F_4,F_5 at m=2. Each header is inverted and both conjugated requests
  undergo literal no-pivot elimination. Every normalized-pair fiber is
  enumerated and checked for equal size.
- **2,007,234 normalized pairs X,Y with YX=I_2**, over F_2 at m=2..6;
  F_3 at m=2..4; and F_4,F_5 at m=2,3. These are enumerated separately
  from the matrix headers and transfer recurrence. Every joint and marginal
  fraction is checked. F_4 is F_2[x]/(x^2+x+1), not Z/4Z.
- **99 transfer cases**, over F_2 at m=2..64 and F_3,F_4,F_5,F_7 at
  m=2..10. Every binary case agrees with the closed form. Local rank-one
  factor weights are separately enumerated over all five fields.
- Four controls distinguish the independence product, omitted zero-factor
  multiplicity, the wrong parity target and first-pivot-only admission.
  At q=2,m=3 the last control distinguishes 2 full-guard headers from 54
  headers passing only the first guards, out of 168.

The entire small census is registered in both normal and optimized Python.
The explicit checks remain active under `-O`. Executed checks corroborate
the written universal proof; they do not replace it.

## Scope and remaining obligations

The transfer theorem is for every finite field; the implemented fields and
dimensions are listed above. Only the binary law is simplified to a closed
form. The assumptions are fixed idempotents with orthogonal rank-one kernels
and a complete, equally weighted GL header domain. No density is asserted
for arbitrary restricted header subsets.

The binary case extends the guard algebra outside the retained normalizer's
odd-prime executable domain. Even over odd fields, no real request producer,
header selection/emission, dispatch, dirty return, stock, precision or full
physical invoice is supplied. These costs remain unknown, rather than zero.
No new kappa, selected-frontier change, supplier admission or complete
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed. Selected cold replay, Lean and Docker were not run.

The verifier uses bounded loops without recursion. The largest transfer has
1,764 states and at most 679,140 stored transitions. Matrix dimensions are
at most six in the direct pair census and four in the header census.
CPython dynamically allocates integers, lists and tuples; this is a managed
runtime deviation from fixed allocation, bounded here by the declared finite
domains. Functions stay below 60 lines. Diagnostics use warnings as errors
in both registered modes; Ruff E/F/B/UP is a local static check.

## Related open work and credit

- [#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227), head
  `3d793eade8de2ba49ec08f8d004c1b2f566a78e6`, supplies the corank-one
  determinant identity and marginal count. All 12 marginal fractions in this
  pair census agree numerically with its formula. New here is the joint law.
- [#4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228), head
  `bb25dcedb5bbbacd3c35359eb6b5488b087bcde6`, gives all-rank single-request
  densities. Its corank-one specialization is the same marginal formula,
  numerically checked here in the same 12 cases. Its intermediate-rank
  recurrence is not used or recounted.
- [#4239](https://github.com/CrocSwap/integer-mult-bounds/pull/4239), head
  `5e24dfb5463d540721687d92c369609da5589523`, gives the orthogonal rank-one
  joint law. At m=2 this theorem becomes its two-request case. The five
  transfer fractions q=2,3,4,5,7 agree numerically with
  (q-1)(q-2)/(q(q+1)); for q=3 the value is 1/6.
- [#4240](https://github.com/CrocSwap/integer-mult-bounds/pull/4240), head
  `9f9c89ed75e9fdae6b6762925b080fb308824858`, counts nonorthogonal rank-one
  first guards. This answers a higher-rank full-guard subcase of its first
  open question. Only the m=2 orthogonal boundary overlaps numerically,
  agreeing on the same five values above.
- [#4246](https://github.com/CrocSwap/integer-mult-bounds/pull/4246), head
  `a2d99d73bf21b39fbb0a9a88917424ff26c2e63c`, counts full chains for
  orthogonal requests. P,Q here overlap when m>2, so its stage product
  does not apply. The m=2 rank-(1,1) boundary agrees numerically on the
  same five values. The laminar-family claim in the
  [handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
  concerns nested or orthogonal requests. This pair is neither when m>2;
  no overlapping count beyond the orthogonal m=2 case is asserted.

All five preceding counting packages were produced by Nick Petalas.
The retained normalizer and recursive-closure lineage is due to source527,
commdata2338 and Jose Manuel. Cinna Davis supplied the #4100 BIT.md
per-request accounting context. Chris R / Clear1nsight's #3950 is earlier
deterministic header-counting context. No predecessor credit is changed.
The written proofs here are self-contained; no unmerged predecessor code
or unavailable Git-history object is imported. SOURCES.json pins the two
retained main-branch contract files, base and original task card.

## Open next questions

1. Can the odd-q transfer be reduced to a closed form or a smaller invariant
   state space? Start by quotienting the q=3 transfer while preserving both
   diagonal guard values and rank(I-A). Such a quotient is not proved here.
2. What is the full-guard law for three or more corank-one requests with
   orthogonal rank-one kernels? Start with a 3 by 3 partial Gram matrix at
   q=2,m=3,4. The four-state simplification no longer applies.
3. Can a real odd-field producer use a fully charged shared-header caller?
   Pin its kernel lines and charge selection, emission, dispatch, dirty
   return and stock. A producer and its physical invoice are still missing.
