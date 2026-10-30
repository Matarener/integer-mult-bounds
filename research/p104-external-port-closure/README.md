# Closing the P104 open program's external recipient histories

This answers [PR3423's 675-port handoff][handoff] at
`15d28c4de37dc47ea07cd7173c8b318fca7a4d75`, using the unchanged literal PR2586
word retained on canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
The result is a source-bound dependency and conditional numerical interface,
not a physical supplier or a new multiplication exponent.

## Result

The 63-bank open program's 675 outgoing ADDs reach 83 distinct recipient banks.
Their actual histories require substantially more inputs:

| Observations required | Events with private cleanup | Initial banks |
| --- | ---: | ---: |
| All 675 recipient states immediately after their port ADD | 2,907 | 263 |
| Final endpoints of the 83 recipients and 63 original banks | 3,812 | 265 |
| Also preserve the original endpoint histories of all 265 dependencies | 4,027 | 265 |

A state-version dependency graph and a separately written reverse-liveness
scan agree on the exact event and input sets. These are least closures in the
literal read/write graph with all touched private lifetimes closed. They are
not minima over algebraic cancellations, rewritten programs or different
implementations. Merely adding the eight erases is insufficient: their forty
cleanup predecessors must be included too.

The final 4,027-event projection has 2,310 ADDs, 1,597 native transports,
104 signs, eight private allocations and eight zero-checked erasures.
It reaches all 265 original endpoints without introducing more inputs.
It omits 1,371 word events and 93 initial banks. **696 omitted outgoing ADDs** to those 93 banks
are explicitly inventoried in [SUMMARY.json](SUMMARY.json); this projection
is not a replacement for the whole word on those omitted banks.

## Additional admission and an exact-half counterexample

Conditional on the inherited native chart identities and Gaussian Newton
module invariance, the coordinatewise-minimal independent dyadic product
entrance for **every retained atomic state** is:

- All 104 initial Y banks in `4B9`.
- The following 38 N banks in `2B9`:
  `2,4,7,9,18,20,27,29,35,36,40,44,45,46,48,49,50,54,58,59,64,65,66,70,74,75,79,80,81,83,84,85,87,88,89,92,98,100`.
- The other 123 dependencies in `B9`: 52 X, 32 D, 29 G, eight Q, and N33/N34.

Here `B9 = E Z[i]^512`, with
`E = [[1,0],[1,1+i]] tensor ... tensor [[1,0],[1,1+i]]` (nine factors).
One common grid `2^-f` can scale every displayed module.
Relative to PR3423 this adds 202 initial banks: 52 more strengthened Y inputs,
38 half-read N inputs, two ordinary N inputs, 52 X, 27 D, seven Q and 24 G.
It does not claim that correlated final-cut domains require these individual
scales; PR3426 studies such cancellations separately. The whole-word product
theorem of PR3406 is credited, not rediscovered: this result specializes the
entrance to the actual recipient closure, where N33/N34 need only `B9`.

The first added incoming boundary is event **312**, `X100 += N100/2` at the
empty frame. Set `N100(x)=2*x_0` on the 512 binary addresses, and all other
initial banks to zero. Every input belongs to `B9`, and all PR3423 63-bank
admissions hold. The division is exact in Gaussian integers, but its output
`X100(x)=x_0` has Newton coefficient `(1-i)/2` at index one, outside `Z[i]`.
The source coefficient is `1-i`. Amplitude four is the positive control.
This exposes an additional recipient admission obligation; it is not a defect
in PR3423, which explicitly left recipient histories open.

## Composed endpoints and widths

Write `A_F = Delta_F`, with the empty-frame map equal to identity. Under the
native covariance premise, at every retained state the exact physical value is

```
v_b(t) = A_frame(b,t) * sum_s r[b,s,t] * A_initial(s)^(-1) * v_s(0).
```

The certificate retains the complete rational rows, actual initial frames and
actual final frames. Initial X banks are not at the empty frame. Final frames
also vary; using PR3423's common frame at event 4516 for the later endpoints
would be incorrect.

All 213 non-X banks in the 265-bank projection return their normalized initial
rows. Each of the 52 X endpoints has its own initial X coefficient one, only Y
increments, and no residual N/D/Q/G dirt. The actual complete 52-by-104 Y map
has rational rank 9: every row has a retained nine-row factorization and a
9-by-9 minor has determinant `-1/128`. This is a different, larger operator from PR3423's
rank-one **subset of port increments**; the remaining histories are included
here. [CERTIFICATE.json.gz](CERTIFICATE.json.gz) provides every endpoint row
and the before/increment/after rows for all 675 ports.

If every initial real/imaginary component of the 265 physical inputs is bounded
by `H`, unitary chart maps give `32 H * ||r||_1` as a payload bound. The maximum
row norm is `127/2`, at event 3589 on X46, giving **2032 H**. This is the retained
whole-word norm bound, now bound to the recipient histories; no sharper global
width claim is made. Native prefix unitarity extends it to complete native
stages. Physical storage, temporary layout, caller heights, ownership, routing,
control, exposed representation conversions and recursive charges remain unpaid.

The inherited unchanged-profile `599/584` stopping decision remains. This
interface certificate does not justify another supplier-construction round.

## Evidence and reproduction

The checker imports no predecessor executable. It binds the unchanged WORD and
NATIVE files and all native occurrence/frame/rank records. Native operator
semantics are **assumed**, not proved by matching those records. PR3382's module
theorem and PR3416's broader native-covariance certificate are credited external
premises; PR3423's 392-occurrence check alone does not cover this larger slice.

The bounded check includes eight structural/semantic rejection groups, 142
one-bit-weaker input-scale controls, two dependent-row rank regression cases,
an exact rank factorization/minor, three independent literal scalar fixtures
comparing the projection with the full ideal word, and the exact-array Newton
counterexample/positive control. The full-word comparison is scalar algebra
under the chart premise, not a rounded native execution on unadmitted inputs.

```sh
python3.12 -B scripts/research_package.py --package research/p104-external-port-closure
python3.12 -I -O -B research/p104-external-port-closure/verify.py
```

Runtime uses only the standard library. `verify.py --emit` prints the complete
certificate; `verify.py --summary` prints its summary.
`oracle.py --full` prints the independently reconstructed closure.
[SUMMARY.json](SUMMARY.json) is the readable summary; [PROOF.md](PROOF.md) states
the conditional implications. Exact base, source hashes, context heads, overlap
coverage, environment and command outcomes are in SOURCES.json and TASK.json.
No heavy native replay, Lean check or selected-frontier replay is claimed.

## Open next questions

1. Can a paid caller supply this 265-bank entrance and physical layout, including
   the 52 additional `4B9` and 38 `2B9` admissions? Start with the explicit input
   list and event-312 witness; stop at any unproved divisibility or ownership
   premise. Current H and input modules are assumptions, not preparation costs.
2. If using the projection inside the original word, how will its omitted
   outgoing effects be supplied and paid? Start with the exact omitted-ADD list
   in SUMMARY.json. The selected endpoints alone do not preserve those effects.
   Any changed supplier/profile must first pass a compatible full cost screen.

## Credit and scope history

Hiroki Kumazaki, with substantial OpenAI Codex assistance for analysis, code,
execution, writing and separate AI-agent review. No independent human or
formal proof-kernel review is claimed. Apache-2.0.

Credit Clear1nsight (PR3423/3382 and the explicit handoff), ywz65 (PR2586 word
and native recipes), Arham Tahir (PR2665 binding and PR2674 atomic row/grid
bounds), Tekalign (PR3025 literal wrapper/ledger), Ross Richardson (PR3068
period domain), Nick Petalas (PR3406 product domain, PR3416 native covariance,
PR3426 correlated entrance), and the original geometry/native/compiler lineage.
Jose Manuel's unchanged-profile stop and Vasek's PR2744 audit remain credited.
The main `p104-whole-word-internal-grid` package already proves the whole-word
row norm and an alternative sufficient enlarged fixed grid.

This refines the current P104 producer/consumer question by taking the released
PR3423 handoff, rather than repeating the preceding PR3044 audit or reopening
fixed-cover matching searches. Entry overlap covered 353 open PRs and 2,277
Discussion records with complete pagination; literal numeric searches have
false-positive matches. Focused PR3423/675-port and canonical-thread checks
found no other published closure for this handoff. Coverage excludes unpublished
work and exhaustive historical diffs. The canonical claim is recorded in TASK.

[handoff]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009429
