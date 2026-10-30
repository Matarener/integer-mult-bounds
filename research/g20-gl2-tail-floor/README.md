# General binary pair bases do not shorten the isolated G20 tails

For each of three isolated four-bank exchanges in exact
[PR5840](https://github.com/CrocSwap/integer-mult-bounds/pull/5840), every
binary GL2 basis choice within its two equal-target pairs still needs at
least **six charged XORs**. The source attains that minimum. This fixes
18 of the current 38 XORs per boundary side **when gates stay component-local**.
It does not prove a global boundary optimum or improve kappa.

This is a new source-specific negative result for the GL2 extension suggested
by Ali Romman's PR5840. Its predecessor enumerates pair permutations in a
particular word normal form. Here all 36 independent binary bases and **all
XOR words on four arbitrary registers** are covered, with no extra workspace.
The exact minimum histogram is `6:2, 7:8, 8:24, 9:2`.

[PROOF.md](PROOF.md) gives the argument and precise hypotheses.
[CERTIFICATE.json](CERTIFICATE.json) supplies all 20,160 matrix potentials
and attaining words. The checker covers all 241,920 directed generator edges
and ten semantic/integrity controls. A separate implementation imports no
producer code and checks every distance using complete 16-input truth tables,
all candidate forward/inverse inputs and both actual source boundary words.

## Reproduce

With Python 3.12 and its standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/g20-gl2-tail-floor
```

Expected in both normal and optimized modes: `PASS_G20_GL2_TAIL_FLOOR`,
`PASS_INDEPENDENT_G20_GL2_TRUTH_TABLES`, then
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct replay is read-only and Git-free:

```sh
python3 -I -O -B research/g20-gl2-tail-floor/verify.py
python3 -I -O -B research/g20-gl2-tail-floor/check.py
```

To regenerate evidence into a fresh directory (never over committed files):

```sh
python3 -I -B research/g20-gl2-tail-floor/verify.py --write-new /tmp/g20-new-evidence
```

Expected output files match the committed certificate and receipt exactly.
The directory must not already exist. No network, predecessor execution,
third-party library, large supplier replay or solver is needed.

## Pins, coverage and limits

Base: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The exact data-only controller is vendored from PR5840 head
`6a043d0fc0199ee5b24c61f883f1943eaf6424be`, Git blob
`73fa9f40a032f11dabf357eba69066fcf9bf0a02`. Both checkers bind its SHA256
and Git blob framing. [SOURCES.json](SOURCES.json) retains full pins.
The unmerged head's ancestry is not authenticated by local base history.
No source executable or complete predecessor archive is imported.

The research domain is all 20,160 invertible binary four-by-four maps, all
12 directed unit-cost XORs, and all 36 independent pair bases on each of
banks `(20,21,24,25)`, `(16,17,28,29)` and `(18,19,26,27)`.
OS assignment seed 14 chooses the first component via `14 mod 3`; enumeration
itself is deterministic and exhaustive. The stopping rule is domain exhaustion,
not a time/depth cutoff. [CLAIM.md](CLAIM.md) records the three candidate tasks,
budget, overlap checks and result. [TASK.json](TASK.json) marks the original
BIT card's scope as changed: its complete-recursive-profile gate is not met.

The local budget included both inverse words. Reducing six to five would have
saved 222 XORs per component over 111 ports, without new helpers or children;
the exact floor blocks this route. The paid and target recursive profiles
are unchanged, so even a scalar saving would not itself improve kappa.
The selected result remains 0.00310045.

The source physical-core identity and native supplier contract are inherited.
There is no full caller, native phase, physical ROW/cache/tape, rounded
primitive, compiler or analytic replay here. The five selected assumptions
retain their status. Exact finite certificates are not a formal proof of the
integer multiplication theorem or an independent human acceptance.

## Open next questions

The remaining 18-register component or gates crossing component boundaries
may permit a cheaper complete boundary. This matters because the present
18-XOR tail floor is conditional on component-local synthesis. First give one
explicit changed word or basis and price both inverse boundaries. New source
values and the complete caller fee would then need fresh checking. No candidate
or larger-domain certificate is supplied; see structured blockers in TASK.json.
Extra workspace and nonbinary bases are also outside this result.

## Credit

Ali Romman supplied PR5840's mechanism, source controller and scope question;
retain PR5834, PR5807/5828, PR5708/5671, ai-nanachi PR5512, Dugongue and the
complete native/controller/compiler lineage. PR5793's general XOR synthesis
and six-XOR reversal are prior work; the algorithm is not imported and the
basic six-XOR exchange is not claimed as new. Historical formal coordinate
SWAP results such as PR2415 have different paid operations. New work is the
actual G20 source binding, all-basis table and two independent representations.

Prepared for **Charan / theon199 with substantial OpenAI Codex assistance** in
research, code, documentation and checks. No subagents or independent human
review. Apache-2.0. Preserve `inputs/PR5840-NOTICE`.
