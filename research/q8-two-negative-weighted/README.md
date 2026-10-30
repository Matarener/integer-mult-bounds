# Exact weighted tariffs for two negative Q8 targets

This package closes PR3487's stated weighted-price obligation. In its positive-only formal `F2[Q8]` model, every negative-generator pair and every two-negative/one-positive generator triple has the exact tariff

```text
alpha*s_i + beta*s_j + 4*min(alpha,beta).
```

The prices alpha for i and beta for j are arbitrary nonnegative reals. The counts `s_i,s_j` include the corresponding negative generators zi,zj. Any finite number of additional roles may start dirty and must return unchanged. Paid calls are binary rank-one idempotents, and only binary scalar GL mixing is free.

The stronger new result is the complete Pareto-minimal class-count set `s+(0,4), s+(2,2), s+(4,0)`. Every legal word, however long, dominates one of these three attainable vectors. Thus a longer cheap-class word cannot evade the bound. PR3487 supplies the unit minima; this package adds the count antichain and weighted corollary, rather than claiming a new unit minimum.

For three negative-generator targets at exactly three total roles, PR3471's retained nine-call result gives four count vectors `s+(0,6), s+(2,4), s+(4,2), s+(6,0)` and tariff `alpha*s_i+beta*s_j+6*min(alpha,beta)`. Extra workspace is outside this three-negative claim.

[PROOF.md](PROOF.md) gives the unbounded domination proof. Separate first-order label ranks and trace parity combine with the retained total call minima. Squaring either positive generator supplies the central sign z, so coordinate words attain every listed vector. The exact rational implementation and independent faithful dirty-column checker are in [tariff.py](tariff.py) and [oracle.py](oracle.py).

## Evidence and source retention

[RESULT.json](RESULT.json) records 212 target/layout fixtures, 644 frontier words, 2,120 rational price cases including zero and unequal prices, 153,280 faithful dirty-input columns and 4,464 deleted-call controls. It also checks 60,608 bounded integer domination cases and 10,666 first-order equations on 5,333 short words. These finite fixtures corroborate the written proof; they do not establish arbitrary width by extrapolation.

A separate signed-axis action is compared with the retained Hamilton group table and with full formal products on every short two/three-role word in the recorded domain. The receipt reports its exact word and column counts. Four optimized behavioral groups reject actual producer omissions, incorrect cheap-class choice, dirty leakage, multiplication/action faults, invalid domain/prices/counts, retained-source drift and receipt overwrite.

The full proof and executable unit-minimum dependency from PR3487 head `d4cf740ed66ca0b7ed82098272e0507eb1c8390d` are retained unchanged under `inputs/pr3487/`. [inputs/RETENTION.json](inputs/RETENTION.json) binds all eighteen source files to their original paths, Git blobs and SHA256 hashes. The nested directory preserves its original relative input layout, so its verifier runs unchanged without Git or a foreign pending commit. This is an executable proof dependency, not a provenance-only duplicate. The nested historical metadata and comparison receipts remain unchanged; the outer SOURCES.json pins only canonical ancestry.

The retained native engine replays all original exclusions, including the three-role three-negative query. Its two largest complete membership streams still use one native implementation. The Hamilton implementation independently checks its stored balls, probes and smaller pair meets; a second complete largest stream is unclaimed. Source retention and replay are not independent human review.

## Reproduce

Use CPython 3.12 and a C++20 compiler. No third-party Python dependency is required. Set TMPDIR to a private existing directory outside the checkout.

```sh
python3.12 -Werror -B scripts/research_package.py \
  --package research/q8-two-negative-weighted
python3.12 -I -O -Werror -B research/q8-two-negative-weighted/verify.py
python3.12 -I -O -Werror -B research/q8-two-negative-weighted/test_package.py
```

The registered hook uses isolated scientific commands. The verifier compiles the exact retained native source with strict warnings and uses private temporary outputs. Publication helpers use ordinary import mode.

```sh
python3 -Werror -B scripts/check_research_commit.py \
  --package research/q8-two-negative-weighted --check-source-history
python3 -Werror -B scripts/export_research_package.py export \
  --package research/q8-two-negative-weighted --output "$RUN/package.tar"
python3 -Werror -B scripts/export_research_package.py check "$RUN/package.tar"
```

For a Git-free replay, extract regular archive members into a new private directory and run the package's verify.py and test_package.py with the same isolated optimized flags. The sources and retained dependency are fully included. The outer canonical catalogue/selected-record pins are provenance; there are no external live inputs. See [VALIDATION.md](VALIDATION.md) for environment, bounds, controls and limitations.

## Open next questions

- Does the three-negative nine-call minimum survive arbitrary finite restored dirty workspace? Start with a five-role exclusion through seven calls or a sign-sensitive proof that avoids a larger census. PR3487's reduction alone reaches five roles. The present weighted corollary does not answer this.
- What is the exact tariff with four independently priced signed generators? Start with a literal count witness beyond the two class prices and state which signed labels are legal. The present positive-only class-count floors do not classify that alphabet.
- Does an actual caller benefit after physical compilation? Supply its eight-block layout, projector sequence, ownership, routing and consumer, then compare the full bill with its direct alternative. No caller or favorable complete physical bill is supplied here, so another dependent construction round is not justified by this result alone.

## Credit and limits

PR3487 retains credit for the two-sided workspace reduction and uniform unit minima; PR3471 for the finite exclusions and three-negative three-role minimum; Tuafo/PR2900 for image restriction; ywz65/PR2587 for support-rank/Sylvester and separate label sums; PR3450 for the combined Q8 character; PR3460 for the one-negative boundary; and Aaron Wang/PR2318 for the two-role values. The retained files preserve Cinna Davis, steph4n-gh, eumemic, Ali Romman, Gareth Davidson, Navinor, woklerx, waynenilsen and the register-model lineage. Arham Tahir/PR3137's physical compiler and PR3461's scalar preparation remain separate.

This is a scoped computer-assisted theorem under the stated formal operation model. It supplies no physical supplier, new kappa, selected-frontier update, or full multiplication theorem. The selected full cold replay, Lean, physical caller/hosting/precision and all-size transfer are unrun or outside scope. Independent human and formal proof-kernel review are unclaimed. New contribution by Nick Petalas under Apache-2.0.
