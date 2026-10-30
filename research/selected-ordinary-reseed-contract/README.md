# Typing the selected ordinary BIT backend for finite reseeding

**Conditional interface lemma, not a supplier admission or a new bound.**
The selected ordinary backend can replace the predecessor-valued A0 in the
PR4814 finite-level construction under the retained completed-endpoint,
ROW/spectator, native, compiler and fixed-tape assumptions. The replacement
uses the actual completed backend, not just its exponent. Six fixed levels
then reach PR5708's stated ordinary component; no G20 predecessor exponent
is needed as the starting backend. The G20 raw/native construction and its
other admission obligations remain separate.

This answers the framework-reading question left in Matarener's
[PR5955](https://github.com/CrocSwap/integer-mult-bounds/pull/5955), at
`52115896549090117a3f3101b17106cad4466408`. It is a source-based mathematical
reading under existing premises, not maintainer approval. The source review
and substitution proof are below; [verify.py](verify.py) only checks the
selected-source bindings, adapter arithmetic and six strict separators.
It does not machine-prove the interface assertions.

## Which source versions and which backend

At base `721c03822c421b7f7fcbb2598993b947c4d88419`,
`certificates/selected-result.json` selects PR6030. Its CLAIM retains ordinary
BIT saving `8590884599/2500000000000 = .0034363538396`, separately from
conservatively admitted BIT `17/5000 = .0034`, uniform BIT before cover
`.003459`, and the complex/outer multiplication saving. This substitution
uses the ordinary value and its completed interface.

PR4814's final merged head is `f56ae4533a7d97d782a2c596a33fe844cd051747`.
Its `research/bit-finite-ordinary-bootstrap/PROOF.md` is byte-identical to the
older `709fcb31cc66bd8ce2165d60f495259502325536` snapshot:
SHA256 `5cabee7e5264ab0d674d5d591b4a3880ad460a546bcf5d53067eeeb9aff68df2`.
Thus its sections 2 and 4 have no consumer-contract drift. That text names
PR4760 as A0; the substitution argument below establishes why that name is
not an essential mathematical restriction when another completed backend
has the same interface.

The exact PR5708 head is `829d01fc031f7323ffcfa423fdfd1f24dcbe3190`.
Its original five levels use PR5679's stronger predecessor value. Its
`ORDINARY-RESULT.json` supplies the outer C1 and strict grid, not the seed
for this replacement. PR5955 separately checked wider tail guards down to
the selected seed; those numerical guards are not the missing endpoint type.

## Clause-to-source map

The selected source manifest `certificates/frontier6030-source.json` pins
both cited notes and the PR4359/PR4470 reviews below. The selected CLAIM
pins the numerical value. Their conclusions retain the five selected
framework assumptions; the table does not independently discharge them.

| PR4814 consumer clause | Selected source evidence and its implication |
| --- | --- |
| Completed ordinary interchange on arbitrary widths and complete chunks | `notes/batched-bit-rows.tex`, “Bit interchange with a remainder” and “Supplying the bit rows from existing digits”, handle every integer width and the finite small-width range. PR4359 review section 3 explicitly identifies the two-call ordinary wrapper, its three paid additions and restored rows. The seed is this completed wrapper, not a raw reverse word or only the before-cover supplier. |
| Preserve preceding/intervening complete spectators | `notes/three-stage-cover-bit.tex`, “Atom contract and common endpoint”, requires every complete spectator and the row coordinate to be preserved. `notes/batched-bit-rows.tex` retains intervening G, unused main digits and remainders. The entire outer ROW is a complete ancestor/spectator coordinate of an inner call. |
| Internally borrow and return row stock | “Supplying the bit rows from existing digits” borrows high digits from the two argument chunks, pads complete rows, invokes the recursion, removes zero padded rows and undoes gathering. Every completed invocation preserves its row index. PR4359 review section 3 charges the logarithmic reserve and completed ordinary wrapper. No external empty stock or restoration by a raw reversed body is substituted. |
| Weighted leaves reduce to ordinary calls | `notes/three-stage-cover-bit.tex`, “Weighted leaves and a genuine local-ring fallback”, writes J_a using four ordinary atom interchanges, three prefix-controlled shifts and a sign. Generated weights depend only on ancestors; no stronger weighted primitive is demanded from A0. The old numerical leaf exponent in that note is replaceable only together with this completed call interface. |
| Fixed-radix outer chunks adapt to binary with volume below four | Proven directly below for two complete equal-range chunks. The selected backend's separate binary-to-internal-q conversion has a fixed factor below q^2 in `notes/batched-bit-rows.tex`; it is already part of that backend's constant and is not claimed to be below four. |
| Fresh finite constants and thresholds, frozen before varying e | PR4814 sections 2–4 freeze each A_(j−1), use it for atom/routing/high-part calls, and choose a new threshold at each fixed level. The selected backend already has fixed finite constants under its assumptions. PR5708's `fee_bounds.eventual_threshold` expressly depends on the completed backend constant and threshold; these must be regenerated for the replacement. |
| Correct saving with enough adapter/stock gap | Selected CLAIM and PR4470 review section 3 identify `.0034363538396`; PR4470 records the essential atom power `.004` rather than the obsolete `.003`. The six new exact separators below use this completed ordinary seed. |

## Conditional substitution lemma

Let B0 be the selected completed ordinary procedure just identified, with
cost `O(V e^(1-b0))`, fixed constants, arbitrary complete chunk widths,
complete spectators fixed at return, and internally borrowed stock returned.
Retain the PR4814/PR5708 uniform supplier and all its native, ownership,
compiler, cover, precision and tape premises. If the strict inequalities

    b_(j−1) < b_j < a_j = (1−rho) C1 + rho b_(j−1)
    < C1 < rho < 1−a_j

hold for a fixed finite list j=1,...,L, then that construction produces a
sequence of distinct completed procedures B1,...,BL with savings b_j.
Replacing the seed changes finite constants and thresholds; it does not
require admitting the exponent of an intervening G20 construction.

**Proof.** At level j choose the already frozen completed B_(j−1). A weighted
leaf, routing call or high-part exchange uses the ordinary-call interface
in the table. Its outer row and all other complete fields are spectators,
so the inner procedure restores its own borrow before the outer program
resumes. The base procedure's correctness on arbitrary simultaneous data
and its complete endpoint allow composition; no intermediate state is
asserted to preserve the outer row or to commute with the outer program.

For an outer q-ary chunk of width w put R=q^w and M=2^ceil(log2 R).
Pad both complete chunks to M, run the binary ordinary interchange, and
unpad. Since R <= M < 2R, the volume multiplier is `(M/R)^2 < 4`.
Swapping the two equal-range coordinates preserves the original square
`[0,R)^2` and its complement, so padded zeros return to the padded region.
Each spectator slice is complete and preserved. The binary width is
`ceil(w log2 q)=Theta_q(w)` for fixed q. The inner backend may choose its
own fixed radix and constants; its internal conversion is absorbed in
its already-established cost. Padding does not execute an unpriced
address-dependent map.

The inherited root costs are

    O(V [ e^(1−rho)
        + e^((1−rho)(1−C1)+rho(1−b_(j−1)))
        + e^rho log e ]).

The middle exponent is `1−a_j`; `rho−a_j>0` and `1−rho−a_j>0` pay the other
two terms, and `a_j−b_j>0` pays the final strict relaxation. All positive
primitive constants, inherited reserve bounds, radix factors and frozen
backend thresholds are finite. Choose a fresh threshold for B_j that
absorbs them and pays the positive gaps. Below that fixed threshold use
individual-digit interchange (or the completed slower backend with a
larger finite constant). A bounded width set cannot obstruct the stated
asymptotic saving, uniformly in the complete spectator volume V.

Freeze this procedure and its constants before going to j+1. Coarse
recursion decreases atom count, while backend recursion decreases j.
There is no self-reference, no depth increasing with input size, and no
requirement that the fixed internal primes agree. Induction gives the
claimed completed interface at every one of the fixed L levels. This
establishes substitutability under the stated premises, not those premises
or the admission of the outer G20 supplier. ∎

## Six-level arithmetic and verification boundary

For PR5708, `C1=14030876239/4000000000000`, `rho=1/100` and strict grid
`10^-15`, use `b_j=(ceil(10^15 a_j)-1)/10^15`. The registered verifier reads
b0 from the selected CLAIM, checks every strict inequality, and verifies
that level five is below and level six equals `.003507719059749`.
This corroborates PR5955's arithmetic only after the interface mapping.

Run, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/selected-ordinary-reseed-contract
```

Expected marker: `PASS_SELECTED_ORDINARY_RESEED_CONTRACT_BINDINGS`. The
normal/optimized checks also test the strict-grid equality boundary and
integer radix padding controls. No G20 global/native replay is run; no
stale numerical threshold is claimed valid for the reseeded program.

## Open next questions

**Source-bound reseeded admission.** To use this in an admission, construct a
new PR5708 admission receipt naming this B0 and six levels, regenerate all
backend-dependent fee/stock/threshold constants, and bind applicable raw,
native and analytic evidence. This matters because the old receipt names a
different seed and five levels. First change those specific inputs in an
isolated admission package; the remaining blocker is the full inherited
supplier and framework obligations, not the scalar recurrence or seed type.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0.
Matarener (#5955, substantial Claude assistance) identified the direct-reseed
question and checked its arithmetic. Ali Romman supplied PR4814 and the G20
composition sources; finite acyclic bootstrapping and nested restoration
are prior work of rohanarun (#185/#199/#204). Nicknames and contributors of
the selected native/compiler, BIT and outer framework retain their source
attribution, including zxv, Cinna Davis and Jacob Alan Sussman. No precursor
construction, selected record or frozen source is changed here.
