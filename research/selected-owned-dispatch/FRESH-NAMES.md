# Capture-avoiding owned banks for the finite compiler

This is an independent written argument, not a formal-kernel proof or a claim that the other four assumptions have been discharged. It distinguishes (A) a finite syntactic allocation theorem from (B) its physical recursive implementation. The compiler's ownership wording is **not** a premise of (A). The physical conclusions in (B) need the explicit tape construction and volume bounds stated below; they do not follow merely from endpoint algebra.

The source cohort for the compiler and existing parking work is main commit `de5ec2e7a6074068452f45b1a191b5c72832df4a`. The new raw P104 word is PR5811's `research/p104-accumulated-block-composition` at commit `883ab9ca680906a0df88fb74ff51d634868af363`. This is a proof binding for that new raw word, not an assertion that the repository's selected PR5599 record already contains it.

## 1. Raw syntax and the exact obligation

A raw unit has disjoint finite sets of formal public fields `P` and owned labels `O`, a finite event word, and an ordered paid-call list. Its typing judgment maintains a live subset `L` of `O`:

* A read or write of a field requires membership in `P union L`.
* `INIT(o)` requires `o in O minus L` and adds it to `L`, writing its specified zero representation.
* `CLEAR(o)` requires `o in L` and removes it from `L`, erasing its owned extent. Neither instruction is permitted on a formal public field.
* `COPY(dst,src)` additionally requires `dst in L` with its prescribed empty/zero state and a distinct initialized source. An arbitrary public input is never silently reclassified as a zero.
* A paid call is on exactly one initialized field of that unit. Its complete descendant computation and boundary adapters return before the next event in the issuing word.
* The word ends with `L` empty. Reusing one owned label for a later lifetime is permitted only after its earlier `CLEAR`.

This is a syntactic condition, not a semantic restoration hypothesis about unknown storage. PR5811's `local.py:replay` checks the actual `INIT`, `CLEAR`, `COPY`, scalar-use, MOVE ownership and final-live-set conditions. Its 29 labels have 31 explicit lifetimes, peak 13. A nonpublic operand before INIT or after CLEAR has `current=None` and fails the required scalar/MOVE frame test. The complete scalar and native semantic identities are separate retained obligations.

The caller must supply an injective map from public formal labels to actual field identities. Values in those distinct fields need not be statistically independent. In particular a child public field may be a parent's privately allocated field, containing an arbitrary correlated linear combination. It remains the **same field**, receives no fresh productive-input credit, and is not erasable by the child's local INIT/CLEAR instructions.

For the whole raw PR5811 P104 caller, the source binding reported by the root checker is:

* `32*104 = 3328` main public roles;
* 18 local occurrences, each with 562 distinct public helpers: `3328+18*562 = 13444` productive roles;
* distinct `(local-occurrence, owned-label)` names for `18*29 = 522` local banks;
* 104 copied-query banks, reused only across the 15 synchronous QUERY_SHEAR events after the preceding event has returned and erased them;
* consequently a safe raw inventory of 626 owned banks and 14070 logical fields, excluding separately counted control/work ports.

The proof below is parametric in the exact typed raw caller. Those arithmetic counts are a binding target, not a replacement for checking its 18 invocations, all 31 local lifetimes, and its query schedule. The raw number 626 is **not** the final compiler's owned count. Expansion creates multiple raw occurrences, each requiring its own tags; complement and exit expansions add occurrences as well.

## 2. Fresh-name theorem

**Theorem.** Let a finite raw syntax satisfy Section 1. Apply any finite sequence of the chronological product, same-owner completion, same-owner splitting, integer lockstep matching, integral replication, source complementation and smaller-rank exit substitution described in the pinned sources. There is a computable capture-avoiding assignment of field identities to the resulting finite program with the following properties:

