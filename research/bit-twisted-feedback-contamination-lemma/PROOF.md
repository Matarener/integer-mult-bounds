# Contamination-charge lemma for every word

## Setting

There are `n = H + Y` registers over F2: helpers `0..H-1`, then targets `H..n-1`.
All inputs are dirty. A state is a matrix `M` in `GL_n(F2)`. Row `r` is the
linear form held by register `r`. A gate `(d,s)` means `r[d] ^= r[s]`, with
`d != s` and cost one. It replaces row `d` by row `d` plus row `s`.

`P = P_{H,Y}` is the set of invertible `M` whose helper rows do not depend on
target inputs. These are the block lower-triangular matrices `[[A,0],[C,D]]`.
The restricted alphabet omits feedback gates (a helper destination with a target
source). The restricted gates generate `P`. Every twisted exit
`[[T,0],[K,I_Y]]` lies in `P`. `d_P` is the restricted minimum and `d_full` the
unrestricted minimum, so `d_full <= d_P` on `P`.

## Construction

The construction maintains three objects:

* a permutation `phi` from physical registers to virtual registers;
* an `H x Y` matrix `Z` (the contamination);
* the state `N` of an emitted restricted word.

It starts with `phi = id`, `Z = 0`, `N = I`. Write `c_b` for helper row `b` of
`N` and `t_j` for target row `j`. The invariant is:

> **(INV)** physical register `r` holds virtual content `v_{phi(r)}`, where
> virtual helper `b` holds `c_b + Z_b t` and virtual target `j` holds `t_j`.
> Equivalently, `M = Pi_phi U(Z) N`, with `U(Z) = [[I,Z],[0,I]]` and
> `(Pi_phi X)_r = X_{phi(r)}`.

The invariant fixes a decomposition of the state; `N` itself always lies in `P`.
A physical gate `(d,s)` acts on the virtual contents as the gate
`(phi(d), phi(s))`. Below, `z = Z_a` is a row and `col = Z[:,i]` is a column.
`|.|` counts ones. Each case lists the emitted restricted gates, the update, and
the reason INV still holds.

1. **Virtual feedback** `h_a ^= y_j`. Emit nothing. Set `Z_a += e_j`. Virtual
   helper `a` becomes `c_a + (Z_a + e_j) t`.
2. **Helper mixing** `h_a ^= h_b`. Emit `(a,b)`. Set `Z_a += Z_b`. Helper `a`
   becomes `(c_a + c_b) + (Z_a + Z_b) t`.
3. **Target mixing** `y_i ^= y_j`. Emit `(H+i, H+j)`. Add column `i` of `Z` to
   column `j`. With `t'_i = t_i + t_j`, we have `t_i = t'_i + t'_j`. So
   `Z_b t = Z_b' t'`, where `Z_b'[j] = Z_b[j] + Z_b[i]`.
4. **Read** `y_i ^= h_a` with `z_i = 0`.
   * Emit `(H+i, H+j)` for each `j` in `supp z`, then `(H+i, a)`, then
     `(b, a)` for each `b` in `supp col`. This costs `1 + |z| + |col|`.
   * Set `Z += col z`.
   * The new target is `t'_i = t_i + c_a + z t`. It equals the actual read
     result `t_i + (c_a + z t)`. Because `z_i = 0`, `z t = z t'`, so
     `t_i = t'_i + c_a + z t'`.
   * Substitute this into helper `b`, which holds `c_b + Z_b t`. It becomes
     `(c_b + col_b c_a) + (Z_b + col_b z) t'`. That matches the emitted
     `c_b ^= c_a`.
   * When `z = 0` and `col = 0`, the read is **clean**: it emits only itself.
     Otherwise (`z` or `col` nonzero) the read is **contaminated**.
5. **Singular read** `y_i ^= h_a` with `z_i = 1`.
   * The actual target becomes `t_i + c_a + z t = c_a + z' t`, with
     `z' = z + e_i`. The term `t_i` cancels, so the virtual target block
     loses rank. When `phi` preserves the blocks (for example at the first
     singular read), the physical target-input block of `M` loses rank too,
     and a frame read off `M` alone (helper rows minus a multiple of the
     target rows, which needs an invertible target block) does not exist
     there. Exchanging helper `a` and target `i` keeps INV in every case.
   * Emit `(H+i, H+j)` for each `j` in `supp z'`, then `(H+i, a)`, then
     `(b, a)` for each `b` in `supp col` other than `a`. This costs
     `|z| + |col| - 1`. The new `N` has `t'_i = t_i + c_a + z' t`, so it stays
     in `P`.
   * Exchange the roles of virtual helper `a` and virtual target `i`, so
     `phi <- sigma o phi` with `sigma = (a, H+i)`. Set `Z_a <- z'`, and
     `Z_b <- Z_b + col_b z'` for `b != a`.
   * Check INV. The new virtual target `i` is the unchanged physical content
     of old helper `a`. That content is `c_a + t_i + z' t = t'_i`.
   * The new virtual helper `a` is the read result `c_a + z' t`. Since
     `z'_i = 0`, this equals `c_a + z' t'`.
   * Every other helper `b` held `c_b + col_b t_i + sum_{j != i} Z_b[j] t_j`.
     Substitute `t_i = t'_i + c_a + z' t'`. It becomes
     `(c_b + col_b c_a) + (Z_b + col_b z') t'`.

