# Slot-free `(w, q, v_N)` consumer misses the dimension screen

**Scoped screen. No new κ.** The selected conditional exponent stays
`605457647/200000000000`. Leaving the PR3882 encoding in place does not
give the retained caller `(x, w)` or `(-y, w)`, and it does not improve
the paired-chain zero-saving moment.

## Result

The encoding tail already puts every corrected sum `w` on a hyperplane
bank and puts `(q, v_N)` on the FULL banks. Its 104 lifts and 104 drops
are 208 rank-one conversions. The 208 data registers still consist of
104 dimension-9 banks and 104 dimension-8 banks, the same multiset as
the channel exit. A coverage law that scores only those dimensions
credits the tail no new endpoint progress.

The FULL banks are not a renaming of `x` and not a renaming of `-y`.
Every row and every column of `B` is nonzero, and `B B^t = 12 I_8`, so
each coordinate of `q` mixes at least two source ports and each
coordinate of `v_N` has `y`-coefficient `+1`. The hyperplane banks are
exactly `w`.

Under the paired-chain constants (idle `39096`, capacity `60736`,
channel mass `2368`), crediting `c` rank units of payload progress per
call gives

```text
M(0) = (62280 - 9 c) / 60736.
```

`M(0) = 7785/7592 > 1` at `c = 0`. The comparison passes only for
`c > 1544/9`. Integer credit needs `c >= 172`; `c <= 171` fails.
Omitting the later fixed-location restoration does not lower the 208,
because those conversions are the tail itself. This is a necessary
credit, not a supplier.

## Task and overlap

Base `32890bc5de034ab8fc93ac88ead7279a6a416d04`. Card
`p104-side-correction`, priority revision 7, scope **refined**.

This is item 1 of the eligible list below. It answers open question 1
of `research/p104-role-exchange-caller-audit`: whether a caller can
accept `(w, q, v_N)` without restoring the original source slots and
pass a replacement coverage law. The fixed-location 192-rank adapter
and the fused source-preserving word stay on that package. They are
not rerun.

Ordered eligible list for session r33, rebuilt on 2026-10-25 against
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. Open handoffs from the
19 October index (discussion comment 19029944) come first. A closed
smallest task is dropped, and a still-open remainder is kept when it
is distinct. Priority-table rows whose stated next decision is still
open come next. Catalogue cards that are not already those rows were
not reached. Dropped before the cut: work this account already
delivered, results on current main, questions covered by an open pull
request, and topics already on a fork `cursor/*` branch.

1. **This package.** Slot-free consumer of `(w, q, v_N)` (comment
   19030045).
2. Bind one actual complete-stream COPY child. The fresh T385 wrapper
   replay is closed on main in `research/t385-r437-copy-audit`.
3. Place L561 onto the four scratch windows before the L546
   subtraction. The closed head-move bill is on main in
   `research/qq16-l546-head-move`.
4. Decide whether the PR2809 continuation serializer parks the ancestor
   chain. The `O_q(V)` reading is on main in
   `research/pr2809-continuation-stack-space`.
5. Trace one blank-return cursor of the 9475-row R437 parent. The
   payload comparison is on main in
   `research/r437-parent-spectator-blank`.

Excluded before this cut: the retiming handoff (comment 19030053),
already covered by #4122, #4128 and open #4567; the four-provider
rebind, on main in `research/mixed-provider-admission`; the matched
QQ16 park/restore bill, covered by open #4167 and #4172; the #4091
1090-call transfer, on main in
`research/fourth-entry-ceiling-transfer`; the rank-8/u2 entrance
obstruction, on main in `research/rank8-u2-entrance-obstruction`; and
the slot, chart, encoding, fiber, port-chart, encoded-exit and
`(N-P)⊗M` notes already delivered by this account.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/p104-slotfree-coverage/verify.py
python3 -B scripts/research_package.py --package research/p104-slotfree-coverage
```

`verify.py` prints

```text
PASS_P104_SLOTFREE_COVERAGE full=104 hyperplane=104 conversions=208 M0=7785/7592 credit>1544/9 integer_credit>=172 no_new_kappa=true
```

The checker hashes `research/p104-role-exchange-residue/geometry.json`,
rebuilds the 104 ports, replays the tail on the 208 linear forms, and
evaluates the screen. Not run: Lean, Docker, the selected cold replay,
native signed-floor execution, and any search for a payload-sensitive
law that awards the credit.

## Open next questions

1. Does a payload-sensitive coverage law award more than `1544/9` rank
   units per call to this encoding? The dimension multiset does not.
   First name one idle endpoint that `q` or `v_N` retires, and show the
   rank units that endpoint was going to pay. Nothing here exhibits
   such an endpoint.
2. What is the sharp FULL-operand lift count of a schedule that emits
   `(-y, w)` while returning every hyperplane sum to its chart, if the
   final bank names may differ from the original slots? The 192-rank
   tariff assumes those original names. First read every nonzero column
   of `B` into a FULL equation and restore that sum. This package does
   not search schedules.

## Credit

The encoding, the inverse formulas and the eight-replacement theorem
are Clear1nsight's `research/p104-role-exchange-residue`. The open
consumer question and the fixed-location 192-rank adapter are that
account's `research/p104-role-exchange-caller-audit`. The paired-chain
constants and the `k <= 328/9` line are the map in
`docs/research/p104-side-correction-scope-map.md`, from the PR2082 /
PR2083 contract. The two-stage scalar target is
`notes/copied-centers-complex.tex`. The channel and the puncture are
Rohan Arun's and Chafik Boukhalfa's.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0. No independent human review and no formal-kernel
acceptance are claimed.