1. Formal public arguments of every simultaneously active class/batch are pairwise distinct.
2. Every owned bank belongs to one uniquely tagged raw occurrence; no other occurrence initializes or erases it.
3. A descendant may borrow an ancestor's field only through an explicit paid-job edge, with the exact field and whole-job rank carried by that edge. On that field, active ownership permissions form a chain, not a fork.
4. A parent resumes, reads or erases its owned field only after its descendant chain and adapters have returned. Its other fields are not implicitly passed to the descendant.
5. Every whole top-level productive field is consumed once by its source assignment, complemented on the specified disjoint coordinates, and restored to its original outer ordering. Internal banks never become new productive-input credits.

**Construction.** Give every statically expanded raw occurrence a distinct path tag `u`. Include the product-copy index, chronological paid-position index, integral replica, class path, unit index, and every complement/exit invocation in this tag. Assign its owned labels the names `(OWN,u,o)`. Top-level public field names have a disjoint tag `(INPUT,i)`. If the same raw label has several sequential lifetimes, it may retain `(OWN,u,o)` because its raw typing proof already forces the prior CLEAR; allocating a different name per lifetime is a safe, more wasteful alternative.

Public argument maps are the actual source/incoming field identities dictated by the schedule. Do **not** demand that all public arguments globally avoid all owned names: a legitimate paid job may pass `(OWN,parent,o)` as a child public argument. The requirement is freshness of the child's **own** bank names from its arguments and from every other occurrence's bank names.

This construction is effective from the finite compiler recipe even when writing out the resulting word is impractical. It uses ordinary finite integer/string operations at precompilation time. No dynamic constant-time lookup of huge names is being asserted.

### Proof for a lockstep class

Induct on its ordered execution events, and on the smaller top rank for inserted complement/exit programs. At entry, the current program's actual arguments are injective. The class has two kinds of input slots:

* Each incoming parent job appears once in the Pascal bijection. Before issuing the round, the parent class owns disjoint fields. Each parent unit issues only one job, so all incoming job fields are distinct. Equal ranks are checked before binding, and the whole-job adapters surround the entire child.
* Every missing input consumes a distinct, not-previously-consumed source slot of the enclosing program. Its occurrence is recorded once by the source enumeration. It cannot collide with an incoming field: an enclosing-program slot currently used as a parent role is already consumed, while a missing source is unconsumed. Nor can it collide with a fresh internal bank, whose name begins with OWN.

Thus public arguments in the new class are injective. Adding `(OWN,u,o)` for each of its units preserves disjointness. On a parent-issued field, push the child's borrow permission over the exact suspended issuer; on a missing source field push it over the enclosing program. The child cannot erase either because both are formal public arguments in its own word. It can initialize/erase only its fresh names. After the entire child class and its adapters have returned, pop those permissions. The parent becomes current owner again before its next event. This is the induction step for each paid round. At class end all local bank lifetimes have ended by the raw typing condition, and all borrowed-role permissions are popped.

The claim is not that the ancestor and descendant represent different physical values; they intentionally refer to one field during a whole-job substitution. It is that no **incomparable live roles** alias and no descendant owns an erase right over its caller's field. The distinction is necessary: requiring all live role names globally distinct would incorrectly reject every legitimate nested call.

### Closure of every compiler constructor

**Chronological product.** In `U x V`, start a separate U occurrence for each productive role of V. Their initial productive fields `(i,j)` and all private tags are distinct. At U's paid position `ell`, V receives exactly one currently owned field from each U copy; these fields are distinct. V's private tag includes `ell`, so it cannot collide with a previous or later V instance or with any suspended U bank. Complete V and undo its adapters before any U copy advances. Never batch two paid positions of one suspended U as if they were distinct owners. This is exactly `p7-TENSOR.md` Section 1.

**Splitting.** Replace rank R by consecutive disjoint-axis jobs on the **same owner**. The first child returns before the next piece begins. The original whole-job normalizers enclose the replacement. This adds no bank, no source argument and no concurrent alias. A zero-rank remainder emits no call. See `p7-TENSOR.md` Section 3 and completion-pass Lemma A.

