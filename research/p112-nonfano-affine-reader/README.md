# Full affine readers do not cheapen the fixed non-Fano decoder

For the four fixed query rays a+b, a+c, b+c, a+b+c, no choice of actual readers
beats the original three-term complete-plane tariff on any of the 4,960
literal PR3370 target triples. The result covers every coefficient field of
characteristic other than two, every ambient reader value and external port,
and separate nonzero query rescalings. It is a scoped computer-assisted
obstruction, with an author proof and two separate implementations.
Independent human and formal proof-kernel review are unclaimed.

[PROOF.md](PROOF.md) derives every reader from an arbitrary vector w, then
reduces all coefficient choices to w in {0,+1,-1} at each target port and zero
elsewhere. [RESULT.json](RESULT.json) records all 800 plane-equivalence classes,
representing 4,960 triples and 1,084,757,832 assignments. Six triples match the
original bill; all others cost more. The first equality witness has term
charges [0,4,4,8], totaling 16 versus original 16.

This closes the arbitrary-w question left by
[PR3515](https://github.com/CrocSwap/integer-mult-bounds/pull/3515). Its one-port
family's best 20 can fall to 16 when all reader ports vary, but cannot fall
below 16. A support-transfer exception alone does not supply a cheaper decoder.
Other query rays and geometries are outside the result. No native caller,
supplier, new kappa or selected-frontier change is claimed.

## Replay

From the repository root with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p112-nonfano-affine-reader
```

The registered commands use only the standard library and run optimized with
warnings as errors. They check the primary census, a separate full census
without the primary symmetry reduction, a full 112-by-112 witness operator,
and five actual CLI corruption rejections. Direct scientific replay also works
without Git when the package and its one declared input retain their paths:

```sh
python3.12 -I -O -Werror -B research/p112-nonfano-affine-reader/verify.py
python3.12 -I -O -Werror -B research/p112-nonfano-affine-reader/independent.py
python3.12 -I -O -Werror -B research/p112-nonfano-affine-reader/test_controls.py
```

Set TMPDIR to an existing private output directory to place disposable control
copies there. The scripts use no network. `verify.py --case 6 24 25` checks one
exact class against the retained result; it does not replace full coverage.
`--write` intentionally regenerates RESULT.json.

## Sources and credit

[SOURCES.json](SOURCES.json) pins canonical labels at main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, and records exact origin commit,
path, Git blob and SHA256 for both retained pending sources. The original
PR3515 proof and Tekalign/PR3370 partition are included unchanged. Scientific
replay needs no pending Git object. Comparisons to the pair-reader and
constant-reader results are separate in [COMPARISONS.json](COMPARISONS.json).

Credit Tekalign for PR3370's orthonormal grouping and rank-32 repair,
Philippe Van Velzen for the paired-plane endpoint model, Arham Tahir/PR3345
and DreamingOfClouds for the underlying repair/support contributions, and the
credited P112/E8/native/compiler/supplier predecessors retained in the source
packages. This contribution adds the full affine support reduction and exact
minimum, while preserving those sources.

## Verification design

Build the Lever led to rerunnable minimizers and a retained exact certificate.
Prove It Works led to checking actual rectangular ranks, every literal witness
entry, corrupt source/result cases, and committed Git-free bytes. Separate
Before Serializing Shared State kept this package isolated and used process-held
locks for worker ownership and shared Git mutations.

The code has no recursion or dynamic code loading. All scientific loops are
bounded by the fixed 112-port, nine-bit input, 4,096-entry subset tables and
finite ternary products. Functions remain below 60 physical lines. Explicit
checks survive `-O`; source hashes, partition/Gram identities, coverage and
exact outputs are checked at their boundaries. State stays local to one class.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates integers,
tuples and lists during elimination and enumeration; fixed allocation cannot
be imposed without replacing its runtime. Each class has at most four rank
tables of 4,096 entries, one live subset-basis table with at most nine vectors
per entry, and bounded assignment lists. The primary retains 800 output rows;
the separate checker streams all 4,960 triples. No growing search frontier is
used. The compensating controls are fixed input hashes, hard dimension checks
and sequential replay. A future larger geometry must derive new capacities
before changing these bounds. Rule 10 uses Ruff E,F,B,UP,ISC,PIE diagnostics,
AST/function-size inspection and CPython `-Werror`; no formal type checker or
proof kernel acceptance is claimed.

## Open next questions

[TASK.json](TASK.json) records the next scoped question. Seek an exact cheaper
literal factorization with a changed query dictionary or target block, then
price its actual complete-plane readers before native construction. No result
here discharges acquisition, scalar execution, frames, arbitrary dirty
restoration, ownership, hosting, stock, precision, physical consumers,
all-size/compiler or outer multiplication obligations.
