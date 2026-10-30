"""tk anatomy WORD [--no-lifetimes] [--no-cache] [--json]

Per-side ledger of ANY word (bulk evaluation of new words): invoice law R0 by class, skeleton/mains, lifetimes by mechanism (markets / twins at hubs /
other ends / signal and other births, with enabling-stop cost), hub ledger per octet frame (HUBCOST), signal, copies.  Read-only.  Engine:
alignbuild/anatomy_core.py (ledger = ALIGNLAW life/attrib + ENDANATOMY exact replay + HUBCOST + gapmap.components).  The exact end replay costs minutes
on a new word and is cached by content sha (alignbuild/out/cache; #6030's is shipped in alignbuild/data); --no-lifetimes skips sections 3 (seconds).
Labels EXACT / MODEL per section in the output and in alignbuild/anatomy_core.py.  Frame classes are tiling-relative (octet class around #6030)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)


def add_parsers(sp):
    p = sp.add_parser('anatomy', help='per-side ledger of a word: R0 classes, skeleton/mains, lifetimes by mechanism, hubs, signal, copies (alignbuild/anatomy_core.py)')
    p.add_argument('word', help='path or name in words/ (e.g. 6030)')
    p.add_argument('--no-lifetimes', action='store_true', help='skip the exact end replay + attribution (section 3; minutes on a new word)')
    p.add_argument('--no-cache', action='store_true'); p.add_argument('--json', action='store_true')


def main(a):
    from alignbuild import anatomy_core as C
    r = C.anatomy(a.word, with_lifetimes=not a.no_lifetimes, use_cache=not a.no_cache)
    print(json.dumps(r, indent=1, default=str) if a.json else C.fmt(r))
    return 0
