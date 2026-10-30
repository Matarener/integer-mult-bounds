# Whole-cover storage installation and immutable current-bank return

This is the storage component of the proposed post-QQ16 connection. It does
not identify the recovery's original values with the caller's required current
values. The continuation component must first perform its proved current-value
and frame reconstruction, in the actual parent numerical representation.

The selected fence is after the complete `QQ16 B_1_2` local-cover sweep
(original event 4), before original event 5's idle sweep and event 6's two-legged bridge. The new global producer binding expands the original event into explicit barriered groups and exposes its `global_fence` (573 in the frozen compilation); the service passes that authenticated fixed event to `expected_event`. It is
not a cut inside one 704-packet gathered local group. Recovery's cover maps
require entire fields and barriers between cover sweeps. The actual source
`finish_group` commits the last group's modifications to `roles['current']`,
sets `group=None`, advances `cover_index` to the cover cardinality and resets
`pc=0`. At this fence the parent's BankPackets is closed. Its next original
`next_group` advances to the next event. `CallerStorage` checks this finite
control fence; the integrated source binding separately authenticates that
its expanded fence corresponds to original selected event 4.

## Physical boundaries

1. **Producer entry/fence.** The active caller owns its complete current bank,
   fourteen input and four derived descriptor roles, finite control and any
   ancestor continuation stack. All original 704 bank packets and eight private
   packets are closed after group commit. Their bodies being empty grants no
   permission to reuse hidden primitive scratch. The parent is not closed and
   cannot be passed to `Machine.run` again.
2. **Prepared service entry.** A separate `BankPackets(F,1,224)` gathers the 224
   selected entire families. Its per-row extent is `Gamma * parent.row_bits`,
   supplied by encoded `Count` multiplication, and its row count is parent
   `unused=U`. Its source remains the exact parent current bank. Each acquired
   field has `V=P*Gamma*U*row_bits` bits and order prefix, cover, unused-row,
   complete within-row address/coefficient/component. The separate native
   compiler interprets this as `P*Gamma` prefixes and `U` rows. No cover,
   spectator, compact field or outer row is discarded. These 224 acquired
   fields remain borrowed inputs while the decoder owns 224 separate outputs
   and 16 separate private fields.
3. **Completed recovery/reconnection return.** D has completed every borrowed
   read. All its private fields are zero or empty and are physically erased.
   Reconnection may reuse those now-retired private roles; its last use also
   closes them. The 224 outputs contain the proved current values in the
   parent's actual frame and numerical representation. The separate native
   Machine and wrapper must be closed, their outputs consumed and their scratch
   closed. `ready` checks every output's exact complete extent before the first
   destructive parent publication. This is a length/ownership test, not an
   arithmetic certificate.
4. **Continuation exit.** Each output is physically transferred to its now
   read-complete acquisition packet. The inherited acquisition `scatter`
   reconstructs the full bank, preserving every unselected family verbatim;
   inherited `commit` copies it to the immutable parent `current` tape and
   retires its acquisition packets. All 240 service fields are empty. The
   parent's control, descriptors and ancestor stack still identify the same
   fence. Original next-group execution performs the idle work, both bridge
   legs and later return. Semantic equality of their inputs must be supplied
   by the integrated continuation proof. The implementation's optional engine tuple checks actual closed/consumed-output flags when supplied; the production integration supplies its real engines. A fixture with no service native calls does not imply their production closure.

## Ownership, generations and return proof

The service constructors allocate fresh, pairwise distinct physical Tapes before
execution: 240 output/private tapes; 224 acquisition tapes, one acquisition
output and 16 acquisition scratch tapes; and a 64-tape descriptor pool. This is
**545 new fixed roles**, in addition to the existing caller, numerical bridge,
separate closed C Machine and wrapper Ordinary inventories. The packed decoder's input/output banks and its controller inventory are additional to these 545 roles and must be retained in the integrated ledger. The two distinct
backend inventories required by #4129 are retained. No parent productive helper,
parent scratch lease, or reserve-bank address is counted as service storage.
The service's own allocation scope runs with the parent scope suspended. Native
execution must likewise suspend the service scope and use its own inventory.

