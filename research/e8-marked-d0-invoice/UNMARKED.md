# The unmarked d=0 invoice

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Unmarked intrinsic invoice

Retain the [PROOF.md](PROOF.md) definitions of C, S, the actual basis F,
its nonzero restricted duals x_j, T=S_{<=7}, and the correction count n_c.
Assume dim S=8+t, t in {2,3}, and C intersect T=0. No marked row or word g
is required. Then

    I = sum_(q in F) w(q)-n_c >= 64.

Proof by contradiction: assume I<=63. For f=|F intersect T|, PROOF.md
Section 4 gives I>=56+7t-6f. Since f<=dim T<=t, f<t would give
I>=62+t>=64. Thus f=t=dim T, S=C direct-sum T, and the actual basis has
t low members b_a and eight high members q_l=p_(h_l)+tau_l with
w(q_l) in {8,9}. The h_l form a basis and their duals mu_l are the
restricted high functionals. In particular corrected high frame indices
are distinct, and the actual map satisfies

    A(h)=-sum_a x_a(h)b_a.

Use the marked proof's notation Sigma,c9,c9_corr,n8,nT,d9. The exact ledger
and the trivial count n_c<=8+t now give

    I=64+Sigma-nT-n8+d9,
    nT+n8 >= Sigma+1+d9,                 (U)
    Sigma+c9 = sum_F w-64 <= 7+t.       (V)

Only these inequalities differ from the marked proof. The one-unit
strengthening in (U) replaces every use of the marked low row.

We use the following elementary obstruction whenever all eight highs are
corrected AND have weight eight (c9=0). Their normals h_l are their own
matched frame axes, up to nonzero scaling. Let L be the set of frame indices
of the corrected lows.
For a frame axis a outside L, the coefficient formula shows A(f_a) is a
combination of the uncorrected low members only. If their union support
has fewer than24 points, the corresponding corrected high contradicts
G2's matched carrying cut24. There is always such an axis when |L|<=3.
If every low is corrected, that union is empty.

The upper boundary cases are as follows.

* t=2, Sigma=9: (V) forces c9=0. Since nT<=2,n8<=8, (U) forces
  nT=2,n8=8. Every low and high is corrected; use the preceding obstruction.
* t=3, Sigma=10: similarly c9=0,nT=3,n8=8, and every member is corrected.
* t=3, Sigma=9: a corrected low costs at least3, so nT<=3. If nT=2,
  (U) forces n8=8,c9=d9=0. The sole uncorrected low has weight at most3
  and support at most4. The all-high obstruction applies outside the at
  most two corrected-low frame indices. If nT=3, all three lows have
  weight3 and support3, so the union support has at most9 points.
  Inequality (U) gives n8>=7. Actual high duality confines each corrected
  high normal to at most two frame axes; PROOF.md Lemma3.1 excludes it.

Thus Sigma<=8. At Sigma=8, at most two lows can be corrected, so (U)
gives n8>=7. Every positive actual low profile other than (7,1) has union
support at most22 by PROOF.md Section 7's list. Duality confines
every corrected high normal to at most two axes, so Lemma3.1 excludes
these profiles. In profile (7,1), nT<=1 and (U) force nT=1,n8=8,
d9=c9=0. The weight-seven low is corrected and the unit low is
uncorrected. The all-high obstruction applies outside the one corrected
low frame index, since the uncorrected support has size1.

Thus Sigma<=7. At Sigma=7, PROOF.md Section 8 gives n8<=4: its argument
uses only cost(T)<=7, dim T>=2, root-only Theorem C, the support bound21,
and actual high duality. It does not use the mark. Also nT<=2. This
contradicts (U), which requires nT+n8>=8+d9.

For Sigma<=6, [SMALL.md](SMALL.md) Sections 3-8 already prove I>=64
without the mark or g. Precisely, root-only classification gives n8<=4;
Sigma=6,5 and Sigma=4,nT=1 are excluded at I<=64 by Sections 5-7,
using the actual coefficient map and carrier arguments. In the remaining
cases nT=0 and the eligible-root rank bound gives n8<=cost(T)<=Sigma,
so the exact ledger gives I>=64. All are contradictions to I<=63.
This proves the unmarked theorem.

## Scope and sharpness

No marked root or word g is assumed. The conclusion is I>=64. The existing
exact I=64,epsilon=1 omitted-g control attains this floor and disproves the
unmarked claim I-epsilon>=64. The marked theorem remains necessary for a
free singleton pivot with a possible rebate; [CONSUMER.md](CONSUMER.md)
derives that distinction from actual factors.

This proof is characteristic-zero written mathematics using the same
declared geometric inputs as PROOF.md. The finite controls and generic Lean
cores do not formalize its complete case assembly.
