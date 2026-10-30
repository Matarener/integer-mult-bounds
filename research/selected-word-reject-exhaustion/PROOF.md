# Selected-word reject exhaustiveness for length-≤2 dest-in divergence

## Claim

Fix the pinned tuned PR589 word
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz` and the B[0]
destination `d = 111` (source alphabet size `n = 2v+R = 661`). Compare Sym
(accumulate-XOR from the pre-gate valuation) with Exp (sequential ADD into the
destination, re-reading the current valuation), as linear maps over `F_2`.

1. **Closed form.** For every finite source list `srcs`, Sym and Exp agree if
   and only if either `d ∉ srcs`, or else `count(d)` is odd and every non-`d`
   value has even multiplicity in the strict prefix before the last occurrence
   of `d`.
2. **Length-≤2 census.** Among all `srcs` of length at most 2 with entries in
   `{0,...,660}`, Sym≠Exp on exactly **661** lists: `{[d,d]} ∪ {[a,d] : a ≠ d}`.
3. **Four named rejects are not exhaustive.** The four B[0] checker rejects named
   in [#3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696)
   (`self_even`, `dest_with_src`, `dup_src`, `self_once`) contain only **two**
   of those 661 divergences (`[d,d]` and `[3,d]`). The other two named rejects
   agree under Sym/Exp. Hence the four are not an exhaustive taxonomy of
   length-≤2 dest-in-sources divergence on the pinned word.
4. Every length-≤2 divergence has `d ∈ srcs`, so
   `len(set([d]+srcs)) < len([d]+srcs)` and the selected checker rejects it with
   `bad operands`. Selected kappa is unchanged.

This is not a restatement of the dest-free Sym/Exp agreement already published
in #3696: the new content is the dest-in closed form, the exact length-≤2 count,
and the negative exhaustiveness answer.

## Proof of the closed form

Only register `d` is written. For `s ≠ d`, Exp therefore always reads `val0[s]`.
Reading `s = d` clears the current destination (`out[d] ← out[d] ⊕ out[d] = 0`).

- If `d ∉ srcs`, every Exp read sees `val0`, so Exp equals Sym.
- If `d ∈ srcs`, let `last` be the last index with `srcs[last] = d`. After that
  clear, Exp's destination coefficient is the XOR of the suffix `srcs[last+1:]`
  (which contains no `d`). Sym's destination coefficient is
  `e_d ⊕ ⨁_s e_s` (multiplicity mod 2). These match if and only if the Sym
  coefficient of `d` is `0` — i.e. `count(d)` is odd — and for every `s ≠ d`
  the Sym parity equals the suffix parity, i.e. the multiplicity of `s` in
  `srcs[:last]` is even.

## Proof of the length-≤2 census

Apply the closed form with `len(srcs) ≤ 2`:

- Length 0 or dest-free length 1–2: agree.
- `[d]`: `count(d)=1` odd, empty prefix → agree.
- `[d,d]`: `count(d)=2` even → disagree.
- `[d,a]` with `a ≠ d`: `count(d)=1`, empty prefix → agree.
- `[a,d]` with `a ≠ d`: `count(d)=1`, prefix `[a]` odd → disagree.
- `[a,a]` with `a ≠ d`: dest-free → agree.

Hence the disagreeing lists are exactly the `n` lists `[a,d]` for
`a ∈ {0,...,n-1}` (the case `a = d` is `[d,d]`), totaling `n = 661`. Direct
linear enumeration over all `1 + n + n^2` lists confirms the count.

## Four named rejects

| name | `srcs` | Sym=Exp? | in the 661? |
|---|---|---|---|
| `self_even` | `[111,111]` | no | yes |
| `dest_with_src` | `[3,111]` | no | yes |
| `dup_src` | `[3,3]` | yes | no |
| `self_once` | `[111]` | yes | no |

So at most two of the four meet dest-in divergence, against 661 total. The
checker still rejects all four (and all 661 divergences) by operand
distinctness; reject-count is not divergence-count.

## What this does not claim

- No new kappa and no production schema change.
- No claim that length ≥ 3 has only 661 divergences.
- No dest-absent schema corollary (left to maintainers; forbidden as a
  definitional follow-up in this loop).
- No restatement that dest-free lists always agree beyond using it inside the
  closed form.
