# Checked scope and replay limits

I use explicit exceptions as verification gates and run the registered
suites with optimization enabled and warnings as errors. I separate the
finite evidence below from the quantified proof and inherited premises.

| Suite | Scope |
| --- | --- |
| sources | Whole 26-file predecessor export, shared physical cohort, four external source pins; changed-binding and second-runtime controls |
| budget | Fine-grid guard, exact norm margin and complete phase allowance; authenticated full Fourier power |
| odometer | 296 residues in three complete cubes, plus a 64-residue prefix in 40 axes; original formula, PR479 reference, carries and local head movement |
| kernel | Complete eight-coefficient numerical kernel against exact eighth-root integer formulas |
| phases | 48 certified phases across precision/shape reuse; exact signed width recovery and two overflow controls |
| failures | Thirteen malformed-input, phase-direction, carry and setup-scope controls; positive numerical kernel after rejections |
| middle | Full physical chirp against staged and dense Fourier models, nonzero rounding, nested call counts and protected return |

For the complete p16, ell2 kernel, I obtain residue sequence
`0,5,4,5,6,3,2,3`, with ten axis visits, three wraps and 48 scalar word
products. The payload hash is
`a44ef78f98f427b61c4bd83141e2eb8661498af99a96e59543f3e355151a82b7`.
In the 40-axis prefix test I obtain 95 visits, 31 wraps and 5828 state-head
moves. I label that test as a prefix; I do not claim to enumerate its cube.

For phase accuracy I compare exact integer norms and outward rational
intervals from Mason Hale's authenticated implementation. I also reuse the
same physical kernel owner with changed precision, shape and row count.
The p16 two-row hash is
`dff3af812286c3d7471ddd842945ea2d9cb4c26e5a3aba2cd76be14516843d95`;
the p17, ell3 hash is
`bfc231d54a87b94b57cde5712831afcfbc53a1684b19ceb7b627190c99ac5566`.

The complete middle-map fixture has p=16, ell=2, A=1, C=1 and source
units `(1,3)`. I use an input of norm at most .6 and compare the physical
return with an exact staged model and a separate eight-term dense Fourier
sum. I obtain a 288-bit payload, hash
`bae3e8da66f4dd74712c006d77fa3c465b6014ca57496de97c40c64534dcbb4b`.
The maximum squared error in p-grid numerator units is 1649/64.
I verify one kernel, two endpoint products and one cyclic call; inside it
I verify two twists, one complete ring convolution, exact narrowing and
one untwist. Inside the ring caller I verify two forward transforms,
one normalized product, one opposite transform and one exact M scale.

The source units in this finite fixture satisfy the declared odd-unit
chirp contract. I do not claim a prime-source outer multiplication run.
I use the retained direct/literal q2 physical child, with its existing
reduced guard. I leave production GL64/O73 execution outside this receipt.

## Exact metadata specialization

I first executed the complete packet with the original q2 setup. It
passed both oracles but exceeded the intended 600-second replay limit
locally. I traced the cost to repeated fractional-power setup. For this
fixed packet, the Fourier precision is 17 and the literal-root precision
is 18. The exact required values are

    floor(17^(997/1000))=16,
    floor(18^(997/1000))=17,
    floor(1^(1/500))=1.

In `chirp_fixture.py` I certify these with integer inequalities
`16^1000<=17^997<17^1000`, `17^1000<=18^997<18^1000` and `1^500=1`.
During the registered finite witness I compare the incoming encoded
values with those literals and return fresh owned Counts. I reject any
other argument. I substitute only the imported setup functions in
`composed_plan` and `active_plan` for the duration of that witness.

I preserve the metadata values, physical child selection, coefficient
precision and numerical operation. I obtain the same payload hash as the
unspecialized run. I check three calls at value 17, three at 18 and six
at 1. I charge setup in the all-size proof; this specialization neither
proves the general compiler nor removes its cost from that proof.

## Failure coverage

I reject short precision, ell>=p, insufficient scale margin, zero rows,
even or oversized source units, and short/extra source or payload words.
I execute a conjugated-basis mutant and an omitted-carry-subtraction mutant
and require failure against the exact kernel oracle. I reject an argument
outside the certified setup fixture. The positive full consumer also
rejects reuse while its output remains live.

The malformed-input checks exposed a scratch leak when a truncated
descriptor interrupted a multi-value decoder expression. I added complete
binary extent admission before decoding. I check restoration after those
ordinary rejections. I do not claim rollback after arbitrary mid-child
injected faults. The width test verifies exact signed numerators and
rejects positive and negative values that need the discarded high bits.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
