# Proof and complete price

Prepared for Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Sources and claim

The input is PR5684 at `d0f6fa2555410a1e23fe4191424c2097ab3d5d97`.
Its word, constructor, price and attribution are retained without edits.
The official 16-file export of PR5678 at
`af814f6f3c477fdd13b8f04380a33cf32004966b` retains the full checker stack,
including its exact predecessor archives. Authentication precedes source imports.
Every exported file has a separate Git source pin. The generated archive has
its own fixed integrity hashes; those hashes do not claim a pre-existing
upstream archive object. Base main is `df0137efd35e11b4445734bf612bdd4c7ebc330c`.

The claim is a complete **conditional** construction at kappa .00310915222.
It preserves the source five framework assumptions. It does not change the
selected frontier, prove a global optimum or give a practical runtime claim.

## 2. A temporal update lemma

Use decoded scalar coordinates for a fixed native word. A cut `c` is immediately
before source event `c`. Suppose field `r` is not read in `[a,b)`. Its operations
in that interval are ADDs into `r` and changes of its native chart. In particular,
there is no SCALE, COPY, initialization or erasure of `r` in the interval.

Remove some ADDs into `r`. Let their total scalar source functional be `g`.
Suppose actual fields `s_j`, at cuts `c_j` in `[a,b]`, satisfy

`g = sum_j q_j value(s_j, c_j)`.

Require `s_j != r` and an actual common frame for each replacement ADD into `r`.
Insert those ADDs at their declared cuts. Every other field follows its original
trajectory: no original operation reads the changed field in the interval.
The replacement sources therefore have their original values. The difference
in `r` is the accumulated replacement sum minus the removed sum. It is zero
at cut `b`, before its next read. The full endpoint is unchanged.

This is an exact linear-circuit identity. No old value is stored or read later
without an operation. Each source is read at its declared physical cut.
Native transports still use their actual charts and phases. Their decoded action
is the identity under the retained native contract. The native replay checks the
changed transport separately; scalar reasoning does not waive that obligation.

## 3. The fixed witness

All event positions below are zero-based in the pinned PR5684 word.
Take `r=715`, `a=823` and `b=14983`. Remove event 13578,
`ADD 715, 747, 1`, at frame 598. The exact prefix calculation proves

```
value(747,13578)
  = value(525,823)/4 - value(712,823)
    - value(525,14983)/4 + value(340,14983)/4.
```

The identity also has a short direct derivation. Let `A=value(525,823)`,
`B=value(712,823)`, `V=value(747,13578)` and `C=value(340,14983)`.
Field 712 has only one write in the interval: event 13572 adds `V`.
The owned value is unchanged between that read and event 13578.
Field 525 has only two writes: event 13737 subtracts four times field 712,
and event 14654 adds field 340. Field 340 has no write from event 11202
through cut 14983, so that last added value is `C`.
Consequently `value(525,14983)=A-4(B+V)+C`. Rearrangement gives the identity.
The complete prefix check independently confirms all 105 source coefficients.

The first two replacement ADDs use frame 3. The last two use frame 396.
Each source and field 715 have that frame at the stated cut. There is no read
of715 in `[823,14983)`. Event14983 is the next read, `ADD 340,715,-4`.
The verifier calculates every coefficient of the displayed identity over Q,
and separately checks the no-read condition and all common frames.

Remove event 13577, `MOVE 715,3,598`, and change event 14982 from
`MOVE 715,598,396` to `MOVE 715,3,396`. The old frame dimensions are0,1,3,
and their binary spaces form a strict chain. Thus the two old queries H1,H2
become one H3. All other source records remain in order and unchanged.
Four ADDs replace one ADD, so the emitted word has 25453 records.
The complete rational replay and a separate dense transpose replay check all
565504 endpoint coefficients. All743 public inputs remain independent;
9 owned fields have11 lifetimes and peak occupancy2.

The alternative rewrite found on field 525 has the same price. It is not added
to this gain. A further scan of771 single visits and214 joint visit sets on
the changed word found no additional gain in that tested domain. These discovery
screens are not an optimality certificate and are not proof inputs.

## 4. Native and ordinary costs

The retained exact native engine lowers every paid request, main adapter and
helper normalizer, including absolute phase. It checks 2917 distinct native maps.
All original helper endpoints and the actual18-call physical caller stay fixed.
All eight owned H7 queries remain; the removed ADD only changes one recipient.
The original centre erasures, other reads, COPY instructions and ownership
contracts remain in the word.

The local paid profile is

```
2184 H1 +459 H2 +495 H3 +92 H4 +159 H5 +22 H6 +15 H7.
```

The unchanged local productive profile is

```
2 H1 +4 H2 +91 H4 +6 H5 +5 H7 +15 H8 +412 H9.
```

The exact local scalar allowance is220326. Native routes and adapters have a
separate allowance 5164000. Their sum stays below the retained local budget 10^7.
The complete raw ordinary upper bound is184647552, below 10^9. The fixed scalar
growth and native tensor growth bounds are unchanged. Thus no new history bank,
free query, uncharged route, COPY, CLEAR or storage lifetime is introduced.

## 5. Complete moment, compiler and outer ledger

The literal caller has 18 forward local calls,15 paid rank-one query shears and
3120 whole idle jobs. It has 66348 paid calls and12958 productive fields.
The target-minus-paid rank mass is760. The complete change from PR5684 is

`Delta P = -18 H1 -18 H2 +18 H3`, `Delta T = 0`.

For every `0<t<1`, `1+2^t-3^t>0`, by strict subadditivity. Hence the changed
bill strictly improves every such signed moment. The proof does not add PR
root decimals or use unchanged target credit after a helper removal.
Two exact rational interval engines verify the full invoice. The unique raw
root in the retained interval below .0034 lies in

`(.00310915224562, .00310915224563)`.

The declared kappa is .00310915222. The tested saving is .003109152225.
The remaining raw headroom is between .00000000002562 and .00000000002563.
This is a ceiling for this fixed invoice in the certified interval, not a
ceiling for other constructions.

The retained completion proof is re-evaluated with cutoff 17, floor 18,
tail offset 1/5, tensor power 1024 and reserve 10^-12. All three tail ratios,
splitting, rounding, complement capacity and shifted exits pass. The finite
compiler threshold is calculated on its exact integer grid and its immediate
predecessor fails. All54 strict outer inequalities and all 4 functional checks
pass. The unchanged ordinary BIT input is admitted at .0034. Its full cover,
atom and stock obligations remain charged through the retained ledger.

The claim exceeds PR5684 by .00000043910, about .01412482 percent.
This modest gain is the result supplied here. A large breakthrough is open.

## 6. Limits and next checks

The all-column native extension, owned-erasure contract, uniform compiler,
precision/tape prescriptions and analytic/recovery framework remain assumptions.
The enormous uniform word and complete rounded multiplier are not executed.
The source receipts and new finite checks do not imply independent human or
proof-kernel acceptance. Independent verification of the temporal identity and
its complete bill is the next review task. A larger construction must keep the
same distinction between an exact scalar identity and a fully paid caller.
