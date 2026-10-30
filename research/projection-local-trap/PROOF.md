# A strict local trap for projection cuts

Let K be any field, V=K^2, and 0<t<1. Write h=2^t, so 1<h<2.
Consider a directed multigraph with fixed vertices carrying 0 and V and
one free vertex carrying a subspace S of V. There are a parallel edges
0 -> S and b parallel edges S -> V, where a,b are positive integers.
Every edge is charged its dimension gap to power t, with 0^t=0.
Every subspace S is legal. Boundaries stay fixed during a projection move.

The complete objective of this graph is

    E(S) = a (dim S)^t + b (2-dim S)^t.

There are precisely three possible objective values:

    E(V)=a h,       E(line)=a+b,       E(0)=b h.

These formulas retain every edge, including parallel multiplicity. There
are no productive credits or unpriced terms in this abstract objective.

## Strict local trap and joint escape

By a rank-one projection move we mean the choice, at each free vertex,
between its current frame F and P(F), for one linear idempotent P whose
kernel has dimension one. This is the move in Dugongue's PR556. In this
two-dimensional space, P has rank one and maps V to a line. There is only
one free vertex, so optimizing all subsets for any such P compares just
E(V) and E(line).

The initial frame V is strictly worse than the zero frame and strictly
better than every changed single-projection frame if and only if

    a>b and a+b>a h.                                      (1)

Under (1), every nontrivial rank-one projection move increases the entire
objective. Exhaustively optimizing each binary move therefore retains V.
This remains true under any sequence that accepts only nonincreasing
objectives. It is a strict local minimum with respect to these moves.

Take P(x,y)=(0,y) and Q(x,y)=(x,0). They are idempotent, have one-dimensional
kernels, commute, and PQ=QP=0. Their joint action sends the free frame to 0.
Every intermediate frame remains between the fixed boundary frames, hence
legal. The joint objective decreases by exactly (a-b)h. The first step
must increase the objective; that is the obstruction to monotone descent.
Since a+b>a h>b h, the zero frame is also the global optimum over all S.

This proves existence over every field. It does not use a finite-field
extrapolation or the correctness of a predecessor's implementation.

## Sharp number of edges in this class

Set delta=2-h, with 0<delta<1, and d=a-b, a positive integer. Condition (1)
is exactly

    a delta>d.

For a fixed d the least possible a is floor(d/delta)+1. This choice has
b=a-d>=1 because delta<1. Therefore the least edge count at that d is

    N_d = 2 floor(d/delta)+2-d.

As 1/delta>1, increasing d by one increases floor(d/delta) by at least one.
Thus N_(d+1)-N_d>=1. The global minimum occurs at d=1 and is exactly

    N_min(t) = 2 floor(1/(2-2^t))+1.                       (2)

It is attained by a=floor(1/(2-2^t))+1 and b=a-1. The strict inequality
matters when the reciprocal is an integer. A tie at a smaller a is not a
strict trap. This is a minimum only within the specified three-vertex,
two-boundary, positive-parallel-multiplicity class. It is not a minimum
over arbitrary frame graphs or physical scalar programs.

## An exact 481-edge example

At t=997/1000, the following strict integer inequalities hold:

    2^997 * 240^1000 > 479^1000,
    2^997 * 241^1000 < 481^1000.

Taking positive thousandth roots gives

    479/240 < h < 481/241.

It follows that 240 < 1/(2-h) < 241. Formula (2) gives N_min=481,
attained by a=241 and b=240. Its profiles are

    initial V:  241 rank-two edges, 240 rank-zero edges;
    any line:   481 rank-one edges;
    final 0:    240 rank-two edges, 241 rank-zero edges.

For every 0<t<=997/1000 the same graph remains a strict trap: h decreases,
so 481>241h persists, while 241h>240h. The 481-edge minimality is asserted
only at t=997/1000. At the linear tariff t=1 there is no trap in this
class: a+b>2a would require b>a, contradicting the cheaper-zero condition.

The pinned selected complex supplier uses C=10940329/3500000000, so its
power exponent t=1-C lies in this interval. This arithmetic comparison
only locates the abstract example in a relevant power range. It does not
embed these parallel edges in the selected supplier, transfer its caller
contract, change its signed invoice or establish a kappa gain.

## What changes for the next search

The binary optimum for one projection can be exact and still provide no
certificate of a joint optimum. To escape this example, a search must
allow a simultaneous corank-two image or temporarily accept a worse
intermediate frame. A richer move must still retain fixed observations,
productive targets, dirty restoration and every physical cost. No such
supplier implementation is established here.
