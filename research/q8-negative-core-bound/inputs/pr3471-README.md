# Multiple negative Q8 targets with restored dirty roles

The positive-label direct bill is sharp for all 152 endpoints in this finite
certificate. No saving or new multiplication exponent is found.

- With exactly three roles, every target list from `{i,zi,j,zj}` containing
  two negatives costs seven calls; every all-negative list costs nine.
  These are 24 and eight ordered endpoints respectively.
- With exactly four roles, two negative-generator targets, one positive
  generator and one restored identity spectator cost seven calls. This covers
  all 96 ordered endpoints, including every spectator position.
- With exactly four roles, two negative-generator targets and two restored
  identity spectators cost six calls. This covers all 24 ordered endpoints.

Here `z=i²=j²=-1` is a group element, distinct from the scalar one in
`F2[Q8]`. Every paid call is `D_N(g)=I+([g]+1)N`, with `g` in `{i,j}` and
`N=u v^T` a binary rank-one idempotent. Each call costs one. All inputs are
independent arbitrary dirty data, including spectators. Acceptance is exact
matrix equality in every group-algebra coefficient. Only scalar `GL_r(F2)`
mixing is free. There are no clean inputs, erasures, free address changes or
higher-rank calls. Extra roles beyond each declared width are outside scope.

This answers a bounded part of [PR3460's multiple-negative handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3460).
That written theorem already handles one negative target at arbitrary width;
its single two-call excess does not establish these multiple-negative bills.
[Aaron Wang's PR2318](https://github.com/CrocSwap/integer-mult-bounds/pull/2318)
already gives all two-role values. The six-call value here extends its negative
pairs to two additional restored dirty roles. The certificate does not prove
an arbitrary-workspace multiple-negative tariff.

## Why the finite exclusion proves each minimum

Move free scalar matrices through paid calls by conjugation. Every conjugated
coordinate projector is a binary rank-one idempotent, and all such idempotents
are allowed. Augmentation sends both the endpoint and each paid call to the
identity, so the residual scalar matrix is the identity. Exhausting this
factor alphabet therefore covers arbitrary interleaved free mixing.

For `r=3`, there are 28 idempotents and 56 factors. For `r=4`, there are 120
idempotents and 240 factors. Each nonzero binary rank-one matrix has a unique
pair of nonzero vectors `u,v`; the condition `v^T u=1` selects exactly the
idempotents. There is no heuristic pruning.

The first-order character with value one on `{i,zi,j,zj}` and zero on
`{1,z,k,zk}` maps `[g]` to `1+chi(g)*epsilon`, with `epsilon²=0`. An endpoint
with `W` generator targets forces `sum N_l=P`, where `P` is its active
coordinate projector. Binary trace gives `n=W mod 2` because every allowed
idempotent has trace one. Thus the triple endpoints need odd call counts,
and the pair endpoints need even counts.

The engine stores complete balls and uses exact meet-in-the-middle equality.
For a target `T`, `P Q=T` is equivalent to `Q=P^-1 T`. The inverse of a
positive call is the same idempotent at label `zi` or `zj`. Reversal and
inversion biject positive prefix words with words in this inverse alphabet.
For each target, the engine transforms the whole inverse ball on the right
by `T` and tests every positive suffix. It includes the prefix ball itself
and every one-factor extension, so all shorter suffixes are covered too.

- Triple/two-negative endpoints have no word through length five, using
  a two-plus-three split. Parity excludes length six; direct words attain seven.
- Triple/three-negative endpoints have no word through length seven, using
  a three-plus-four split. Parity excludes length eight; direct words attain nine.
- Four-role/two-negative/one-positive endpoints have no word through length
  five, using a two-plus-three split. Parity excludes length six; seven is attained.
- Four-role/negative-pair endpoints have no word through length four, using
  a two-plus-two split. Parity excludes length five; six is attained.

Role permutations and the Q8 automorphism interchanging `i,j` preserve the
paid alphabet and unit prices. The representatives are `332,334,352` and
`333,335` at width three, and `3320,3340,3520` and `3300,3500` at width four.
Digits encode `1,z,i,zi,j,zj,k,zk` as `0,1,2,3,4,5,6,7`. These are ten
role-bound symmetry orbits, or seven shapes if the same triple is identified
across its two tested widths. The independent oracle enumerates every labelled
target and checks that these representatives cover exactly the 152 endpoints.

## Evidence and replay

[RESULT.json](RESULT.json) is a deterministic receipt, not a trusted input to
the search. The native engine recomputes all membership tests before comparing
it. Its stream counts include repeated states and must not be read as distinct
word counts. The largest positive prefix ball and inverse ball each have
91,955 states at width three/depth three. Width four/depth two has 42,041 states.
The largest stream tests 10,131,881 candidate occurrences.

The separate Python oracle builds Q8 by integer Hamilton multiplication and
uses ordinary full matrix/group-algebra convolution. It independently regenerates
all stored balls, checks all 64 native group products and 8,502 probe matrices,
and separately repeats the three-role two-negative and four-role pair meet
queries. The longest three-plus-four query and the four-role two-plus-three
stream use the native search after these checks; a second full implementation
of those complete membership streams is unclaimed.

All 152 direct words match their complete formal endpoints. Every one of their
1,056 single-call deletions fails. Positive three-call controls produce hits in
the search. Behavioral controls reject actual native faults in the paid action,
noncommuting product order and fourth-role restoration, as well as source drift,
receipt type corruption and receipt overwrite attempts. These checks corroborate
the finite exhaustive certificate. They are not proof-kernel verification.

Requirements are Python 3.12 or newer and `clang++` or `g++` with C++20 support.
The wrapper compiles with `-Wall -Wextra -Wconversion -Wsign-conversion -Wshadow
-Wpedantic -Werror`. Set `TMPDIR` to a private directory outside the checkout;
binaries, ball dumps and temporary exports are removed when replay finishes.

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/q8-multiple-negative-census
python3.12 -I -O -Werror -B research/q8-multiple-negative-census/verify.py
python3.12 -I -O -Werror -B research/q8-multiple-negative-census/test_package.py
```

Direct commands also work from the committed Git-free package export with its
two declared inputs. They make no Git or network calls. The generic package
runner additionally checks the historical catalogue and selected-record pins.
[VALIDATION.md](VALIDATION.md) records diagnostics, resource bounds and limits.

## Sources and credit

The scientific baseline is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
[SOURCES.json](SOURCES.json) pins Aaron Wang/PR2318's pair certificate and
ywz65/PR2587's mixed uniform proof. Both remain byte-for-byte unchanged.
Nick Petalas/PR3450 supplies the inverse-label class tariff and combined
character; PR3460 supplies the sign-sensitive equality boundary and the present
handoff. No pending foreign Git object is required for replay.

Retain Cinna Davis/PR1925/2047/2248, steph4n-gh/PR1573, Tuafo,
eumemic/PR288, Ali Romman/PR468, Gareth Davidson/PR1333, Navinor/PR1822,
woklerx/PR1443 and the retained register-model lineage. Arham Tahir/PR3137's
physical compiler and Nick Petalas/PR3461's scalar preparation distance are
separate from this formal paid-word census. New work is Apache-2.0.
Nick Petalas. Independent human and formal proof-kernel review are unclaimed.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19010131)
records the live scope. Initial complete overlap at 02:57-58 UTC on
2026-10-18 covered 381 open and 2,761 closed PR bodies plus 2,306 Discussion
records. This coverage excludes arbitrary diffs and unpublished work.
Submission refresh at 03:05-06 UTC retained the same canonical main and guidance;
complete pagination covered 381 open and 2,761 closed PR bodies plus 2,311
Discussion records, with no warnings or new matching Q8 contribution.

## Open next questions

Does a larger restored dirty workspace permit multiple negative-generator
targets to share their sign charge? A sign-sensitive second-order invariant,
or one exact word outside these certified domains, would decide more than
another unchecked search. The first-order character forgets the sign, so it
cannot supply the missing bound. [TASK.json](TASK.json) records this question.

The three-negative target at width four, arbitrary widths, nonuniform prices,
nilpotent couplings, other target classes and native physical supplier costs
are unclaimed. An actual paid caller, ownership/access/movement/precision
invoice and a completed consumer remain separate obligations. The selected
cold replay, Lean, Docker, all-size multiplication theorem and selected-frontier
update are unrun. No broader construction round is reserved.