**Completion.** After the entire original/product word, issue the complementary coordinates on the original productive owner. All its earlier descendants have returned. It is the same arbitrary field, not a new blank/helper. Whole-job normalizers and the complementary axes must still be semantically valid under the native/spectator assumptions. Name freshness itself does not depend on that algebra. See `p7-TENSOR.md` Section 2.

**Integral replication.** Tag each flow copy by its replica index, supply disjoint slices of the a*S top arguments, and tag every replicated raw bank separately. Exit batches combine distinct issued fields; replication does not identify their storage.

**Source complements / gaps N-s.** First partition the original program arguments by source rank, then into batches of the exact smaller-program width. This partition has no repeated field. Run each N-s program before that field enters the flow, using freshly tagged internal banks. It receives the same original field, not a new output. Its return restores the enclosing program's permission and whole-field layout. Zero gaps are omitted. The other possible 'gap', runtime remainder axes e=Nf+r, is a sequential same-field tensor operation; it allocates no new productive owner.

**Exit substitution.** At a deepest class, take the issued fields in their fixed order, partition into integral B_e batches, and invoke the smaller compiled program on each distinct batch with fresh occurrence tags. Every such program returns and has its role ordering/adapters undone before the issuer resumes. Strong induction on e<N proves the same fresh-name statement for its complement and exit descendants. This is `FINITE-PRECOMPILATION.md` Sections 3–4, not an appeal to its physical-closure hypothesis.

These are all constructors used by the described finite compiler. The proof therefore extends the raw typing property to its complete finite result. A safe compiled owned inventory is the sum of raw-bank counts over **all** expanded occurrences, with their full work-port inventory. Its size may be enormous but is a fixed integer after choosing the compiler N and before the eventual multiplication input width. Reuse is optional; it is not needed for existence.

## 3. What prior work already established

`lockstep-live-role-audit/README.md` gives the same core live-role induction as I1–I6; `live_roles.py` executes it, but only selected small/adversarial rules or partial/interface checks for enormous instances. The exact code points are `Compiler.uniform` (distinct fields, source complements, once-only source use), `Compiler.run_class` (matching, one owner per round, unique own tags, child completion), and `Compiler.sub/blackbox` (smaller-program interface).

`lockstep-completion-pass/PROOF.md` Lemma B already establishes a global logical LIFO allocation theorem, including nested smaller programs and the compatible path/exit peak recurrence. It is incorrect to claim a new theorem merely because its examples are finite. Its proof does, however, call a bank's empty live-role stack an erasure contract: that logical fact alone does not blank physical record cells. Our fresh-name argument uses the raw event typing, and the physical construction must implement those erasures separately.

No new rank/moment saving follows from this allocation argument. No all-column chart identity, rounding bound, or integer recovery theorem is proved here.

## 4. Runtime segmented recursion: a sufficient noncircular implementation

Static fresh names do not mean allocating a new physical tape for every runtime depth. Let F be the now-fixed finite uniform supplier, with W=B_N productive slots and K total data/work/descriptor roles. Its fixed instruction positions and bank-role identities can be compiled into finite control. For each runtime node retain K disjoint **logical segments**, implemented on a fixed finite set of physical tapes. A segment is a local delimiter, a finite coded body, and an end marker. The child has a new segment on each tape; the parent's body remains to its left.

The required implementation has four parts, each with a separate obligation:

