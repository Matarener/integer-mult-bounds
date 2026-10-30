# Exact coordinate-translation covers for sharp switch guards

## Statement and contract

Let `r>=1`, `B=2^G>=4`, `N=2^m`, and `q=3r+1`. Assume

```text
q <= B,                 q(B-2) <= N.
```

For each target, retain two arbitrary dirty radix-`B` control digits `u_i,t_i`
and an `m`-bit window `W_i` above that target. All these coordinate fields
are disjoint. The target bits and any other bits are spectators for the
guard test. The conservative sharp good set is

```text
G = product over i of {0,...,B-2} x {0,...,B-2} x {0,...,N-B+1}.
```

A coordinate translation adds a separately chosen constant modulo each
coordinate's own period. It preserves each field, every active target bit,
inactive high control digits, and all other spectators. It is **not** an
ordinary addition on the concatenation of the control digits. Its execution
cost is not assumed free.

A menu `D_0,...,D_(s-1)` covers if every guard tuple `x` has some
`D_k(x) in G`. The minimum possible menu size is exactly **`3r+1`**.
The lower bound permits unrelated constants in all coordinates and menu
entries; it does not assume the diagonal form of the attaining menu.

This is a scoped proof about covers of this specified product. A state
outside `G` is not necessarily an incorrect compact-switch execution.
The theorem does not lower-bound menus that exploit a larger actual
agreement set, coordinate mixing, state-dependent translations outside a
fixed menu, or a different guard predicate.

## Lower bound

There are `3r` independent coordinate fields. Every coordinate good set is
proper: `B-1` is bad for each control digit and `N-1` is bad for each
window because `B>2`.

Take any `s<=3r` coordinate translations. Assign a different coordinate
`j(k)` to each menu entry `k`. If that entry adds `a_(k,j)` modulo the
coordinate period `P_j`, choose

```text
x_(j(k)) = P_(j(k)) - 1 - a_(k,j(k)) mod P_(j(k)).
```

Choose the remaining coordinates arbitrarily. Independence makes all these
choices simultaneous. Translation `k` sends its assigned coordinate to
`P_(j(k))-1`, so it fails the corresponding guard. Every menu entry fails.
Thus any covering menu needs at least `3r+1` entries.

This is an obstruction to a constant-size guard-guaranteeing translation
menu when the number of simultaneously guarded targets is unbounded.
It is not an obstruction to the existing sparse repair.

## Attaining menu

Write `d=B-2`. For `0<=k<q`, set

```text
D_k: u_i -> u_i+k mod B,
     t_i -> t_i+k mod B,
     W_i -> W_i+kd mod N,          for every i.
```

For one control digit, the forbidden preimage in phase `k` is the singleton
`B-1-k mod B`. These singletons are distinct because `q<=B`.
Consequently a fixed digit forbids at most one phase.

The bad window interval has length `d` and is `[N-d,N-1]`. Its preimage
in phase `k` is

```text
[N-(k+1)d, N-kd-1].
```

The `q` displayed intervals are disjoint ordinary integer intervals inside
`[0,N-1]`, because `qd<=N`. A fixed window forbids at most one phase.

There are `3r` coordinates, so their union forbids at most `3r` of the
`q=3r+1` phases. At least one phase is good. This proves the upper bound
and hence optimality. The least good phase defines a deterministic selector
`sigma(x)` depending only on controls and windows.

For the CRT convention `K=64G` and `m=K-1`, the window-size condition is
automatic once `q<=B`: `N=B^64/2>=B^2>=q(B-2)`. This substitution is an
arithmetic observation, not a claim that a particular caller's remaining
parameter, placement or implementation obligations have been checked.

## Source-correct logical switch interface

The credited compact-switch premise is the following endpoint contract.
For every Boolean source tuple `f(y)` omitting every active target and the
borrowed controls, a raw bijection `S_f` agrees on `G` with the ideal map
`T_f`, which XORs each `f_i(y)` into target `i` and restores the controls,
windows and other coordinates. Use live post-increment digits and disjoint
target-free windows. The sharp one-target range and the disjoint-coordinate
extension are stated in unpaidmoon's PR4321. Hiroki KUMAZAKI's PR4169 treats
arbitrary functions at the CRT caller. Ryanson Jonathan's PR4329 distinguishes
`K-1` window bits from a target-inclusive `K`-bit reading. These endpoint
claims are cited premises here; their previous verifiers and counts are not
audited or replayed.

Let `D_(k,y)` be the data-field part of `D_k`. Change the source function to

```text
f_(i,k)(y') = f_i(D_(k,y)^(-1)(y')).
```

This source still omits all active targets and borrowed controls. Merely
using `f_i(y')` would generally apply the wrong switch because the translation
changes guard bits on which `f_i` may depend.

For an arbitrary address `x`, put `k=sigma(x)`. Then `D_k(x) in G`, so

```text
D_k^(-1) S_(f_k) D_k(x)
  = D_k^(-1) T_(f_k) D_k(x)
  = T_f(x).
```

The last equality holds because `D_k` preserves active target bits, and
`f_k(D_(k,y)(y))=f(y)`. This proves a total logical address implementation
with no guard exception, conditional on execution of the indicated
translations, selected raw macro and transported source.

The selector is invariant under `T_f`: its controls and windows never
change. An abstract reversible implementation may compute `sigma` into an
initially zero selector register of `ceil(log2 q)` bits, retain it across
the controlled conjugation, and uncompute it afterward. The final address
has the same selector value. This is a clean owned-register requirement,
not permission to treat a productive dirty helper as zero-initialized.

## Cost boundary and stopping decision

The guard-cover result is an exact lower bound and construction. The
logical conjugation theorem is conditional on the credited raw endpoint
contract. Neither is a physical fixed-tape implementation or a complete
multiplication theorem. In particular the following costs remain unknown:

- Independent modular translation of each control digit and guard window,
  including delivery and inverse translation.
- Computing, storing, routing and erasing the selector with legally owned
  state, and gating the appropriate macro on its value.
- Evaluating the transported source, preserving ordinary-callee ordering,
  and charging full-field shuttles and preparation on the selected sectors.
- A complete comparison with the existing sparse-repair bill, with native,
  stock, precision, compiler and outer obligations retained.

Unknown costs are not zero. A finite guard cover alone does not admit a
supplier or improve kappa. The family decision is to retain this first
scoped result and stop before any implementation expansion. The next
decision needs a priced one-target selector/translation contract.
