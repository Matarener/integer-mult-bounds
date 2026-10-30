"""Literal inverse-transpose native K companion; default is read-only.

--write authors B-PROGRAM/B-MODULE, never the frozen forward science.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse,gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def need(ok,why):
    if not ok:raise ValueError(why)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def calculate(root):
    verify=load('wholeK_backward_preflight',root/'verify.py');verification=verify.calculate(root)
    need(json.loads(json.dumps(verification))==json.loads((root/'VERIFY-RESULT.json').read_bytes()),'frozen forward executed-mutant preflight')
    original=json.loads(gzip.decompress((root/'K-PROGRAM.json.gz').read_bytes()))
    original_digest=sha256((json.dumps(original,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
    ce=load('wholeK_backward_primitive',root/'inputs/clifford_exact.py')
    n=original['axis_dimension'];ports=original['port_order'];olddefs=original['definitions'];definitions={}
    def define(word):
        word=json.loads(json.dumps(word));key=sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest();definitions.setdefault(key,word);return key
    def conjugate(word):
        out=[]
        for e in word:
            if e[0]=='D':out.append(['D',e[1],[(-a)%4 for a in e[2]]])
            elif e[0]=='phase':out.append(['phase',(-e[1])%4])
            else:need(e[0]in('P','X'),'no Gaussian hidden in monomial');out.append(e)
        return out
    def literal(word):
        value=ce.ident(n)
        for e in word:
            if e[0]=='P':part=ce.perm(n,e[1])
            elif e[0]=='D':part=ce.diag(n,e[1],e[2])
            elif e[0]=='X':part=ce.xgate(n,e[1])
            elif e[0]=='phase':part=ce.Op(n,ce.identity(n),[tuple(e)])
            else:need(e[0]=='C','known primitive');part=ce.cgate(n,e[1],e[2])
            value=value.then(part)
        return value
    translated={};checks=0
    def translate_path(path):
        nonlocal checks
        key=json.dumps(path,sort_keys=True,separators=(',',':'))
        if key not in translated:
            pre=conjugate(olddefs[path['before_monomial']]);post=conjugate(olddefs[path['after_monomial']]);axes=path['child_axes'];mask=sum(1<<a for a in axes)
            result={'before_monomial':define(pre),'child_axes':axes,'after_monomial':define([['X',mask]]+post),'rank':path['rank'],
                    'absolute_phase_proof':'Conjugate each original literal gate; C_minus=X_mask C_plus exactly, including absolute phase.'}
            before=literal(olddefs[path['before_monomial']]).then(ce.fourier(n,axes)).then(literal(olddefs[path['after_monomial']]))
            after=literal(pre).then(ce.fourier(n,axes)).then(ce.xgate(n,mask)).then(literal(post))
            need(after.tab==tuple((x,z,(-p)%4)for x,z,p in before.tab),'actual backward child conjugated signed tableau')
            need(ce.rank([x for x,z,p in after.tab[n:]])==path['rank'],'actual backward child Gaussian rank')
            translated[key]=result;checks+=1
        return translated[key]
    program=[];paid=Counter();ordinary=Counter()
    def boundary(role,p,mask,name):
        key=define([['X',mask]]);program.append(['BOUNDARY_MONOMIAL',role,p,key,name]);ordinary['X']+=1
    for p in ports:boundary('X',p,1,'input_Q_minus2')
    for e in original['program']:
        kind=e[0]
        if kind=='MONOMIAL':
            _,role,p,key,name=e;word=conjugate(olddefs[key]);newkey=define(word)
            program.append(['MONOMIAL',role,p,newkey,'inverse_transpose_'+name]);ordinary.update(g[0]for g in word)
        elif kind=='PAID_PATH':
            _,role,p,old,new,path=e;record=translate_path(path)
            program.append(['PAID_PATH',role,p,'conjugate:'+old,'conjugate:'+new,record]);paid[record['rank']]+=1
            for key in ['before_monomial','after_monomial']:ordinary.update(g[0]for g in definitions[record[key]])
        else:
            need(kind=='ADD','invertible original opcode only');_,dr,dp,sr,sp,a,b,chart=e
            program.append(['ADD',sr,sp,dr,dp,-a,b,'conjugate:'+chart]);ordinary['ADD']+=1
    for p in ports:
        # Consecutive commuting X masks for D^2 and Q^2 are literally composed.
        boundary('X',p,(1<<n)-1,'output_D_squared_then_Q_squared')
        boundary('Y',p,((1<<n)-1)^1,'output_D_squared')
    need(paid=={8:512,9:512,15:512,16:512},'backward paid profile unchanged')
    need(ordinary=={'ADD':38912,'P':7680,'D':7680,'X':6656,'phase':3072},'backward full literal ordinary invoice')
    rows={(r,p):{(r,p):F(1)}for r in ['X','Y']for p in ports}
    charts={(r,p):'conjugate:'+('line:'+str(p)if r=='X'else'ground')for r,p in rows}
    for e in program:
        if e[0]=='PAID_PATH':
            _,r,p,old,new,path=e;need(charts[r,p]==old,'backward actual paid entrance');charts[r,p]=new
        elif e[0]=='ADD':
            _,dr,dp,sr,sp,a,b,ch=e;need(charts[dr,dp]==charts[sr,sp]==ch,'backward ADD actual same chart')
            for q,c in rows[sr,sp].items():
                v=rows[dr,dp].get(q,F(0))+F(a,b)*c
                if v:rows[dr,dp][q]=v
                else:rows[dr,dp].pop(q,None)
    expected={(r,p):{(r,p):F(1)}for r in ['X','Y']for p in ports}
    for reader,row in original['literal_scalar_K_rows'].items():
        for source,a,b in row:expected['X',source]['Y',int(reader)]=-F(a,b)
    need(rows==expected,'all1024 actual inverse-transpose scalar columns')
    primitive_checks=0
    for sn in range(1,5):
        for mask in range(1,1<<sn):
            axes=[a for a in range(sn)if mask>>a&1];positive=ce.fourier(sn,axes);inverse=positive.adjoint();compiled=positive.then(ce.xgate(sn,mask))
            need(inverse.tab==compiled.tab,'positive-child inverse signed tableau')
            for x in range(1<<sn):need(inverse.zero_state(x)==compiled.zero_state(x),'positive-child inverse absolute all-column phase')
            primitive_checks+=1
    first=next(e[5]for e in program if e[0]=='PAID_PATH');oldfirst=next(e[5]for e in original['program']if e[0]=='PAID_PATH')
    word=definitions[first['before_monomial']]+[['C',1<<a,1]for a in first['child_axes']]+definitions[first['after_monomial']]
    oldword=olddefs[oldfirst['before_monomial']]+[['C',1<<a,1]for a in oldfirst['child_axes']]+olddefs[oldfirst['after_monomial']]
    state,den=verify.sparse(oldword,n);newstate,newden=verify.sparse(word,n)
    need(newstate=={x:(a,-b)for x,(a,b)in state.items()}and newden==den,'actual rank8 backward absolute conjugate phase')
    # Exact noncommuting block normalization: C_K is never moved across Q.
    def reduce_word(word):
        out=[];q=d=0
        def flush():
            nonlocal q,d
            if d:out.append(('D',d))
            if q:out.append(('Q',q))
            q=d=0
        for op,power in word:
            if op=='Q':q+=power
            elif op=='D':d+=power
            else:flush();out.append((op,power))
        flush();return out
    need(reduce_word([('Q',2),('D',2),('D',-1),('Q',-2)])==[('D',1)],'backward source diagonal boundary')
    need(reduce_word([('D',2),('D',-1)])==[('D',1)],'backward reader diagonal boundary')
    need(reduce_word([('Q',2),('D',2),('D',-1),('Q',-1),('C_K',1)])==[('D',1),('Q',1),('C_K',1)],'backward upper block without commuting C_K,Q')
    payload={'schema':'odd-E8-whole-K-backward-literal-word/v1','forward_scientific_payload_sha256':original_digest,
             'axis_dimension':n,'cube_tuple':original['cube_tuple'],'port_order':ports,'definitions':definitions,'program':program,
             'transformation':'Same chronological E -> E^-T. Real scalar ADD swaps roles and negates coefficient. Monomial becomes complex conjugate. C_minus child is emitted as positive C_plus followed by X_axis_mask.',
             'boundary':'Input X Q^-2; output both banks D^2 then output X Q^2. Consecutive X-bank output masks are literally composed into X_all25.',
             'normalized_endpoint':'B_K=diag(D,D) U(-Q C_K), without requiring [C_K,Q]=0',
             'all_widths':'One-copy address maps tensor-lift; phase theta -> i^(f theta). Owner scalar coefficients transposed/negated once, never raised to width f.'}
    canonical=(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode();encoded=gzip.compress(canonical,mtime=0)
    summary={'schema':'odd-E8-whole-K-backward-native/v1','status':'PASS','forward_scientific_payload_sha256':original_digest,
             'backward_scientific_payload_sha256':sha256(canonical).hexdigest(),'paid_profile':dict(sorted(paid.items())),
             'ordinary_literal_profile':dict(sorted(ordinary.items())),'distinct_conjugated_paid_paths':checks,
             'all_independent_scalar_columns':1024,'small_dense_child_inversion_cases':primitive_checks,
             'actual_rank8_word_absolute_phase_checked':True,'normalized_endpoint':payload['normalized_endpoint'],
             'helpers':0,'owned_fields':0,'COPY':0,'CLEAR':0,'new_kappa':False,
             'scope':'Literal backward native K companion, including ordinary boundaries. It does not supply H or close/admit an outer caller.'}
    return summary,payload,encoded
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=HERE);ap.add_argument('--write',action='store_true');args=ap.parse_args();root=args.package.resolve()
    summary,payload,encoded=calculate(root)
    if args.write:
        (root/'B-MODULE.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');(root/'B-PROGRAM.json.gz').write_bytes(encoded)
    else:
        need(json.loads((root/'B-MODULE.json').read_bytes())==json.loads(json.dumps(summary)),'frozen backward semantic receipt')
        need(json.loads(gzip.decompress((root/'B-PROGRAM.json.gz').read_bytes()))==json.loads(json.dumps(payload)),'frozen backward actual word')
    print('PASS whole-K literal backward native; columns1024; '+summary['backward_scientific_payload_sha256'])
if __name__=='__main__':main()