`CallerStorage` uses a fixed finite output/private selector and phases
`closed -> decode -> reconnect -> ready -> closed`. It permits no new generation
before the preceding outputs retire, no early commit, and no indexed output
access after retirement. Only a compiled, nonescaping use of these selectors is
claimed. An unrestricted Python client can retain a raw Tape reference, so this
is **not** a general revocable-handle API or a claim that arbitrary stale Python
references become harmless. The actual inherited ScratchPool has its own
active-lease discipline; its contracts remain separate.

At the fence, the whole current bank is preserved by acquisition. All subsequent
arithmetic operates on disjoint service storage and dedicated engines. The
parent descriptors, primitive pools, capsule, protected output, other live
roles and ancestor stack are unreachable from these declared destinations.
Thus their complete bodies and canonical heads are preserved. The baseline keeps the fixed
current-bank identity; the opt-in internal-role adoption below updates every
source role binding while preserving the public output and borrowed input identities. At publication, source `transfer`
consumes each output into its acquisition packet. Since all input reads have
ended, erasing that old acquired packet is legal. Source `scatter` emits exactly
one full replacement bank, choosing the selected packet at each selected family
and the original bank at each other family. `commit` then pays the physical copy
into the original current role. Every output retires after its actual last
publication use. The parent is ready to execute its original next instruction.

This proof is at arbitrary admitted packet extent. It is conditional on correct
arithmetic, source closed-scratch and admission contracts. It does not promise
rollback from arbitrary malformed primitive failures after publication begins.
All returned extents and closure conditions are checked before publication;
source mutation during the suspended interval is outside the admitted execution.

For the default fixed-copy path, the unchanged #3464 source-relative parent-return theorem applies directly:
current `machine.py`, `parking.py`, `bank_packets.py`, and `selected_binding.py`
are byte-equal to that package's `inputs/pr3385` files. Therefore subsequent
recursive descendants preserve the restored continuation under #3464's callee
completion and primitive-closure premises. Its `4B+733` stack-frame length is an
encoding identity, not the service invoice or a new arithmetic theorem.

## Constructive local bill and high-water backing

Let F=14336, Gamma be the selected cover cardinality, P the outer-prefix count,
U the exact unused-row quotient, and E=Gamma*row_bits. Then

```
B = P*F*E*U                 complete immutable parent bank bits
V = P*E*U                   one full family field bits
bE = bitlength(E*U)          encoded within-prefix field extent
bP = bitlength(P)
```

`row_bits` retains the actual component width H_b, both real/imaginary
components, coefficient count and every address field. It is not based on W_c
unless a separate proved representation conversion produces the parent's actual
format before publication.

The local storage invoice is the **sum of executed disjoint intervals**:

```
T_descriptor
+ T_gather(B,P,F,E,U)
+ T_discard_owned_dirt
+ T_private_zero_check_and_retire_at_D_end
+ T_private_zero_check_and_retire_at_reconnection_end
+ T_validate_224_outputs
+ sum(i=0..223) T_transfer(old_acquired_i, completed_output_i)
+ T_scatter(B,P,F,E,U)
+ T_commit_and_release(B,224,V)
+ T_finite_control.
```

Every term names source or new physical loops. `T_descriptor` includes encoded
multiplication, division/stock checks, construction and retirement of Counts;
it is the packet/compiler component's bill and must not be treated as zero or
counted twice. The arithmetic/native/correction invoice is additional. The
baseline's unchanged work remains in both full comparisons. This storage
mechanism removes no original arithmetic interval by itself.

For equal old/new field lengths V and canonical heads, literal counting of the
current `parking.transfer` gives `7V+7` reads, `3V` writes and `6V+10` moves,
**16V+17** cell actions per output publication into acquisition storage. For
unequal old/new lengths A/V the corresponding total is `5A+11V+17`. This
transfer is actually executed; #3380's different implementation's 22V+13 saving
is not imported. `scatter` and `commit` subsequently perform full-bank passes
and are charged separately.

A deliberately loose explicit bound for the storage loops (excluding encoded
arithmetic in `T_descriptor` and finite-control instructions) is

```
4096 * (B + P*F*(bE+1) + 240*V + D_dirty + bP + 1),
```

