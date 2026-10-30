#!/usr/bin/env python3
"""[toolkit hygiene] import every toolkit module (top level + subpackages) and assert os.environ is unchanged by the import.
usage: tests/import_env_test.py [--list] [--fast: only the modules that used to set the env, ~10 s]   Modules that fail to import for other reasons are reported (SKIP) but only an env change is a FAIL."""
import sys,os,glob,importlib,traceback,io,contextlib
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
for k in ('TK_FREE_BOUNDS','TK_NATIVE_CORE'): os.environ.pop(k,None)
sys.path[:0]=[TK,TK+'/infra']
SKIP={'tk','regress','kernel2_test','synth.rlever_sign'}           # tk.py snapshots env deliberately; kernel2_test is a script-style test (K2UNIFY lane); rlever_sign = RESIDUAL analysis script that runs at import (imports RESIDUAL geo, which sets the env)
mods=[os.path.basename(p)[:-3] for p in sorted(glob.glob(TK+'/*.py'))]
FASTMODS=['alias_core','macros','prims_mined','prims_role','splitretire','pscreen','genpipe','prims','gensearch.build','synth.backgen_measure','synth.k2search_validate','alignbuild.api','alignbuild.anatomy_core']
for sub in ('synth','gensearch','wsearch','k2','alignbuild'):
    for p in sorted(glob.glob(TK+'/%s/*.py'%sub)): 
        b=os.path.basename(p)[:-3]
        if b!='__init__': mods.append('%s.%s'%(sub,b))
if '--fast' in sys.argv: mods=FASTMODS
bad=[];skip=[];ok=0
for m in mods:
    if m in SKIP: continue
    before=dict(os.environ)
    try:
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()): importlib.import_module(m)
    except BaseException as e: skip.append((m,type(e).__name__)); 
    after=dict(os.environ)
    if after!=before:
        d={k:(before.get(k),after.get(k)) for k in set(before)|set(after) if before.get(k)!=after.get(k)}; bad.append((m,d)); 
        for k in list(d): 
            if before.get(k) is None: os.environ.pop(k,None)
    else: ok+=1
for m,d in bad: print('FAIL env changed at import:',m,d)
if '--list' in sys.argv: print('SKIP',skip)
print('imported %d modules env-clean, %d env-changing, %d import errors (skipped: %s)'%(ok,len(bad),len(skip),','.join(m for m,_ in skip)))
print('ALL PASS' if not bad else 'FAILS %d'%len(bad)); sys.exit(1 if bad else 0)
