# Complete P104 words with optimal amplification prices

Two actual words make the precision tradeoff explicit. The source before
public gauge optimization has sharp ideal field amplification 131,072. The
cheapest PR5830 gauge word has amplification 65,537 at scalar allowance 200,546.

| Complete word | Sharp peak | Scalar allowance | Instructions |
| --- | ---: | ---: | ---: |
| Original scalar-budget word | 96 | 224,878 | 27,102 |
| Minimum-amplification word | 2 | 242,734 | 27,107 |

The first word fits the original PR5824 allowance 224,880. **No smaller peak
fits that budget** in the complete source gauge class: a strict peak below 96
needs at least 224,992 scalar primitives. The second word attains the output
lower bound 2, and 242,734 is its minimum scalar price. Its exact scalar cost
is higher than the original; both words still fit the retained full local
allowance 10^7 after every route, helper and owned term is added. Their totals
are 5,545,878 and5,563,734. All native ranks, targets and the 12-slot pool stay fixed.

Both complete words are emitted. This is a constructive ideal-amplification
result under the retained unitary native-chart and exact-reset premises.
It is not a rounded-child error theorem, a physical reset implementation,
a new kappa or a selected-frontier change.

## Sharp source norms and complete boundary

At every actual representation epoch, compute the exact rational RAW row
for each field. Let G_a be its maximum row l1 norm during that epoch. With
gauge exponent x_a, the exact peak is the maximum of 2 and G_a*2^x_a.
The fixed 2 includes the unscaled public output boundary.

Under the inherited unitary frame maps, the triangle inequality gives this
field Hilbert-norm bound at every admitted tensor width. It is sharp: choose
each independent input as the inverse initial-frame image of one common unit
vector, with the sign of its coefficient in an attaining row. The final
frame is unitary. RESULT.json retains literal attaining coefficient rows.
A separate replay of each emitted word recomputes its actual peak, including
all entry, exit and lowered SCALE operations. No predecessor numerical norm
or error constant is transferred to the new words.

The public endpoint contains x+y for two independent unit-bounded inputs.
Its norm can equal 2. Thus no word with this unchanged exposed boundary can
have a smaller ideal peak. The minimum-amplification word attains this floor.

## Exact price certificates

For cap T, each nonzero G_a imposes the exact integer bound
x_a <= floor(log2(T/G_a)). The strict cap uses one less when T/G_a is an
exact power of two. There is no floating logarithm or exponent search box.

The source cost graph has edges z=e+x_a-x_b with tariff w*abs(z). Original
edge duals satisfy abs(y)<=w. Each norm constraint has a nonnegative
multiplier m. The checker requires full conservation, including the norm
edges from each constrained node to the anchor. For every feasible x,

```
sum w*abs(e+x_a-x_b)
  >= sum e*y - sum upper_bound_a*m_a.
```

A retained integer potential attains this lower bound. The full scalar
allowance is 179,604 plus twice the exponent objective; all public boundary
scales and the exact sign-parity minimum are included. The cap 96 objective
is 22,637. The strict-below 96 objective is 22,694, which proves the budget
obstruction. The cap 2 objective is 31,565.

The same checker verifies complete optimum certificates for all 16 caps
2^b, b=1,...,16. Selected points are:

| Peak cap | Minimum scalar allowance |
| ---: | ---: |
| 2 | 242,734 |
| 64 | 227,354 |
| 96 | 224,878 |
| 128 | 224,278 |
| 256 | 221,202 |
| 4,096 | 208,906 |
| 65,536 | 200,650 |

The complete curve is in RESULT.json. The 16 cap certificates prove tariff
optima. Full forward/reverse and actual emitted-prefix checks run on the two
retained words. No claim about arbitrary rescheduled circuits follows.

## Legal implementation and verification

All entry and exit conversions are charged. Each emitted word has 769 entry
and 769 exit scales. Four cap 2 exits have coefficient plus or minus 65,536.
The source scalar alphabet excludes that single coefficient. They are
therefore lowered to factors plus or minus 32,768 and 2. This preserves the
exact scalar charge and endpoint; intermediate magnitudes stay between the
original endpoints. The source coefficient limit is unchanged.

The source PR5830 checker retains its explicit operation-bound API. Both
words satisfy its strict structural bound 27,504, every frame and ownership
condition, and the original per-coefficient bound. Complete 782-axis forward
and 611,524-coefficient reverse checks prove the public and dirty-owned
endpoints. The source constructor also checks the representation invariant
at every scalar and native event. Exact dual controls reject a false price,
a negative norm multiplier and an unsupported lower cap.

```sh
python3.12 -B scripts/research_package.py --package research/p104-priced-amplification
```

Registered normal and optimized replay needs only the standard library.
The exact official PR5830 export is retained and authenticated. Temporary
extraction does not alter the frozen source or the read-only package.
The default verifier uses no Git, network or optimization solver.

For a new source-bound candidate, install `networkx==3.5` in an isolated
Python 3.12 environment and run, from this package:

```sh
python3.12 -B search.py --cap 96 --output candidate.json
python3.12 -B search.py --cap 96 --strict --output strict-candidate.json
```

Search uses integer network simplex and a finite exact penalty. The separate
standard-library checker accepts only a feasible potential and a matching
conserved dual. NetworkX is search software, not an acceptance dependency.

## Open next questions

Price actual rounded primitives on the two emitted words and compare their
complete time/precision costs. Peak 2 costs 17,854 more scalar primitives than
the original budget, while peak 96 preserves that budget. A completed-operation
error theorem must include native-child errors, COPY and reset residuals,
owned return and every changed conversion. The current exact-error runtime
work in Discussion 2750 applies to a different frozen word. All five framework
assumptions and full physical/compiler admission remain open.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. PR5830
supplies the complete coefficient graph, gauge constructor and exact scalar
cost premise. Retain PR5824/5822/5812, all P104 authors in NOTICE, and the
PR5819/Adam Gall/ywz65/PR2878 norm/precision context. The dual and triangle
inequality are standard mathematics. New work is the full source norm-price
frontier, exact budget optimum and two complete legal words. Apache-2.0.
Coordination: https://github.com/CrocSwap/integer-mult-bounds/discussions/5804.
