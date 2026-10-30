# B08 source-to-replay integrity review

Status: PASS for the expanded33-file snapshot in the final integration section below, after two bounded fixes made by the root. This review concerns proof-source integrity and portable replay, not an independent proof of the cold-factor or pressure theorems. The original seven outputs and both added independent-review receipts are covered by this source audit.

## Frozen provenance and execution

All26 ORIGINS records were checked against their retained file length and SHA256, FROZEN-SHA256 entries, and the corresponding original local/archive file bytes. They match. The runtime closure is eight frozen Python files: seven declared stage mains plus cold_factor_search.py, imported only for qrank. All other imports are standard library. The auxiliary cold_factor_search main and the full compensation word interpreter are not executed. The compensation word bytes are authenticated as provenance; R and K are reconstructed from the transported D/A source.

All14 adaptations are source-path substitutions or replacement of a stored-receipt equality expression by Portable.equal. They do not alter a rank, field operation, inequality, loop domain, mathematical control, proof text or output field. The original --write branches remain frozen but are unreachable through the wrapper, which replaces sys.argv by the stage source path alone. Every expected receipt is present and authenticated before execution; nothing is silently regenerated in place.

For source modules under frozen/, SourceFileLoader.get_code is replaced with authentication of the exact bytes being compiled, followed by the enumerated unique substitutions and compile(..., dont_inherit=True, optimize=0). The nested cold_cosets/cold_factor_search imports take this path. Cached Python code is not consulted for those modules. The eight historical mathematical sources contain zero Assert AST nodes; they use explicit need checks, so those checks also survive optimized callers independently of the optimize=0 protection.

## Complete equality and defects corrected

Every field of each of the seven scientific JSON outputs is compared by canonical JSON after only relocation of three original absolute provenance prefixes. No timing, theorem, coverage, source hash or other receipt field is ignored. Canonical serialization distinguishes JSON true from integer1. Each stage must compare exactly its one declared receipt, and all frozen inputs are authenticated again afterward.

The initial comparator silently merged dictionary keys that became equal after path normalization. An independent concrete control changed an original sources hash and added its relocated alias carrying the expected hash; that corrupt receipt was initially accepted. The root fixed normalize(dict) to reject duplicate normalized keys, and added this exact collision control. This was a comparison-integrity defect, not a counterexample to the frozen mathematics.

The initial controls bootstrap imported verify.py through an ordinary source loader before protection was installed. The actual repository launcher already isolates caches, but a direct exported control invocation could have read stale verifier bytecode. The root changed this bootstrap to compile verifier source bytes directly with optimize=0. No frozen mathematical source changed for either fix.

## Launcher, controls and portability

The reviewer ran controls.py through the actual scripts/research_package.py run_python_replay function in normal and optimized modes, using Python3.12.14. Both passed. The retained evidence is LAUNCHER-CONTROLS.log, SHA256 b4f56a0e08e3dabd87bd7a7e360a98e2ea96f13f4a893f5fcc08cf824266de14.

The controls relocate the package to a temporary path containing spaces, reject changed frozen source and receipt bytes, reject omitted coverage and changed mathematical data, distinguish Boolean/integer substitution, and reject the newly discovered path collision. They construct a valid poisoned timestamp cache, first prove an ordinary Python loader accepts it, then prove the nested protected import executes the frozen source. Cache directories use parents=True, so this test works with the repository launcher's fresh -X pycache_prefix tree. Unexpected acceptance is raised outside the caught rejection path, and the intended rejection marker is checked.

The registered source closure needs no Git, network, original workstation tree, NumPy, or undeclared scientific module. Relocation covers ordinary imports and relative data dependencies. Original archive paths in ORIGINS are provenance only. This source review and the relocated controls are not a fresh full seven-stage standalone export replay; the root owns that broader validation.

