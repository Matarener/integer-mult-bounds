# Conditional saving 0.003125811 from PR6030

Under the same five assumptions as the reviewed PR6030 construction,

\[
T(n)=O(n(\log n)^{0.996874189}).
\]

This exceeds the quoted selected saving `0.003125804` by `0.000000007`.
It is a small **parameter refinement of the unchanged construction**, not a
new circuit, a newly reviewed record, or a novelty claim. The general corollary
in [PROOF.md](PROOF.md) permits every fixed saving below `0.0031258115`.

- [Proof and scope](PROOF.md)
- [Exact rational certificate](CERTIFICATE.json)
- [Pinned source identities](SOURCES.json)
- [Validation receipt](VALIDATION.json)

Use Python 3.12 or newer, with no third-party runtime dependencies:

```sh
python3.12 -B research/pr6030-parameter-refinement/verify.py
python3.12 -B -m unittest discover -s research/pr6030-parameter-refinement -p test_verify.py -v
python3.12 -O -B -m unittest discover -s research/pr6030-parameter-refinement -p test_verify.py -v
```

`verify.py --write` regenerates the certificate. Authentication precedes imports
of the vendored arithmetic. The checker reproduces every baseline outer row,
then verifies two independent moment enclosures, paid completion/splitting,
the explicit compiler threshold, BIT admission and all 54 strict plus four
functional outer predicates. Rejection controls cover corrupted invoice bytes,
an exponent above the fixed-invoice crossing, zero compiler gap, closed precision
slack and an insufficient BIT contract.

The unchanged complete finite source was freshly replayed in the isolated
checkout `/tmp/integer-mult-frontier-research`, pinned at
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`. That checkout is not needed for
the self-contained arithmetic checks above. The main workspace's historical
construction and selected record were not replaced.

All five inherited framework assumptions remain. No enormous uniform word,
complete rounded multiplier, or Lean proof is supplied. The proof's final
section records the limited remaining headroom and open physical questions.

The source construction and arithmetic retain DreamingOfClouds, Ali Romman,
the cumulative P104 community, Jacob Alan Sussman, Cinna Davis, zxv, Cao Yifan
and the other credits in the pinned review. Prepared with OpenAI Codex
assistance. Apache-2.0.
