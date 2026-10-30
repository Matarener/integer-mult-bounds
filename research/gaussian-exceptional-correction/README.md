# Exact Gaussian exceptional correction and whole transform precision

The exceptional correction left open in [PR 5813](https://github.com/CrocSwap/integer-mult-bounds/pull/5813) now has an explicit algorithm for arbitrary inputs. A pruned Walsh circuit replaces dense rank-one measurements, and an integral Smith circuit computes the whole normalized Gaussian response with a proved precision schedule. A new sharp invoice bounds both passes, including the work before and after the diagonal channels. These results do not yet establish a higher κ.

## Main results

For n>=1, N=2^n, π=1+i and A_n=([[i,1],[1,i]]/π)^(tensor n), the following constructions are proved informally.

| Result | Concrete output |
|---|---|
| Exact exceptional algorithm | Two pruned Walsh passes with O(N log(t+1)) incidences instead of Nt dense incidences, including multiplier height, true normalization precision, exact quotient and cleanup |
| Integral all-output alternative | C=S diag(1,π²) T with unimodular Gaussian-integer S,T; tensorization gives every output with no assumed exceptional cache or input symmetry |
| Sharp complete precision bill | Both Smith passes have addition-precision mass between N[np+n(n+1)/2] and N[np+n(n+1)/2+n], versus nN(p+n) at fixed modulus |
| Actual native matching | The repository's coordinate C gate is exactly A_1; the actual two-sided monomial recipe identifies its lifted central primitive as A_(rf), with phase and spectators retained |
| Complete caller interface | Source-version sampling, unequal numerator tags, backwards precision demands, explicit transposes and a charged exact in-place installation adapter |

The Smith invoice is a whole-transform sum over all coordinate labels. It makes no probabilistic input assumption. At p=n its exact ratio to the literal fixed-modulus addition mass is (3n+1)/(4n); at fixed p the ratio tends to one half. This is an addition-operand precision comparison, not a measured runtime ratio or a new multiplication exponent.

## Proofs and actual costs

Start with [assembly and invoice](assembly-and-invoice.md), A1-A5. It proves the sharp bound, matches the source's actual native recipe, and closes a subtle interface gap: a source-preserving owned output is not automatically an in-place MOVE. The supplied exact adapter computes forward, swaps actual payloads and headers, then uses the paid inverse routine to zero the owned old value.

The other mathematical notes supply the complete algorithms:

- [Pruned exceptional correction](correction-algorithm.md): uniform Newton-remainder divisibility, literal gather and transpose circuits, exact normalization and coefficient-valuation-dependent prefix precision.
- [Integral Gaussian delivery](consumer-construction.md): explicit Smith factorization, every T/S stage modulus, arbitrary-input example, full addition mass, exact size/precision recursion and current native kernel identification.
- [Causal shared delivery](shared-tail-delivery.md): actual source snapshots, immutable precision-tagged caches, backward demands, source-equal recipe installation and a Fourier gauge compiler with every actual boundary charged.

The spectral algorithm pays its working precision p+2n-R-1, coefficient products and final exact quotient. The alternative Smith algorithm avoids Walsh inversion denominators but still pays every triangular pass and layout visit. Merely keeping the small final diagonal bank would omit real work. The native kernel is implemented at its physical width n=rf, not at the fixed nine-bit frame-label dimension.

## Consequence for κ

The exceptional algebraic response and native normalization are now explicit. The remaining step is a better ALL-SIZE time invoice. For p=Theta(f), n=rf and fixed native grade r, the literal Smith addition mass is Theta(2^(rf)f²). Compared with an input field of Theta(2^(rf)f) bits, this is an ordinary N_bits log N_bits scale. A better leading precision coefficient alone does not certify N_bits(log N_bits)^(1-κ).

The best inspected pending claim is PR 5811's κ=.00312418633064; the selected conditional record remains .00310045 with admitted BIT .0034. This contribution claims neither improvement nor admission. The five existing framework assumptions remain. The complete formulas and next constructive targets are in [assembly and invoice](assembly-and-invoice.md), A6.

## Open next questions

1. **Reuse a real bank.** Identify actual unchanged source versions serving several native requests, then emit the shared gather, each update and each full delivery. The released four accumulations are already predecessor work.
2. **Fund one commuting patch.** The supplied gauge compiler counts every actual entry, exit, import, recipient and dirty restoration. Give a literal current patch whose entire bill wins. The actual chart chirps prevent treating the whole word as one common Walsh gauge.
3. **Reduce growing-width passes.** Give a concrete representation that uses fewer ordinary axis passes while preserving every independent endpoint. Its encoder, decoder, precision and physical movement must appear in the same word and invoice.

## Evidence and attribution

One coordinator and three workers developed and independently reviewed the informal proofs. There was no mathematical computation, solver, operator/invoice replay or Lean run. Source retrieval and publication byte checks are separate from scientific verification. The preprint's headline ETH claim is not assumed.

Exact source pins, overlap limits and credits are in [SOURCES.md](SOURCES.md) and [NOTICES.md](NOTICES.md). New text is Apache-2.0 with substantial OpenAI Codex assistance. The authoritative DAG and active Lean sources were not modified.
