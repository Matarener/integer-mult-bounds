# Least actual-body borrowing on Count tapes

This closes the encoded-selector and setup-invoice part of [PR3486's
handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19010306)
at `991861d40a1ebdbbf35be9adc1726e6af5b71e49`. The predecessor proves the
threshold with host integers; this package computes it using the retained
binary Count tapes and fixed physical roles. It is an opt-in setup component,
not a selected supplier, default-backend change or new multiplication bound.

## Result

For compiled radix/profile constants, fix the atom width
`w=ceil(e^(A/C))` before borrowing. The selector returns the least `k` with

```
2*k < e,
n = floor((e-k)/w) >= m,
q^k >= S_D(n),
D(n) = 0 if n<m, otherwise 1+D(r*floor(n/m)),
S_0 = 1, S_d = Q * (W*|GL_m(F_q)|*q^(m*m*(w-1)))^d for d>0.
```

`selector.select_body_stock` uses encoded bisection, actual-body depth at
every trial, and MSB-scanned Count exponentiation. It accepts the same compiled
profile vocabulary and returns the seven owned Count fields plus `fits` used
by the existing ordinary plan hook. No host-decoded input or input-dependent
depth table is used. On no fit, `width` is retained, `depth/borrowed/body/remainder`
are zero and `stock/rows` are one; these are explicitly nonadmitted sentinels.
The caller must close every plan with `close_plan`.

For `h=1+ceil(log2(e+1))`, the complete setup invoice is

```
time  O(h^3 + h^2*(e+w*h)^2),
space O(e+w*h), on at most 24 roles including the borrowed input.
```

Constants depend on the compiled radix/profile. This includes width selection,
level construction, discarded trials, **full** trial radix powers, final-plan
recomputation and cleanup. It fits within the inherited 64-role setup allowance.
For the selected fixed exponent `17/10000`, the time is `O(e^2*h^2+h^3)`.
The relation `e=O_q(log V)` makes this a fixed polynomial setup addition to the
inherited full payload bill. These are conditional tape-operation bounds, not
measured performance or a new universal physical compiler proof.

## Discriminating examples

Use `q=2,m=2,r=1,W=Q=1,w=1`:

| Original width | Exact decision | What it checks |
| --- | --- | --- |
| 12 | No fit | `k=6` covers the stock but violates strict `2k<e`. |
| 13 | `k=6,n=7,D=2,S=36,R=64` | Actual-body depth fits where the old `D(e)` choice needs `k=8` and fails. |
| 24 | `k=9,n=15,D=3,S=216,R=512` | Required-stock substitution cycles `8 → 11 → 8`; the least admitted `k` exceeds its own required digit count of 8. |

With width exponent `1/3`, `e=61` gives `w=4,k=30,n=7,remainder=3`.
The literal tape tests also cross the ceiling-width boundaries `8/9` and
`64/65`. These are reduced setup examples, not selected GL64 payload runs.

## Verification and scope

```sh
python3.12 -B scripts/research_package.py --package research/encoded-body-depth-borrowing
python3.12 -I -O -B research/encoded-body-depth-borrowing/verify.py
```

The standard-library replay authenticates 20 unchanged source inputs and the
retained PR3486 proof. Runtime uses the predecessor's already-archived tape
vocabulary; no executable or Git object from pending PR3486 is needed.
`verify.py --emit` prints the deterministic receipt without overwriting it.

- **171 literal Count cases**, 84 fitted, match independently written forward
  enumeration and inverse-depth slab specifications. Physical constructors and
  numerical decoding are disabled during selection. Borrowed inputs return
  unchanged at their origin; all temporary/result leases close.
- The independent integer methods agree on **5,760 cases**. All 1,139 admitted
  plans satisfy the padded quotient and compatibility guards at every depth.
- Twelve controls cover invalid contracts, zero input, a semantic failure after
  complete trial construction, and executed mutants using old depth, omitting
  Q, weakening strict fit, using the wrong radix exponent or returning the false
  bisection endpoint. The five algorithm mutants reach the semantic oracle.
- The observed peak is **19 setup roles**; the written 24-role bound comes from
  a separate inventory of allocation sites, including constructor temporaries.

The first literal replay exposed a scan-origin bug in the new exponentiation;
the fixed code moves right from `LEFT` before using the retained rewind loop.
The published tests exercise this path. Successful, fallback and the tested
semantic-failure cleanup are covered; arbitrary interruption or allocation
failure inside inherited arithmetic is not a transactional guarantee.

The optimality, stock and inverse-depth theorems remain PR3486's results.
[PROOF.md](PROOF.md) establishes their encoded refinement and setup invoice.
It retains the NODE-guard covering constraint, fixed width, completed-callee,
pointwise restoration, source, ordinary/C0 physical and uniform-cost premises.
The simultaneous full-depth-format consumer needs its separate stronger
contract. All children, helpers, padding, routing and consumer costs remain.
No selected payload, full cold replay, human review or proof kernel is claimed.

## Open next questions

1. Bind this plan factory to one fully specified reduced completed ordinary
   caller, checking both padded returns, all dirty spectators and fallback.
   Start at the existing `execute_plan` hook; its physical caller contract must
   be explicit. This package verifies setup and does not execute that payload.
2. Can exact saturation reduce rejected-trial radix-power work? Start by capping
   the comparison at the actual stock, proving the same threshold, and retaining
   full materialization for the accepted plan. No faster implementation is
   established here.

## Attribution and coordination

Hiroki Kumazaki with substantial OpenAI Codex assistance for analysis, code,
execution, writing and separate same-session AI-agent checks. Apache-2.0.
Credit Nick Petalas (PR3486 threshold and PR3246 one-factor reserve), Tekalign
(PR3264 consumer), Jose Manuel (PR2899/2809 encoded arithmetic and physical
setup), David Arias (PR2753 recursive caller), Ross Richardson (PR2420 format
contract), and their retained BIT/geometry/compiler lineage. The byte-identical
predecessor proof retains its source, hash and author attribution in SOURCES.json.

Base: canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6. This changes the `selected-stock-envelope` card to the live encoded
implementation handoff. Entry overlap covered 410 open PRs and 2,332 Discussion
records with complete pagination, plus focused current-thread checks; it excludes
unpublished work and exhaustive historical diffs. [Canonical claim/result](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19010614).

The publication refresh also found the concurrent [factor-two padding
claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19010608).
That work changes the covering premise to permit `S/2<R<S` and explicitly stops
before a full encoded borrowing selector. This package keeps `R>=S` and supplies
that selector only for the existing covering contract; no result is transferred
between the two admission predicates.
