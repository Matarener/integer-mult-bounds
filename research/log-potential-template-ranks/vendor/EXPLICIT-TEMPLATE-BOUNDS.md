# Explicit finite ranks, without an unperformed search for the first success

Apache-2.0. Substantial OpenAI assistance. The integer lockstep flow is Jacob
Alan Sussman's Theorem 1G. The native finite precompilation argument and its
independent audit are in `../architecture/FINITE-PRECOMPILATION.md` and
`../transfer-audit/AUDIT.md`. This note strengthens the quantitative choice
of the fixed template rank. It does not claim to materialize that template.

## 1. Use a strict superpotential rather than an unknown exact root

Write `L(n)=P_n/B_n` for the exact normalized number of paid rank-one leaves
in the integer compiler, including source complements and every exit batch.
Choose rational `0<t<z0<z<1` such that

```
sum_paid r^t < sum_targets W_k*k^t.
```

The literal finite flow cancels internal jobs. With normalized source weights
`w_s` and exit counts `x_e`, it therefore gives the inequality

```
sum_e x_e*e^t <= sum_s w_s*s^t,     sum_s w_s=1,
L(n)=sum_s w_s*L(n-s)+sum_e x_e*L(e).
```

There is no need to evaluate the exact root. Separately the exact positive
rank-one surplus gives `sum x_e*e <= sum w_s*s`. Induction, including the
ordinary base programs, then proves `L(n)<=n` for every positive integer n.
Calls on owned centers occur in the paid list and are included in both
inequalities. Owned centers contribute no source credit.

## 2. An explicit point beyond which the improved induction works

Put `m=max(k)`, `k_min=min(k)`, `r_max=max(r)`. The finite flow has sources
`n/m<s<=n` and exits no larger than

```
E(n)=r_max*(n/m)^theta,     theta=log(r_max)/log(k_min)<1.
```

Choose rational `theta_bar>theta`, and put `h=1-theta_bar>0` and
`delta=z0-t>0`. In our two cases the exact integer inequalities prove
`m^h<2` and `2*r_max<=16`. Since `n>=m`,

```
m*E(n)/n < 16*n^(-h).
sum_e x_e*e^z0 <= (16*n^(-h))^delta * sum_s w_s*s^z0.
```

The source complements pay for this exit term. Concavity gives

```
n^z0-sum_s w_s*(n-s)^z0 >= eta*sum_s w_s*s^z0,
eta=z0*m^(z0-1).
```

The exact logarithm intervals check `z0>1/2` and `m^(1-z0)<2`, hence
`eta>1/4`. Set

```
H0=ceil((3+4*delta)/(h*delta)),       n0=2^H0.
```

This exceeds the finite base range. For every `n>=n0`, the exit coefficient
is at most `1/8<eta/2`. Set `A=n0^(1-z0)`. For `n<=n0`, the elementary
bound `L(n)<=n` implies `L(n)<=A*n^z0`. For larger n, every complement and
exit has smaller rank, so the exact recurrence and strong induction imply
the same bound. No unknown asymptotic constant is left in this estimate.

## 3. Specify one winning finite ambient rank

Set

```
H1=floor(H0*(1-z0)/(z-z0))+1,         N=2^H1.
```

Then `A*N^z0<N^z`, so the integer compiler at this **specified** rank N
has `P_N/B_N<N^z`. Its recursion, ordered batch replication, role ownership,
and native adapters define a finite word; all its remaining paid calls
have rank one. The complete word can be defined without having emitted its
astronomical list of instructions in this research session.

The two choices checked by `explicit_template_bounds.py` are:

| Family | Tested mixed saving `1-t` | Uniform saving `1-z` | `theta_bar` |
| --- | ---: | ---: | ---: |
| Complex | 0.002305 | 0.002304 | 9/10 |
| BIT | 0.002769 | 0.002760 | 15/16 |

The angle bounds use the exact integer tests `5^10<6^9` and `7^16<8^15`.
The machine-readable receipt gives H0 and H1, strict rational margins, the
source hashes, and controls that reject reducing either exponent by one.

This is an explicit theoretical construction with very large fixed
constants. It is not a practical-sized generated algorithm, a formal proof,
or a claim that the small rank-57/rank-50 examples attain these savings.
Native closure, the delayed BIT cover, scalar costs, precision and row stock
are separate premises supplied by the other source-bound arguments. Their
constants must be substituted using this compiled word, not inherited from
the old small supplier.

Replay from the repository root:

```sh
python3 -B research/kappa-rebuild/controller/explicit_template_bounds.py
```
