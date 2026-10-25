# Complete physical Gaussian expansion tile

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I implement the source-bound normalized Gaussian expansion `S/2` for a
complete target tile. The producer generates directed real coefficients and
ordered factor pages. The consumer executes the actual signed convolution,
keeps the fine grid through normalization, restores scale during final-grid
extraction, and streams overlapping source windows through two short banks.

This closes the coefficient-generation and complete normalized-output
handoff in [Hanson Sun's PR1243](https://github.com/CrocSwap/integer-mult-bounds/pull/1243).
I retain [Artus Krohn-Grimberghe's PR371](https://github.com/CrocSwap/integer-mult-bounds/pull/371)
final-grid correction and the verified physical cohort from
[PR3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851).
The complete tensor/CRT caller remains open. I leave the selected frontier
unchanged and claim no complete multiplication theorem.

For integer `p>100`, integer `2<=alpha<sqrt(p)`, exact `u=alpha²`,
`1<t/s<2`, and the retained production halo domain, I prove conditional bounds

```text
error < (sqrt(2)+2^-11)*2^-p < p²*2^-p,
output norm < 1,
online time O(Lp log²(p+2)), space O(Lp), catalogue O(Lp).
```

I charge coefficient preparation as separate polynomial(t,p) work. A future
bulk caller must reuse those pages with its paid spectator schedule.
The expansion proof does not require `u*(t/s-1)>=1`; the older combined
S/E statement has a narrower domain. [PROOF.md](PROOF.md) gives the exact
assumptions, crop identity, tail bound, arithmetic errors and complete bill.

You can use these public interfaces inside `expansion_sources.opened()`:

```python
producer = TilePreparation()
page = producer.run_production(s, t, d, alpha, p, tile_index)
result = Tile().run(page, source_halo)
```

Parameters are canonical borrowed `Count` values. Supply complex p-grid
records in increasing unwrapped global source order, then zero-pad through
the declared capacity. Consume each protected return before reusing its
owner. The explicit-grid methods support bounded fixtures; they do not
silently inherit the production tail theorem. The consumer requires the
matching producer's Gaussian pages, not merely arbitrary valid framing.

I retain these implementation boundaries:

| Files | Responsibility |
|---|---|
| `expansion_sources.py` | Authenticate the complete prior export, correction archive and common physical cohort |
| `expansion_geometry.py`, `expansion_records.py` | Signed global origins, short stencils, exact factor identity and fine-grid guards |
| `expansion_prepare.py`, `expansion_block.py` | Actual real-coefficient producer and complete normalized block |
| `expansion_tile_geometry.py` | Paired microbox halo and production admission |
| `expansion_tile_prepare.py`, `expansion_tile.py` | Complete ordered catalogue and monotone overlapping-window consumer |

I execute two nonzero normalized blocks and two complete tiles. The tiles
exercise an unchanged source start, a periodic seam, padding and a clipped
last block. I compare them with separate exact staged arithmetic and directed
periodic Gaussian sums, and check the complete word invoices. I also test
nineteen failure/ownership controls and positive reuse. Production checks
exercise encoded metadata at four tiles, including a one-record ceiling
transition; they do not allocate the production-sized P-grid payload.
[EVIDENCE.md](EVIDENCE.md) records the scope, hashes and earlier failures.

Run the eight registered checks with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/physical-gaussian-expansion --check-only
python3.12 -B scripts/research_package.py --package research/physical-gaussian-expansion
```

The manifest allows at most 1180 seconds in total and 450 seconds for its
longest command. For a committed export, follow
[the repository exporter](../../docs/research/package-export.md); the
verifiers work outside Git with the declared inputs. I run the official
launcher to isolate Python bytecode, even with `-I -O -Werror -B`.

## Open next questions

- Can a contributor implement the full tensor caller with canonical global
  coordinate gathers, short mixed-radix moves, periodic halos and page reuse?
  Start with one complete tensor and restore its natural target order before
  invoking PR3763 once. Full-support routing and the physical field-move
  primitive remain obligations.
- Can a contributor join the physical CRT entrance and return to the complete
  Gaussian maps? Start with one interval and check both endpoints and both S
  factors in integer recovery. The complete Gaussian/CRT/integer join remains
  outside this package.
- Can a reviewer validate the quantified source and precision correspondence?
  Inspect the crop, final extraction, small-u-theta domain and inherited word
  recovery against their exact pins. These are AI-assisted author checks;
  independent human or formal-kernel review remains open.

## Sources and credit

I pin canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, in [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).
I retain the pre-implementation decision and status in
[Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664).
The whole PR3851 export has head `7ab67b4a84d28cd562b9711aa315ca5b47822b37`;
the PR371 correction archive has head `988ef67986c313445936fc7103908b6163b9d47e`.
The loader authenticates their bytes, inventory and receipts before import.

I credit eumemic and icekylinx for the corrected real-chirp work; Hanson Sun
for the packed-correlation audit and explicit handoff; Artus
Krohn-Grimberghe for final-grid accounting; Chafik Boukhalfa for the Gaussian,
chirp and locality predecessors; RaD/hipotures for the retained blocked,
microbox and bulk-transfer reports; Mason Hale for the numerical reference;
Dugongue for the word-ABI and inverse precedents; Harvey and van der Hoeven
for the classical multiplication framework; and Douglas Colkitt and the
OpenAI manuscript contributors for the repository sources and research
framework. The complete nested exports retain their additional authors,
licenses and notices. I do not present their work as a new invention here.

OpenAI Codex assisted with mathematics, implementation, source-analysis
agents, tests and prose. I made no independent-human-review claim. This
contribution follows the repository's Apache-2.0 license; retained sources
keep their source-specific notices.
