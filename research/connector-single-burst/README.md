# A gap-optimal two-burst schedule for the frozen escape circuit

The eight-field normalized binary escape circuit from Ali Romman's PR5673
can put its eight rank-one, square-zero thin queries in **two bursts of four**,
instead of the source's three bursts of six, one and one. The new schedule
preserves all six full-call matrices and the complete polynomial endpoint.
**Two is optimal:** no reordering of those full calls admits a single burst,
even with arbitrary constant connector matrices over any characteristic-two
field. No new physical supplier or kappa is claimed.

The lower-bound package checks all **720 orders and seven gaps (5,040 cases)**.
Every case has an explicit XOR certificate of `0 = 1`, using at most three
coefficient equations. The upper bound is an emitted fourteen-call word,
checked in the full polynomial ring. The two aggregate burst matrices have
rank four and are not themselves square-zero; each is explicitly decomposed
into four rank-one square-zero queries. It is those eight queries that are
replayed and counted.

The one-burst lower bound is also a corollary of PR5673: at all x variables
zero, a single aggregate burst is forced to be `I+sum R_i`, which has equal
leaf signatures; its theorem permits arbitrary thin matrices. The literal
linear certificates here corroborate that corollary without using its proof.
**The distinct constructive result is the two-burst schedule and the resulting
exact optimum for this frozen word.** PR5681's static rank witnesses are
complementary and do not supply this chronology.

The full-call frames and eight-field inventory are frozen. This does not
cover changed full matrices, extra full calls, connector entries depending on
the stage variables, or larger circuits. It does not settle PR5673's seven-query
timeouts: fewer queries spread among multiple gaps remain a different question.
The inherited optimistic P104 invoice is unchanged and loses for every concave
moment; no physical/native lift, compiler or outer admission is supplied.

## Reproduce

From the repository root, Python 3.11+ standard library only:

```sh
python3 -B research/connector-single-burst/verify.py
```

Expected: `PASS_SINGLE_BURST_OBSTRUCTION`, 720 full orders, 5,040 checked
certificates, six rejected mutations, an eight-query two-burst schedule, and the full-word
negative control.
The checker is read-only, works without Git/network/solver, and also runs with
`python3 -I -O -B`. It checks all polynomial coefficients, not stage-variable
samples or just first mixed coefficients. Typical runtime is about one minute.

Optional deterministic regeneration (keep the committed file unchanged):

```sh
python3 -B research/connector-single-burst/generate.py --output /tmp/burst-certificates.json
cmp /tmp/burst-certificates.json research/connector-single-burst/CERTIFICATES.json
```

The checker does not import the elimination/search generator. It shares the
small matrix/polynomial engine, so this is not claimed as a fully independent
implementation or proof-assistant verification. No repository-wide or selected
frontier replay is required by this isolated note; neither is claimed here.
The optional generic package registration was not used; this directory is a
standalone, source-bound research package.

## Proof and certificate format

Write `x_j=D_j+1` and work in `K[x_0,x_1,x_2,e]/(e^2)`, where K has
characteristic two. A frozen full call is

`(I+x_j P_i)(I+e R_i) = I+x_j P_i+e R_i+e x_j R_i`.

The source checker verifies `P_i R_i=R_i P_i=R_i`. Every stage appears twice,
so exponents of each x variable are at most two. The e-free endpoint is the
required `A=product_j(I+x_j E_j)` for every one of the 720 orders. Write the
full-call product as `A+e B`.

Any consecutive burst reduces exactly to `I+e Z`, with `Z=sum Z_i`, because
`e^2=0`. Allowing arbitrary Z relaxes all rank, nilpotence and native-realization
constraints. If L and R are the e-free suffix and prefix at a chosen gap, the
required endpoint `(1+e)A` is equivalent to

`L Z R = A+B`.

This is a linear system in the 64 constant entries of Z. Each coefficient of
`x_0^a x_1^b x_2^c` and each matrix entry supplies an equation. There are
27*64 equations, including zero equations. Row index is
`64*(9*a+3*b+c)+8*i+j`; unknown index is `8*u+v` for `Z[u,v]`.
The associated column is the encoded polynomial `L E_uv R`.

