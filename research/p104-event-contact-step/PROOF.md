# One contact changes the complete P104 paid profile

## Source and statement

The input is the exact PR5569 word at
`af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf`. See
[SOURCES.json](SOURCES.json) for the source bytes and retained PR5545 engine.
All event numbers below are zero-based source indices.

The construction changes the chart of `ADD 451 += 228` at event 12658.
It retains every scalar instruction, coefficient and position in the scalar
sequence. It also retains all 735 public initial and final frames, 527 helper
targets, eight owned lifetimes and the 104 literal ports.

At each of the 18 forward local calls, the paid change is

```text
H2 - 2 H3 + H4.
```

The complete conditional claim is kappa = 0.00308189. This claim uses the
five inherited framework assumptions and the source helper-endpoint contract.
It does not change the selected record.

## Exact contact identity

Let O, A, B and C denote the following binary subspaces. Each list is an
independent basis in the fixed nine-dimensional ambient space.

| Frame | Name | Basis | Dimension |
| --- | --- | --- | --- |
| 3 | O | `[]` | 0 |
| 262 | A | `[11,21,486]` | 3 |
| 737 | B | `[11,21,33,455]` | 4 |
| 520 | C | `[1,10,20,32,64,390]` | 6 |

Their spans satisfy O < A < B < C. The replay checks these inclusions on
the complete binary spans. Chart transport preserves the abstract row.
Two transports through an intermediate chart compose to the direct transport.
A common chart change commutes with addition of two rows.

Register 228 stays at A after event 9575. Its next scalar use after the
changed contact is event 12674 at C. Register 451 stays at O after event
12591. Its next scalar use after the changed contact is event 14424 at B.
The constructor checks every intervening register access, including reads.

The old paths are 228: A to C, and 451: O to A to B. They meet at A for
the addition. The new paths are 228: A to B to C, and 451: O to B. They
meet at B for the same addition. Thus both abstract rows agree at their
next unchanged use. Every other row is unchanged. This proves the local
identity for arbitrary inputs, including arbitrary helper inputs.

The old bill is H3 + H3 + H1. The new bill is H1 + H2 + H4. Their
difference is H2 - 2 H3 + H4. Paid count and rank mass are unchanged.
The only newly used ordered native frame pair is (3,737). The exact
native replay checks this pair and all 2,921 distinct paid/target pairs,
including their signed Pauli images, absolute phases and ranks.

## Strict concave gain

For 0 < k < 1, x raised to 1-k is strictly concave on positive x. Hence

```text
2^(1-k) + 4^(1-k) < 2 * 3^(1-k).
```

Let M(k) be target moment minus paid moment. The new complete moment is

```text
M_new(k) = M_parent(k) + 18 * (2 * 3^(1-k) - 2^(1-k) - 4^(1-k)).
```

It is strictly larger throughout that range. This is a change to the paid
profile. It is not extra numerical precision for the same equation.

The exact rational engines give these crossing intervals:

| Word | Lower endpoint | Upper endpoint |
| --- | --- | --- |
| PR5569 | 0.00308181851522 | 0.00308181851523 |
| This word | 0.00308189496866 | 0.00308189496867 |

The raw gain is strictly between 0.00000007645343 and 0.00000007645345.
The claimed endpoint is 0.00308189; it is tested at 0.0030818905. Its raw
headroom is between 0.00000000496866 and 0.00000000496867.

The checker also bounds M_new'(k) with rational intervals on [0,0.0034].
The derivative lies between -255126 and -237752, so the crossing is unique
on that band. Its upper endpoint is the raw funding ceiling for this fixed
invoice under the retained BIT cap. A different word, endpoint contract or
BIT supplier is outside this ceiling. No global optimum is claimed.

## Complete caller and costs

The unchanged caller has 18 forward local calls, 15 query shears and
3,120 whole idle jobs. It has 66,852 paid jobs, 12,814 productive fields,
rank-mass surplus 760, maximum paid rank 72 and maximum target rank 145.
The verifier derives the invoice from the physical event list and checks it
again from the two controller path lengths. It prices all helper targets,
normalizers, main adapters, query shears, idles, routes and owned operations.

There are 25,140 local events and 21,686 scalar/owned events. The scalar
allowance is 217,428, the route allowance is 5,164,000 and the complete
nonrecursive bound is 184,647,552, below the retained 1,000,000,000 budget.
Peak owned occupancy stays one. The sum of local paid ranks is 6,013.
The source report's old literal 5,894 is replaced by this derived sum in
the native growth bound. This report correction does not change the
moment or the claimed gain.

Two exact moment engines check the tested endpoint. The compiler checks
include all three tail ratios, the completion and splitting terms, the
integer threshold and the retained BIT stock. All 54 strict and four
functional outer predicates are positive. The source engine rejects its
insufficient BIT and old-cutoff controls. The new controls reject a missing
source transport, a wrong contact frame, a wrong coefficient, a descending
public return and the unchanged word presented as an improvement.

## Scope

This is an author-checked conditional construction. Finite exact replay
and the chart identity do not prove the full integer multiplication theorem.
The native all-column realization, owned erasure, uniform compiler closure,
precision/fixed-tape execution and analytic recovery remain inherited
assumptions. The free helper endpoints are inherited from PR5561/PR5569;
this contact changes none of them. The enormous uniform word and a complete
rounded multiplier are not materialized. Independent scientific review and
hosted CI are separate from the local checks.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
All retained source notices and predecessor credit remain in the package.
