# F2-right-vector diagonal minimum

**Exact paid-call minimum.** For every \(\mathbb F_2\)-algebra \(R\) and every finite register count \(n\), a product of factors \(I+uy^T\) with \(u\in R^n\) and \(y\in\mathbb F_2^n\) equals a diagonal matrix only when the number of factors is at least the number \(t\) of diagonal entries different from \(1\). The coordinate factors \(I+(d_i-1)e_ie_i^T\) attain \(t\). The same count is exact for every finite group algebra under the narrower legal alphabet \(I+(g-1)xy^T\), including nonabelian groups and labels in \(1+\mathfrak m^2\).

The right-vector restriction is sharp. Over \(\mathbb F_2[z_1,z_2]/(z_1^2,z_2^2)\), one outer product with right vector \((z_2,z_1)\) equals \(\operatorname{diag}(z_1z_2,z_1z_2)\), so \(t=2\) drops to one factor. **No new kappa.** Selected \(\kappa\) stays `0.001672660197076918`.

Prepared by Wentao Li with substantial AI assistance.

## Scope and evidence

Original card: `bit-new-register-model`. Scope status: **changed**. The card asks whether a larger or nonabelian register model escapes the three-register obstruction. This package answers a different question: the diagonal minimum for the \(\mathbb F_2\)-valued right-vector alphabet on an arbitrary \(\mathbb F_2\)-algebra. The written argument is [PROOF.md](PROOF.md). [RESULT.json](RESULT.json) records the finite controls: 256 Klein multiplier pairs agree, 1,049,600 Klein words have 0 span failures and 0 diagonal violations, the binary-right-vector one-factor save count is 0, and 19,740 length-at-most-2 words in \(\mathbb F_2[S_3]\) have 0 violations. The three-transposition coordinate word attains 3.

## Pin search

Base `bb4bccbf42844d2801487450727c2f63e10d1d0f`. The chain-ring product theorem in `research/bit-cyclic-root-barrier/PROOF.md` assumes \(R=\mathbb F_2[z]/(z^q)\) and allows right vectors with entries in \(R\). It states that the column lemma is not asserted for arbitrary group algebras, and its Klein witness \(U=(x,y)^T\) is a socle-dimension counterexample, not a shorter legal diagonal. A search of that proof finds no statement for every \(\mathbb F_2\)-algebra. `research/bit-one-relation-any-registers/PROOF.md` is the torsion-free rational-frame model and says a finite torsion representation cannot replace its hypothesis. Neither note implies the count above: the chain-ring conclusion is false for the displayed ring-valued right vector, and the one-relation lemma does not apply to \(\mathbb F_2[G]\).

This is not a cyclic root-lift census and not a graded-image argument. Identity coordinates are restored dirty roles. Free \(\mathrm{GL}_n(\mathbb F_2)\) changes of basis are outside the alphabet.

## Reproduce

From the repository root:

```sh
python3.12 -I -O -B -W error research/f2-right-vector-diagonal-minimum/verify.py
python3.12 -I -O -B -W error research/f2-right-vector-diagonal-minimum/test_verify.py
python3.12 -B scripts/research_package.py --package research/f2-right-vector-diagonal-minimum
```

Expected:

```text
PASS_F2_RIGHT_VECTOR_DIAGONAL_MINIMUM klein_words=1049600 s3_words=19740 violations=0 sharp_factors=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/f2-right-vector-diagonal-minimum outcome=completed
```

Default verify is read-only and compares [RESULT.json](RESULT.json). `--write-receipt` refuses to overwrite. Admission uses `need()` and still fires under `-O`. `test_verify.py` multiplies the Klein ring and \(S_3\) with its own coefficient and permutation code.

## Open next questions

1. Do free \(\mathrm{GL}_n(\mathbb F_2)\) changes of basis between paid factors realize a diagonal with fewer than \(t\) factors? The column argument evaluates \((P-I)\) on the standard basis, so a basis change can move the endpoint out of that coordinate frame. A first step is the \(n=2\) alphabet with every change of basis and length 1. The blocker is the missing invariant, not another order-at-most-16 group-label search.
2. Native frame, hosting, and precision bills remain unpriced. A first step is a single legal coordinate word with an existing supplier meter. The blocker is that this note has no physical schedule.

## Credit

Credit the chain-ring diagonal theorem and the Klein socle witness in `research/bit-cyclic-root-barrier` (merged as [#2513](https://github.com/CrocSwap/integer-mult-bounds/pull/2513)), and the torsion-free boundary in `research/bit-one-relation-any-registers`. Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao), [@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under Apache-2.0.
