# Literal-slot defect of the old correction

Let the two banks have the same finite dimension. Write \(I\) for the identity,
\(H\) for a linear projection (\(H^2=H\)), and \(J_0=I-H\). Then
\(HJ_0=J_0H=0\) and \(J_0+H=I\). Let \(T\) be invertible, \(K=T^{-1}\), and let
\(D\) be any matrix of the same size. No hypothesis makes \(D\) commute with
\(T\).

The old correction and the ordered terminal encoding are
\[
P=\begin{pmatrix}I&0\\K&I\end{pmatrix},
\qquad
L_T=\begin{pmatrix}D&HT\\0&I\end{pmatrix}.
\]
The literal slot swap on the image of \(H\), fixing the complementary ports, is
\[
\Pi=\begin{pmatrix}J_0&H\\H&J_0\end{pmatrix}.
\]
The literal encoding is \(A_T=\Pi L_T\).

## Ordered commutator, without \(HT=TH\)

Block multiplication gives
\[
PL_T=\begin{pmatrix}D&HT\\KD&KHT+I\end{pmatrix},
\qquad
L_TP=\begin{pmatrix}D+HTK&HT\\K&I\end{pmatrix}.
\]
Subtracting and using \(KD-K=K(D-I)\) yields the identity
\[
PL_T-L_TP
=
\begin{pmatrix}-HTK&0\\K(D-I)&KHT\end{pmatrix}.
\]
If in addition \(HT=TH\), then \(KT=TK=I\) implies \(HTK=H\) and \(KHT=H\), so
\[
PL_T-L_TP
=
\begin{pmatrix}-H&0\\K(D-I)&H\end{pmatrix}.
\]
The bottom-right block is \(H\) only under that commutation. A triangular \(T\)
that moves mass between \(J_0\) and \(H\) keeps the unsimplified identity and
rejects the simplified one.

## Literal slots

Assume now that \(H\) is a projection and \(HT=TH\), hence \(HK=KH\) and
\(J_0K=KJ_0\). Then \(\Pi^2=I\), and
\[
A_T=\Pi L_T
=
\begin{pmatrix}J_0D&H\\HD&HT+J_0\end{pmatrix}.
\]
The same expansion, reduced by \(J_0H=0\), \(H^2=H\) and \(HTK=H\), gives
\[
PA_T-A_TP
=
\begin{pmatrix}-HK&0\\KJ_0(D-I)-H&KH\end{pmatrix}.
\]
On an input \((a,0)\) the first-bank image of this commutator is \(-HKa\).
If \(a\) is supported on the image of \(H\), that image is \(-Ka\). If \(a\) is
supported on the image of \(J_0\), the first bank is \(0\).

Thus the ordered defect \(-Ha\) and the literal defect \(-HKa\) are different
whenever some value of \(T\) on the image of \(H\) is not \(1\).

## What a uniform scalar cannot cancel

Suppose the diagonal entries of \(T\) on the image of \(H\) are not all equal.
Then \(-Ka=\lambda a\) cannot hold for every \(H\)-supported \(a\), for any
single scalar \(\lambda\). A uniform bank multiplier is not an intertwiner of
\(P\) through \(A_T\).

If those diagonal entries are equal to one value \(t\), then \(\lambda=-1/t\)
does cancel the first bank for every \(H\)-supported amplitude. It still does
not cancel a vector with a nonzero \(J_0\) component, because \(-HKa\) has no
\(J_0\) component and \(\lambda a\) does.

## Conjugation

Whenever \(D\) is invertible, \(L_T\) is invertible and
\(P_{\mathrm{enc}}=L_TPL_T^{-1}\) satisfies \(P_{\mathrm{enc}}L_T=L_TP\).
The literal-slot operator that satisfies the same relation for \(A_T\) is
\(\Pi P_{\mathrm{enc}}\Pi\), not \(P\) and not \(P_{\mathrm{enc}}\). This
identity prices neither \(\Pi\) nor the rank of \(HD^{-1}\) as a native tariff.

## What this does not prove

It does not exhibit an adjacent completed-call pair, a helper-role match, or a
complete bill. It does not rerun the 10,816-line census of PR #3954. Linear
rank is not a native-call lower bound. No \(\kappa\) changes.
