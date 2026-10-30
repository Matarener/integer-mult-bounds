"""Explicit quadratic-state integration of PR5698 physical replay.

Derived from Ali Romman PR5698. Every physical reconstruction and check stays
in place. Only the exact state comparison uses the quadratic engine.

Emit and check each actual native map in the new coframes.

Source modules and notices are retained without edits. The source is checked
before import. Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from pathlib import Path
from hashlib import sha256
import gzip
import importlib.util
import json
import sys
import optimize as O
from quadratic import equal_operators

ROOT = Path(__file__).resolve().parent / 'source'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def decode_recipe(P, ce, recipe, op, equality=equal_operators):
    left=P.monomial(ce,recipe['left'],9)
    if recipe['rank']:
        right=P.monomial(ce,recipe['right'],9)
        decoded=right.then(ce.fourier(9,range(recipe['rank']))).then(left)
    else:
        O.need(recipe['right'] is None,'Ordinary recipe has no child wrapper')
        decoded=left
    O.need(equality(decoded,op),'Stored recipe literal tableau and absolute phase')
    return recipe

def build(folded, expected=None, equality=equal_operators):
    word = O.source(); c = word['canonical']; sys.path.insert(0,str(ROOT/'source'))
    import native_extensions as X
    import rebuild_native as N
    P = load('coframe_prune', ROOT/'source/prune_native.py')
    V = load('coframe_buffers', ROOT/'source/verify_buffers.py')
    ce = load('coframe_clifford', ROOT/'source/clifford_exact.py')
    inv = O.inventory(word); O.need(not (set(folded)&set(inv['anchored'])), 'All protected coframes stay fixed')
    coframe = lambda i: 0 if i in folded else i
    frames = {}; maps = {}; helpers = []; programs = {}; replays = {}
    expected_helpers = {} if expected is None else {h['role']:h for h in expected['helpers']}
    def lower(key, op):
        return N.lower_exact(P,ce,op) if expected is None else decode_recipe(P,ce,expected['maps'][key],op,equality)
    def frame(i):
        if i not in frames: frames[i] = ce.canonical_frame(9,c['frames'][i])
        return frames[i]
    def compile_map(direction, a, b):
        key = direction+':transport:'+str(a)+':'+str(b)
        if key not in maps:
            op = frame(a).adjoint().then(frame(b))
            if direction == 'backward': op = P.conjugate(ce,op)
            recipe = lower(key,op)
            O.need(recipe['rank'] == abs(len(c['frames'][b])-len(c['frames'][a])), 'Literal coframe Gaussian grade')
            maps[key] = recipe
        return key
    warps = {}
    for w in c['warps']:
        G = ce.transpose(tuple(w['G_columns']),9); gi = ce.inv(G,9); tr = ce.transpose(gi,9)
        quad = tuple(1<<i ^ sum(ce.parity(a&b)<<j for j,b in enumerate(tr)) for i,a in enumerate(tr))
        warps[w['op']] = ce.perm(9,G).then(ce.diag(9,quad))
    for direction, program in word['programs'].items():
        backward = direction == 'backward'
        rows,receipt = X.literal_replay(V,c,program,backward)
        O.need(all(rows['L',r] == V.expected(('L',r),[],backward,False) for r in range(632)), 'All source independent columns and native words')
        replays[direction] = receipt; out = []; paid = Counter()
        for event in program:
            kind = event[0]
            if kind == 'scalar':
                out.append(['scalar',event[1],coframe(event[2])])
            elif kind in ('climb','center'):
                if kind == 'climb': role=['L',event[2]]; a,b=event[3:5]
                else: role=['C',event[1]]; a,b=event[2:4]
                a,b = coframe(a),coframe(b); key=compile_map(direction,a,b)
                rank=maps[key]['rank']
                if rank: paid[rank]+=1
                out.append(['transport',role,a,b,key])
            elif kind == 'warp':
                _,role,op,a,b=event
                O.need(coframe(a)==a and coframe(b)==b, 'Unchanged actual native warp endpoints')
                key=direction+':warp:'+':'.join(map(str,(op,a,b)))
                if key not in maps:
                    body=warps[abs(op)] if op>0 else warps[abs(op)].adjoint()
                    physical=frame(a).adjoint().then(body).then(frame(b))
                    if backward:physical=P.conjugate(ce,physical)
                    maps[key]=lower(key,physical)
                    O.need(maps[key]['rank']==0,'Every retained actual warp is ordinary')
                out.append(['native',role,a,b,key])
            else:
                O.need(kind in ('adapter','phase'),'Retained source marker')
                out.append(event)
        O.need(dict(sorted(paid.items()))==O.profiles(word,set(folded))['paid'],'Complete emitted query profile')
        programs[direction]=out
        print('PASS_NATIVE_MAPS',direction,len(maps),flush=True)
    helper_cache={}
    for role in range(224,632):
        a,b=coframe(c['start'][role]),coframe(c['final'][role]);target=O.grade(c['start'][role],c['final'][role],set(folded),inv['dims'])
        row=dict(role=role,start=a,end=b,rank=target,orientations={})
        for direction in ('forward','backward'):
            key=(direction,a,b)
            if key not in helper_cache:
                op=frame(a).adjoint().then(frame(b))
                if direction=='backward':op=P.conjugate(ce,op)
                if expected is None: helper_cache[key]=N.normal_form(P,ce,op,target)
                else:
                    recipe=expected_helpers[role]['orientations'][direction]
                    O.need(recipe['rank']==target,'Complete target grade')
                    decode_recipe(P,ce,recipe['factorization'],op,equality)
                    pre=P.monomial(ce,recipe['outer_pre_monomial'],9)
                    post=P.monomial(ce,recipe['outer_post_monomial'],9)
                    actual=pre.then(op).then(post); positive=ce.fourier(9,range(target))
                    O.need(equality(actual,positive),'Independent helper boundary normalization')
                    helper_cache[key]=recipe
            row['orientations'][direction]=helper_cache[key]
        helpers.append(row)
    plan=dict(schema='actual-restricted-gaussian-coframes/1',folded_frames=sorted(folded),
              main_normalizers='source/INTERSECTION153-ROUND3-MAIN-NORMALIZERS.json.gz',programs=programs,maps=maps,helpers=helpers)
    canonical=json.dumps(plan,sort_keys=True,separators=(',',':')).encode()
    return plan,dict(source_replays=replays,distinct_literal_maps=len(maps),distinct_helper_normalizers=len(helper_cache),
                     helpers=len(helpers),plan_sha256=sha256(canonical).hexdigest(),
                     program_events={d:len(p)for d,p in programs.items()})