1. **Sandbox every primitive port.** Given an actual finite ordinary tape machine for a retained primitive, translate its finite alphabet to fixed-length nonblank codes inside a local segment. Coded virtual blanks are distinguishable from unused physical cells. Extend the coded body locally when the simulated head visits a new virtual blank, and never cross the local origin. If the source tape is two-sided, a folded two-track representation gives a one-sided local simulation with constant slowdown. Translate work/counter/descriptor ports as well as data ports. This supplies trace confinement from machine syntax; mere endpoint preservation would not supply it.
2. **Explicit transfer, not ancestor alias access.** Before a recursive call, copy/move the exact selected complete field into a dedicated bridge, park the parent, install the child input in its own local segments, and erase the bridge. On return, place **all** child output fields in an output bridge, pop/clear the child segments, install those bytes in their exact parent owners, and erase the bridge. Return the completed computed fields, including numerical residuals; never overwrite them with an ideal value used in a proof oracle. The child cannot directly read an ancestor body. Parent public or private status changes no step of this mechanism.
3. **Physical continuation.** Store the finite return-PC, which owner/port is to receive each output, and runtime width/row descriptors in a delimited continuation. Fixed PC/owner identities have constant-size encodings after F is fixed. Width division by the fixed N, remainder handling and stopping tests must be finite scans/counters with their cost included; no uncharged Python object or host call stack is permitted. The existing delimited/segment continuation proofs give the local push/pop operations once these descriptors are supplied; they do not supply this dispatcher by themselves.
4. **Complete-volume price and reserve.** Let V_u include the actual complete row, compact and spectator records at node u with the fixed global record precision. Charge all primitive work, bank initialization/clear scans, bridges, descriptors and continuation at that node. It suffices to prove local administrative time and occupied/visited segment length at most C_F*V_u (or its already allowed polylog-p factor), with C_F depending on the fixed expanded template. For complete-row recursion the retained row reservation gives V_child=V_parent/W with W>=2. Then the active-chain volume is at most V_root/(1-1/W); fixed-role parking/bridges/metadata have O(C_F V_root) live/high-water extent. Time is C_F*sum_u V_u, and is included in the existing nonchild weighted-tree allowance. The width here is the final B_N, not the raw 13444.

The physical query primitive already scans, copies, adds and blanks complete N=2Mp-bit fields with a fixed instruction set. Its proved local cost is at most 256N+256 plus the completed child's separate cost; all eight ports must be fresh/distinct inside its current node. They may be the segment roles just constructed. Its private Z may be nonzero across the child interval. A child is not permitted to share Z's parent segment; it gets a transferred input and its own translated ports. Its local signed-range/no-overflow requirement remains a precision premise.

Under the four explicit implementation parts above, induction over the well-founded runtime call tree supplies owned allocation, parent preservation and physical erasure. No semantic assumption that an unmodified child 'never looks at ancestor storage' is needed: confinement is enforced by the translation. The induction is over a finite computation for each input; the machine itself uses only its physical continuation tape.

**Important cost caveat.** A geometric bound for live cell contents is not alone a bound for a simulator retaining every historical Python allocation. The implementation must reuse the same physical segment extents after pop. Cleared tape cells are counted in high-water space even though blank; their locations are recycled, not accumulated as new logical tape objects. Similarly, a whole-root scan at every depth is not covered by the local-volume argument.

## 5. Precise dependency split and failure modes

Do not invoke `FINITE-PRECOMPILATION.md` Section 1 item 4 in its full wording to justify owned storage: it already assumes that constantly many owned fields may be supplied with full cost and that ordinary recursion has the old restoration interface. That would be circular. Sections 3–4 supply a finite combinatorial program, ranks and batch identities. Section 2 here supplies its capture-avoiding typing. Section 4 must supply actual allocation/parking/erasure and its charge.

Likewise, keep the remaining `precision_tape` premise explicit: numerical range/precision and the existence and local cost of the actual retained primitive tape machines can remain conditional. It must **not** be used to assume the very global owned-bank reserve or ancestor-preservation ABI being proved. `native_all_columns` may provide exact operator/whole-job identities and arbitrary complete spectator semantics, but is not a substitute for an actual finite-control machine to sandbox. Analytic recovery and the compiler's rank/moment existence remain separate.

Concrete rejected errors are: (a) one bank per depth when two class units are live, (b) two child arguments referring to the same parent field, (c) a child INIT/CLEAR targeting a public formal argument that happens to be its parent's private field, (d) a missing-source slot reused after it was already consumed by an ancestor class, (e) parent advance/erase before child return, (f) physical child scanning the parked prefix and restoring it only at the endpoint, and (g) popping before child outputs are saved. Endpoint identities do not exclude (f); the existing `recursive-parking-boundary` example makes its cost depend on the ancestor length.

