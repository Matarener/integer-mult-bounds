# High-cube fitted B1 call bridge

This package proves the source-bound caller/callee fit for every reached high-route swap call in the fitted regime. For fixed prime q>2^80, u>=311311, N=d^2>=4 and F>=1, the exact PR2915 extents satisfy P q^u G q^u S = V=q^(uN)F, the encoded width passed to B1 is exactly u, and each call matches PR2899's complete ordinary-interface domain.

Under PR2899's retained C0 premises and successful execution with sufficient capacity, the B1 endpoint and uniform time bound transfer to the actual call. The optional whole-cube cost corollary also uses PR3301's separate outside-call invoice, which is author-checked and still awaiting independent review. The proof does not establish a fitted payload run or a numerical enclosing capacity.

## Reproduce

~~~sh
python3 scripts/research_package.py --package research/high-cube-b1-fit-bridge --check-only
python3.12 scripts/research_package.py --package research/high-cube-b1-fit-bridge
~~~

The verifier uses the standard library. It checks byte-pinned sources and archives, exact division width selection, symbolic extent identities and rejection controls. The proof supplies the universal quantifiers; finite checks are corroborating evidence only.

The released [PR3301 package](../high-cube-paid-composition/README.md) identifies the fitted B1 call contract as its next question. This result supplies the source-bound call mapping under PR2899's written hypotheses. See [PROOF.md](PROOF.md) for assumptions, parameter ranges and exact conclusions. [TASK.json](TASK.json) records the refined task and open gaps. The current selected result remains κ=836330098538459/500000000000000000; this package does not change it.

## Open next questions

- Does the source-bound ordinary theorem extend to bases outside its pinned fixed-prime range q>2^80, including primes 3<=q<=2^80 or composite q? PR3301 uses broader q>=3 notation, which remains conditional until the C0 domain is established. First step: trace the exact q-dependence of the C0 constants and either prove a range extension or narrow the high-cube statement.
- What numerical tape backing and role capacity does the enclosing selected caller provide at the fitted B1 call? The current result assumes sufficient capacity. First step: join PR3301's adapter lifetime invoice to the PR2899 fixed-role inventory at the same call boundary.
- Can the source chain be formalized or cold-executed on the actual GL64 payload? A large fitted payload is not run here. First step: produce a bounded, source-authenticated GL64 call trace or a proof-assistant refinement for the exact C0/B1 interface.

The structured `why_it_matters`, first-step and blocker fields for each question are in [TASK.json](TASK.json).
