# Optimize a target partition with all piece fees

Use a declared menu of smaller targets to replace one existing target. The tool
searches every permitted multiplicity vector with the same total rank, charges
each piece fee, and returns the best complete invoice at a rational exponent.

```sh
python3 -B scripts/optimize_target_partition.py BASELINE.json PLAN.json \
  --exponent 0.9969 --bits 128 > partition.json
```

The plan has schema `integer-mult-target-partition/v1`, `target_rank`,
`max_pieces`, and `options`. Each option has a unique `id`, a smaller positive
`rank`, and a `fee` invoice. Each fee uses the baseline contract and has no
target credit; an empty paid histogram is an explicit zero-fee declaration.
The baseline must contain at least one target of the replaced rank R.

If option i is used n_i times, require `sum n_i*r_i = R` and between two and
`max_pieces` total pieces. The cost change is

`R^t + sum_i n_i*(fee_i(t)-r_i^t)`.

The returned invoice removes one rank-R target, adds all chosen piece targets,
and adds every fee. Other paid jobs and targets remain in the bill. The fee menu
must include any per-piece adapter, route, or restoration charge. Nonadditive
interactions need a different model or a complete combined option.

For example, partition a rank-16 target using free rank-1 and rank-4 pieces and
a rank-9 piece with one paid rank-1 fee. At `t=1/2` and at most eight pieces, the
best choice is four rank-1 and three rank-4 targets. Its signed cost improves by
6. The tool finds this complete partition; a single split need not be optimal.

## Exact finite optimization

Each power has a directed dyadic bound from the existing power evaluator. After
scaling by `2^bits`, all dynamic-program costs are integers. A state records
processed options, total target rank, and piece count. Each transition chooses
the multiplicity of the next option. Every legal count vector appears once.
The minimum lower-weight path bounds the true optimum from below. The minimum
upper-weight path supplies a feasible partition and bounds it from above.

A third pass excludes the chosen count vector. It adds one Boolean state that
records whether an earlier multiplicity differs from that vector. A difference
cannot disappear because each option is processed once. This pass gives the
minimum lower bound of every alternative. `certified_optimal` is true only when
that bound is at least the chosen upper bound, or no alternative exists. The
common `R^t` term cancels in this comparison. Interval overlap leaves optimality
unresolved; it does not prove equality.

`recommendation` separately reports a certified improvement, no strict
improvement in this menu, or unresolved improvement. The minimum is over proper
partitions; the baseline remains available when a partition costs more. A narrow
menu cannot establish a general obstruction to target refinement.

Limits: replaced rank 2..256, 2..32 pieces, 1..16 menu options, 128 distinct power
ranks, and 16..256 dyadic bits. Conservative count/support checks ensure every
possible menu combination stays within invoice schema limits. Inputs are hashed.
Invalid plans exit 2 without a partial result; a valid menu with no partition
returns `feasible: false`.

## Open next questions

Prove that the proposed pieces are independently useful targets. Implement the
source maps and complete the fee inventory. Check the complete caller after the
replacement. The optimizer does not supply those proofs or admit a new κ.

Credits: exact knapsack dynamic programming, the existing signed-invoice and
power-bound tools, mightyOil's T16 audit, and retained predecessors. Prepared for
Ali Romman with OpenAI Codex assistance. Apache-2.0.
