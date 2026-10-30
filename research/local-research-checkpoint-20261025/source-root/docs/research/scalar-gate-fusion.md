# A concrete scalar-gate fusion pays back its apparent saving

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-09. Apache-2.0.

**Reject this one common-frame fusion. No improved supplier or κ.** We tested
a specific two-gate region in the selected complex word, crossing an actual
frame transition. In the aligned-register model below, its best common-frame
implementation costs two recursive rank-three transforms instead of one, even
allowing a retained copy of the unchanged control. This holds for every choice
of common exact Clifford frame within that model and its fixed boundaries.

The experiment does not exclude distributed fusion, changed boundaries, or a
new recursively closed family of mixed-frame operations. It does exclude
changing the common frame as a way to rescue this particular rewrite. The
[previous round's optimistic near-full-child packing](kappa-sixteenth-domain-round.md)
remains unimplemented; this region provides no instance of it.

## The actual region and its external contract

The pinned PR186 complex word has consecutive retained forward operations
16579 and 16580, using zero-based indices:

```
y = role 6795; x = role 6766; z = role 6983
16579: y += x, at frame U of dimension 5
16580: x += z, at frame V of dimension 8
```

The physical frame lists satisfy `U⊂V`. Their relative exact operator is
`R=T_V T_U^(-1)`, with Fourier rank `d=8−5=3`. The local core dimension is
22 and the full supplier dimension is `m=66`. The complete binary bases and
source hashes are in the [receipt](scalar-gate-fusion.json).

Both operations remain after terminal-sink deletion. None of their three
registers is a donor, recipient or deleted sink, and no compensation deadline
intervenes. They are consecutive in the actual rest-phase chronology, rather
than merely consecutive node labels in the producer DAG.

Cut the incoming/outgoing register edges at these two gates, retaining the
rest of the physical word. In register order `(y,x,z)`, the boundary frames are

```
inputs:  (U,U,V)
outputs: (U,V,V).
```

The two private registers use their original incident frames. The shared `x`
register crosses `U→V` between gates. External incoming/outgoing alignments,
later uses and the literal inverse cleanup stay outside this replacement and
are unchanged. This is a fixed-boundary subcircuit test, not permission to
merge its costs with unexamined neighboring edges.

On arbitrary physical streams the exact region acts as

```
(y,x,z) ↦ (y+x, R*x+z, z).
```

In particular, the first output needs the old `x`, not `R*x` or `R*x+z`.
All three inputs remain arbitrary; no dirty value is set to zero.

## Exact fused schedules and their complete charge

Move both scalar gates to `V`:

1. Apply `R` to `y` and `x`.
2. Execute `y+=x`, then `x+=z`.
3. Apply `R^-1` to `y`, returning it to its required frame `U`.

The endpoint is exactly `(y+x,R*x+z,z)`. Its three recursive calls have
widths `[3,3,3]`. Omitting the final return gives `R(y+x)` in the first
output and is wrong.

Alternatively move both gates to `U`: apply `R^-1` to `z`, execute the two
gates, then apply `R` to `x` and `z`. This also costs `[3,3,3]`. The final
return of `z` restores its arbitrary incoming value and its original frame.

There is a better version that the cost comparison must allow. Retain the
original `z`, copy it to a temporary stream, apply `R^-1` to the copy, and
use the copy in the second scalar gate at `U`. Apply `R` to the updated `x`
and clear the temporary by a scan. The original `z` needs no return transform.
This costs `[3,3]`, plus ordinary copying/clearing work. The temporary is
dependent storage, not another independent role that could enlarge `W`.
We grant the inherited linear copy/clear interface for this favorable screen.

The baseline uses the two scalar gates with only one width-three call on
`x` between them. Its recursive list is `[3]`. The scalar-gate count is the
same. Every old later operation sees precisely its old
inputs, so the inherited complete-word cleanup remains valid.

The checker uses matrices over rational Laurent polynomials in the actual
invertible operator `R`. It verifies every block of the forward map and both
inverse compositions. It does not assume `R²=I`: binary symplectic equality
alone would lose exact Clifford phases. A separate rational realification of
the complex one-axis `C` operator checks all 12 input columns of a small
three-register instance, including its non-involutory square. That small check
is an algebra control, not execution of the 66-axis supplier. The copy-based
schedule is also checked on all three independent inputs and clears its
temporary. It is not treated as a reversible permutation of four independent
registers; the checker rejects that interpretation of copy/clear.

## Why no other common frame helps

In the tested aligned-register model, both updated streams `y,x` are converted
to one common exact Clifford frame `K` and returned to their specified output
frames. The unchanged control `z` may bypass the core while a converted copy
supplies its value. Allow any `K`, even outside the present local subspace
family, and grant any pointwise scalar realization of the two gates there. Let

`A=dist(L_U,L_K)`, `B=dist(L_V,L_K)`.

The Lagrangian distance `dist(L,L')=m−dim(L∩L')` is the Fourier-rank charge
for the retained exact frame transitions. It is symmetric and obeys the
triangle inequality, so `A+B≥dist(L_U,L_V)=3`.

There are three charged `U` incidences: input/output `y` and input `x`.
There are two charged `V` incidences: output `x` and the incoming copy of `z`.
The untouched original `z` needs no output alignment. The favorable bill is
therefore three children of rank `A` and two of rank `B`, with zero ranks
omitted. Requiring in-place restoration of `z` would incorrectly add a third
`B` to this favorable bound. Any factored implementation
of an individual alignment has total rank at least its direct distance.
Each role retains its original volume `V_stream/W`; treating three independent
streams as one function call does not reduce their total volume.

For any recursive exponent `0<σ≤1`, subadditivity gives

`3A^σ+2B^σ ≥ 2(A^σ+B^σ) ≥ 2(A+B)^σ ≥ 2·3^σ`.

The original local contribution is `3^σ`, with the same normalization.
Thus **the best contribution in this aligned-register common-frame model is
exactly twice the old one**, attained by `K=U` with the retained-control copy.
The argument permits arbitrary common frames, not just a finite search of
known subspaces. It does not cover general coded boundary adapters, additions
at other frames, or partial updates that avoid aligning a whole updated stream.

Even illegally pooling all six required rank units into one width-six
child would cost more than the original width-three child. At the proposed
complex saving `3/40`, that optimistic ratio is `2^(37/40)>1`, checked by
exact rational enclosures. This makes the rejection robust to the tempting
but unproved cross-role pooling assumption from the preparation screen.

## What the experiment teaches and where it stops

Common-frame commutation is a valid identity when the same address operator
acts on every incident register. Here even the favorable copy-based schedule
retains an extra alignment; carrying work through the scalar gates does not
remove it. Relabeling the exact composite as a new typed child also
does not give it a faster implementation: the retained factorization already
uses just one relative transform plus two pointwise additions.

A different fused primitive would need a recursively closed implementation
that improves on that factorization, or a larger region whose external
obligations genuinely change. This experiment supplies neither. The common
frame bound applies to this cut and cannot be summed indiscriminately over
overlapping regions, where a boundary might be shared or removed.

Stop the experiment at this rejection. No second region, larger frame search,
new supplier compilation, production edit or background goal was launched.
The selected conditional witness remains `κ=0.000661885549259598`.

## Reproduction and attribution

```sh
python3 -B scripts/audit_scalar_gate_fusion.py --check docs/research/scalar-gate-fusion.json
python3 -B tests/test_scalar_gate_fusion.py
make selected-record-check
```

The tests include all 135 Lagrangian subspaces of a six-dimensional binary
symplectic control space. This checks the small metric ledger independently;
the all-dimension conclusion follows from the stated triangle inequality,
not from exhaustive testing in that control space. Adverse operator checks
reject missing alignment, missing restoration, a false involution assumption
and unpaid commutation.

The frozen word and frame choices retain Dugongue's PR186 on chafreaky's
PR181, eumemic's PR168 and their cumulative lineage. The exact frame metric
and representatives are inherited from icekylinx's
[general Clifford-frame note](../../notes/general-clifford-frames.tex).
This addition supplies a bounded source-specific fusion diagnostic, not a
new claim of priority for the underlying linear-algebra identities.
