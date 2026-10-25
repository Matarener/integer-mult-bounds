# Generation scripts (not needed for verification)

These scripts produced `CERTIFICATES.json.gz` and `CERT-INDEX.bin.gz`. They need numpy 1.26 and
scipy 1.13, and were run from a scratch directory containing a repository checkout at `imb/`.

1. `quad.py` computes the tariff classes of all quadruples (`quad_classes.pkl`). It then screens
   them with the block-rank LP and writes `quad_weak.pkl`.
2. `phitable.py` builds the zeroed-block bound table, `phitab4.npy`.
3. `quad3.py <chunk> 12` solves the zeroed-block and mixed LPs for the weak classes, first over
   subsets of the cheap cross pairs and then over all 4096 zero sets.
4. `fastcheck.py` holds the exact checker shared with `verify.py`.
5. `gen_quad.py` rationalizes every certificate, checks it exactly, deduplicates, and writes the
   two artifacts.

`verify.py` re-derives the tariffs and the bound table itself, and trusts nothing produced here
beyond the certificate data, which it checks exactly.
