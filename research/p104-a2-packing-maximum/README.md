# The P104 A2-triangle packing maximum is 33

A packing of pairwise disjoint A2 triangles in the pinned 104-port set has at
most **33 triangles**. The explicit [packing](PACKING.json) attains this bound,
covering 99 ports and leaving five. Thus at least five partners require another
scheme in the disjoint-triangle routing architecture of
[Matarener's PR6217](https://github.com/CrocSwap/integer-mult-bounds/pull/6217).
This is a scoped proof with a finite attainment certificate. It supplies no
routing word, supplier admission, new kappa or complete multiplication theorem.

PR6217 reports a 33-triangle packing and explicitly leaves its maximality open.
The new contribution is the parity obstruction to 34, which settles that
question. The witness here was found separately; no predecessor packing or
routing theorem was audited. This contribution was produced by Nick Petalas.

## Proof

Write `u = 511`, the all-ones vector in `F_2^9`, and identify an integer port
label with its nine bits. Use the source's A8-coordinate root `r(q)`. For a
weight-three port, `x(q) = 3r(q)` has coordinate 2 on its support and -1
off it. For a weight-seven port with zero positions `a < b`, it is
`x(q) = 3(e_a-e_b)`. Both cases give the same coordinatewise identity:

```text
x(q) mod 2 = u XOR q.
```

For an A2 triangle, choose signs so that one of its roots is a signed sum of
the other two. This also follows directly from its norm-two Gram matrix. If
`A = <r_a,r_b>`, `B = <r_b,r_c>`, `C = <r_c,r_a>` are signs with `ABC = -1`,
then

```text
||r_c - C r_a - B r_b||^2 = 2 + 2ABC = 0.
```

Reduce the resulting integer relation among the three `x` vectors modulo
two. Signs disappear, and the displayed coordinate identity gives

```text
q_a XOR q_b XOR q_c = u                    for every A2 triangle.
```

The XOR of the 104 distinct labels in the pinned port list is zero. This is
one finite input calculation, authenticated and performed by `verify.py`.
Suppose 34 disjoint triangles existed. They would cover 102 ports, whose XOR
would be the XOR of 34 copies of `u`, hence zero. The two remaining labels
would consequently XOR to zero. They would be equal, contradicting their
distinctness. The counting bound already excludes 35 triangles, so the
maximum is at most 33.

The certificate lists 33 triangles by zero-based index in the pinned port
list. The checker verifies disjointness and every signed root identity over
the integers. It also checks the nonconflicting binary labels and the A2
Gram signs. It leaves precisely indices `12, 13, 54, 58, 98`, whose labels
are `73, 265, 152, 200, 239`. This proves attainment and finishes the proof.
The upper bound covers every possible A2 triangle, by the argument above;
it does not rely on an enumeration or a solver's infeasibility verdict.

The underlying parity argument is classical: if `6m+2` distinct binary
labels have total XOR zero, disjoint triples with one common XOR cannot
cover all but two labels. A putative `2m` triples would have total XOR zero,
forcing the remaining pair to coincide. The contribution here applies
this argument through the root/port parity identity to resolve the stated
P104 packing question.

## Evidence and reproduction

Only the port list is a live external input. Its path, Git blob and SHA256
are in [SOURCES.json](SOURCES.json), pinned at canonical main
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`. The verifier imports no predecessor
code and requires only the Python standard library. It does not enumerate
or recount PR6217's triangle catalogue or replay its routing claims.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p104-a2-packing-maximum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/p104-a2-packing-maximum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/check_research_commit.py --package research/p104-a2-packing-maximum --check-source-history
```

Elsewhere, replace the absolute interpreter path with CPython 3.12. Both
normal and optimized modes are registered in [VERIFY.json](VERIFY.json).
The final marker is `PASS_P104_A2_PACKING_MAXIMUM`. Each direct run prints a
generated receipt with SHA256 hashes of the package and live input. No
receipt is handwritten or stored in the package.

The checks cover all 104 root/label parity identities, the 33 attaining
triangles, all 487,200 ordered pairs of disjoint triples in the zero-XOR
eight-subsets of four-bit labels, and fifteen rejecting controls. The small
label enumeration corroborates the general parity argument independently of
the P104 geometry. It is not its universal proof. The rejecting controls
include overlapping triangles, a nontriangle, bad indices and types, a false
two-port leave, a missing triangle, duplicate ports and failed parity premises.
All mathematical checks remain enabled under `-O`.

## Scope and engineering decisions

The upper bound is for disjoint A2 triples in this exact port set. It does
not exclude overlapping routing schemes, different port sets, added helpers,
multistage relays or a different boundary contract. Maximality of a geometric
packing does not prove legal data delivery, dirty restoration or a favorable
complete signed invoice. The selected frontier and its five framework
assumptions are unchanged. Independent human and formal proof-kernel review
are unclaimed. No selected scientific replay, Lean or Docker build was run.

The verifier has no recursion or subprocesses. All geometry uses nine
coordinates, 104 ports and 33 triples. The small-label loop is bounded by
`C(16,8) * C(8,3) * C(5,3) = 7,207,200` candidate iterations before filtering.
JSON inputs are limited to 64 KiB. Functions stay below 60 lines and use
explicit runtime contracts instead of removable assertions.

Power-of-ten deviations apply to rules 3 and 9 in `verify.py`. Python's
managed runtime allocates integers and containers during checks; input sizes
and the fixed finite loops bound live state. The negative-control helper
uses only the explicitly named validator functions as call targets. Its
lifetime is one synchronous call, and every control must raise `ValueError`.
Normal and optimized warning-strict replay exercise these bounds and targets.
A fixed-storage native implementation or removal of the control helper would
be needed if hard real-time allocation or static dispatch became a requirement.

## Open next questions

- Can a legal wire-plus-helper program for one A2 triangle beat the complete
  swarm invoice? Start with one certified triangle, arbitrary initial public
  data and every physical entry, exit, sign correction and restoration charge.
  A constructive program and its full bill remain missing.
- Can the five exceptional partners be handled more cheaply by an overlapping
  or multistage scheme? Start with the five listed labels and name the changed
  contract. This packing result supplies no implementation or cost allowance.

Structured questions and the recorded scope change are in [TASK.json](TASK.json).
No follow-on search is part of this contribution.

## Credit

Matarener retains PR6217's routing question, reported 33-triangle construction
and routing lemmas, at head `6aa982f08190fb3f2bff8f4dee3eeaf0ba0412d9`.
Matarener's merged PR6166, `p104-carrier-code-uniqueness`, supplies the pinned
ports and A8-coordinate root interpretation. Ali Romman and DreamingOfClouds
retain the P104 word lineage, including PR5827, PR5907 and PR6030; the native,
caller, compiler and BIT contributions retain their existing attribution.
Root-system facts and binary parity are classical. The new maximality result,
attainment certificate and checker were produced by Nick Petalas. Apache-2.0.
