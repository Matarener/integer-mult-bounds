# Independent dyadic certificates for E8 span transfer

**Independent verification; no new κ.** This package corroborates Nick Petalas's
[PR6198](https://github.com/CrocSwap/integer-mult-bounds/pull/6198), at
`2a804fcb32f46d66018185194b55f1f2b217523d`: the E8 span inputs S1, S2,
S3prime and W2 hold over every field whose characteristic is not two.
The field-range theorem remains Petalas's contribution. DreamingOfClouds's
PR2819 supplies the original characteristic-zero statements and classification.

The new evidence is a **code-disjoint row-module certificate**, checked solely
by integer matrix products after clearing powers of two. It imports no
predecessor executable, modular rank routine or determinant engine. Root data
are reconstructed from the doubled E8 lattice's norm equation. Instead of a
reflection-orbit search, 120 explicit dyadic isometries transport the fixed
anchor to every root line and check all 28,800 signed-root images.

For every matrix A, the certificate supplies a basis E, coefficient matrix C
and pivot columns J satisfying `E = C A`, `E[:,J] = I` and `A = A[:,J] E`.
All coefficients lie in `Z[1/2]`. These identities certify the exact rank
after passage to **any** field of characteristic different from two; this
is not extrapolation from a finite prime sweep. [PROOF.md](PROOF.md) gives
the argument and binds the configuration to the original source definitions.

The checker covers **6,595 matrices**: the predecessor's 6,539 obligations,
plus both the anchors and complements for all 28 rationally dependent
neighbor pairs excluded from S3prime. Their ranks are respectively two and
six in every permitted field. This checks the exclusion boundary directly,
rather than using projected-direction equality to omit those cases.

| Family at the fixed anchor | Cases | Certified rank |
| --- | ---: | ---: |
| S1 complement | 1 | 7 |
| Two anchors / S2 complement | 119 each | 2 / 6 |
| Independent three anchors / S3prime complement | 1,512 each | 3 / 5 |
| Dependent three anchors / their complement | 28 each | 2 / 6 |
| Three distinct W2 projected directions | 3,276 | 3 |

An explicit characteristic-three control records an important distinction:
two independent anchors can have a singular Gram matrix (determinant 48).
Their common orthogonal roots still span the six-dimensional ambient
orthogonal complement. The proof does not invert that Gram matrix or assume
the anchor subspace is nondegenerate.

## Reproduce

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -I -W error -B research/e8-dyadic-span-audit/verify.py
```

Expected status: `PASS_E8_DYADIC_SPAN_AUDIT`, with 6,595 splitting witnesses,
120 transports, 28,800 root images and 13 rejecting internal controls.
The verifier is read-only and does not require Git or network access when the
package and its four declared source inputs are present. Its JSON output
contains the decompressed certificate digest and exact source hashes.

Full registered verification, including optimized Python, whole-command
corruptions and complete certificate regeneration:

```sh
python3.12 -B scripts/research_package.py --package research/e8-dyadic-span-audit
```

To regenerate the mathematical artifact into a temporary file:

```sh
python3.12 -I -B research/e8-dyadic-span-audit/build_certificate.py --output /tmp/e8-audit-rebuilt.json.gz
```

Compare its **decompressed payload**, not its gzip container. The committed
payload SHA256 is
`3cb55e6121cf4db6589ff825c23b9b50ee3599fdc2348d42e22336100b94f9ce`.
The generator uses ordinary rational row reduction with dyadic unit pivots;
the checker does not import the generator or trust its reduction steps.
Both share this package's explicit configuration specification, which is
independent of the predecessor's code. This is implementation independence,
not independent human or proof-assistant review.

## Provenance and verification scope

Base: canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8, selected κ `0.003125804`. [SOURCES.json](SOURCES.json) pins the
four PR2819 input files. [predecessor/SOURCE.json](predecessor/SOURCE.json)
pins the exact PR6198 proof retained verbatim, by Git blob and SHA256; that
pending source is a statement input, not a Git-ancestor or admitted result.
It is deliberately outside the generic source-history manifest. The local
checker authenticates its bytes separately.

[RESULT.json](RESULT.json) is the generated mathematical receipt.
[VALIDATION.json](VALIDATION.json) records commands actually executed and
their scope. Tests include wrong combinations, omitted/misbound cases,
misclassification of a dependent triple, damaged transports, odd torsion,
and corruption of each of the four declared source inputs and the retained
predecessor proof. Every rejection must have its intended diagnostic and
must not print the pass marker. The regeneration test compares the full
uncompressed artifact. No predecessor scientific replay or selected cold
replay is claimed.

The OS draw was **84**, independent verification; the separate OS nonce was
`12126638887154793261`. Its remainder modulo three selected this task ahead
of an order-17 Clifford audit and a fixed-cubic coframe audit. [TASK.json](TASK.json)
records the exact scope, candidates, stopping rule and bounded overlap checks.
The catalogue formal-interface card is explicitly changed to this geometric
certificate audit; no selected caller or framework assumption is discharged.
Discussion posting was unavailable through the plugin and the public browser
was signed out, so the advance claim is local. There was no sprint issue among
the open issues. Sparse local-note coverage and unindexed Discussion records
remain limitations of the overlap search.

## Limits

This audit does not establish the remaining pinning/sign/SAT implications of
the rank-nine classification in positive characteristic. It does not apply
the statements to P112/P104 punctures, prove a decoder cost floor, implement
a physical supplier or change the multiplication bound. The selected record
and its five framework assumptions are unchanged. No Lean build, hosted CI
pass, human review or complete multiplication theorem is claimed.

## Open next questions

The useful next step is still PR6198's stated boundary: audit the field
assumptions in PR2819's remaining classification implications, starting with
an explicit list of divisions and nondegeneracy assumptions. The present
certificates settle only these four geometric inputs. Repeating more prime
sweeps or enlarging this same finite census is not needed. A later formal
proof may consume the three row-module identities directly, but must also
bind the lattice enumeration and caller's statement.

## Credit and license

Prepared for **@CubeJerry** with substantial **OpenAI Codex**
assistance for research, implementation, proof exposition, checking and
packaging. Apache-2.0. Nick Petalas retains the all-odd-field result and
PR6198's determinant/reflection certificates. DreamingOfClouds retains PR2819
and the PR2784 classification lineage. CubeJerry/PR3095 and conorholds/PR3755
retain the earlier dyadic-minor and reflection methods for different span
questions, as credited by PR6198. Row reduction and split-module reasoning
are classical. No priority over the predecessor's theorem is claimed.
