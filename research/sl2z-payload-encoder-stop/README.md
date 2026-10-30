# The one-XOR shear carrier does not encode integer B

**Negative stop on a lossless payload. No new κ.** Selected κ stays
`0.001672660197076918`.

## Question

PR #3905 shows that `B = X²Y²` needs four calls in the formal shear alphabet.
PR #3947 shows that a three-bit quotient sends that same `B` to one XOR,
`b ^= c`, and that this quotient is not a faithful encoding of the integer
matrices. Discussion reply 19032401 asks for the next piece, not another formal
word: name a payload subspace and an injective encoder/decoder/consumer, prove
the commuting diagram, and price conversion, storage, and dirty return.
**Stop if that caller already has the one-XOR endpoint.**

This package answers that stop. It does not redo the faithful-word moment test
`M(a) < 1`.

## Result

Let

```text
X = [[1, 1], [0, 1]],  Y = [[1, 0], [1, 1]],  B = X²Y² = [[5, 2], [2, 1]].
```

`B² − I = [[28, 12], [12, 4]]`. Its only integer kernel vector is `0`, because
`12x + 4y = 0` forces `y = −3x` and then `28x + 12y = −8x = 0`. The gcd of the
four entries is 4, so `B² ≡ I` modulo `M` only for `M` dividing 4.

The projective action of these matrices modulo 3, restricted to the sum-zero
plane in `F₂⁴`, reproduces the published carrier

```text
ρ(B) = [[1, 0, 0], [0, 1, 1], [0, 0, 1]],
```

which is `b ^= c` on column vectors and has order 2. `ρ(X³) = I` while
`X³ = [[1, 3], [0, 1]] ≠ I`, so the carrier is not an injective encoding of
the integer generators.

**Integer payload.** A map of order 2 cannot intertwine with `B` on a
`B`-invariant subset `S ⊆ ℤ²` through an injective encoder, except `S ⊆ {0}`.
One use of the 3-bit block distinguishes at most 8 payloads, and one use of
the 6-bit two-block caller at most 64. The box `{0, …, 2ᵐ − 1}²` exceeds 8
states at `m ≥ 2` and exceeds 64 states at `m ≥ 4`. Under the identity 4-bit
packing, `(1, 0) ↦ (5, 2)` has Hamming distance 2, so it is not one XOR.

**Mod-4 quotient.** This is the largest modulus on which `B² = I`. The action
has 4 fixed points and 6 transpositions, which would fit the cycle type of the
6-bit caller as a lookup. No wiring does so: every placement of the four
address bits into `(a, b, c, p, q, r)`, with the other two bits constant,
fails to realize `B` mod 4 after `b ^= c`. The Boolean map itself is the
linear circuit

```text
(x0, x1, y0, y1) ↦ (x0, x1 XOR y0, y0, x0 XOR y1)
```

with **two XORs**, no AND, and no use of the carrier. Those two output parities
use disjoint inputs, so two XORs is the XOR count of this circuit. Routing the
same map through the carrier cannot undercut a circuit that does not need that
extra XOR.

**Exact legal caller.** On an `m`-bit nonnegative address, `Y, Y, X, X`
overwrites the pair by `B`. Each step is one integer addition. A fixed
full-adder of `W` bits, final carry required to be 0, costs `2W` XOR, `2W`
AND and `W` OR. The four widths are `m+1`, `m+2`, `m+2` and `m+3`, so the bill
is

```text
XOR = 8m + 16,   AND = 8m + 16,   OR = 4m + 8.
```

The input address is consumed. Restoring it costs a clean copy, `2m` further
XORs, and `2m` stored bits. The adder carry returns to 0. There is no spectator
role in this address model. For `m = 4` the consuming bill is 48 XOR, 48 AND
and 24 OR, against one incorrect carrier XOR.

Checked for every pair at `m = 1..5`, and at the `m = 8` corner
`(255, 255)`.

## What this does not claim

No supplier, no group-algebra register, no selected cold replay, and no κ.
The mod-4 two-XOR circuit is a quotient, not an implementation of integer `B`.
A lookup table whose cycle type embeds into the 6-bit caller is not a legal
free conversion. Unknown gate-sharing across a different alphabet is not priced
as zero.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/sl2z-payload-encoder-stop
```

Expected first line:

```text
PASS_SL2Z_PAYLOAD_ENCODER_STOP ... wiring_hits=0 mod4_direct_xor=2 ... no_new_kappa=true
```

Standard library only. Base `bb4bccbf42844d2801487450727c2f63e10d1d0f`.
Priority revision 6.

## Open next questions

Can the low two bits of an exact `m`-bit address use the mod-4 two-XOR map
while a carry into the high half replaces one of the four additions? The first
step is one shear's high-half recurrence on a single `m = 4` witness. It is
blocked if that carry is itself an addition: the split then does not beat
`8m + 16` XORs plus the matching ANDs and ORs.

## Credit

PR #3905 (1337isnot1337 / OpenAI Codex) for the integer shear target and the
four-call formal minimum. PR #3937 and PR #3947 (ToikY / OpenAI Codex) for the
commutative obstruction, the three-bit carrier, the one-XOR invoice, and the
payload question in discussion reply 19032401. The kernel argument, the wiring
exhaustion, the two-XOR quotient circuit, and the fixed-width adder bill are
new here.

Prepared by unpaidmoon with substantial Cursor Grok 4.7 assistance. Apache-2.0.
