# Exact dyadic capacity of a helper cut

This scoped interface theorem computes the maximum simultaneous unit
pairings over D=Z[1/2]. For full dyadic bases of the eligible prefix and
suffix modules, form K. Its capacity is the number of Smith invariant
factors that are powers of two, or the minimum rank modulo an odd prime.
The algorithm returns both an attaining unit block and an upper-bound
certificate. Complete kappa is unchanged.

[PROOF.md](PROOF.md) gives the optimum and its helper-handoff application.
[capacity.py](capacity.py) computes the Smith transformations, saturated
kernel bases and unit block. [verify.py](verify.py) checks them by an
independent gcd-of-minors calculation. [RESULT.json](RESULT.json) records
2,401 exhaustive integer 2-by-2 matrices and 75 rectangular dyadic cases
through 5-by-5, the causal controls and five rejecting controls.

The causal prefix/suffix fixture has rational pairing rank one but
capacity zero because K=[5]. The converse fixture K=diag(3,5) has capacity
one although no entry is a unit. These prevent both rank-only false
positives and entry-only false negatives in helper searches.

## Reproduce

Python 3.12 and the standard library suffice:

```sh
python3 -B scripts/research_package.py --package research/dyadic-helper-channel-capacity
```

Both modes must print `PASS_DYADIC_HELPER_CHANNEL_CAPACITY`. The launcher
must print `PASS_REGISTERED_RESEARCH_PACKAGE`. Inputs are authenticated
before science. No Git or network is used by the scientific replay.

## Scope, source and credit

Base: canonical main `6cf7a683f447b9f1e2333791907fd92be5009a63`, priority 7.
The pinned [PR5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602)
proof supplies the causal helper interface. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19184494)
is separate from active physical cut searches. Current guidance and the
selected record were rechecked. Remote pages were complete; local notes
were sparse. No exhaustive novelty claim is made.

Credit Ali Romman's [PR5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599),
PR5602, [PR5609](https://github.com/CrocSwap/integer-mult-bounds/pull/5609)
and [PR5611](https://github.com/CrocSwap/integer-mult-bounds/pull/5611),
Nick Petalas's [PR5115](https://github.com/CrocSwap/integer-mult-bounds/pull/5115),
and their retained source lineage. Smith reduction and the Euclidean
algorithm are classical. The new contribution is their exact application
to the full dyadic helper pairing, with constructive and obstruction
certificates. Ali Romman with substantial OpenAI Codex assistance;
Apache-2.0. No independent human or proof-kernel acceptance is claimed.

Physical carriers, wire permutations, common frames, scalar work, growth,
all native maps, ownership, the caller and compiler costs remain payable.
No current P104 cut census, complete selected replay or outer funding run
was performed. The synthetic causal fixture is not a physical supplier.

## Open next questions

Apply this criterion to one source cut that has positive rational rank
but no known dyadic unit pairing. Use saturated kernel bases and publish
its Smith certificate before optimizing a circuit. A physical gain then
needs a permitted carrier and the complete revised paid/target invoice.
