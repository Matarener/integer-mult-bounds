# One rational three-pair shortcut is obstructed

This is a proof for one specified topology. It does not classify rational or
dyadic controllers. All coefficient statements below are over a field of
characteristic zero. The same argument works over any field when the displayed
nonzero coefficients and inverses exist.

The candidate uses seven alternating local calls. Begin with `F0,R0`. At clock
one, bring pair one alongside pair zero and apply an arbitrary dual `GL2` map.
Run `F1,R1` at stages two and three. Bring pair two to clock three and attempt
the next forward call using only pairs one and two. A later return of pair zero
would have supplied a third internal idle event. With the two final climbs,
this was a prospective five-segment three-pair controller.

Write initial scalar variables as `x0,x1,x2,y0,y1,y2`. Immediately after
`F0,R0`, pair zero is `(-y0, x0+y0)` and pair one is `(x1,y1)`.
Let the first top bridge be

\[
M=\begin{pmatrix}a&b\\c&d\end{pmatrix},\qquad ad-bc\ne0,
\]

and the bottom bridge be its inverse transpose. After `F1,R1`, the top rows
of pairs zero and one have initial-X components `b*x1` and
`b*x0/(ad-bc)`. Pair two still has top `x2`. Therefore `b != 0` would make the
top diagonal block full rank three. The required second rank-decreasing reverse
call instead forces **b=0**, so `a,d` are nonzero.

The two top rows then become `-a*y0` and `-y1/d`. The initial-Y components of
the two bottom rows are

\[
\left(\frac1a,-\frac{c}{ad}\right),\qquad
\left(-c,\frac1d\right).
\]

Their determinant is `(1-c^2)/(a*d)`. The intervening forward call must lower
the bottom diagonal rank by one. Including the untouched `y2` row, this forces
**c^2=1**. Thus the full bottom-Y row space is

\[
\operatorname{span}\{y_0-(c/d)y_1,\ y_2\}.
\]

At the proposed next interface, the accessible top rows belong to pairs one
and two. Their Y projections span only `y1`. This span meets the bottom-Y row
space trivially. The determinant of the three displayed directions, in the
ordered coordinates `(y0,y1,y2)`, is `-1`.

An arbitrary top basis change on these two accessible pairs does not alter
that accessible row space. A forward shear updates the bottom diagonal matrix
by `D + u*w^T`, where `w` is the chosen top-Y projection. If `w` lies outside
the row space of `D`, every vector in the left kernel of the updated matrix
must already lie in the left kernel of `D`: split
`v^T D + (v^T u) w^T = 0` into the two independent row spaces. The rank cannot
decrease. If `w=0`, the diagonal block is unchanged. In either case the required
forward rank decrease is impossible.

The obstruction holds for arbitrary coefficients at the first dual interface,
including non-integral dyadic values, and arbitrary basis changes at the next
two-pair interface. It says nothing about an earlier return of pair zero,
another clock topology, more interfaces, a changed local word, or an independent
primal/bottom first interface.

The proof uses the retained rank-saturation law: nine calls on four pairs, or
seven calls on three pairs, leave no spare rank-neutral local call after the
first one. The construction and local rank law retain the repository's
Johnny Franks / report M and recipe-floor lineage. This proof and its explicit
topology analysis were developed with substantial OpenAI assistance.
