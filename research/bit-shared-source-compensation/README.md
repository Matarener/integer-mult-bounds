# Four scalar ADDs saved in an actual shared-source BIT packet

An exact common-source factorization saves four ADDs in a pinned BIT packet
whose address projectors do not commute, while preserving every recursive
query and its charge. A separate audit
identifies why source-only query sharing fails on this packet's independent
dirty helper inputs. Its complete transport repair adds four rank-two queries.
No recursive moment improvement or new kappa follows.

The scientific base is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Both frozen inputs match [PR4021](https://github.com/CrocSwap/integer-mult-bounds/pull/4021)
at `c01f97ecfc7fa64847f6abd8f7b231e1df8c7b70` byte for byte;
[PUBLIC-PREDECESSOR.json](PUBLIC-PREDECESSOR.json) records their paths and hashes.
The frozen R438 word has 660 independent ordinary inputs and one private COPY
row that must be zero when opened and restored when erased. All other helper
inputs are arbitrary. Payloads are Boolean functions on pair-address space;
the signed integer lift is checked separately. The inherited public target
shear is Boolean: its integer lift still has even dirty-target terms.

## Exact packet and the failed mechanism

At original zero-based records 23325 and 23333, source 17 is added to helpers 444
and 413 at common frame 509. Their subsequent queries are:

| Helper | Record | Frame transition | Charged rank |
|---|---:|---|---:|
| 413 | 23405 | 509 to 390 | 2 |
| 444 | 23424 | 509 to 392 | 2 |

Writing P and Q for the corresponding symmetric delta projectors gives
`(PQ-QP)[0,1]=1/8`, so they do not commute in any odd address characteristic.
The original queries act on distinct helper registers and commute as
whole-register operations; noncommutation refers to their address labels.
Their common source contribution does not make the helpers' full inputs equal.
The actual entering rows contain independent h413 and h444 pivots. The
unchanged suffix distinguishes their contributions at public targets 111 and 114
with coefficient pairs `(1,0)` and `(0,1)`.

A source-only tour produces transformed copies of x but leaves each helper's
independent dirt untransformed. The required maps are `p(d+x)` and `q(e+x)`;
the proposed source-only maps are `d+px` and `e+qx`. Their missing terms are
`(p+1)d` and `(q+1)e`. Explicit Boolean point-indicator inputs at actual moved
addresses detect both errors. The proof excludes every source-only excursion
word in this stated class; it does not exclude arbitrary mixing of helper dirt.

[REPAIR.json](REPAIR.json) specifies a complete exact repair: retain both
helper queries, move each source read after its helper query, and transport
source 17 out and back for each read. Every inverse transport is charged.
Source17 returns before another reader and both helper delivery cuts are met.
The repair costs four additional rank-two queries, with no new field or COPY.

## Exact scalar sharing control and complete invoices

The same frame 509 prelude has an actual common-source factorization. Evaluate
its entering rows at cut23325, after retiming the existing arrival query for
v=371 and before any prelude ADD. With all seven source operands at this cut,
its two output rows are
`a'=a+b+u+C` and `b'=b+v+C`. First compute `b+=C+v` using six ADDs, then
`a+=b; a+=u; a-=v`. This uses nine ADDs instead of thirteen. C is never assumed
clean or materialized for free. One existing arrival query for v moves earlier
within the audited interval; its rank and cost are unchanged.

| Complete local word | Recursive queries | Rank mass | ADDs | COPY/ERASE episodes |
|---|---:|---:|---:|---:|
| Frozen comparator | 2913 | 5101 | 36005 | 9 |
| Source-transport repair | 2917 | 5109 | 36005 | 9 |
| Scalar sharing control | 2913 | 5101 | 36001 | 9 |

The comparator histogram is
`{1:1322,2:1342,3:79,4:39,5:102,6:11,7:18}`.
The repair adds `4e2`; the scalar control leaves it unchanged. Neither introduces
new helpers, private fields, COPY episodes or an uncharged retained output.
The frozen source-subtraction cleanup is unchanged. A separate execution of
the complete literal inverse also saves four scalar ADDs for the control;
that is not another saving inside the forward supplier.

For `Phi_m(r)=m^b*r^(1-b)`, the repair's complete query delta is `4Phi_m(2)>0`.
At m64 and b=1/500 this lies strictly between
`8.055644400453750470661584` and `8.055644400453750470661592`.
The scalar control's recursive moment delta is exactly zero under an unchanged
owner/controller contract. It cannot discharge the requested positive query
saving or the primitive b target. Native tape costs, all-size precision and
physical owner/compiler admission have not been established for either edit.
For the original word and scalar rewrite, the independent full-word signed
row-l1 prefix maxima are both 1302 forward and 1446 inverse;
cancellation-blind positive-majorant peaks are both 8402567 and 630744.
These comparisons do not substitute for an all-size precision theorem.

## Evidence and limits

The source audit replays all independent integer columns, original frame
conditions, COPY equality guards, the frozen suffix responses and literal
inverses. The algebra checker retains every group-basis coefficient in a free
product of involutions; its positive identities specialize to every actual
address action. It never infers formal group-algebra equality from a small
matrix representation. Actual-address counterexamples separately establish the
negative claims. An independent implementation reconstructs the source frames
using inverse Gram matrices and replays all 660 integer columns.

Run the registered checks from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/bit-shared-source-compensation
```

The generic hook uses the catalogue card `bit-new-register-model` as provenance
for this user-assigned changed scope; [TASK.json](TASK.json) records the narrower
question and stop rule. [SOURCES.json](SOURCES.json) pins that catalogue and the
selected record. Mathematical replay uses only the bundled archives and scripts,
so it also runs without Git or predecessor checkouts from any directory:

```sh
python3 -I -B /absolute/path/to/bit-shared-source-compensation/verify.py
python3 -I -O -B /absolute/path/to/bit-shared-source-compensation/verify.py
```

See [source audit](source-audit/README.md),
[word and compensation proof](algebra/SHARED-SOURCE-PROOF.md), and
[independent review](independent/REVIEW.md). Source lineage and overlap limits
are in [SOURCE-NOTES.md](SOURCE-NOTES.md). Exact executable evidence, written
all-input identities and formal-kernel proofs are distinct: there is no
formal-kernel or native execution certificate here.

## Open next questions

Structured next steps and blockers are in [TASK.json](TASK.json).
A further query-sharing attempt must escape the tested source-only restriction.
Possible approaches include carrying independent helper residuals jointly
through paid queries and cancelling all cross terms, or changing the downstream
demand so both residuals need not be separately available. These are candidate
directions, not an exhaustive classification. A scalar common-source
factorization alone does neither. Any such
attempt needs its own legal delivery cuts, paid source access, restored helpers,
complete cost comparison and demand/owner closure before recursive expansion.

Ross Richardson, with substantial OpenAI Codex assistance in derivation,
implementation, writing and separate AI review. Apache-2.0. No independent
human or formal-kernel review is claimed.
