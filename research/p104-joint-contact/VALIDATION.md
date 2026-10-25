# Validation scope and reproduction

Environment: macOS arm 64, CPython 3.12.13, standard library. Author-side
checks include parallel Codex agents; they are not independent human or
proof-kernel acceptance. No selected record or frozen predecessor is edited.

## Completed scientific checks

1. The exact official 33-file PR5545 export was checked and its full original
   verifier replayed before searching the successor. It reproduced
   `PASS_P104_CONTACT_COMPLETE_KAPPA_00304117`.
2. The successor passed sparse exact forward rows and dense exact reverse
   columns, all 743 rows/552,049 coefficients, all 527 helpers, all 735 arbitrary
   public inputs, eight owned lifetimes and peak one. Scalar coefficients
   and order are exactly unchanged.
3. A separate peer implementation, importing neither constructor nor native
   checker, passed normal and optimized read-only execution. It confirms
   six ADD and fifteen SCALE chart edits, both new contact invoices and
   three real endpoint/chart/owned mutants. Its complete receipt and fixed
   inputs are retained under `peer/`.
4. Fresh native lowering and the separate Gaussian/absolute-phase interpreter
   passed 2,979 maps, 1,054 helper normalizers and 208 main adapters. The source
   phase mutant is rejected. Fresh caller construction and 265-axis physical
   checking passed with all 104 ports, both orientations and the exact
   retained controller.
5. Both full invoice counts, both rational moment engines, strictification,
   compiler grid with rejected predecessor, ordinary/admitted BIT stock and
   all 58 outer predicates passed. Complete paid/target counts are 69,912/12,814.
   The raw crossing lies in (.00304153116714, .00304153116715); tested saving
   is .0030415305; claimed conditional saving is .00304153.
6. The complete publication verifier ran with `--write`, regenerating WORD
   and RESULT and repeating the actual source reconstruction, peer, native,
   caller, price and semantic controls. It emitted
   `PASS_P104_JOINT_CONTACT_COMPLETE_KAPPA_00304153`.

## Registered and cold replay

The registered normal/optimized pair is run with

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-contact
```

The complete verifier passed in normal and optimized modes, comparing all
saved semantic artifacts and executing every listed native/caller/price
and semantic control. The final manifest retains these exact argument
arrays with a 540-second bound each and adds normal/optimized 30-second
funding-review commands. Those two new commands also passed. They use
an independently written third rational interval engine and bind its
audited outputs to this publication. Their science digest is
`611b766fc6bfe599b9ae56d5e78b90f6608b5ed3a14baf1d119ca630a5829c9c`.

Every complete replay compares all saved semantic
artifacts. Compression streams are not mathematical equality checks;
retained immutable source/peer inputs keep their exact byte hashes.
Committed-byte/source-history preflight passed at scientific commit
`5109e17d3f8b7cdc54c01362098d06d622e2fc96`: all43 package files,
canonical source ancestor`32890bc5de034ab8fc93ac88ead7279a6a416d04`.
The official committed export and its integrity checker both passed.

That exact export was relocated to a new directory with spaces, without
Git. Every file was set read-only(0444), PATH was empty and the interpreter
was absolute, isolated and bytecode-write-disabled. All four commands
passed: full normal169.510s, full optimized99.029s, independent funding
normal0.191s and optimized0.150s. All44 exported files including the export
manifest remained byte-identical, with no new runtime files. The normal
and optimized full logs have the same SHA256:
`219d7d9082668896579616e33d4ea65ff4a33d8c3e282f32ae2d2ece100bcde1`.
The two funding logs also match:
`13f7b14d9cdffeebe73b1c8a62dd9d8654df1fd1ab9a9bb1834b7c71164e8c06`.
This paragraph records that completed run; its addition changes only this
documentation, with every scientific code/input/output byte retained.

The scientific core at publication head
`79072da5404a01056df2af2e4132324b01c72366` also passed hosted run
40194668767: plan in 3m55s and full registered replay in 8m18s, with committed
inputs unchanged. This is a historical exact-head result, not a claim about
later heads or scientific adoption.

The subsequent verification-only appendix leaves WORD, RESULT, pricing,
source capsule and complete construction code unchanged. Its four-map
dense audit passed normal/optimized read-only replay in 2.23/2.15s. Each mode
checks all 2,048 columns and 1,048,576 complex entries, phase/sign/boundary/rank
controls and source pins. The parent wrapper additionally binds it to this
publication and checks two actual temporary source corruptions before
import. It registers two extra 30-second commands; all six declared command
timeouts total 1,200s. The source arithmetic interpreter is credited
unchanged reuse from PR5548, not a newly authored independent engine.

The bound native wrapper at scientific appendix commit
`b8581ee21af9b4bde69112ad6f5b921bb9f34c68` also passed an official-export
cold replay: new path with spaces, files0444, no Git, empty PATH, absolute
isolated Python. Normal/optimized runs took2.286/2.203s and produced
identical stdout SHA256
`754f8bd5d5d3bc31acbea201f5705cdfcab9da3693e05d24afd5019b52d24e68`.
All69 exported files including the manifest remained byte-identical.
The wrapper makes only its own temporary mutation copies writable.
Of the previous43 files, only README, PROOF, VALIDATION and VERIFY changed;
all earlier scientific code, inputs and outputs stayed exact. This final
paragraph is a documentation-only record of that completed cold run.

## Limits

All five framework premises in PROOF.md remain. Native algebra is checked
without materializing exponential-size matrices. The uniform compiler word,
rounded integer multiplier and machine tape are not materialized. A passing
certificate, package runner or CI job does not establish scientific adoption,
selected promotion, a complete multiplication theorem or contributor status.

Retain the predecessor and new-work attribution in README.md/PROOF.md.
