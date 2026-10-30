# Exact crossing-cell residual tariffs

The [self-contained proof](PROOF.md) answers PR3569's open attainment question
for coordinate-aligned target groups. Closure cells may cross any number of
orthogonal coordinate lines. The VVV optimum is its block lower bound plus an
explicit ternary cell energy. Its lower bound is attained exactly when each
pinned incidence component has an exact cover satisfying the stated pair
conflicts. MMM always attains its bound in this geometry.

For one cell per group, with positive private-coordinate counts s_A,s_B,s_C
and m common coordinates, the exact result is

```text
S = s_A+s_B+s_C, s = min(s_A,s_B,s_C)
original D = S+3m
VVV minimum = D+min(m,2s)
MMM minimum = 2S+3m
```

Thus connected crossing-cell excess is unbounded. The optimal VVV reader changes
from all positive cells to one negative smallest private group when m passes
2s. This classifies a support penalty. No cheaper decoder, new physical supplier,
kappa improvement or selected-frontier change is claimed.

The theorem covers every coefficient field of characteristic different from
two and arbitrary ambient readers. Groups must use the same coordinate basis.
Different bases inside shared blocks, general nonreducing spans, partial bases,
arbitrary representatives, mixed-group closures, characteristic two and
arbitrary-query classification are outside scope. Author-written proof completion
is distinct from independent human or formal proof-kernel acceptance.

## Evidence and replay

The [fixtures](FIXTURES.json) include all 109 nonempty-group subsets of the seven
three-cell incidence types, 32 seeded six-cell cases, and eight private/common
threshold cases. Two implementations agree on all 26,487 VVV assignments,
ordered total-charge hashes, histograms, minima and first witnesses. The second
implementation enumerates MMM and reconstructs actual rectangular binary Gram
matrices. It also checks 39,784 integer and F3/F5/F7 operator entries with two
ambient coordinates. Six malformed contracts and two forged records reject
through both optimized CLIs, followed by 16 restored successes and two positives.
These finite checks corroborate the written all-size argument.

From the repository root, with CPython 3.12 and the standard library:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-crossing-attainment
python3.12 -Werror -B scripts/check_research_commit.py --package research/p112-crossing-attainment --check-source-history
```

The three scientific/control commands also run without Git or network, from a
regular byte copy of this package. Set TMPDIR to an existing private directory
for the controls, then run:

```sh
python3.12 -I -O -Werror -B research/p112-crossing-attainment/verify.py
python3.12 -I -O -Werror -B research/p112-crossing-attainment/independent.py
python3.12 -I -O -Werror -B research/p112-crossing-attainment/test_controls.py
```

[RESULT.json](RESULT.json) records the exact finite results;
[VALIDATION.md](VALIDATION.md) describes bounds and verification limits.

## Sources and credit

Nick Petalas. Apache-2.0. The mathematical proof and runtime are self-contained.
[SOURCES.json](SOURCES.json) pins canonical provenance only. PR3569's exact proof
is retained under COMPARISONS with its origin commit/path/blob/SHA256, solely
as handoff and comparison context. No foreign Git object or network is needed
for scientific replay, and no inherited mathematical premise is hidden there.
Credit retains PR3569/3560/3549/3538, Philippe Van Velzen and Arham Tahir's
expanded-identity method, Tekalign/PR3370 and the retained P112/E8/native/compiler
lineage. Those broader results are not recertified.

## Open next questions

The structured [TASK.json](TASK.json) asks for equality conditions with different
shared-block bases and the complexity of the three-partite pinned exact-cover
problem. Neither an efficient general algorithm nor a hardness theorem is
claimed. Native acquisition, coefficient execution, frames, dirty restoration,
hosting, precision, stock, compiler/all-size admission, complete suppliers and
consumers, and outer multiplication transfer remain unrun and unclaimed.
