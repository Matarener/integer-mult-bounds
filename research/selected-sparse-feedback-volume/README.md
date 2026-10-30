# Sparse feedback needs arithmetic volume, conditioning, or native-cut entropy

For the selected coupled boundary `(C_f x+B_f y/2,y)` with restored auxiliaries,
this package proves a genuine sparse-coordinate necessary condition:

    8 K S + Re(Delta_Q) >= f V / 2.

Here S counts actual updated coordinates in all scalar ADDs, K bounds every
full-machine prefix condition number, and Delta_Q is an explicitly defined
preconditioned-entropy jump across the sole native call. Variable-sized masks,
arbitrary feedback and mixtures, arbitrary dirty restored auxiliaries and
clean returned auxiliaries are included. Routing/scaling maps are granted free
in this lower bound; their physical invoice remains additional.

If the rank2f target child runs before arithmetic, with only payload-preserving
monomials before it, its jump is zero and **S >= fV/(16K)**. A constant-K
child-first adapter therefore costs Omega(fV), including sparse implementations.
The general interleaved or ill-conditioned sparse family remains open. No
coefficient-only premise, unconditional arithmetic lower bound, new selected
profile, supplier admission or kappa improvement is claimed.

The distinction matters: PR4009 proved a count of full-array passes. Multiplying
that count by V is invalid after changing to sparse masks. The present proof
uses a different potential and charges each scalar coordinate update directly.
Ordinary determinant and ordinary quasi-entropy cannot detect the triangular
correction; the block preconditioner here gives exactly fV/2. The proof also
keeps the child's contribution instead of treating a large native operator
as an ordinary scalar gate.

[PROOF.md](PROOF.md) contains the self-contained all-dimension argument. This
adapts Ailon's conditioning/quasi-entropy method and Ailon--Yehuda's
preconditioned potential; it does not claim a new general lower-bound method.
The novel scoped part is the chosen coupling preconditioner, its exact boundary
value, the explicit native jump, and the complex coordinate-shear/restored-clean
auxiliary extension. Two same-team AI proof reviews found no issue; this is
not human peer review or formal-kernel acceptance.

## Evidence and reproduction

Python3.12 standard library only:

```sh
python3 -B scripts/research_package.py --package research/selected-sparse-feedback-volume
```

The registered normal and optimized runs check exact Gaussian-rational
endpoint fixtures at f=1,2, all32 complex two-row column invariants in a
four-shear fixture, nonunit monomial invariance, and a clean-auxiliary fixture
with unspecified off-domain input behavior. An explicit interleaved native
call has jump1+i, so the zero-jump corollary cannot be silently generalized.
Five controls reject a wrong preconditioner orientation, omitted native jump,
clean-output leakage omitted inverse-dual conjugation and noncommuting BA/AB substitution. Exact logarithms
in these fixtures use only power-of-two squared norms. The quantified entropy
inequality is a written proof, not inferred from these examples.

The verifier is standalone and requires no network or pending-PR checkout.
Its matrix fixtures check the theorem's algebra, not a new native lowering.
PR4009 at `89a358aac11d11e0539eb95c27600e7677be7ce4` supplies the prior literal
195/521 binding and all-f Pauli identification. The application here explicitly
inherits that identification. The abstract theorem holds for any unitary A,B
with the stated B-row flatness. No frozen predecessor is copied or changed.

## Open next questions

1. Can a genuinely interleaved candidate make Re(Delta_Q) large enough while
   keeping its paid preparation volume and conditioning small? Compute the
   proposed native-cut matrices and this potential first; a bound on that
   jump is the missing step for a broader obstruction.
2. Can an ill-conditioned sparse proposal improve the complete cost after
   precision and restoration are charged? Supply a bound on the full prefix
   condition numbers and an actual error/bit invoice. The theorem does not
   equate a growing K with a specific number of extra precision bits.
3. What cost model admits variable-size native calls or nonlinear preparation?
   Such a change needs its own operator and paid boundary before extending
   this one-child linear model.

## Sources, overlap and credit

Scientific base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority6. Parent
entry intake at10:46UTC covered733 open PR bodies including drafts and the
latest active1166/1901 coordination; broader discussion coverage was partial.
Live PR4023 (fixed-support unary query bounds) and4027 (H6 U9 compensation)
have different operators and alphabets. Adjacent PR3954's paired-owner P104
normalization discussion uses the earlier full-array bound, not this sparse
volume theorem. This review is scoped overlap evidence, not proof of novelty.
The sibling sparse coordinate-pair construction is a complementary upper bound;
its proof and complete primitive costs remain separately attributable.

Method credit: Nir Ailon, [arXiv:1403.1307](https://arxiv.org/abs/1403.1307),
and Nir Ailon and Gal Yehuda, [arXiv:1604.02557v4](https://arxiv.org/abs/1604.02557),
Section1.1 and Lemma1.1. Boundary credit: [PR4009](https://github.com/CrocSwap/integer-mult-bounds/pull/4009),
[PR3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989), Gonzalo Mier's
[PR3975](https://github.com/CrocSwap/integer-mult-bounds/pull/3975), and their
retained selected/native lineage, including Cinna Davis and the selected1094
sources. New work Apache-2.0. Prepared by Clear1nsight with substantial OpenAI
Codex assistance in research, proof, exact implementation, independent agent
review and packaging.
