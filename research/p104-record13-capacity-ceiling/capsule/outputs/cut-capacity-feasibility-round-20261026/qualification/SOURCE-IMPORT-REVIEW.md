# Static selected import/call graph

All42 INPUTS SHA256 pins were checked during preparation, including the complete24-file export. Source files were read as text/AST only. No source module was imported, no compressed WORD was decoded and no scientific function or control was executed by the preparer.

The module named `local` is the pinned export's `inputs/pr5599-local.py`, registered explicitly before importing `pr5599-construct.py`. Its top-level imports are Python standard library: collections, fractions, functools, hashlib, pathlib, gzip, importlib.util, json and sys. Its top-level HERE/ROOT path declarations do not read a framework. Selected `replay` calls only its local `need`, `span`, `add` and standard-library arithmetic/containers. `native`, `reverse_columns`, `read` and `load` are not called. The native framework paths appear only inside the uncalled `native` function. L.ROOT is not reassigned or used by selected routines.

The pinned split module imports deepcopy, Fraction and `local`. Selected `split` calls `check_cut`, `basis`, `inverse`, `L.need`/`L.add`, and standard-library/container arithmetic. `check_cut` checks its literal cut rather than scanning a family. Exactly first12 `split` calls occur, followed by one final local replay and the record13 `check_cut`; the broad `construct` wrapper with repeated replays is not called.

The export's parent `construct.py` imports only deepcopy and Fraction. Only `construct_parent` is called; its broader `construct` is not called. The pinned `delayed.py` imports only deepcopy, hashlib.sha256 and json; only its `construct` is called, including its authenticated canonical parent/output hashes and fixed markers.

The released5615 `capacity.py` imports only Fraction. It is not loaded until stage/cut/owned/current-role/known-channel premises pass. Only `smith` and `capacity` are called; they call local `need`, `eye` and integer arithmetic. The checker implements full-width exact product and independent certificate checks. Its kernel certificate reduces to at most six independent original rows before invoking the released Smith algorithm; the source `kernel` function is not needed.

Runtime import roots are explicitly checked against each module's frozen standard-library/local whitelist before executing that module. Every source/import byte is authenticated first. The normal/-O children use isolated Python and a fresh temporary bytecode prefix to avoid unrelated import paths or stale caches. Byte authentication, rather than an AST whitelist alone, is the primary source trust boundary.

Uncalled files retained solely as provenance or complete-export authentication include source pricing, native/framework closure archives and later preparation modules. Pinning their bytes does not authorize invoking them. This review is static source inspection, not proof that the future run will fit60s or512MiB.
