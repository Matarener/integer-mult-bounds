# Prime supply for the actual many-axis tensor caller

This supplies the odd, pairwise-coprime source lengths explicitly left open by [PR4024](https://github.com/CrocSwap/integer-mult-bounds/pull/4024), bound to [PR3935](https://github.com/CrocSwap/integer-mult-bounds/pull/3935)'s actual `TensorPlan.production_axis`. It repairs one parameter-regime implication; no new κ or complete supplier is claimed.

Let D be the actual scalar-axis count, d=D+1, and targets be 2^ell or 2^(ell−1), with the final axis full. For **ell≥2^32, 2≤d≤ell^334** and **target_halo+2w≤2^(ell−3)**, choose distinct primes from each interior interval `(t(1−1/(3d)), t(1−1/(4d))]`. Each interval contains at least D primes; every chosen length meets the complete source ratio/period guards, and the full product ratio satisfies **T/S<3/2<2**.

[PROOF.md](PROOF.md) derives the effective sufficient domain from Fiori–Kadiri–Swidinsky [Corollary22](https://arxiv.org/pdf/2206.12557v2), an imported analytic theorem. It proves a conservative uniform fixed-tape trial-division/list construction with `O(r² ell²+D ell)` steps and `O(D ell+ell)` visited backing for the source-length producer, r=2^ell, including sequential output and scratch/head restoration. Under the retained D=Theta(p^.997), ell=Theta(p^.003), V≥2^(cp) laws this setup is 2^o(p)=o(V). An explicit p cutoff needs the fixed growth/halo constants. The (ell,d) cutoff is intentionally enormous, not a practical search target.

The old source08/Cinna Davis selector uses `log(t)>8d`, valid eventually in its original small-dimension family. It does not directly cover this newer family, where log(t)/d→0. Chafik's PR1786 and JosieElliston's audit already use explicit PNT error bounds for fine intervals; the new result is the exact newer-caller binding, guard-safe band, explicit sufficient domain and complete ordering/product/setup argument.

## Evidence and boundary

The executed program is a **host-integer finite reference**, `encoded_execution=false`. It authenticates five retained files before extracting the complete source `production_axis` AST and checking it with a semantic Count adapter. It does not import or run the predecessor numerical engine or encoded arithmetic runtime. The fixed-tape algorithm and its bill are written constructions, not literal encoded executions.

Five small coprime cases cover both target scales, repeated scales, nonmonotone flags and final-axis ordering. An independent checker imports no primary executable and reconstructs primes with Eratosthenes, exact predicates, product and emitted source/flag hashes. The primary includes8 internal controls; the separate suite checks50 expected rejections and5 positives. See [RESULT.json](RESULT.json), [INDEPENDENT.md](INDEPENDENT.md) and the executable checks. These corroborate the finite reference and symbolic inequalities; they do not reprove the imported analytic theorem or execute giant primes.

Unrelated `production_common` Gaussian/precision/separation policies, numerical tensor composition, native premises, CRT integer recovery and final normalization, complete physical reserve/stock, supplier integration and frontier admission remain open. The repeated7×7 predecessor fixture remains conformance evidence and is not repurposed as coprime production supply.

## Reproduce

Python3.12, standard library; no network, Git, external inputs or package writes are required at replay. All5 source exports are local and pinned by byte size, SHA256 and Git blob in [SOURCES.json](SOURCES.json) and [SOURCE-PINS.json](SOURCE-PINS.json).

```sh
python3.12 -B scripts/research_package.py --package research/many-axis-prime-supply
```

From a Git-free package export, run `verify.py`, `independent.py`, and `test_verify.py` with Python3.12 and `-B`. The default independent command checks the colocated complete primary receipt. All commands also work with `-O`. The huge threshold is checked symbolically without forming 2^(2^32) or an axis list of that size. [TASK.json](TASK.json) records the changed task scope, overlap coverage, cutoff and remaining questions. The historical selected-record/catalogue pins are provenance, not runtime inputs.

## Open next questions

1. Lower and admit the written sequential prime producer at the actual encoded `TensorPlan`/CRT interface. First review the full source/head/output contracts and period premise; literal production implementation and complete caller integration are blockers.
2. Complete numerical tensor composition and integer recovery under the actual policies. Coordinate with Jose Manuel's [Discussion3664 clarification](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19036660), retaining the total gamma and both final S factors. Prime supply alone does not discharge those obligations.

## Credit

ToikY prepared this source binding, proof and checks with substantial OpenAI Codex assistance and separate AI review contexts. Credit Jose Manuel/jmbarrancoml, Tekalign/tekuuu, Cinna Davis, Chafik Boukhalfa, JosieElliston, Fiori–Kadiri–Swidinsky, source08/OpenAI manuscript/Douglas Colkitt, Harvey–van der Hoeven and Agarwal–Cooley. Frozen exported READMEs retain the deeper lineage. [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE) preserve attribution and Apache-2.0 terms.
