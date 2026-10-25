# Maximal entrance of the native event after warp 0

SPDX-License-Identifier: Apache-2.0. This is a source-bound calculation on one
frozen word, not a proof-assistant certificate and not a new kappa.

## Domain

Frames are subspaces of \(V=\mathbb F_2^9\). The word is the PR #3929 base
word. Warp array index 0 is lender 243 at original B position 916. Eight
native events precede it. The next native event is warp array index 13, on
lender 349 at the same B position. Its original entrance is

\[
U=\operatorname{span}(416,70,19,13),
\]

dimension 4, and its map \(G\) is the published invertible column map.

Freeze the prefix through warp 0, the ordered scalar operations and their
original frames as floors, every native map, and the terminal caps. A later
scalar frame must contain its original frame and the incoming frames of its
operands. A later native entrance must contain its original entrance and the
incoming lender frame; its exit is the image under the unchanged map. PR #3933
proved that, in this domain, backward capacity produces the unique maximal
legal seed and the least-join completion is legal exactly when that seed is.

## Entrance

The backward pass on the suffix after warp 13 returns

\[
C=U+\operatorname{span}(7),
\]

dimension 5. The same pass on warp 0 returns the entrance PR #3933 recorded,
\(U_0+\operatorname{span}(7)\). That is a control on the transcription, not a
new proof of the warp-0 theorem.

Of the 31 lines of \(V/U\), the forward least-join test admits only
\(\operatorname{span}(7)\). The original entrance is legal. One explicit
dimension-6 join of \(C\) with another quotient line fails the terminal caps.
The verifier checks these statements on the hashed word.

## Three charges

The least completion of \(C\) inserts one identity scale on register 349.
That scale is the entrance charge, \(+1\,H_1\).

The named caller fields are unchanged, including `restore`. Terminal
end-climb counts stay \(H_1:289\), \(H_2:77\), \(H_3:54\). Cleanup gains
exactly one inverse scale on the buffered lender and no other gate. A swapped
exit on the same entrance fails the frame bill.

The forward histogram changes by

\[
+28\,H_1-16\,H_2-4\,H_3+4\,H_4.
\]

Rank mass stays 5134. The warp-0 least completion, run with the same code, has
delta \(+27\,H_1-14\,H_2-H_3+H_4\), matching the canonical delta stated by
PR #3933. Warp 13 is not that completion: the lender, the original entrance,
and the delta differ.

## Power tariff

For \(q\in\mathbb R\),

\begin{align*}
f(q)
&=28-16\cdot 2^q-4\cdot 3^q+4\cdot 4^q\\
&=4\bigl((2-2^q)^2+(3-3^q)\bigr).
\end{align*}

The integer endpoints are \(f(0)=12\) and \(f(1)=0\). For \(q\in[0,1)\),
\(3^q<3\), so the second summand is positive and \(f(q)>0\). At the rank-mass
tariff \(q=1\), \(f(1)=0\).

The ordinary raw-moment comparison uses the same sign. A child of rank \(r\)
contributes a positive multiple of \(r^{1-a}\). Substituting \(q=1-a\) makes
the moment difference a positive multiple of \(f(1-a)\). It is therefore
strictly positive for every \(a\in(0,1]\) and zero at \(a=0\).

This delta is the one PR #3933 already factored for the published nonminimal
warp-0 recipe. The identity applies to any histogram with these four
coefficients. It does not identify the two words.

## What this does not show

No search of the other 62 native events, no native-phase replay, no
PR #3945 owner fill, and no selected cold replay. A loss on warp 13 does not
forbid a different warp from lowering a power tariff. Unknown owner-fill cost
is not zero. Selected \(\kappa\) stays \(0.001672660197076918\).
