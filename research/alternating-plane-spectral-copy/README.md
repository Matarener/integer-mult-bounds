# Alternating-plane spectral decoder: a copy floor of 672

**Scoped negative result. No new kappa.** For all 336 nondegenerate alternating
planes in the even subspace of F2^7, let A be the plane-orthogonality graph.
The fitting family I+cA has minimum real rank 168, only at c=-1/2. Every
factorization of I-A/2 with exactly 168 scalar terms has additive full-plane
COPY mass at least 672. This uses the full allowance of two unpaid
coordinates per port.

This was a search for a changed two-direction port geometry, separate from
P104 PR integration. It did not produce the requested large kappa gain.
The local alternating-plane native operation is prior work. The contribution
is the exact graph spectrum, the complete support certificate and the copy
bound for its minimum-rank spectral decoder.

## Evidence and replay

[PROOF.md](PROOF.md) gives the argument. [RESULT.json](RESULT.json) records
the exact polynomial identity, spectral multiplicities, all 651 four-space
minor checks, 336 native phase/rank checks, 336 column-factor tariff controls
and four rejected corruptions. Floating spectral discovery is not used by
the verifier. Standard-library Python 3.12 is sufficient:

```sh
python3.12 -I -B research/alternating-plane-spectral-copy/verify.py
python3.12 -I -O -B research/alternating-plane-spectral-copy/verify.py
python3.12 scripts/research_package.py --package research/alternating-plane-spectral-copy
```

The direct replay takes about three seconds, reads no Git objects or network
data, and writes nothing. `--output NEW.json` writes a receipt to a new path
and refuses to overwrite a file. [VALIDATION.md](VALIDATION.md) separates the
executed checks from unrun obligations.

## Open next questions

The cost theorem requires exactly 168 terms for this one fitting matrix.
It does not exclude overcomplete decoders or other fitting matrices. The
336-term column factorization attains cost 672 as an algebraic tariff control;
no native copy program is supplied for it. The finite native checks do not
supply a full caller, all-width implementation, BIT supplier or outer bound.
The selected result is unchanged.

- Can an overcomplete factorization of this K have cost below 672? A useful
  first step is an explicit factorization with some columns outside Im(K),
  exact support tariffs and all cancellations checked. The image-space proof
  does not settle that question. A profitable full supplier remains unbuilt.
- Can another fitting matrix on these ports have cost below 672? Start with
  a complete scalar matrix and its actual factorization. A smaller numerical
  rank alone is not a copy invoice.

The search should not expand into native caller construction until an exact
decoder has a favorable budget. The lower bound here is a local cost result,
not a universal obstruction to two-direction mechanisms.

## Sources, overlap and credit

Canonical main: `6cf7a683f447b9f1e2333791907fd92be5009a63`, priority revision 7.
[SOURCES.json](SOURCES.json) pins the source context without changing it.
The donor requested a new mechanism after the separate P104 contribution.
[TASK.json](TASK.json) records this changed scope and overlap limits.
Canonical discussion: [#5620](https://github.com/CrocSwap/integer-mult-bounds/discussions/5620).

The native convention and alternating projector are retained from
Clear1nsight's `p104-translated-progress`, Chafik Boukhalfa's
`p104-native-channel` and their Clifford lineage, including Rohan Arun,
Ali Romman and icekylinx.
The former already uses the plane (011,110) as a control. The full-plane
additive tariff comes from CubeJerry's plane contract and Mark/Matarener's
`plane-port-global-rank-dual`, with Ryanson Jonathan, Philippe Van Velzen,
Cinna Davis, Adam Gall and the source-credited contributors. Their fixed
56-plane result is not reapplied as a theorem for these 336 planes.
The historical plane endpoint and two-coordinate budget are also prior work.

Prepared for Ali Romman with substantial OpenAI Codex assistance. Discovery
and verification were written in the same AI-assisted session. No independent
human review, proof-assistant check or literature-priority guarantee is
claimed. Apache-2.0.
