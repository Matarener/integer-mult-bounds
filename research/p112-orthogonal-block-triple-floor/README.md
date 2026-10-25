# An orthogonal block refinement of the triple-reader floor

The [proof](PROOF.md) establishes the sharp original tariff for every exact
at-most-four-term realization of three alternating-half indicators over any
field, with arbitrary ambient factors, under an explicit orthogonal block
contract. The three distinct target groups may have unequal sizes and different
binary spans. Each group must contain either a complete Gram-I basis of a block
or none of it, and each complete plane must stay inside one block. Bases and
plane pairings may differ within a shared block.

If n_k counts the binary dimension present in exactly k groups, the new residual
bounds are VVV >= n_1+3n_2+3n_3 and MMM >= 2n_1+3n_2+3n_3. The original bill is
D=n_1+2n_2+3n_3. The residual bounds are sharp over allowed basis choices. This
extends [PR3549](https://github.com/CrocSwap/integer-mult-bounds/pull/3549)'s
common-span result within the stated block contract; general different spans
remain open. It is a scoped obstruction, with no supplier or kappa claim.

[RESULT.json](RESULT.json) records all 11,856 complete assignments across eight
fixtures. Two implementations match every charge stream and histogram; the
separate implementation also checks exact integer coefficients and gauged
finite-field identities. The written proof supplies the all-dimension claim.
[VALIDATION.md](VALIDATION.md) describes coverage and limitations.

From the repository root, using CPython 3.12 and an existing private TMPDIR:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-orthogonal-block-triple-floor --check-only
python3.12 -Werror -B scripts/research_package.py --package research/p112-orthogonal-block-triple-floor
python3.12 -Werror -B scripts/check_research_commit.py --package research/p112-orthogonal-block-triple-floor --check-source-history
```

The five scientific/control commands in [VERIFY.json](VERIFY.json) also run from
a Git-free export containing the package and its declared inputs. No network or
third-party Python dependency is needed. Source closure includes both retained
pending proofs with origin commit/path/blob/SHA256, and canonical classification,
selective-map and support-transfer proof/runtime inputs in [SOURCES.json](SOURCES.json).
Origin commits document credit; replay does not require their foreign Git objects.

## Open next questions

- Remove the orthogonal block-refinement or complete-plane compatibility premise.
  First derive a rectangular rank inequality for one nonreducing pair of spans,
  or give an exact lower-cost factorization; the exploratory random sample is
  not evidence of a universal exclusion.
- Determine when the residual bounds are attainable for arbitrary different bases
  inside shared blocks. Compare the exact annihilator constraints of one
  noncommuting example; no such classification is supplied here.

The original broad hypothesis, narrowed deliverable and scope history are
recorded in [TASK.json](TASK.json). Physical execution, native acquisition,
restoration, hosting, precision, stock, compiler/all-size admission and complete
supplier/outer obligations remain open. Independent human and formal proof-kernel
review are unclaimed.

Nick Petalas. Apache-2.0. Credit to PR3549, PR3538, PR3513, PR3505, Philippe Van
Velzen/Arham Tahir's expanded-identity method, Tekalign/PR3370 and the retained
P112/E8/native/compiler lineage in the source proofs.