**End of the word.** Suppose `M_L` is in `P`. Since `N_L` is also in `P`, the
frame `Pi_phi U(Z)` is in `P`. Its helper rows have no target columns.

* A helper row is either `Z_b` (if `phi(r) = b < H`) or `e_j` (if `phi(r)` is
  a target). So `phi` maps helpers to helpers, and `Z = 0`.
* Hence `M_L = Pi_phi N_L`. Fix this by permuting registers inside each block.
  Each transposition is a three-XOR swap, which is a restricted word.
* The number of transpositions is `n - cyc(phi)`.

## Lemma

Let `w` be any word of length `L` whose product `M` lies in `P`. The
construction outputs a restricted word computing exactly `M` with length

`L - f_v + c(w)`, where

`c(w) = sum_{contaminated reads} (|z| + |col|) + sum_{singular reads} (|z| + |col| - 2) + 3 (n - cyc(phi_L))`

Here `f_v` counts virtual feedback gates (case 1). Hence `d_P(M) <= L - f_v + c(w)`.

No step assumes that a target block is invertible. Case 5 is the singular
case. Every term of `c` is nonnegative: in case 5, `|z| >= 1` and `|col| >= 1`.

## Corollaries

1. **Deletion.** Suppose every read is clean (`Z_a = 0` and `Z[:,i] = 0` at
   the read). Then case 5 never occurs, `phi = id`, `f_v` equals the number
   `f` of feedback gates, and `c = 0`. The restricted word is `w` with its
   feedback gates deleted. So `d_P(M) <= L - f`.
2. **Where a gain must come from.** Suppose `d_full(M) < d_P(M)`, and let `w`
   be a minimum unrestricted word for `M`.
   * `w` contains feedback, since otherwise it would be restricted.
   * Its first feedback gate occurs while `Z = 0`, so `phi = id` then. Hence
     `f_v >= 1`.
   * Then `c(w) >= d_P(M) - L + f_v >= 2`. So `w` has a contaminated or
     singular read.
3. If `c(w) <= f_v(w)` for some word `w` of length `L` for `M`, then
   `d_P(M) <= L`.

A singular read can have surcharge `0` (for example `z = e_i`, `col = e_a`).
So `c(w) = 0` does not imply that every read is clean. The converse in
Corollary 1 is what holds.

## Mechanical corroboration

`lemma.py` asserts INV after every gate and the length identity at the end.
`verify.py` checks the following words:

* For every element of every `P_{H,Y}` with `n <= 4`: one BFS-minimum
  unrestricted word and one random-detour word, 6,628 words in total. For each,
  the output reproduces `M` and `d_P(M) <= |output|`.
* 8,400 random words ending in `P` with `n = 2..8`, over every split; half
  are forced to exits `[[T,0],[K,I]]` with random `T`, and 3,998 end at
  twisted exits (`T != I`).
* 2,800 free random words, where only the per-gate invariant is checked.
* Together these words exercise 2,946 words with singular reads, 1,612 words
  with relabel swaps and 4,705 words with contaminated reads.

`numpy_crosscheck.py` runs the construction on one greedy (first-gate) minimum
unrestricted word for each of the 333,712 five-register exits `[[T,0],[K,I]]`
(333,552 twisted plus 160 settled `T = I` shears). In 35 of the 4+1 words the
construction meets a non-clean read, and each has `c = f_v + 1`: the
construction outputs a restricted word of length `L + 1`, so the lemma alone
does not certify those 35 exits. The census does (`d_P = d_full = L`). Which
words are non-clean depends on the greedy choice of minimum word.

As a positive control, `numpy_crosscheck.py` also finds every element of the
five-register `P_{H,Y}` where feedback strictly helps: exactly 120 (60 in
`P_{2,3}`, 60 in `P_{3,2}`), each with gap 1 and none an exit (target block
`D != I`). On one greedy minimum word of each it asserts Corollary 2:
`f_v >= 1`, a non-clean read, and `c >= f_v + 1`.

`verify.py` reports `lemma_words = 15,028`: the 6,628 + 8,400 words ending in
`P`. The 2,800 free words check only the per-gate invariant.

This is a written proof plus finite corroboration. It was reviewed only by AI
passes in the same loop; there is no human review and no formal (Lean) proof.
