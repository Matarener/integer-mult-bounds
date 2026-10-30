# Retained predecessor inputs

These two gzip files are unchanged predecessor data, not new constructions.
They are retained so the new obstruction checker has a small, self-contained
source closure. Both compressed byte hashes are enforced before decoding.

Source: [PR5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569),
head `af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf`:

| Retained file | Original repository path | Compressed SHA256 |
| --- | --- | --- |
| `pr5569-WORD.json.gz` | `research/p104-priced-handoff/WORD.json.gz` | `12224e9a13a49c830b304338a8d31610fb43da15d1a650537733c27f7864310f` |
| `pr5561-WORD.json.gz` | `research/p104-priced-handoff/inputs/pr5561-WORD.json.gz` | `b3701d78bee3661382ebe5414e678dfc9ee292e254cb9dc56339c2d2f45fdf44` |

The second file is the PR5561 headline word retained by PR5569. It supplies the
known 706/173 successful cleanup as a positive control; it is not our baseline.
The package's standard provenance pins refer to the retention commit in its own
published history. Original source paths and head are attribution and audit
information, not a claim that a foreign PR commit is an ancestor of this PR.

Credit: Joel Pulikkan (GamingPuzzled), with Claude Opus 5.5 assistance, for
PR5569; DreamingOfClouds for PR5561 and PR5553; thu-nmrc for PR5551;
aliromman for PR5544/5545; David Arias, Cinna Davis and Gareth Davidson for the
retained local verifier lineage; zxv for the productive-helper paradigm and
PR5554; Cao Yifan for PR4610 native semantics; GamingPuzzled for PR5472.
The source credits PR2305/2152/2219 as earlier lineage. Apache-2.0.