where D_dirty is the total discarded service-body length at entry. The bound
allows both private closure phases, all output checks and all source rewind,
clear, gather, scatter, commit and release loops. To verify the bound, a Counter
initialized from a b-bit nonnegative canonical Count and decremented n times
has at most `64*(n+b+1)` physical actions: initialization/closure is linear in
b and the sum of trailing-zero ripple lengths over a full countdown is below n.
Each bit scan/copy adds a fixed number of reads/writes/moves. There are at most
2PF per-prefix field counters in scatter and PF in gather, plus the fixed
output/private checks; rewind/clear passes are linear in their actual bodies.
The factor4096 dominates these explicit multiples. Descriptor arithmetic is
outside this estimate and must retain its separately executed Count bill.

Additional simultaneously retained payload volume is at most `B+464V+D_dirty` during
publication (acquisition bank output B, 224 old/new acquisition fields, 224
recovery outputs, 16 private fields, and retained backing from any initially longer discarded dirt), plus encoded descriptors and the numerical
engines/bridge's separately charged high-water backing. Some lifetimes overlap
less; this upper bound deliberately does not claim that erasure releases Python
allocation. Across sequential invocations fixed physical roles retain their
maximum backing. Parent ancestry and the inherited native recursive workspace
are additional and already belong to their own source contracts.

## Optional completed whole-bank adoption

`commit(..., adopt=True)` replaces only the final `BankPackets.commit` interval,
after the same output transfers and actual complete scatter. The parent
`roles['current']` is an internal role; its public `Machine.output` and the
borrowed root input remain on their original physical tapes. A caller insisting
on an immutable internal current-bank physical tape uses the default copy path.

At this completed fence, the exact source's relevant current aliases are:

- `parent.roles['current']`;
- its single position in `parent.parked`;
- the same logical position in `parent.parking.roles`;
- `acquisition.source`, whose last read ended during scatter.

The parent's own BankPackets is closed with `source=None`. Group is None and no
primitive is active. Capsules, public output, numerical descriptors, native and
wrapper inventories are separate. The returned bank is the complete binary bank
created by actual scatter; exact length is inherited from that completed source
scatter and the prior output preflight, not established by a binary scan alone; the optional code additionally scans its complete
binary body and preserves the removed copy loop's alphabet rejection. It checks
both origins by actual head-relative marker reads. Registered external-role
inventories may name neither exchanged tape; this explicit precondition prevents
a stale cached external alias from silently surviving the exchange. Raw current
aliases must not escape the fixed compiled service boundary.

The finite-control transaction swaps the old current physical tape with
`acquisition.output`, updates `roles['current']`, `parked`, and `parking.roles`
together, and ends `acquisition.source`. It then physically clears the old bank,
now the acquisition output, erases its owned marker and performs the same source
acquisition release. Every other physical role and its body/head is unchanged.
The fixed role universe has not grown. Finite control can represent this as one
permutation of the fixed physical roles; pointer assignments are a host
representation of that finite selector, not data-dependent RAM addressing.

`current_bindings` checks the entire original constructor correspondence
`parked == (*roles.values(), *bank.packets, *private)` and the identical Parking
role tuple before and after the transaction. Omitting either parked or parking
updates rejects. The default publication and adopted publication leave the same
logical bank and subsequent source continuation. All next source operations use
these updated tables. A second invocation on the same closed Machine is allowed
after its public output is consumed; acquisition's next `arm_empty` rearms the
old current tape as its now-empty output.

An ancestor frame contains only four-bit encodings of role bodies and fixed
role delimiters, not physical aliases. Its logical role order and length do not
change under the transaction. Consequently, after child roles close, actual
`Parking.restore` restores each ancestor word into the current binding of that
logical position. The #3464 induction therefore extends under this finite
permutation: decoded ancestor values and all next-continuation selections are
unchanged. This is a new role-binding adaptation of its unchanged codec, not a
claim that #3464 already proved the opt-in modification. Synthetic nonempty
frames are exercised through actual source Parking, explicitly as codec oracles.

Let B>0 be the complete old/new current-bank bit length. Between completed
scatter and the common `release` interval, literal source counting gives:

