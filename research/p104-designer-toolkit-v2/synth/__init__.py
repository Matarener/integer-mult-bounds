"""tk synth -- from-scratch / from-spec word synthesis (SYNTH lane).  See ../module docstring.  spec.py gen.py repair.py sample.py."""
def add_parsers(sp):
    p=sp.add_parser('synth',help='word synthesis from parameter specs: --spec-from WORD | --gen SPEC | --roundtrip WORD | --random N --seed S (sampler around the anchor spec)')
    p.add_argument('--spec-from',help='write the spec of this word (alias/path) to --out')
    p.add_argument('--gen',help='spec file -> DAG -> word (+ repair) -> evaluate')
    p.add_argument('--roundtrip',help='alias/path: spec_from_word -> gen -> realise -> IncrWord; compare with the anchor (invoice diff)')
    p.add_argument('--random',type=int,default=0,help='draw N specs (knob perturbations of the anchor spec) and evaluate each')
    p.add_argument('--anchor',default='5718',help='anchor word for --random (alias/path); 5718 is the fuzz-tested profile'); p.add_argument('--profile-name',help='verifier profile (default: the anchor alias)')
    p.add_argument('--seed',type=int,default=0); p.add_argument('--out'); p.add_argument('--store',help='SQLite store (default: jsonl only; "default" = SEARCH/store.sqlite)')
    p.add_argument('--classes',default='all',help='comma list of knob classes to draw from (see synth/sample.py KNOBS)'); p.add_argument('--no-repair',action='store_true'); p.add_argument('--cpuq',help='write W/jobs/pending/NAME.sh running this sampling (resumable)')
    p.add_argument('--budget',type=float,default=0.5,help='CPU hours cap for --random (stops drawing when reached)'); p.add_argument('--frontier',default='.0031131380')
    p.add_argument('--front-gen',action='store_true',help='FRONTGEN: build a word from scratch with synth/frontgen.py (unhinted front end + dim-0 junk), evaluate (legal, value check, kappa) and print the gap to --anchor by cost line; --out F writes the word')
    p.add_argument('--back',default='star',help='with --front-gen: back-end method (synth/backgen.py): star|gray|dilworth  (spec key back=generated:<method>)')
    p.add_argument('--learned',type=int,default=0,help='GENLEARN: N draws of the learned modes (synth/learned.py) around --anchor (template) or with --front-gen; use --helpers learned / --schedule learned')
    p.add_argument('--helpers',default=None,help='with --learned: helper mode (learned)'); p.add_argument('--schedule',default=None,help='with --learned: main-register schedule mode (learned)')
    p.add_argument('--no-gap',action='store_true',help='with --front-gen: skip the cost-line gap report (regress uses this)')
    p.add_argument('--strict-bounds',action='store_true',help='do NOT set TK_FREE_BOUNDS=1 (default for the sampler / --front-gen: the 26000 event cap and public/owned inventory are package conventions')
def main(a):
    from . import sample; return sample.main(a)
