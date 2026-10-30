#!/usr/bin/env python3
"""tk -- the designer toolkit.  See README.md.   Subcommands: price check retime diff hops sens evretime pricer gen"""
import sys,argparse
sys.dont_write_bytecode=True
def build():
    ap=argparse.ArgumentParser(prog='tk',description=__doc__); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('price',help='exact kappa (fast; --real = real verifier stack via hq)'); p.add_argument('word'); p.add_argument('--real',action='store_true'); p.add_argument('--wait',action='store_true'); p.add_argument('--json',action='store_true'); p.add_argument('--no-cache',action='store_true')
    p=sp.add_parser('check',help='legality oracle with error localisation'); p.add_argument('word'); p.add_argument('--native',action='store_true'); p.add_argument('--exact',action='store_true'); p.add_argument('--wait',action='store_true'); p.add_argument('--max',type=int,default=50); p.add_argument('--json',action='store_true')
    p=sp.add_parser('retime',help='exact lattice retime'); p.add_argument('word'); p.add_argument('--free',required=True,help='comma list of starts,finals,stops,mainstops,mainends'); p.add_argument('--pin',help='mainstops: keep main-register intermediate frames'); p.add_argument('--tl',type=float,default=900); p.add_argument('--out'); p.add_argument('--wait',action='store_true'); p.add_argument('--inline',action='store_true',help='run in this process (inside an hq job)'); p.add_argument('--name')
    p=sp.add_parser('diff',help='what changed between two words'); p.add_argument('a'); p.add_argument('b'); p.add_argument('--json',action='store_true')
    p=sp.add_parser('hops',help='hop/role/restore counts of a delivery program'); p.add_argument('matrix'); p.add_argument('--signed',action='store_true'); p.add_argument('--program'); p.add_argument('--points'); p.add_argument('--json',action='store_true'); p.add_argument('--recomb',action='store_true',help='submit CP-SAT recombination via hq')
    p=sp.add_parser('evretime',help='event-level exact retime, free ADD placement'); p.add_argument('word'); p.add_argument('--k',type=int,default=2); p.add_argument('--maxm',type=int,default=0); p.add_argument('--tl',type=float,default=900); p.add_argument('--out'); p.add_argument('--wait',action='store_true'); p.add_argument('--inline',action='store_true'); p.add_argument('--name')
    p=sp.add_parser('pricer',help='rank-r owned-pivot pricing (PR5392 generalisation)'); p.add_argument('--synth',action='store_true',help='rank-8 synthetic (k=1,2 relations)')
    p=sp.add_parser('gen',help='S4GEN/GENX hub-partition generator for window B (#4610 word)'); p.add_argument('preset',nargs='?',default='full0'); p.add_argument('--realise',action='store_true',help='also run realise6 (about 220 s, via hq)'); p.add_argument('--wait',action='store_true'); p.add_argument('--tag'); p.add_argument('--env',action='append',default=[],help='extra KEY=VAL for gen_run3.py')
    p=sp.add_parser('sens',help='kappa marginals of the exact invoice'); p.add_argument('word'); p.add_argument('--calls',type=int,default=18); p.add_argument('--json',action='store_true')
    return ap
def main():
    a=build().parse_args()
    import importlib; m=importlib.import_module(a.cmd); r=m.main(a); sys.exit(r or 0)
if __name__=='__main__': main()
