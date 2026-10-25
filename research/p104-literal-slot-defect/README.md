# Literal-slot defect of the old P104 correction

**Negative interface certificate. No new κ.** Selected κ stays
`0.001672660197076918`.

Discussion #1166 comment 19034066 asks for one adjacent completed-call pair
whose encoded exit matches the next entrance on every role. This package does
not supply that pair. It certifies the obstruction that pair would have to
cancel if it reused the old correction, and it shows a uniform scalar bank
multiplier cannot cancel it when the N-port scales differ.

## Result

Let \(H\) be a projection, \(J_0=I-H\), \(T\) invertible, \(K=T^{-1}\), and
\(D\) any matrix of the same size. With
\[
P=\begin{pmatrix}I&0\\K&I\end{pmatrix},
\qquad
L_T=\begin{pmatrix}D&HT\\0&I\end{pmatrix},
\qquad
\Pi=\begin{pmatrix}J_0&H\\H&J_0\end{pmatrix},
\qquad
A_T=\Pi L_T,
\]
the ordered commutator is
\[
PL_T-L_TP=\begin{pmatrix}-HTK&0\\K(D-I)&KHT\end{pmatrix}
\]
with no assumption that \(H\) commutes with \(T\). When \(HT=TH\) and \(H\) is a
projection, \(\Pi^2=I\) and the literal-slot commutator is
\[
PA_T-A_TP=\begin{pmatrix}-HK&0\\KJ_0(D-I)-H&KH\end{pmatrix}.
\]
On an N-port amplitude the first bank of that defect is \(-Ka\). If two N-port
diagonal entries of \(T\) differ, no scalar \(\lambda\) satisfies \(-Ka=\lambda a\)
for every such amplitude. If they agree at \(t\), then \(\lambda=-1/t\) works
on the image of \(H\) and still fails as soon as a complementary port is
present. The ordered conjugated correction \(L_TPL_T^{-1}\) does intertwine
\(L_T\); the literal slots require the extra conjugation by \(\Pi\).

The block multiplication is in [PROOF.md](PROOF.md). `verify.py` recomputes it
over the rationals on one \(4\times 4\) witness with unequal N-port scales and
a noncommuting \(D\), on the constant-scale sharpness case, and on the two
dropped hypotheses (commutation, idempotence).

## Scope

Task `p104-side-correction`, scope **changed**. The card asks for a
chronological correction program with a complete bill. Comment 19034066 is
item 4 of this session's eligible handoff list, and the list has fewer than
21 entries, so the session refines that item instead of constructing the pair.
The refinement is the commutator, not a caller.

Base `bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6.
PR #3954 already records these block formulas for the P104 shapes
\(H=\mathrm{diag}(0_8,I_{96})\) and checks them inside its full root census.
This package separates the dimension-free identity and the scalar obstruction
from that census. It does not import PR #3954.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-literal-slot-defect
```

Direct check:

```sh
python3 -B research/p104-literal-slot-defect/verify.py
```

Expected marker:

```text
PASS_P104_LITERAL_SLOT_DEFECT ordered=general literal=projection_and_commutation distinct_scales=no_scalar constant_scale=-1/2 pi_required=1 no_new_kappa
```

The same command passes under `-O`. Not run: Lean, Docker, a selected cold
replay, the 10,816-line census, and hosted CI.

## Open next questions

1. Does one adjacent pair that uses \(\Pi P_{\mathrm{enc}}\Pi\), rather than
   \(P\), match every helper role as well as both data banks, and is the
   resulting bill favorable? The scalar obstruction does not answer that.
   First step: pin one helper entrance and exit from the PR #3954 endpoint
   and price \(\Pi\) as a real slot exchange. Blocker: this identity has no
   helper schedule and does not convert linear rank into a native tariff.
2. Which portwise diagonal corrections, other than \(K\) on the image of
   \(H\), can cancel the first bank for every N-port amplitude? The identity
   says the first bank is exactly \(-HKa\), so any such correction is fixed
   on that image. First step: state the allowed diagonal alphabet and test
   it on two distinct N-port scales. Blocker: a new alphabet is a different
   contract from the old correction \(P\).

## Credit

The block shapes, the literal swap \(\Pi\), and the P104 reading of \(H\) and
\(T\) are Chris R / Clear1nsight's PR #3954, from the handoff in discussion
#1166 comment 19034066. That package retains the PR #3882 / #3940 residual
boundary and the native P104 lineage (Rohan Arun, Chafik Boukhalfa, Adam Gall,
and the contributors named there). The dimension-free expansion, the scalar
obstruction, and these checks are new.

Prepared by unpaidmoon with substantial AI assistance (Cursor Grok 4.7).
Apache-2.0. No independent human or formal-kernel review is claimed.
