# Prepared-page verification boundary

I generated `inputs/p48-catalogue-v2.tar.gz` from the actual
`TensorPreparation.run` return, using producer commit
`2dbbd2c37` and the authenticated source archives. I used CPython3.12.13 on
Darwin arm64. The preparation and catalogue check completed with exit0 on
2026-10-19 at04:05UTC. I measured317.011 seconds for preparation and319.063
seconds through the page checks.

I used two original source axes `(7,7)`, target axes `(8,8)`, flags `(1,)`,
`ell=3`, `p=48`, `alpha=2`, `inner_bits=1`, `P=80`, `sigma=4`, expansion
radius1, expansion capacity8, target halo1 and compression bandwidth1.
The producer constructed one global axis, four old-H principal windows and
eight expansion blocks, then reused that profile for the identical second
axis. It used peak168 scratch leases; the catalogue reader used71.

The archive contains one regular file,
`gaussian-tensor-p48-page-20261019.bin`, with113537 bytes. Each byte represents
one serialized tape cell. Its SHA256 is
`46dbbc4b4aff71548e8203fa5837762ea3f78117564952e8087a339e55ef208a`.
The immutable archive SHA256 is
`7e10a7344d19674c68cc64537cbec48b2ff038a907ca00f92fab1c41aaae9af8`.
I retained this portable container at commit
`ff1d8bf104e2b763aa1f57086e2f777c0af467f4`. The strict source check rejected
the first container's macOS sidecar; I removed that container and preserved
the numerical payload unchanged.

I split verification at the existing explicit coefficient-page port after
one combined producer/consumer attempt reached600 seconds. The producer
check regenerates the whole page and compares it byte for byte with this
artifact. The consumer checks authenticate the archive and its sole member,
then pass those exact bytes to the actual tensor consumer. They do not call
a replacement coefficient function. I retain the producer's cost and
verification time separately from each numerical consumer run.

Any change to the source archives, producer arithmetic, coefficient formulas,
parameters, framing or serialization requires a new regeneration check.
Passing a consumer check alone does not establish the producer dependency.
These explicit finite parameters do not meet the production locality domain;
I compare their complete staged operator, without claiming its production
Fourier-error guarantee.

The coefficient and numerical sources retain their predecessor credit.
Jose Manuel (`jmbarrancoml`) prepared this artifact with substantial OpenAI
Codex assistance. I have not obtained independent human review.