The root's initial B08-REPLAY.log, SHA256 ea81de1bece6831e2598defa050fc4d017fff8ffdd4f895c0ca708b3a97b9be0, was inspected and contains all seven PASS_R429_READER_FLOORS stages plus PASS_REGISTERED_RESEARCH_PACKAGE. It predates the comparator correction. The root plans a fresh full registered replay after final source integration; this reviewer did not duplicate heavy stages.

## Initial seven-output inspected snapshot

- verify.py: 5ce6a07bdcb71af16699621e1b9f9dc571f284c044915bdf705a78388d702c8d
- ADAPTATIONS.json: 422b264da3cdd9e33665bad5c97509583fd5b029e9cc717b7e3173b345745672
- FROZEN-SHA256.json: b7a4950a44d53a01802324b662e5497605c9a51d98c6429acd85351cb713cab9
- ORIGINS.json: b7521036fd75f4c5112fc948b14a8d1b9006e734eeea53c66b16de4b525df976
- controls.py: 1f1b8d1a07b5bf8a0608cbee6dbe35e5b41a018a2bea88848bd7558df3408357
- VERIFY.json: 33777b969907650f62a54ea170437221da56ca6c4d4a33f06d8167a37bc05c80

Package-wide metadata must continue to bind the verifier/adaptation/provenance files themselves; the frozen-input map is not intended to authenticate its own verifier. No remaining source-binding defect was found in this snapshot. Final written mathematical claims, finite-census completeness, the all-factor implications and caller-credit assumptions remain the separately assigned mathematics reviews. This audit establishes neither a native reader implementation nor dirty restoration, a complete supplier, formal-kernel proof, or a new exponent.

## Final independent-review integration

The added cold and pressure checkers, their two receipts, and three canonical upstream comparison files expand the frozen set from26 to33. All33 ORIGINS entries were freshly checked against their frozen size/hash and original source bytes; the retained-name set equals FROZEN-SHA256 exactly. All11 registered Python files compile after their declared adapters. The prior p111-copy-rank-certificate verifier is hash-only; it is not executed. The executed mathematical closure is the original eight Python files plus the two independent checkers, all using only stdlib imports.

The nine added adaptation entries only relocate OLD/RAW/COMP and the three canonical comparison inputs, and replace each independent checker's final write_text by Portable.equal. No arithmetic or proof controls are changed. Both complete frozen independent receipts parse and positively compare, with no fields excluded. They enter the same collision-rejecting, scalar-type-preserving canonical comparison and authenticated optimize=0 source loader as the original scripts.

verify.INDEPENDENT appends the cold checker to eleven and the pressure checker to pressure. Each stage resets sys.argv for each module, runs both mains, and requires the exact two-receipt set. Omitting either independent equality call therefore fails final coverage. Other stages still require their original single receipt. All nine scientific outputs are thus required across the seven registered stage commands. The combined timeout allocation is1110 seconds; changes add validation rather than dropping any original domain. The final controls.py is byte-identical to the version that passed this reviewer's actual-launcher normal/optimized controls.

Final hashes:

- verify.py: e7403d75b4e860d45fff425693731841f16ffdaf70fd81afb8ce2f976a3489bf
- ADAPTATIONS.json: 2ef1696ea25a2e05eaf96fcbee4a9a583e87590006b7051c0df24308b554252b
- FROZEN-SHA256.json: 6d85242787a980fcb59053aa2e8e294027507a6a06cd125b278441e4de45801e
- ORIGINS.json: fa7de39aefba8b410cd6ef6af09456ea416856467f5b36adedfc0c4760475553
- controls.py: 1f1b8d1a07b5bf8a0608cbee6dbe35e5b41a018a2bea88848bd7558df3408357
- VERIFY.json: 6ba88eb180fd3f8404973f8fcada4d1c102af3f2f929634a228c852ccb1e7cc7

The root is running the final full registered suite after this integration. No heavy scientific stage was repeated by this reviewer. Full final replay/export/hosted success must be reported from the root's corresponding receipts, not inferred from this source audit. README mathematics and attribution are being finalized by the root and their specialist owners; this audit does not certify a changing prose snapshot.
