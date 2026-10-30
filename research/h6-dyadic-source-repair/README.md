# Sharp dyadic repair of the H6 source map

For the inherited 30,960-port H6 kernel, let `C=I-K`. Over `Z[1/2]`, its
localized Smith factors are

```
1^30400, 11^336, 209^208, 4807^16.
```

Its determinant is `2^1472 * 11^560 * 19^224 * 23^16`, a dyadic nonunit.
Any dyadic repair making C unimodular has rank at least **560**. A finite
certificate identifies **560 actual physical rows** whose replacement is
sufficient algebraically, matching that lower bound. The untouched 30,400
rows form a primitive submodule; the proof gives existence of completing
rows, not their coefficients or a paid circuit.

A stable invertible extension with C as its upper-left block likewise needs
exactly 560 auxiliary directions algebraically. Its elementary Smith blocks
send `(x,h)` to `(d*x+h,-x)`: helper dirt enters the output and helpers change.
They do not provide a restored-helper source interface. An exact standalone
endpoint `(x,h)->(Cx,h)` remains impossible for a dyadic unimodular map.

This is a source-bound algebraic theorem and small exact certificate. C is the mathematical complement I-K, not the current native K response.
No native complement producer or legal source/output gauge is supplied. The
complete spectrum and sector identities are inherited from the pinned
spectral/moment proof. Neither the dense 30,960-square matrix nor its Smith
reduction is freshly computed. Native source flags, basis costs, dirt
compensation/restoration, banks/copies, precision/tape, controller and joint
outer transfer remain unresolved. **No new kappa or physical supplier is
claimed.**

[PROOF.md](PROOF.md) states the source premises, determinant and localization
argument, complete physical row certificate and stable-extension boundary.
`derive.py` and the separate `independent.py` replay the small arithmetic;
`SOURCES.json` pins the original Git objects and every live input. The primary
geometry stays live rather than being copied into a provenance archive.

Reproduce with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -O -B -Werror scripts/research_package.py --package research/h6-dyadic-source-repair
python3.12 -I -O -B -Werror research/h6-dyadic-source-repair/verify.py --out /tmp/fresh-smith-result
```

The registered replay authenticates inputs before and after, uses isolated
optimized child interpreters and writes only fresh external temporary output.
The local coefficient count for the three types of Smith blocks excludes all
basis/frame/owner costs and is not a native rank tariff.

## Open next questions

- Can the named 560-row completion be synthesized at actual source frames?
  First construct explicit dyadic completion coefficients and a paid word.
  Primitive completion does not price basis changes or legal access.
- Can a stable completion meet a useful dirty-helper caller contract? First
  specify and price its dirt compensation and restoration. The unit blocks
  alone leave these obligations open.

Credit Dominik Scholz's PR606 E8 geometry/factorization, DreamingOfClouds'
H6/Walsh proposal, and PR1830's spectral/compensation/encoder audit with its
retained predecessor lineage. The spectral theorem is reused explicitly;
this contribution derives its dyadic Smith consequences and supplies the
actual row-support certificate. No priority is claimed for Smith theory,
primitive module completion or generic rank perturbation bounds.

Ross Richardson, with substantial OpenAI Codex assistance in derivation,
separate audit and packaging. Separate AI implementations are not human
review or formal-kernel verification. Apache-2.0.
