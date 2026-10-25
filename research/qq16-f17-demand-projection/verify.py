#!/usr/bin/env python3
"""F17 demand projection. Chris R / Clear1nsight, OpenAI assistance; Apache-2.0.

Source/operator primitives: ywz65 PR2707 and Arham Tahir PR2681. Source bytes
are authenticated before execution. This is a scoped changed-consumer audit.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEC='research/qq16-line-normalized-decoder/'


def need(ok, why):
    if not ok: raise ValueError(why)


def decode(raw):
    def unique(pairs):
        out={}
        for k,v in pairs:
            need(k not in out,'duplicate JSON key'); out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=unique)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()


def module(path, raw=None):
    out=types.ModuleType(path.stem); out.__file__=str(path)
    exec(compile(path.read_bytes() if raw is None else raw,str(path),'exec'),out.__dict__)
    return out


def authenticate():
    raw={}
    for pin in decode((HERE/'SOURCES.json').read_bytes())['files']:
        if pin['usage']!='input': continue
        data=(ROOT/pin['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest()==pin['sha256'],'source SHA256: '+pin['path'])
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],'source Git blob')
        raw[pin['path']]=data
    return raw


def load(raw):
    L=module(ROOT/DEC/'verify.py',raw[DEC+'verify.py'])
    P,R,routes,labels,_=L.load_source()
    source=decode(raw[DEC+'WORD.json'])
    need(source==L.lower(P,R),'complete source word regeneration')
    return P,R,routes,labels,source


def projection(P,source):
    result=[]
    for e in source:
        # No stage-2 line/map is needed on U: logger writes only selected A.
        if (e[0]=='line' and e[3]==-1) or (e[0]=='map' and e[2]==2): break
        op=e[0]
        if op in ('begin','end') or (op=='clear' and e[1].startswith('F')):
            result.append(e.copy())
        elif op=='add':
            dst,src=e[1:3]
            if dst.startswith('F') or (dst.startswith('W') and src.startswith('Y')) or (
                dst.startswith('W') and int(dst[1:]) in P.U and src.startswith('F')):
                result.append(e.copy())
        elif op in ('clear','line','map') and e[1].startswith('W'):
            p=int(e[1][1:])
            if op=='clear' and e[2]=='wide': continue
            if op=='map' and e[4] and p not in P.U: continue
            result.append(e.copy())
    for p in P.V: result.append(['clear','W'+str(p),'identity'])
    return result


def demand(P,R,routes,y2):
    q=P.query(R,routes,1,y2,range(112)); correction=P.inject(R,routes,1,q,P.U)
    return [P.add(y2[p],correction[p],-1) for p in range(112)]


def native(P,labels):
    columns=0
    for q in labels:
        pivot=(q & -q).bit_length()-1
        basis=(q,)+tuple(1<<j for j in range(9) if j!=pivot)
        inverse={P.act(basis,x):x for x in range(512)}
        need(len(inverse)==512,'native basis bijection')
        for x in range(512):
            t=inverse[x]
            need({P.act(basis,t):(1,1),P.act(basis,t^1):(1,-1)}=={x:(1,1),x^q:(1,-1)},'positive rank1 kernel')
            columns+=1
    return columns


def calculate():
    raw=authenticate(); P,R,routes,labels,source=load(raw)
    replay=module(HERE/'replay.py').replay
    B=module(HERE/'budget.py')
    word=projection(P,source)
    old=decode(raw['research/qq16-current-frame-consumer/WORD.json'])
    epilogue=[{'coefficient':'-1','consumer':True,'dst':'Z'+str(p),'op':'add','src':'X'+str(p)} for p in P.U]
    need(old[-96:]==epilogue,'actual published consumer epilogue')
    old_receipt=decode(raw['research/qq16-current-frame-consumer/RESULT.json'])
    need(old_receipt['contract']=='Checkpoint Z=x1_U; consumer Z-=X2_U yields y1_U, both in F_U1; all sources restored.','published demand contract')
    need(old_receipt['invoice']['retained_F0_T_source_arrays']==8,'old retention premise')
    y2=[{('Y'+str(p),P.AXES):Q(1)} for p in range(112)]
    expected=demand(P,R,routes,y2)
    counts=replay(P,word,routes,labels,None,y2,expected)
    # Test the B1 identity on independent x1,y1, without any F0 relation.
    x1=[{('x1_'+str(p),P.AXES):Q(1)} for p in range(112)]
    y1=[{('y1_'+str(p),P.AXES):Q(1)} for p in range(112)]
    future=P.inject(R,routes,2,P.query(R,routes,2,y1,P.U+P.T),P.A)
    u=[P.add(y1[p],future[p]) for p in range(112)]
    qa=P.query(R,routes,1,x1,P.T); qb=P.query(R,routes,1,u,range(112))
    ka=P.inject(R,routes,1,qa,P.U); pa=P.inject(R,routes,1,qa,P.T); pb=P.inject(R,routes,1,qb,P.T)
    forwarded=[P.add(y1[p],ka[p]) if p in P.U else (u[p] if p in P.A else
               P.add(P.add(u[p],pb[p],-1),pa[p],-11)) for p in range(112)]
    recovered=demand(P,R,routes,forwarded)
    need([recovered[p] for p in P.U]==[y1[p] for p in P.U],'B1 demand identity')
    replay(P,word,routes,labels,None,forwarded,y1)
    controls={}
    def reject(name,mutate):
        changed=deepcopy(word); mutate(changed)
        try: replay(P,changed,routes,labels,None,y2,expected)
        except (ValueError,KeyError) as error: controls[name]=str(error)
        else: raise ValueError('ineffective control: '+name)
    reject('owned dirt',lambda w:w.pop(0))
    reject('normalization',lambda w:w.remove(next(e for e in w if e[0]=='line')))
    reject('query sign',lambda w:next(e for e in w if e[0]=='add' and e[1]=='F0').__setitem__(3,'-1'))
    reject('injection sign',lambda w:next(e for e in w if e[0]=='add' and e[3]=='-1/4').__setitem__(3,'1/4'))
    reject('map translation',lambda w:next(e for e in w if e[0]=='map').append('omit_shift'))
    reject('private cleanup',lambda w:w.remove(['clear','F0','identity']))
    reject('temporary cleanup',lambda w:w.remove(['clear','W0','identity']))
    reject('borrowed clear',lambda w:w[0].__setitem__(1,'Y0'))
    reject('output inverse map',lambda w:w.remove(next(e for e in w if e[0]=='map' and e[4])))
    need(len(P.U)==96 and len(P.V)==16,'demand ports')
    invoice={'rank_one_children':counts['line'],'rank_eight_children':0,'native_rank_mass':counts['line'],
             'native_monomial_wrappers':2*counts['line'],'full_cover_maps':counts['map'],
             'unit_ADDs':counts['unit_ADD'],'quarter_ADDs':counts['quarter_ADD'],'CLEARs':counts['clear'],
             'real_scalar_primitive_allowance':8*counts['unit_ADD']+12*counts['quarter_ADD']+2*counts['clear'],
             'owned_full_cover_outputs':96,'owned_full_cover_temporaries':16,'peak_local_owned_scratch':8,
             'early_record_banks':0,'untouched_borrowed_current_Y':112,'current_X_reads':0}
    baseline=decode(raw[DEC+'RESULT.json'])['invoice']
    packet=decode(gzip.decompress(raw['research/joint-query/certificate.json.gz']))
    profiles={n:B.profile(packet,B.expand(packet,n)) for n in ('F_0','B_1_2')}
    base={r:Q(profiles['F_0'][r]+profiles['B_1_2'][r],2) for r in profiles['F_0']}
    need(base=={1:2428,2:418,3:432,4:142,5:82},'producer profile')
    coverage=decode(raw['research/complex-local-word-ceiling/RESULT.json'])
    need(coverage['selected']['local_profile_per_call']['8']==8,'retained eight-rank8 profile premise')
    model=coverage['model']
    need((model['m'],Q(model['live_families_per_call']),model['centre_per_call'],model['idle_rank_cap'])==(73,Q(896,9),64,51),'coverage model')
    kappa=Q(decode(raw['certificates/selected-result.json'])['kappa'])
    need(kappa==Q(836330098538459,500000000000000000),'selected target')
    a=kappa/(1-kappa)
    full=B.moment(base,counts['line'],64,True,a); waived=B.moment(base,counts['line'],64,False,a)
    need(full[0]>1 and waived[1]<1,'budget split')
    need(B.moment(base,61,64,True,a)[1]<1<B.moment(base,62,64,True,a)[0],'retained threshold')
    need(B.moment(base,121,64,False,a)[1]<1<B.moment(base,122,64,False,a)[0],'waived threshold')
    two_base=dict(base);two_base[8]=Q(1)
    three_base=dict(base);three_base[8]=Q(3,2)
    two=B.moment(two_base,112,64,False,a);three=B.moment(three_base,112,64,False,a)
    need(two[1]<1<three[0],'retained rank8 pair threshold')
    return {'status':'PASS_QQ16_F17_DEMAND_PROJECTION no_new_kappa',
        'demand':{'source_pr':2512,'ports':list(P.U),'logical_output':'y1_U','frame':'F17',
                  'cut':'immediate post-B1','source_retained_T':8,'new_retained_T':0},
        'events':len(word),'word_sha256':hashlib.sha256(canonical(word)).hexdigest(),
        'counts':dict(counts),'invoice':invoice,'removed_from_full_decoder':{
            k:baseline[k]-invoice[k] for k in ('rank_one_children','native_rank_mass','native_monomial_wrappers',
                'full_cover_maps','unit_ADDs','quarter_ADDs','CLEARs','real_scalar_primitive_allowance')},
        'positive_native_kernel_columns':native(P,labels),'demanded_formal_terms':sum(len(expected[p]) for p in P.U),
        'controls':controls,'producer_profiles':profiles,'selected_a':str(a),
        'budget':{'centre64_retaining_eight_rank8':B.decimal_interval(full),
                  'centre64_waiving_eight_rank8':B.decimal_interval(waived),
                  'retained_profile_max_pair_calls':61,'waived_profile_max_pair_calls':121,
                  'with_112_H1_max_integer_retained_H8_per_pair':2,
                  'with_112_H1_first_excluded_integer_H8_per_pair':3,
                  'two_H8_per_pair':B.decimal_interval(two),'three_H8_per_pair':B.decimal_interval(three),
                  'pair_call_reduction_still_required_with_rank8_retained':counts['line']-61,
                  'waived_profile_normalized_allowance':B.decimal_interval((1-waived[1],1-waived[0]))},
        'scope':'One demand; complete local primitive counts; fixed-profile optimistic screen only. No physical/global admission.'}


def main():
    actual=calculate()
    need(canonical(actual)==canonical(decode((HERE/'RESULT.json').read_bytes())),'complete RESULT mismatch')
    P,_,_,_,source=load(authenticate())
    need(canonical(projection(P,source))==canonical(decode((HERE/'WORD.json').read_bytes())),'complete WORD mismatch')
    print(json.dumps(actual,sort_keys=True,indent=2))


if __name__=='__main__': main()
