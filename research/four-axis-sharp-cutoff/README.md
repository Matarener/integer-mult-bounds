# Sharp four-axis native cutoff

The exact four-axis affine/quadratic Gaussian monomial thresholds are
**(12,9,10,11)** by residue. The least cutoff is **9**, and the test window
**9,10,11,12** is sharp. The former sufficient window was 11,12,13,14.
This reduces a native identity verification bound. Complete kappa is unchanged.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[COEFFICIENTS.json](COEFFICIENTS.json) and [SOURCES.json](SOURCES.json).

```sh
python3 -B scripts/research_package.py --package research/four-axis-sharp-cutoff
```

Python 3.12 and the standard library suffice. Expected markers:
`PASS_FOUR_AXIS_SHARP_CUTOFF` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
The normal and optimized runs check all 65536 phase witnesses, 20160 maps,
37800 hyperplane cosets, 730626 low-width multisets and five rejection controls.
The proof includes the all-width padding and kernel arguments.

The finite witness file can also be rebuilt with C++17:

```sh
c++ -O3 -std=c++17 research/four-axis-sharp-cutoff/build_certificate.cpp -o /tmp/four-axis-certificate
/tmp/four-axis-certificate > /tmp/four-axis-witnesses.txt
python3 research/four-axis-sharp-cutoff/pack_witnesses.py /tmp/four-axis-witnesses.txt /tmp/four-axis-witnesses.json.gz
```

The decoded witness vector must match WITNESSES.json.gz. Gzip headers can
differ between Python versions. Generation is optional;
the registered verifier checks every witness without trusting the generator.
No compiler, physical caller, selected cold replay or full multiplication proof
is included. The fixed grammar and full dirty-input/return contract are required.

## Open next questions

For higher dimensions, find a nonzero conjugacy-invariant GL(n,2) coefficient
function with zero pointwise-hyperplane coset sums. Translation summation then
extends it to the affine group as in this proof. Such a certificate would reduce
sharp representation thresholds to exact full-span phase-character realization.
A general all-dimension existence and optimal character bound remain open here.

For physical use, bind a complete four-axis endpoint to the grammar before
using the smaller window. Its expansion and physical invoice remain separate.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0. Predecessor
roles and classical methods are credited in the proof.
