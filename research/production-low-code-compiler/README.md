# Direct production low-code compilation

The actual historical physical complex controller fixes
`q*=213*2^80+1`, but its retained `LowCodes` trial-divides through q and
scans up to q symbols at every coordinate. This package replaces those
scans with exact closed-form prefix counts and inverse interval selection.
It preserves the source's complete lexicographic GL codes, mixed-radix
encoding, request/view tags and code width.

The all-size source-equivalence proof and conservative compilation bound are
in [PROOF.md](PROOF.md). For dimension d, L=ceil(log2(q+1)) and
B=d²L+ceil(log2(2R+1))+2, the bit-work upper bound is
`O(d^4 L³ log(d+1)+d B²)` and mathematical working storage is `O(d²L+B)`.
These are offline compilation costs, not a fixed-tape runtime tariff.
The existing PR2234/controller witness7 certifies the selected prime; this
package reuses that certificate in constructor admission.

The verifier compares all48 GL2(F3),480 GL2(F5) and11,232 GL3(F3) matrices
with the unchanged source. A separate determinant enumeration checks the
complete GL2 ordering. Every reachable small prefix checks the interval
formula, including a zero-length exceptional interval. Three genuine
q*GL64 classes exercise endpoints and a seeded dense ordinal. Each rank/unrank
pair uses8,192 direct coordinate visits; the receipt also records the
field-sized alphabet counts that the old source would perform.

The actual nested production archive chain is authenticated through
PR3087→PR3055→PR2899→PR2809. Unchanged `Catalogue.low_classes` and
`compile_route` source definitions consume the new codes at q*, d=64;
the latter compiles a fixed integral shear and its complete target code.
These are bounded source-slice consumer checks. They do not instantiate
all requests, construct the complete factory or execute a production payload.

```sh
python3.12 -B scripts/research_package.py --package research/production-low-code-compiler --check-only
python3.12 -B scripts/research_package.py --package research/production-low-code-compiler
# Direct replay also works in a checked Git-free declared-input export:
python3.12 -I -O -B research/production-low-code-compiler/verify.py
```

Default replay is read-only and requires byte-exact typed RESULT equality.
`--write-result` writes only a missing result. Scientific controls reject
invalid certificates, composite/uncertified fields, invalid codes and dependent
matrices; an omitted exceptional subtraction and Fermat-only primality test
have explicit falsifiers. Separate CLI controls reject missing/changed
sources and altered typed receipt bytes. Assertions are not used for gates.

The eager outer macro tuple and complete GL64 execution remain open. This
historical R480/T16 controller is not the newer selected PR5413 native
supplier. No recursive invoice or runtime arithmetic is changed; no new κ,
full multiplication theorem, practical complete factory or tape-space
reclamation is claimed.

## Open next questions

Can the outer macro schedule be compiled without complete materialization
while preserving exact PCs and chronological dispatch? Start from actual
`compile_node`, its low-class loops and the separately investigated regional
Cursor emitter. Variable residual lengths and complete runtime/header costs
remain the blockers.

Can the full source request/chart preparation be built at q*? First isolate
and authenticate that phase, then identify every remaining eager construction
site. The current compiler closes only its low-code prerequisite. Structured
questions and the changed task scope are in [TASK.json](TASK.json).

## Attribution

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Jose Manuel supplies the GL lexicographic ranking and source packet proof,
`Constraints`, original low-code and physical caller/ordinary/complex engines;
all unchanged source notices remain in their pinned archives. The current
work adds closed prefix formulas, direct selection, certified admission and
source-equivalence/cost evidence, not a new GL ranking construction or prime.
PR2234 supplies the fixed prime certificate. The physical caller retains
Douglas Colkitt's selected source, David Arias, Nick Petalas, Adam Gall,
Aakash Thakkar and the predecessor authors credited in the retained archives.
No independent human or formal-kernel review is claimed.

Canonical investigation:
[Discussion2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-19173180).
