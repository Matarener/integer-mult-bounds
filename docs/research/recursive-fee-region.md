# Price two kinds of fees together

Use a complete old and new invoice plus two explicit paid-only fee patterns.
The tool returns every feasible tradeoff between their multiplicities that
preserves weak cost order for **all increasing concave tariffs** with `f(0)=0`.

```sh
python3 -B scripts/recursive_fee_region.py OLD.json NEW.json \
  ROUTE_FEE.json RESTORE_FEE.json --fixed-a 2 > region.json
```

All four invoices use the [same schema](recursive-invoice-preflight.md) and must
have the same contract. Each fee must contain paid work and no target credit.
The first fee has multiplicity x; the second has multiplicity y. Fractional
multiplicities describe a relaxation. Actual job counts require integers.

At each rank breakpoint k, form the exact inequality

`x sum_a count*min(rank,k) + y sum_b count*min(rank,k) <= -delta_hinge(k)`.

The report includes all coefficients and ranks. A negative right side makes the
region empty: adding nonnegative fees cannot repair that hinge. Otherwise the
tool clips a bounding rectangle against each half-plane with rational arithmetic.
It returns the vertices in boundary order and the binding ranks at each vertex.
Because both fee patterns are nonempty, each coefficient is positive, and the
region is bounded. It can reduce to the origin.

The union of breakpoints suffices. Each hinge sum is linear between successive
breakpoints and constant after the last one. The standard hinge decomposition
of an increasing concave tariff then proves the stated weak cost order. This is
an exact test for that tariff class, and a sufficient test for all `r^t` with
`0<t<1`. It is not a necessary test for the smaller class of power tariffs.

For example, remove three paid rank-2 jobs. Let fee A be one rank-1 job and fee B
one rank-4 job. The region has vertices `(0,0)`, `(3,0)`, `(2,1)`, and `(0,3/2)`.
Two A fees leave room for exactly one whole B fee. The report gives both the
rational bound and the ranks that reject the next whole B fee. This arithmetic
example does not claim that the removed jobs can be removed from a source word.

An equal-mass concentration can improve every strict power tariff yet allow no
positive fee under this stronger test: the linear tariff has zero slack. Use the
[exact power comparator](recursive-power-comparison.md) when that distinction
matters. Do not interpret an empty or zero fee region as a global obstruction.

Limits: 512 distinct ranks across the signed change and both fee patterns, plus
the invoice schema limits. The optional fixed A multiplicity is a nonnegative
integer at most `10^60`. Invalid inputs exit 2 without a result. Each input is
bound by its exact byte hash.

## Open next questions

Bind each fee pattern to actual route and restoration operations. Check the
combined source construction and its compiler obligations. This tool does not
prove fee completeness, target independence, a native map, or a new κ.

Credits: the classical hinge decomposition, existing invoice comparator,
mightyOil's T16 audit, and retained predecessors. Prepared for Ali Romman with
OpenAI Codex assistance. Apache-2.0.