| Tape actions | Default fixed-copy commit | Optional adopted commit | Saved |
|---|---:|---:|---:|
| Reads | 9B+13 | 4B+11 | 5B+2 |
| Writes | 3B+1 | B+1 | 2B |
| Unit moves | 8B+16 | 4B+14 | 4B+2 |
| Total | 20B+30 | 9B+26 | **11B+4** |

The adopted column includes the origin tests, complete binary scan and paid old
bank erasure. The same release of all acquired fields cancels constructively.
Everything before completed scatter is identical. Thus in this tape-I/O model

```
T_install_adopt = T_install_copy - (11B+4).
```

A model charging finite control additionally retains its explicit fixed-role
selector cost `c_R` (and accounts for any common control cancellation). No
unqualified wall-time saving is inferred. Across reached installations, subtract
`sum(11B_u+4)` once per completed installation and charge the corresponding
finite-control terms; do not subtract it again from native descendants. This
reduces an actual expense of the new connection, not the original source's
arithmetic toll, and by itself establishes no affordable supplier or new kappa.
The 545-role inventory and payload/high-water bound remain unchanged; per-role
backing may move between the two owners but no backing is claimed released.

## Reuse and evidence

| Contribution | Classification | What is reused and what is not |
|---|---|---|
| Sagar Thakrar #3464, head56b856a8c6dbd44c4a15bde694c08bbaff6f3e2f | Reuse unchanged | Four principal controller files are byte-identical; successful arbitrary-depth parent return applies under original callee and closure premises. No new whole-service cost follows from frame length. |
| Tekalign #3380, head072fd13a64095122bdad44009ab216aa4e1c1c1c | Adapt with new proof and cost | Reuse its finite internal-role permutation idea at the completed full-bank boundary, with the actual complex Machine's three current-role bindings updated. Baseline fixed-copy commit remains available; the new saving is 11B+4, not 22V+13. |
| Victor Li #3993, heade4fa89214086fb096c4276bbea891a1e6fae6c7b | Regression evidence only | Its stale-lease and CALL empty-pool examples motivate phase/closed-pool tests. It is a BIT Machine contract, not an imported invariant about the complex service. |
| Jose Manuel #3055 / actual source cohort | Reuse unchanged where inherited | Compact/native dirty-restoration support remains in #4129's actual source closure. Service storage does not reprove or replace its ordinary/native admission premises. |

`lifecycle.fixture()` executes the actual retained Machine, BankPackets,
Tape/Count operations, original child entry/return and two actual bridge scalar
legs per cover. It uses two-dimensional reduced geometry with 224 whole cover
families, two covers, two outer prefixes and 3,584 owner/address-dependent complex
values. All224 outputs and all16 private roles are exercised. The service
transformation is identity and is labelled **storage-only**; it is not an
endpoint double being called actual QQ16 arithmetic. Original and installed
complete runs have the same endpoint. It checks all other parent role bodies and
heads including the empty root ancestor stack, the baseline immutable current identity, borrowed
root/descriptor preservation and eventual cleanup. Controls reject early commit,
parent/output alias, unrestored private dirt, unclosed native output, a short
224th output before destructive publication, retired selector access and double
commit. The optional `fixture(adopt=True)` executes two complete root invocations
on the same actual Machine, with 20 original child entries and 20 returns; the
second root exercises original recursive returns after the first role exchange.
Both roots produce the same reference endpoint and preserve public output/input
contracts. `adoption_fixture()` separately meters both commit paths at bank
lengths 2, 6, 18, 66; exercises four nonempty frames through actual Parking and
restoration into rebound logical roles; and rejects omitted parked/parking
updates, a cached external current alias, and an invalid returned binary symbol.
These nonempty frames are explicit codec fixtures, not a claimed selected native
execution. The all-depth adaptation is the logical-role-order argument above.
The full lifecycle fixture's metered subtotal includes its deliberately executed
rejection controls and is labelled accordingly, not used as the production bill.

Open next question: compose this storage mechanism with the independently
source-bound D/current-value reconstruction and actual numerical/native route
at the selected global fence. The storage witness alone is not significance B;
publication requires the integrated mechanism and its same-boundary invoice.
