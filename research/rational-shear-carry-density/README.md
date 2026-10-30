# Exact nonzero-carry frequency for rational shears

For a nonzero reduced coefficient `a/h`, canonical low digits `x,y` in
`{0,...,q-1}`, and `gcd(h,q)=1`, the exact zero-carry count is

```text
A = |a|, H = max(A,h), m = floor((q-1)/H)
Z = (m+1)q - A*m*(m+1)/2
nonzero exact carries = q^2 - Z
```

This is a scoped written proof with finite corroboration. Both coefficient
signs have the same count. For `q>=|a|+h` and every width `w>=2`, the formula
also counts nonidentity high-digit translations. Smaller radices can have
nonzero exact carries whose high residues vanish; an explicit example and
the separate prime-field `GL_n` law are in [PROOF.md](PROOF.md).

The limiting nonzero proportions for coefficients `1`, `1/2` and `1/4` are
`1/2`, `5/8` and `25/32`. For `1/2^s` the limit increases strictly to one
as `s` grows. Smaller coefficient magnitude alone therefore does not establish
sparser carries. This is a new per-input count, building on Ali Romman's
[#5841](https://github.com/CrocSwap/integer-mult-bounds/pull/5841) carry
contract and its explicit allowance for zero corrections at particular inputs.
No predecessor verifier is imported or replayed.

The helper-contract card is changed to this local carry-sparsity question.
Exact uniform frequencies need a priced skipping or amortization argument
before they can reduce a worst-case supplier invoice. This package does not
supply that program, a complete G20 route, a physical caller, a new kappa or a
complete multiplication theorem. The selected frontier and its five framework
assumptions retain their previous status.

## Evidence and reproduction

From the repository root, with CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -X dev -W error -B research/rational-shear-carry-density/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rational-shear-carry-density/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rational-shear-carry-density
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rational-shear-carry-density --check-source-history
```

An equivalent CPython 3.12 path works. The direct verifier prints
`PASS_RATIONAL_SHEAR_CARRY_DENSITY` inside a generated JSON receipt bound to
every package file's SHA256. It never writes a receipt or bytecode cache.
Both registered commands run the same coverage under normal and optimized
Python. Explicit exceptions enforce acceptance in both modes.

The finite checker enumerates 3,848 scalar fixtures and all 1,353,470 low
pairs in those domains. It compares 168,044 full-width low-pair cases with a
separate direct modular product, including small-radix cancellation, and
checks 14,176 arbitrary-high inputs. The matrix oracle enumerates all 23,318
matrices in its six domains, including 13,950 invertible matrices, and checks
104 coefficient/domain combinations. The domains are `GL_2` at primes
2, 3, 5 and 7, and `GL_3` at primes 2 and 3. Five exact limiting fixtures,
sixteen dyadic monotonicity cases, thirteen invalid-input rejections and three
semantic separating controls are also checked. These finite domains corroborate
the written proof; they do not replace its universal quantifiers.

[SOURCES.json](SOURCES.json) pins the historical catalogue and selected record
in reachable base history. It also records the original head, Git blobs and
SHA256 hashes for two unchanged source documents retained under `inputs/`.
Those documents preserve attribution and the precise question boundary. No
pending predecessor Git object or external package is needed for replay.
[TASK.json](TASK.json) records scope, environment and structured next questions.

## Implementation limits

The public count evaluator rejects coefficient components above `2^16` and radices
above `2^127-1`. These are checker bounds, not theorem restrictions. The
enumeration domains are fixed in the source. There is no recursion, subprocess,
network access, mutable global state or search that stops on a hoped-for answer.
Every function is shorter than sixty lines. All arithmetic is exact.

Power-of-Ten rule 3 requires a managed-runtime deviation for Python's integer,
tuple and dictionary allocations. Only bounded finite menus and matrix sizes
are kept live; matrix enumeration streams its candidates, retaining at most
`q^2` counters with `q<=7`. Scalar enumeration keeps constant-size state, and
the evaluator's public numeric limits bound integer sizes. The fixed package
has eight files; its receipt rejects an inventory exceeding sixteen. A native
fixed-capacity implementation is the follow-up if the checker becomes a
runtime component. Warning-strict normal and optimized replay, AST parsing and
compilation are the available diagnostics; no repository-wide diagnostic
configuration is changed.

No selected cold replay, source native/tape suite, formal proof-kernel run,
physical skipping implementation or complete supplier admission is performed.
Independent human review is unclaimed.

## Open next questions

1. Can a legal zero-carry branch beat unconditional translation after its
   predicate, retained cache and erasure are paid? Start with one released
   quarter-shear leaf and the literal tape interface. The missing branch
   implementation and amortization contract prevent a supplier-cost claim.
2. What is the joint zero-carry count for one complete fused route? Begin with
   one exact two-coordinate restriction in #5841. Correlated coordinates and
   multiple coefficients prevent multiplication of these one-shear marginals.

## Credit

The new proof, count and verifier were produced by Nick Petalas. Credit Ali
Romman #5841 for the fused carry contract and per-input boundary, Nick Petalas's
earlier elementary carry identity, ToikY #5801/#5805, Tekalign #3343/#4000,
JoyboyBrian and all retained G20/native/ROW contributors. Their unchanged source
notices remain in `inputs/`. Arithmetic progressions and uniform general linear
group row counting are classical. Apache-2.0. Independent human and formal
proof-kernel review are unclaimed.
