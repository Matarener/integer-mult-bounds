# Shorter complete G20 scalar windows

This package constructs a new word from exact PR5708. It removes **245 ADDs
per local call**, from 11,824 to 11,579. The 18-call source can therefore
remove **4,410 ADDs**. The local positive majorant falls from 3,189,524 to
2,653,582. It still needs 22 bits. No new kappa is claimed.

The construction changes 191 windows in three rounds. All 685 arbitrary input
axes are retained, including 48 dirty owned axes. Every native or owned boundary
has the same complete scalar state as the source. Every frame, paid query,
helper target and owned clear is retained. The peak owned reserve is still 48.
The complete recursive invoice is unchanged.

## Construction and proof

Each candidate is a contiguous ADD-only window in one actual native frame.
It has at most four roles. The frozen PR5793 tool searches the complete binary
linear groups of sizes 6, 168 and 20,160. Its independently checked potentials
give a lower bound for each endpoint. The replacement attains that bound.
A separate literal truth table checks every input to each selected window.

Dynamic programming chooses a minimum-length cover by disjoint windows in each
pass. A strict length decrease makes the repeated pass terminate. A final pass
checks every eligible window and finds no strict reduction. This is a fixed
point in this grammar, not a global circuit optimum. Neutral or longer moves,
more than four roles and changed native frames are outside the search.

All roles in a window have the same invertible physical frame. Thus a scalar
matrix equality there is the same equality on the full payload functions.
Insert the equal matrices between the unchanged prefix and suffix. This proves
full context equality at every admitted width, subject to the source native
contract. It also preserves any source phase, because no native map changes.
The source native theorem is reused; it is not independently proved here.

The checker separately runs the full scalar word forward and backward. It
compares the complete state before every query, INIT and ERASE. A wrong ADD
direction, a missing ADD, a changed frame and missing owned erasures reject.
Frozen inputs are checked by SHA256. Regenerated compressed words are compared
by their decompressed bytes.

## Actual finite costs

The retained CALLS.json has 18 full local calls. The source primitive formula
charges each ADD once as a scan and once as an emitted record. Installing this
word therefore removes 8,820 primitive-count terms, from 952,838,314,401 to
952,838,305,581, with all other source allowances retained. This is a count in
the source cost schema, not a machine-time measurement. The coarse 2^64 ceiling
and the recursive exponent remain unchanged. No new owned field, scalar
coefficient, native query, route or target credit is introduced.

This package emits the local replacement and the exact edit list. It does not
re-emit the global source stream, its index/hash descriptors or its compiler
receipt. Those bookkeeping artifacts must be rebuilt before supplier admission.
The context proof gives the stated 18-call substitution and cost difference;
it does not claim that the old stream hashes describe the new word.

## Reproduction

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/g20-four-role-resynthesis
```

The direct `verify.py` command also works without Git. Use `--output NEW_DIR`
to generate the word, edit list and receipt in a new directory. Source origins
and byte hashes are in ORIGINS.json. The source and tool are self-contained;
no unmerged commit is required for replay.

## Open next questions

Can a changed native route turn these scalar identities into a complete signed
moment gain? Start from the emitted word and preserve every live external role.
An actual native path, full target ledger and fresh compiler bill are required.
The current result does not fund a larger mechanism search by itself.

## Credit and limits

Credit Dugongue, ai-nanachi and the complete PR5679/5708 source lineage. Credit
the PR5793 exact synthesis tool. See NOTICE and the retained source README.
New application: Ali Romman with substantial OpenAI Codex assistance, no
subagents. Apache-2.0. These are author checks. Independent acceptance, hosted
scientific replay, source framework assumptions and full supplier admission
remain separate. The selected frontier is unchanged.
