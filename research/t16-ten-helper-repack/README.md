# A ten-helper interacting T16 repack

On the exact PR3375 physical owner map, a two-row swap followed by an eight-row
rotation gives conditional **kappa = 0.001673628867926940**, up from
0.001673628681907313. The exact gain is `186019627/10^18`.
The completed idle delta is `+H2 -2H3 +H4`; strict concavity proves a moment
improvement for every real `0<a<1`.

The [proof](PROOF.md) gives the literal program, intermediate profile and full
scope. Ten helpers relocate and 23 serialized rows change including offsets.
Two original helpers leave one shared bin. The first swap makes the moment
worse; accepting only neutral or improving intermediate maps misses this route.
The final supplier uses the completed static map, with no additional runtime step.

This is a conditional finite packing construction, not an optimum or a selected
frontier update. The selected word, widths, 144-call order and entire physical
invoice remain fixed. Complex still binds. All inherited compiler, physical,
precision, all-size, analytic and bit-interface premises remain.

## Reproduction and evidence

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/t16-ten-helper-repack
```

Expected final markers include `PASS_T16_TEN_HELPER_REPACK`,
`PASS_TEN_HELPER_INDEPENDENT`, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
For an external run directory:

```sh
python3.12 -Werror -B research/t16-ten-helper-repack/verify.py --work "$RUN_DIR"
```

`RUN_DIR` must not exist. The verifier writes only there unless `--write` is
explicitly requested. Without `--work`, it uses a disposable directory under
`TMPDIR`. Set `TMPDIR` to your session cache before the registered replay if
all temporary files must stay under one output root.

The unchanged eleven-stage strict admission checks all 69,120 roles and 144
calls. Controls include 69 admission, 12 bit-supplier, 6 independent T16,
15 controller and 11 owner controls. Both exact moment engines and both
seven-step bootstrap paths pass all 47 outer inequalities. The complete typed
invoice comparison retains prefix 512 and physical row coefficient 16,469.
Actual charts are 10,004. [ADMISSION.json](ADMISSION.json),
[INVOICE.json](INVOICE.json) and [RESULT.json](RESULT.json) preserve the evidence.

`independent.py` reconstructs the entire owner array separately from the new
generator. Behavioral tests reject omitted and reversed rotations, a wrong
helper width, altered source bytes and a changed invoice charge. They also
check the intermediate deterioration and run under optimized Python.
[VALIDATION.json](VALIDATION.json) records actual environments and checks.

## Sources and scope

Canonical base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6,
card `selected-packing`. Predecessor PR3375 is pinned at
`62fd8039cc40749cea6238e7807db9a63b4d6765`. Its original result, proof,
construction and patch are retained; a 240-row patch from canonical PR2169
reconstructs its exact payload. No unmerged Git object or solver is required.
[SOURCES.json](SOURCES.json) pins the complete admission inputs.

Concurrent [PR3381](https://github.com/CrocSwap/integer-mult-bounds/pull/3381),
head `ef1f7b1f9cb582767e448dc047b2359ded28076f`, reports a larger gain after
changing paired-call chronology and extending the lift. This contribution keeps
the exact PR3375 call order and unchanged lift. Its `+H2-2H3+H4` program differs
from that reported `H1-H3-2H7+H16` construction. No global-best claim is made,
and PR3381 is not independently replayed here.

The first attempt failed only because it nominated the predecessor's chart
count 10,005. The strict audit measured 10,004. After correcting candidate
metadata, a fresh unchanged eleven-stage run passed. Neither the verifier nor
the invoice equality was weakened.

Credit Pierre / hexapode, Nick Petalas, Gonzalo Mier, Philippe Van Velzen and
the retained compiler, physical, bit, owner and moment authors named in the
[proof](PROOF.md). Original notices remain. New material is Apache-2.0.
Substantial AI assistance was used for this investigation.

## Open next questions

Can another interacting exchange improve this exact completed map? Nominate a
literal multi-helper exchange and replay the complete owner and invoice
contract. This result supplies no packing optimum or universal search closure.
The structured question, relevance, first step and blocker are in `TASK.json`.
No additional construction round is started here.
