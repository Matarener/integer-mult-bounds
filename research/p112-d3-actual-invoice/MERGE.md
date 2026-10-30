# Same-axis correction merge and the t=3 sum 33 boundary

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.

Use the exact actual-basis contract in PROOF.md. The t=2,d=3 proof is
completed first, so this reduction has no circular dependence on t=3.
At adapted t=3 inside sum 33 the raw budget forces c9=0, and I<=64 forces
n_c>=33+40-64=9. There are only eight frame axes.

The following reduction applies when all six actual inside words
are low and the correction count is at least nine, as at Sigma=33.
Two corrected members have the same frame axis by pigeonhole.
Write their duals x_i=lambda_i f and x_j=lambda_j f, with nonzero
scalars. Replace them by

    q*=lambda_i q_i+lambda_j q_j.

The other nine original basis members and q* are independent, span
a ten-dimensional S', and contain C by the original actual expansion.
Their restricted duals are the nine unchanged nonzero duals and f.
Let z be the excluded label of f. Both old support spans contain z.
Writing pi_z for the binary quotient by the line F2*z, the invoice
contribution of a piece with dual f is exactly dim pi_z U(piece).
Since U(q*) is contained in U(q_i)+U(q_j),

    dim pi_z U(q*) <= dim pi_z U(q_i)+dim pi_z U(q_j).

Thus the invoice does not increase. The raw weight drops at least one,
because dim(U(q_i)+U(q_j))<=w(q_i)+w(q_j)-1. In particular the
new raw sum is at most 72.

Let T' span ALL low words of S'. Since S' is a subspace of S,
T' is a subspace of T and dim(C intersect T')<=3. Two outside members
cannot be the chosen pair, because their restricted duals are independent.
If both members are inside, four unchanged low actual members remain;
their span has dimension four inside S', so its intersection with C
has dimension at least 4+8-10=2. If one member is outside, its dual
vanishes on D=C intersect T; the proportional inside dual therefore
also vanishes on D. All of D lies in the span of the five unchanged
inside low members, so dim(C intersect T')>=3.

Hence the merged actual basis has d'=2 or3, raw at most 72, and
invoice at most 64. Applying the complete t=2 budgeted d2 theorem or
the complete t=2 budgeted d3 theorem (PROOF.md and ADAPTED-T2.md) gives the intended
contradiction. This audit does not supply a correction-pair argument
when fewer than nine members are corrected.
