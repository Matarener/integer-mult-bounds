# Why the fixed `L/2` substitution has a justification for one functional

This note is local to the PR943 singleton prefix-walk model used by
PR2542/PR2634/PR2691 and corrected by #2973. It is the mathematical content of
`verify.py`; the numeric receipt is in [RESULT.json](RESULT.json).

## 1. Setup

For a word `w` of length `L` over `[0, n)`, put `q_0 = 0` and

```
q_{i+1} = q_i XOR (1 << w_i),
```

and let `S` be the **set** of distinct prefix states. Restoration means every
label occurs a positive even number of times, so `q_L = q_0` and `L` is even.
Universality is `S + S = F2^n`. A walk is *simple* when `q_0 .. q_{L-1}` are
distinct; the closing state adds no new point.

A nonzero linear functional `l` with indicator vector `v in F2^n` partitions `S`
into its kernel class `E` and other coset `O`. Write `s = |E|`, `t = |O|`, and

```
a = C(s,2) - |{x XOR y : x != y, x, y in E}|,
b = C(t,2) - |{x XOR y : x != y, x, y in O}|.
```

## 2. The correct budget, for any functional

`E` is a linear subspace of codimension one, so `E \ {0}` has `Q - 1` elements
with `Q = 2^(n-1)`, and `O + O` lands in `O` while `E + E` lands in `E`. If `S` is
universal then every nonzero kernel-coset mask is a sum of two distinct points of
`E`, and every mask of the other coset is a sum of a point of `E` and one of `O`.
Hence

```
a + b <= C(s,2) + C(t,2) - (Q - 1).
```

Nothing in this argument mentions weight parity. Setting `s = L/2 + d` and
`t = L/2 - d` and using `C(m+d,2) + C(m-d,2) = 2C(m,2) + d^2`, define

```
base(n, L) = 2C(L/2, 2) - (Q - 1),
correct budget = base(n, L) + d^2.
```

**The word-level defect in the retained engines is substituting `L/2, L/2` while
grouping by some functional `l`.** That substitution is valid exactly when
`s <= L/2` and `t <= L/2`; it is *stronger* than the true budget by exactly the
slack `d^2`, and it is sound for a given word only when

```
a + b <= base(n, L).
```

A word is **falsely pruned** when `base < a + b <= base + d^2`: the substituted
budget rejects a universal word that the correct budget admits.

## 3. The alternation lemma

**Lemma.** For every `i in [0, L)` and every functional `l_v`,

```
l_v(q_{i+1}) XOR l_v(q_i) = v_{w_i}.
```

*Proof.* `q_{i+1} XOR q_i = 1 << w_i = e_{w_i}`, and `l_v` is linear, so
`l_v(q_{i+1}) XOR l_v(q_i) = l_v(e_{w_i}) = v_{w_i}`. Done.

`verify.py` checks this identity on every emitted word at `(4, 8)` for all 15
nonzero `v` (3480 checks) and raises on any violation.

**Corollary.** `l_v(q_i) = i mod 2` for all `i` if and only if `v = 1^n`.

*Proof.* The forward direction forces `v_{w_i} = 1` for every `i`, so every label
of `w` lies in `supp(v)`; that alone does not give `v = 1^n`. The statement that
matters is the other one: `l_v(q_i) = i mod 2` holds for **every** walk only when
`v = 1^n`, because then each step flips the value. For any other `v` the class
value is constant across a step whose label lies outside `supp(v)`, so no
alternation is available. Formally: for `v != 1^n` pick a coordinate `j` outside
`supp(v)` and the walk that places label `j` on its first step; the value does not
flip there. Equivalently, weight parity *is* the all-ones functional. QED.

## 4. What follows

The bound `s, t <= L/2` used by the substitution is the statement that the two
classes are the time-parity classes. By the corollary that is available for
exactly one functional, the all-ones one `v = 1^n`. For every other functional
the class sizes are produced by the walk and are bounded only by `|S|`, so the
substitution can understate the budget by `d^2` and reject a universal word.

That is a mechanism, not a census. Whether it actually fires, and for which
functionals, is measured in [RESULT.json](RESULT.json) and summarised in the
README table. The measured `weight >= n - 1` regularity is **not** derived here.

## 5. Scope

This is a scoped lemma plus a finite certificate on nine small `(n, L)` domains,
`n <= 7` and `L <= 14`. It is not a corrected seven-label census, does not decide
`f(7)`, and does not change any selected result, supplier or kappa.