# Exact joint width-price region for the staged544 ideal

**New scoped result; no new kappa.** The complete optimal face at PR3815's
fixed exponent contains twelve packing patterns. The two columns outside
its chosen basis enlarge three of PR3862's sufficient price ranges:

| Width move | Previous basis range | Sharp range, helper-calls per owner replica |
|---|---:|---:|
| 5 to 4 | 18 | 18 |
| 6 to 5 | 28 | 48 |
| 7 to 6 | 28 | 88/3 |
| 8 to 7 | 30 | 30 |
| 9 to 8 | 28 | 48 |

For nonnegative adjacent inventory flows x5..x9, the common width prices are
attained exactly when

```
x6+x7+x8+x9 <= 48
x5 <= 18+x6
x7+x8 <= 30+x6+x9
3*x7 <= 88+x6+x8+x9.
```

This is a complete region in the fractional, clock-free, fixed-bin relaxation,
at `a=0.001730578437266246818741`. It supplies constructive rational packings,
not a physical supplier. The counterexample x6=x7=28 fits each old individual
range but violates the joint region. An explicit feasible packing and a
strict positive objective gap certify the failure of simultaneous sharpness.
The original screen's global lower bound remains valid outside the region.

This helps screen combinations of prospective staging changes before circuit
implementation. It does not establish that any extra staging exists or pays
its full physical costs. Net inventory flows can reuse newly produced widths;
disjoint changes to original helpers must additionally respect availability.

## Evidence and reproducibility

From the repository root, Python 3.12 standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/staged544-joint-price-region
```

Expected markers: `PASS_STAGED544_JOINT_PRICE_REGION`,
`PASS_INDEPENDENT_STAGED544_JOINT_PRICE_REGION` in the second JSON status,
`PASS_STAGED544_JOINT_REAL_CLI`, and registered outcome `completed`.
The package commands run with `-I -O -Werror -B`; no dependencies are installed.

For one inventory query:

```sh
python3.12 -I -O -B research/staged544-joint-price-region/verify.py --flows 0 48 0 0 0
```

The JSON reports `sharp_common_price: true` and a twelve-column witness.
`--flows 0 28 28 0 0` reports false. Negative inventory or negative flows
are rejected. The script first checks the frozen complete certificate.

[PROOF.md](PROOF.md) gives the universal linear elimination argument.
[RESULT.json](RESULT.json) contains exact outward bounds, boundary witnesses,
the separator, a non-tight feasible counterexample and semantic controls.
Two implementations separately classify all 2,551 patterns, with exactly
12 symbolic zero reduced costs and 2,539 strictly positive certificates.
They use different dual reconstruction, enumeration and exponential bounds;
neither imports the other checker or executes predecessor code.
Finite rational grids and actual CLI mutations are controls, not the proof
of the continuous region. All five axial boundary packings have integral
aggregate counts at T360; chronology and per-call ownership are untested.

## Source pins, independence and overlap

Canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6;
repository OS assignment `a1fddd441a9e9145c53ad1534170023f`, independent
verification, refined card `independent-moment`. The older card's #2979
mechanism now has live downstream audits; this session checks a new sharpness
implication in the changed-inventory relaxation rather than another moment root.

Exact retained bytes, Git blob IDs, SHA256 and paths are in [ORIGINS.json](ORIGINS.json):

- Erwan Secousses / ChaloupeMusic [PR3815](https://github.com/CrocSwap/integer-mult-bounds/pull/3815),
  `77ffbf287b6ca198b4a31e3835db3bae60718b93`, basis/model source.
- Sagar Thakrar [PR3862](https://github.com/CrocSwap/integer-mult-bounds/pull/3862),
  `b12d58d7b391b0d8490d6ebebe5cd0d4f57653b6`, proof and certificate for the
  individual basis ranges and width-unit screen.
- The model comes through dataisfire [PR3734](https://github.com/CrocSwap/integer-mult-bounds/pull/3734),
  `fa041037a3374eaa08feeca0b26a5d6893194147`, and zxv's PR3682. Their native
  provider, owner fill and full admission are inherited context, not rerun here.

Source constants are parsed with `ast.literal_eval` and compared to the model;
byte hashes are checked before mathematical execution. Retained source files
are data, never imported. All replay bytes are self-contained; no pending
Git objects or network access are required by the standalone checkers.
SOURCES.json pins the catalogue and selected record as historical provenance.

Entry overlap checked all six pages of 592 live open PR bodies, recent #1166
handoffs, the staging thread and the local overlap helper. The helper's remote
cache was missing; live API/browser reads supplied current coverage. Search API
results alone were incomplete, so the paginated inventory was used. This is
not exhaustive historical code-diff or every Discussion reply coverage.
PR3815 proves the incumbent ceiling; PR3862 prices widths and sufficient basis
ranges; PR3857/3875 refine/certify endpoints; PR3883 audits admission; PR3886
excludes a single-ADD retiming class. None is relabelled as this joint-region
contribution. Frozen predecessors are unchanged. No record priority is claimed.

## Scope and remaining obligations

The completed claim concerns one fixed-exponent ideal packing LP and the exact
region where its common dual is sharp. It adds no endpoint digits or kappa.
Literal staging identities, local-profile compensation, arbitrary dirty
restoration, source access, stock, chronology, per-call collisions, physical
and recursive costs, inherited all-size/compiler/precision/analytic/BIT
assumptions, human review and proof-kernel acceptance remain open.
The selected construction and frontier are unchanged. The existing selected
baseline binding check was run; its full cold replay was unnecessary and unrun.

## Open next questions

1. Construct one actual width-6..9 staging inside the enlarged region. First
   supply before/after words and the local-profile delta, then price them with
   these constraints. Dirty restoration and the full physical bill are blockers.
2. Certify the next optimal face outside the region. The explicit coupled
   counterexample supplies a feasible starting point and a separating row.
   Its successor optimum and any physical implementation remain unknown.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit and license

New independent reconstruction and joint-region analysis by ToikY, with
substantial OpenAI Codex assistance, including a separate AI implementation
and adversarial review. No independent human or proof-kernel review is claimed.
Apache-2.0. Credit Erwan Secousses / ChaloupeMusic for PR3815's model and dual;
Sagar Thakrar for PR3862's width-price screen and basis ranges; dataisfire for
PR3734; zxv for PR3682; Ross Richardson for PR3605 staging; Jeremy Kothe and
the retained supplier lineage. hexapode's PR3795/3802 chronological allocations
retain their separate result and priority. Retained predecessor headers and
notices remain intact.
