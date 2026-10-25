# Proof sketch: one dirty role does not lower the S3 longest Coxeter double

## Object

Work in the formal group algebra `F₂[S₃]` with paid address labels
`x=(1 2)` and `y=(2 3)`. A paid factor is

```text
D_N(g) = I + ([g]+[e]) N,
```

where `g∈{x,y}` and `N=uvᵀ` is a rank-one idempotent in `M₃(F₂)`
(`vᵀu=1`; exactly 28 projectors). This gives **56** paid factors. The target
is

```text
diag([xyx], [xyx], [e]) ∈ M₃(F₂[S₃]).
```

The third diagonal entry `[e]` forces the dirty helper role to restore.

## Upper bound

The direct word that runs the geodesic `x y x` on role 0 with projector
`E₀₀` and then the same geodesic on role 1 with projector `E₁₁` has length
**six** and equals the target. Each factor is an admitted paid call.

## Lower bound

Every paid factor is an involution, so backward search uses the same
generators. Exact breadth-first balls from the identity and from the target
have layer sizes

```text
[1, 56, 1750, 45396]
```

through radius three. Any word of length `L≤5` has its state at step
`min(2,L)` inside

```text
ball(I, 2) ∩ ball(T, 3).
```

That intersection is empty, and the symmetric split
`ball(I,3) ∩ ball(T,2)` is likewise empty. Therefore no paid word of length
at most five realizes the target, and six is minimal in this declared model.

## Independent witness

A second engine stores states as frozensets of `(row,col,group)` atoms and
does not import the primary packed-integer transition. It rebuilds the same
balls, agrees on zero MITM hits, and confirms the direct six-call endpoint.

## Limits

This is a finite three-role theorem for one fixed S3 target. It does not cover
a fourth dirty role, other S3 target triples, physical hosting/precision, or a
supplier invoice. Selected kappa is unchanged.