The small companion `fresh_names_controls.py` is a finite regression fixture for (a)–(d) and legal ancestor-owned borrowing. It is not an all-size proof, not the P104 raw-word checker, and not a replacement for the runtime construction.

## 6. Pinned primary sources

All paths in the first list are pinned to [main de5ec2e7](https://github.com/CrocSwap/integer-mult-bounds/tree/de5ec2e7a6074068452f45b1a191b5c72832df4a).

* `research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md`, Sections 1, 3, 4 and 6: hypotheses versus actual finite schedule, bank tags, correlated parent centers.
* `research/kappa-rebuild/transfer-audit/AUDIT.md`, Sections 3–5: independent source/owner matching and limits of physical closure.
* `research/higher-moment-strictification/vendor/p7-TENSOR.md`, Sections 1–3 and 6: product, completion, splitting and expanded owned inventory.
* `research/lockstep-live-role-audit/README.md`, Section 1; `live_roles.py`, `Compiler.uniform`, `run_class`, `sub`, `blackbox`: I1–I6 and concrete source matching.
* `research/lockstep-completion-pass/PROOF.md`, Lemmas A and B: constructor preservation and already-proved logical nested-bank allocation.
* `research/selected-owned-query-private-stream/PROOF.md`, Actual record and source contract; Addition and erasure; Explicit physical cost and backing; Open next questions: local eight-port lifecycle and exact limits.
* `research/segment-continuation-stack/PROOF.md`, Contract and finite control; Cleanup and pop invariant; Complete action invoice; Source binding and limits: no free dispatcher or output installation.
* `research/recursive-parking-boundary/README.md`, recursive boundary contract and locality counterexample: endpoint preservation is weaker than cost confinement.
* `notes/batched-complex-rows.tex`, Complete rows and compact fields; Integer axis counts; Stopping and weighted-tree bounds: exact complete-field volume contraction and nonchild allowance.
* `research/final4610-independent-admission/SPECIALIZATION.md`, Sections 4–6: expanded inventory/count constants, which must be replaced by the actual fixed compiled word.

The new word's primary source is [PR5811 commit 883ab9ca](https://github.com/CrocSwap/integer-mult-bounds/tree/883ab9ca680906a0df88fb74ff51d634868af363/research/p104-accumulated-block-composition): `local.py:replay` and `PROOF.md` Sections 3–6. Its canonical WORD hash is `a06445539ad73fe16deae66fef8c52ffc39f5f14c765eab3dc3d98e0e2d8074c`; the source typing and the full actual caller binding should be retained as separate machine-readable evidence.

Credit: the lockstep combinatorial flow is Jacob Alan Sussman's Theorem 1G; the repository finite compiler/product/strictification proofs are zxv and their cited authors; Mark/Matarener supplied the live-role and completion-stack audits; the physical copied-query and continuation packages retain their original authors and notices. The present argument is a source-bound synthesis and independent circularity review, not a claim to originate these earlier theorems.

## 7. Follow-up: the retained BIT caller also needs a binding

The selected ordinary BIT saving 17/5000 comes through `research/query-thinned-controllers/PROOF.md`, Sections 1–4 (PR4440), and is retained by the PR4470 and PR5599 reviews. It is not the newer unselected g20 BIT research. The fixed finite compiler and fresh-name proof apply to BIT too, but a check of the complex caller alone cannot establish its input syntax.

`check_bit_ownership.py` now supplies an independent finite typed census of that precise BIT source. It reads four pinned Git blobs from de5ec2e7: the PR589 WORD, its 249-records.bin and frames.json, and the query-thinned BIT-CONTROLLER.json. `BIT-OWNERSHIP.json` binds their byte and Git-blob hashes. No source producer or verifier is imported. Both orientations of all 27234 records pass their current-frame, private-lifetime and operand checks; each contains nine private COPY/ERASE episodes. The outer controller has 18 full invocations, 15 thin query contexts and 11454 public fields, and the literal recount recovers all 57555 paid jobs.

A safe chosen raw bank allocation is 18 separate local centers plus 111 per-port thin-query banks, or 129 owned banks, with 18*9+15*111=1827 lifetime episodes. The source invoice says one query stream reused sequentially; using 111 here is a deliberate larger safe allocation. It preserves the mathematical word but requires substituting the larger finite storage constant. It is not a proof that the source's old stock already reserved 129 banks. The borrowed COPY-target mutation rejects.

The delayed GL cover adds fixed bijective right routes on each complete field, not new productive arrays or destructive operations. Its capture-free application follows `DELAYED-COVER-BRIDGE.md`, Sections 2–4: each current raw field keeps its identity across a route, matched child fields are arbitrary actual fields, and inverse routes return before the parent resumes. Native/projector semantics, common external weight independence, local-ring fallback, cover stock and pricing remain the separate retained premises. Typed banks do not prove those premises.

## 8. Follow-up: a noncircular local-space source bridge

The runtime allocation theorem needs a linear **visited/high-water space** bound for isolated nonrecursive macros. A time bound O(V e^tau) alone would be insufficient. The relevant primary material, all at de5ec2e7, separates as follows.

1. `upstream/build/sections/02-streams.tex`, Lemmas `elementary-streams` and `ordered-affine-streams`, proves O(V) tape **time** for the elementary splitting/merging, fixed pointwise maps, digit moves, ordered rotations and fixed rational scalings, including shape arithmetic, counters, rewinds and erasure of visited work. Consequently their visited extent is O(V), directly from the step bound. The final paragraph gives linear-bit-time exact fixed-point addition, sign/power-of-two operations and record reversals, conditional on guard bits. These implications do not use recursive ownership.
2. `notes/compact-control-movement.tex`, controlled-rotation proof, explicitly uses two piece tapes, an output and fixed arithmetic tapes. The total pieces/output are O(V); the offset workspace is a fixed polynomial in A, absorbed by the complete superpolynomial record R. Its exceptional repair stores a subset of at most M complete records, keys of O(A) bits, marked holes in one full stream and a fixed number of stable-radix-sort tapes. Thus records/holes use O(V), keys use O(MA)=O(V), and fixed-polynomial-A work fits O(V) in the stated domain. Repeated radix passes reuse those tapes. This is a space derivation from the listed algorithm, not an inference from its full running time.
3. The compact selected-addition proof also invokes a **recursive arbitrary-width chunk-swap**. To make its O(V) workspace available without assuming ownership, first apply the allocator to the retained typed BIT supplier (Section 7) and its O(V) nonchild stream macros. Complete-row BIT children have volume V/W; see `notes/batched-bit-rows.tex`, finite integer depth bound and Fixed tapes and descriptors. All root main chunks remain spectators, so root descriptor bit lengths remain O(log(2V_child)) and polynomial descriptor preparation is O(V_child). The active-volume geometric series then supplies linear-space BIT. After that theorem, using BIT as a completed compact-movement subroutine supplies O(V) local workspace for the complex layer. This is a dependency order, not mutual induction on an unproved completed-owned ABI.
4. `upstream/build/sections/04-swap.tex`, A fixed-tape depth-first schedule, already describes parking other streams, copying active child input, pushing the finite PC/descriptor and restoring outputs without scanning ancestors. It is useful source evidence for the required ABI, but quoting its global ownership/cleanup assertion wholesale would skip the very construction under review. Use its local elementary macros and complete-row geometry; the new explicit segment/bridge lowering supplies the global physical invariant.

There is still a source-binding obligation for any retained BIT macro outside those elementary streams, including the old atom-interchange supplier used in delayed-cover routes. Its own fixed finite local circuit and stream recursion must have the same local-space argument or an independently proved local-space interface. The selected delayed-cover source prices those calls but does not make their whole physical implementation follow from the PR589 lifetime census. Likewise, outer analytic/resampling machinery is not covered merely because its final products consume the complex supplier. A claim about the repository's entire `owned_erasure` assumption must state exactly which of these retained subroutines are included and which obligations remain under another assumption; it must not conceal a global owned ABI inside `precision_tape`.
