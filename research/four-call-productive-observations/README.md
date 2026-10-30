# A four-call partial-observation saving with two nonzero output updates

This contribution was produced by Nick Petalas. Apache-2.0.

**Finite exact certificate with a scoped algebraic proof.** Four fixed children
need exactly **two** paid adapters under partial observation, versus **three**
when both outputs are observed at every boundary. Their final endpoint is
`(x+a, y+a, a, b)` on arbitrary dirty input `(x,y,a,b)`. Both output-update rows
are nonzero. The complete fixed-child bills are **10 versus 11 XORs**.

This answers Open next question 2 of commdata2338's
[PR #2020](https://github.com/CrocSwap/integer-mult-bounds/pull/2020), at
`f4f8d2afdd3fec60c7739dcd826497e9738f80c1`. Its length-at-most-three census
and model are cited premises, not replayed deliverables. The new result is
one sharp four-call instance. No new kappa or supplier is claimed.

## Contract

Keep #2020's four coordinates `(d0,d1,w0,w1)`, all initially arbitrary.
A compulsory child `(o,s,t)` performs these two XORs in order:

```text
d[o] ^= w[s]
w[t] ^= w[1-t]
```

An adapter is one of the two workspace shears or one of the four XORs from
workspace into an output. Each costs one. Arbitrary finite adapter words may
occur before the first child and after any child. The children are indivisible
and their order is fixed. Outputs cannot feed workspace or each other. There
are no free operations, clean helpers, copies, erasures or extra coordinates.

The eager reference undoes each child's workspace shear immediately. At an
interior observation, only the specified outputs must match this reference.
At the end, both outputs and both original workspace coordinates must match.
The full-observation comparator has the same adapter alphabet and may also
retain noncanonical workspace between children.

Use the child sequence

```text
(0,0,0), (1,0,1), (1,0,0), (1,0,0).
```

Observe both outputs after children 1 and 3, and only `d0` after child 2.
The final boundary observes the complete state. Thus only one output at one
interior boundary is hidden. The two workspace shear directions both occur.

## Attaining words

Put `U: w0 ^= w1` and `L: w1 ^= w0`. The partial-observation word uses
`L` after child 2 and `U` after child 4, with no entry adapter.

| Completed boundary | Candidate state | Required eager outputs |
| --- | --- | --- |
| Child 1 | `(x+a, y, a+b, b)` | both: `(x+a,y)` |
| Child 2, then L | `(x+a, y+a+b, a+b, b)` | only `d0=x+a` |
| Child 3 | `(x+a, y, a, b)` | both: `(x+a,y)` |
| Child 4, then U | `(x+a, y+a, a, b)` | complete state |

For full observation, use `U` after child 1, `L` after child 2, and
`d1 ^= w1` after child 4. After child 3, workspace is `(a+b,b)` and the
outputs are `(x+a,y)`. Child 4 restores workspace to `(a,b)` but leaves
`d1=y+a+b`; its final output adapter removes b. This costs three adapters
and satisfies every full observation. Eager execution costs four adapters.

## Why the minima are exact

Every workspace shear is an odd permutation of the three nonzero vectors
of `F2^2`. Four child shears have even parity. Since data adapters do not
change workspace, any program restoring workspace must use an even number
of workspace adapters. With no workspace adapter, the four child shears
`U,L,U,U` have a nonidentity product. Thus at least two adapters are required
even under partial observation. The displayed word attains two.

Suppose a full-observation program had at most two adapters. The same parity
argument and nonidentity product force exactly two workspace adapters and
no data adapters. With no data adapters, the full observations force the
workspace row read by each child to equal the incoming a. Child 1 is the only
writer of d0. The observations of d1 after children 2 and 3, and at the final
boundary, force that same reader row a for children 2, 3 and 4.

Each of children 1, 3 and 4 applies U after its read. Immediately afterward,
the first workspace row differs from a by the nonzero second workspace row.
Workspace remains invertible, so this difference cannot vanish. Restoring
the required first row therefore needs an adapter in each of three disjoint
gaps: between children 1 and 2, between children 3 and 4, and after child 4.
Two workspace adapters cannot cover them. Hence full observation needs at
least three total adapters; the full-observation word attains three.

This proof is an identity over every vector space over a characteristic-two
field. In particular, it holds coordinatewise on dirty binary streams.
The independent finite checks below establish the same minima directly.

## Evidence and reproduction

`verify.py` enumerates every boundary placement and every ordered adapter
word of lengths 0, 1 and 2. There are respectively
`1`, `5*6=30` and `binom(6,2)*6^2=540` schedules, including entry preparation,
repeated gates and two gates in the same gap. Every shorter program is in
this list. No full-observation schedule succeeds; exactly two of the
two-adapter schedules satisfy partial observation, and none shorter does.

A coefficient-row interpreter and a separately written literal Boolean
interpreter agree on every one of the 571 schedules. The latter executes
each schedule on all 16 dirty inputs under both observation contracts,
giving 18,272 complete executions. Three attaining words add 48 executions.
Six semantic controls include a newly observed hidden output, missing final
restoration, a moved adapter, a clean-input false positive and its dirty
counterexample, and forbidden output-to-workspace feedback.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/four-call-productive-observations/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-call-productive-observations
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-call-productive-observations --check-source-history
```

Use the reviewer's Python 3.12 path in place of the local interpreter path.
The registered commands repeat the verifier normally and with `-O`. Both
print `PASS_FOUR_CALL_PRODUCTIVE_OBSERVATIONS partial=2 full=3 xor=10/11`.
The verifier emits a generated JSON receipt bound to SHA256 hashes of all
five package files and the pinned source contract. It writes nothing to the
checkout. Local replay used CPython 3.12.15 on macOS 27.0.1 arm64.

The predecessor README is the only declared external input. Its byte hash
authenticates the cited contract, without running predecessor mathematics.
The catalogue and selected record are historical provenance. Exact base,
Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).

## Limits and expansion decision

This is a fixed-call interface result. The two update rows are equal, so the
net update has rank one. Both outputs receive the incoming a.
If the children can be opened or replaced, two direct XORs implement the
same final endpoint. Ten is therefore not an unrestricted circuit minimum.

The comparison charges eight compulsory child XORs and every adapter. It has
no source-bound recursive caller, native frame maps, ownership/stock schedule,
tape movement, precision bound, compiler closure or outer invoice. Those costs
remain unspecified. No selected cold replay, Lean proof, independent human
review or full multiplication theorem is claimed.

The search stopped at its first improving four-call instance. Its initial
test hid d1 at all three interior cuts. Inspecting the attaining word showed
that it already meets the stronger observations after children 1 and 3, so
the certificate uses those stronger observations. No four-call census or
further construction search was run. Stop this contribution at the witness;
a physical expansion needs a named caller and a complete favorable bill.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates tuples,
lists and integers during verification. Four coordinates, four-by-four
coefficient matrices, five gaps, at most four adapters per positive word,
571 shorter schedules streamed one at a time, and 16 inputs bound live
mathematical data. Functions stay below
60 physical lines; all loops have these finite bounds. There is no recursive
search, dynamic code, network use or subprocess in the scientific verifier.

## Open next questions

- Can a four-call instance save adapters when its two final update rows are
  linearly independent? This would remove the rank-one limitation. First
  restrict #2020's model to rank-two net updates and seek one witness. The
  present result leaves that domain unsearched and unreserved.
- Does a real mandatory child chain permit this single hidden-output cut?
  First bind the actual observer, child and dirty-return contracts, then
  charge their full physical invoice. No qualifying caller is supplied here.

## Credit and scope

commdata2338's #2020 supplies the model, independent earlier census and the
explicit four-call question. Aaron Wang / navinor's #1155, Adam Gall's
`observer-safe-restoration`, and Sagar Thakrar's
`reader-restoration-cuts-seed53` supply the restoration and observation
lineage credited by #2020. Cinna Davis's #1930 studies a different
output-to-source prefix-chain contract. None of their files or credit lines
is changed or copied into this package.

The new contribution is the four-call witness, its two sharp minima and
their direct exhaustive check. The `coverage-law-change` card is marked
changed in [TASK.json](TASK.json): this is an abstract boundary-cost side
result, rather than a new productive target split on the selected word.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221578)
records that scope. Publication and archive intake do not establish supplier
admission or change the selected frontier.