For each order/gap, `xor_rows` in CERTIFICATES.json lists equations whose
left sides cancel and whose right sides sum to one. `verify.py` reconstructs
these equations and checks the sum literally. No solver verdict is trusted.
Because the equations and certificates use only 0 and 1, the contradiction
persists under extension to **every characteristic-two field**. This is a
finite, source-specific algebraic certificate proof; it is not a formal proof
of the multiplication theorem or of arbitrary connector schedules.

The two-burst witness is replayed directly as a complete polynomial word.
Its eight explicit rank-one square-zero factors prove that the minimum
occupied-gap count for these normalized binary queries is exactly two. This
is not a physical native implementation: arbitrary binary query maps still
need a characteristic-zero/native lift and paid adapters.

## Complete optimistic price and stopping decision

The schedule retains eight fields, six full calls and eight rank-one thin
queries, without new algebraic helpers or copies. At the pinned PR5599 P104
local tariff, the optimistic 104-port price is

`208 H25 + 624 H9 + 6*(helper profile) - 6*(paid profile) - 832 H1`.

The verifier derives this from the byte-pinned P104-TARIFF-SOURCE.json and
records the complete signed histogram. Its linear margin is **-336**; every
positive coefficient has rank at least 8, and every negative coefficient has
rank at most 7. Hence for `0<=t<=1` its moment is at most
`-336 * 8^(t-1) < 0`, since `r^(t-1)` decreases with r. This favorable price
already fails. Any required native frame adapters, source access, copies,
restoration, owned work and recursive implementation must still be supplied
and charged; they are not assigned zero cost or hidden in a kappa claim.
There is therefore no reason to run the outer assembly or seek more digits.

## Sources, credit, scope and experiment record

Base commit: `df0137efd35e11b4445734bf612bdd4c7ebc330c`.
[SOURCES.json](SOURCES.json) pins PR5673 at
`c10f75f09e41803ae8efe478331a7509b7379b2f`, including the source Git blob and
SHA256. SOURCE-WORD.json is a byte-for-byte copy of its ESCAPE-WORD.json.
No predecessor code is imported. [CLAIM.md](CLAIM.md) records assignment seed
26, candidate selection, overlap and stopping rule. [RESULT.json](RESULT.json)
records completed coverage and controls. No timeouts or unresolved cases occur
in the stated domain. This is an exhaustive finite obstruction, not an
impossibility theorem for changed circuits.

Ali Romman supplied the source escape word and PR5673 theorem/search package;
Cinna Davis supplied the controller/simplex lineage, and PR5617/5631/5649
precede the connector work. PR5681 at
`67f07448eec5ad8d84bdf96b46981ac0b893592f` provides complementary static rank
witnesses; its code is not used. The current accepted conditional kappa at this
base is 62009/20000000 from PR5599, whose review and construction were read.
This note does not modify it or discharge its five native-realization,
ownership, compiler, precision/tape and analytic assumptions. No physical
adapters, restoration, recursion or outer assembly are implemented here.

Prepared for GitHub contributor **theon199** with substantial **OpenAI Codex**
assistance in analysis, implementation, testing and writing. No subagents or
independent human review. New work is Apache-2.0; source attribution is
retained in [NOTICE](NOTICE).

## Open next questions

- Can two or more occupied gaps admit fewer than eight legal rank-one thin
  queries for these fixed full matrices? Start from the saved two-burst
  witness, impose square-zero/rank constraints and replay every coefficient.
  The two-burst factors supply an eight-query starting point; minimizing
  occupied gaps does not minimize the number or cost of queries.
- Does a changed full-call frame admit a useful single-burst word? First
  generate the changed matrices and rerun the exact linear feasibility
  screen. Any positive word still needs a characteristic-zero/native lift,
  complete paid adapters, owned work, restoration and compiler admission.
