# One clean helper does not lower the bank-exchange floor

This result was produced by Nick Petalas. It is an exact finite certificate
with a written reduction to a scalar circuit problem. Independent human and
formal proof-kernel review are unclaimed.

## Statement and changed premise

Let `a0,a1,b0,b1` be independent inputs over F2 and let `z=0` initially.
A paid ADD replaces one of these five wires by its XOR with a distinct wire.
Every one of the twenty ordered directions is allowed. A word is finite,
straight-line and independent of the input values. No other operation is
allowed, including reset, overwrite, free permutation or intermediate basis
change. The final helper must be zero for every data input.

For any `A,B in GL(2,F2)`, the requested data endpoint is

```text
(a', b') = (A b, B a),       z' = 0.
```

Every such word needs at least six ADDs. Two endpoint choices attain six,
so the minimum over the allowed endpoint bases is exactly six.
This does not determine every endpoint's exact length above that floor.

Charan .'s [PR #5851](https://github.com/CrocSwap/integer-mult-bounds/pull/5851)
proves the corresponding no-scratch floor. Its exact source head is
`c698080add27ea02f62da393f27f05c537558ff8`. That package explicitly excludes
added scratch. The new claim grants one zero helper and all incident ADDs.
The predecessor result and its complete distance census are cited, not
replayed or used to prove this stronger finite statement.

## Exact state reduction

Represent each live wire by its four coefficients on the independent data
inputs. The initial five rows are `(1,2,4,8,0)`, with bit `i` denoting input
`i`. The matrix is five by four, rather than a five-by-five identity: its last
input is fixed to zero, and must not be treated as independent dirt.
An ADD XORs the source row into the destination row. This description is
exact by induction on the word, including every use of the helper.

The two nonzero rows of an invertible binary two-by-two matrix are any
ordered pair of distinct elements of `{1,2,3}`. There are six choices per
bank, hence exactly 36 target coefficient states

```text
(4u, 4v, w, x, 0),
u,v,w,x in {1,2,3}, u != v, w != x.
```

Here `4u` means an ordinary integer left shift by two in the row encoding.
Independent invertible entrance and exit bases within the two banks give
exactly this endpoint class. All instructions realizing the endpoint remain
paid. A choice of endpoint does not grant free basis changes during the word.

## Complete exclusion of length at most five

Let `Ball_r(q)` be the set of coefficient states obtained from `q` by at
most `r` ADDs. Every ADD is its own inverse. Therefore a word of length at
most five from the initial state `s` to a target `t` exists if and only if

```text
Ball_2(s) intersects Ball_3(t).
```

For the forward implication, split after at most two instructions. The
remaining suffix has length at most three, and its reverse reaches the split
state from `t`. The reverse implication concatenates the prefix and reversed
suffix. Shorter words are included throughout.

The generated certificate and independent checker establish the following
finite facts. Forward distance layers are `1,16,166`, totaling 183 states.
For each of the 36 targets, backward distance layers are `1,16,166,1302`,
totaling 1,485 states. Every one of the 36 intersections is empty. The
53,460 backward states counted over targets need not be distinct across
targets; no union cardinality is claimed.

`generate.py` builds the coefficient-state balls by breadth-first layers.
It emits their sorted-state SHA256 digests, counts and two attaining words.
`verify.py` imports no generator code. It evaluates wires on every one of
the sixteen data assignments, stores five literal sixteen-bit truth tables,
and enumerates all padded words of lengths two and three directly. The
padding symbol does nothing and only includes shorter paid words. It is
not a free data operation. There are `21^2=441` padded prefix words and
`36*21^3=333396` padded backward words for the main exclusion.
The checker reconstructs every digested state set and checks disjointness.
Hashes bind the certificate; exact enumeration supplies the exclusion.

This is a complete exclusion in the finite stated circuit model, rather
than a heuristic search failure. It remains a computational certificate,
not a proof-assistant theorem.

## Attainment and vector inputs

For each pair of distinct wires `(i,j)`, the three ADDs

```text
i += j;  j += i;  i += j
```

swap their arbitrary initial values. Swapping `(0,2)` and `(1,3)` attains
`A=B=I`. Swapping `(0,3)` and `(1,2)` attains the crossed orientation in
both banks. Both words have six instructions and leave the helper untouched.
The verifier checks both complete truth tables and helper restoration.
The swap identity is standard and is not claimed as new.

The same identities apply coordinatewise to arbitrary equal-length vectors
over F2, with one full vector ADD as the unit operation. A universal shorter
word would in particular work on one-bit inputs, contradicting the finite
exclusion. The same floor also holds for an arbitrarily dirty restored
helper: specialize its initial contents to zero. The attaining words already
leave every possible helper value untouched.

## Source relevance and limitations

Ali Romman's [PR #5840](https://github.com/CrocSwap/integer-mult-bounds/pull/5840),
head `6a043d0fc0199ee5b24c61f883f1943eaf6424be`, supplies the G20 bank-boundary
construction and general-basis question. Under #5851's retained decomposition
into fixed chain instructions and isolated four-wire exchange components,
granting one private clean helper to a component cannot reduce its six-ADD
floor. That conditional application uses the cited source decomposition;
the actual controller is not imported or independently replayed here.

Two or more helpers, cross-component gates, sharing with the chain, changed
tariffs, nonlinear operations, data-dependent control, and a nonrestored helper
are outside this certificate. There is no global boundary minimum, native
implementation, physical supplier admission or new kappa. Initialization,
ownership, movement and all other physical helper costs are unpriced here;
granting the clean helper at no extra charge favors a proposed improvement.
Any complete implementation must pay those costs as well as every ADD.
The five selected framework assumptions and selected frontier are unchanged.

## Verifier bounds

All enumeration loops have fixed finite bounds. The largest direct word set
has at most 9,261 entries and each state uses at most eighty bits. Only one
target's balls are live during the main exclusion. Certificate input is capped
at 64 KiB, the endpoint inventory at 36 and each attainment at six ADDs.
Functions stay below sixty lines. Explicit exceptions preserve checks under
optimization. There is no recursion, subprocess, network, runtime code
generation or mutable external state in the direct verifier.

Python integers, sets and JSON require managed allocation. The fixed domains
bound it; no allocation-free execution is claimed. Seven explicit mutations
exercise certificate rejection, without callbacks or input-selected code.
Warning-strict normal and optimized
replays provide the available interpreted-language diagnostics. No global
lint configuration or unrelated source is changed.
