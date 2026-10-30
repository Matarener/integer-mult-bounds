"""Read-only independent phase audit, standard library only."""
import argparse,copy,gzip,hashlib,json,time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import exact_phase as e
P=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def key(d):return json.dumps({k:v for k,v in d.items()if k not in ('recipe','coverage')},sort_keys=True,separators=(',',':'))
def authenticate():
    s=json.loads((P/'SOURCES.json').read_text())
    for row in s['external_public_inputs']:
        e.need(sha(P/row['local_path'])==row['sha256'],'source bytes '+row['local_path'])
    for tag in ['base','extra']:
        r=json.loads((P/'frozen'/('NATIVE-'+tag+'.json')).read_text())
        e.need(r['word_sha256']==sha(P/'frozen'/('WORD-'+tag+'.json.gz')),'native receipt word binding')
        e.need(r['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','native predecessor receipt status')
        e.need([s['step']for s in r['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in r['steps']),'native historical stage receipt')
        for f in ['clifford_exact.py','bw_phases.py','bw_adapters.py','bw_gauss.py','bw_transport.py']:
            origin='native/new/code/borrow/'+('vendor/clifford/'if f=='clifford_exact.py'else '')+f
            e.need(r['source_sha256'][origin]==sha(P/'vendor'/f),'native source binding '+f)
    return s

def release_binding():
    f=P/'frozen'
    evidence=json.loads((f/'EVIDENCE.json').read_text())
    release=json.loads((f/'RELEASE.json').read_text())
    manifest=json.loads((f/'FINAL-PACKAGE-MANIFEST.json').read_text())
    native=json.loads((f/'NATIVE-RECEIPT-CORRECTED.json').read_text())
    e.need(sha(f/'FINAL-PACKAGE-MANIFEST.json')==release['manifest_sha256']==evidence['final_package_manifest_sha256'],'release manifest link')
    e.need(sha(f/'RELEASE.json')==evidence['release_receipt_sha256'],'release receipt link')
    providers={}
    for tag in ['base','extra']:
        h=sha(f/('WORD-'+tag+'.json.gz'));r=native['providers'][tag];inventory=r['complete_native_files']
        e.need(h==r['word_sha256']==inventory['local/FULL-WORD.json.gz']==evidence['fresh_native'][tag]['word_sha256']==evidence['inputs'][tag+'_word'],'release native word links')
        e.need(h==manifest['new/borrow/words/BORROW-WORD-43'+tag+'.json.gz'],'release manifest word link')
        e.need(inventory['local/CANONICAL-WORD.json.gz']==evidence['fresh_native'][tag]['canonical_sha256'],'canonical inventory link')
        e.need(native['cache_files'][h+'/local/CLIFFORD-RECIPES.json']==inventory['local/CLIFFORD-RECIPES.json'],'recipe inventory link')
        providers[tag]=dict(word_sha256=h,retained_complete_recipe_sha256=inventory['local/CLIFFORD-RECIPES.json'],fresh_subset_recipe_scope='40 interface classes regenerated separately; not a byte replay of complete retained recipe payload')
    return dict(status='PASS_FROZEN_RELEASE_CROSSLINKS_ONLY',providers=providers,release_sha256=sha(f/'RELEASE.json'),final_manifest_sha256=sha(f/'FINAL-PACKAGE-MANIFEST.json'),limitations=['Full recipe payload not included in this local certificate; native receipt contains its hash.','Full manifest source archive and release execution not replayed.','Native receipt manifest refers to its own source context; it is not equated to the final package manifest.','Author EVIDENCE discloses frozen-spec corrections and successful-prefix reuse; no uninterrupted fresh release assertion.'])

def expected_coverage(words):
    out={};counts={}
    def add(d,label):out.setdefault(key(d),[]).append(label)
    for tag,(a,b)in words.items():
        e.need(len(a['warps'])==len(b['warps'])==72,'warp cardinality')
        promoted=[];actual=[];indexonly=[]
        for r,terminal in b['helper_final'].items():
            if terminal==a['helper_final'][r]:continue
            promoted.append(int(r));e.need(a['start_extra'].get(r,[])==b['start_extra'].get(r,[])==[],'cold promoted entrance')
            e.need(len(a['helper_final'][r])==4 and len(terminal)==5,'promotion width')
            for version,w in [('old',a),('new',b)]:
                add(dict(kind='residual',entrance=w['start_extra'].get(r,[]),terminal=w['helper_final'][r]),dict(provider=tag,kind='terminal',helper=int(r),version=version))
        for i,(old,new)in enumerate(zip(a['warps'],b['warps'])):
            e.need(old[1]==new[1]and old[2]==new[2],'warp identity or binary map changed')
            if old[2:]==new[2:]:
                if old!=new:indexonly.append(i)
                continue
            actual.append(i)
            for version,w in [('old',old),('new',new)]:
                for sign in [1,-1]:
                    add(dict(kind='warp',G_columns=w[2],entrance=w[3]if sign>0 else w[4],terminal=w[4]if sign>0 else w[3],sign=sign),dict(provider=tag,kind='warp',index=i,register=w[1],version=version,sign=sign))
        e.need(len(promoted)==26 and len(actual)==5 and len(indexonly)==47,'changed interface coverage')
        counts[tag]=dict(promoted_helpers=promoted,changed_native_warp_indices=actual,index_only_warp_changes=indexonly)
    return out,counts

def coverage_check(items,words):
    expected,counts=expected_coverage(words)
    actual={key(item):item['coverage']for item in items}
    e.need(len(actual)==len(items),'duplicate recipe descriptor')
    e.need(actual==expected,'source-to-interface coverage')
    return counts

def controls(items,words):
    results=[]
    def rejects(name,fn):
        try:fn()
        except (ValueError,KeyError):results.append(name);return
        raise ValueError('control accepted: '+name)
    warp=next(x for x in items if x['kind']=='warp'and len(x['entrance'])==5)
    residual=next(x for x in items if x['kind']=='residual'and len(x['terminal'])==5)
    for side in ['left','right']:
        z=copy.deepcopy(residual);z['recipe'][side]['phase']=(z['recipe'][side]['phase']+1)%4
        rejects('residual '+side+' global phase',lambda z=z:e.check_item(z))
    for name,mut in [
        ('warp global phase',lambda z:z['recipe']['left'].__setitem__('phase',(z['recipe']['left']['phase']+1)%4)),
        ('warp linear phase',lambda z:z['recipe']['left']['linear_Z4'].__setitem__(0,(z['recipe']['left']['linear_Z4'][0]+2)%4)),
        ('warp quadratic cocycle',lambda z:(z['recipe']['left']['quadratic_rows'].__setitem__(0,z['recipe']['left']['quadratic_rows'][0]^2),z['recipe']['left']['quadratic_rows'].__setitem__(1,z['recipe']['left']['quadratic_rows'][1]^1))),
        ('warp translation',lambda z:z['recipe']['left'].__setitem__('offset',z['recipe']['left']['offset']^1)),
        ('warp signed inverse',lambda z:z.__setitem__('sign',-z['sign'])),
        ('warp wrong terminal',lambda z:z.__setitem__('terminal',z['terminal'][:-1])),
        ('warp singular G',lambda z:z['G_columns'].__setitem__(0,z['G_columns'][1])),
    ]:
        z=copy.deepcopy(warp);mut(z);rejects(name,lambda z=z:e.check_item(z))
    z=copy.deepcopy(residual);z['terminal'].append(z['terminal'][0]);z['recipe']['rank']=len(z['terminal'])
    rejects('dependent terminal frame basis',lambda:e.check_item(z))
    z=copy.deepcopy(residual);z['recipe']['rank']=4
    rejects('promoted residual billed as width4',lambda:e.check_item(z))
    z=copy.deepcopy(residual);z['recipe']['left'],z['recipe']['right']=z['recipe']['right'],z['recipe']['left']
    rejects('residual wrappers swapped',lambda:e.check_item(z))
    z=copy.deepcopy(items);z.pop()
    rejects('one interface omitted',lambda:coverage_check(z,words))
    z=copy.deepcopy(items);z[0]['coverage'][0]['provider']='other'
    rejects('coverage provider relabelled',lambda:coverage_check(z,words))
    # A phase-blind permutation checker provably accepts this mutant. Our check rejects it above.
    clean=e.decoded(warp['recipe']['left']);m=copy.deepcopy(warp['recipe']['left']);m['phase']=(m['phase']+1)%4
    e.need(clean[0]==e.decoded(m)[0] and clean[1]!=e.decoded(m)[1],'phase-blind witness')
    # Explicit inverse/unitary controls on every compiled monomial over every basis column.
    mono_count=0
    for item in items:
        for side in ['left','right']:
            if item['recipe'][side]is None:continue
            k=e.decoded(item['recipe'][side]);mono_count+=1
            for x in range(e.SIZE):e.need(e.mono(e.mono({x:(1,0)},k),k,True)=={x:(1,0)},'monomial inverse')
    return dict(rejected=results,phase_blind_mutant_preserves_all_512_permutation_columns=True,monomial_inverse_columns=mono_count*e.SIZE)

def run(with_controls=True):
    authenticate();items=json.loads((P/'RECIPES.json').read_text())['items']
    words={tag:tuple(json.load(gzip.open(P/'frozen'/(name+tag+'.json.gz')))for name in ['old-WORD-','WORD-'])for tag in ['base','extra']}
    counts=coverage_check(items,words)
    checks=[e.check_item(item)for item in items]
    result=dict(status='PASS_INDEPENDENT_QUADRATIC_PHASE_INTERFACES',coverage=counts,unique_interfaces=len(items),source_occurrences=sum(len(x['coverage'])for x in items),all_basis_columns=len(items)*e.SIZE,items=checks)
    result['lift_cocycle']=e.cocycle_certificate(items)
    result['release_binding']=release_binding()
    if with_controls:result['controls']=controls(items,words)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--emit',type=Path);args=ap.parse_args();t=time.monotonic();result=run()
    if args.emit:
        e.need(P not in args.emit.resolve().parents,'receipt output must be outside package')
        args.emit.write_text(json.dumps(result,indent=2)+'\n')
    else:e.need(result==json.loads((P/'RESULT.json').read_text()),'retained result mismatch')
    print(result['status'],json.dumps({k:result[k]for k in ['unique_interfaces','source_occurrences','all_basis_columns']}),'seconds',round(time.monotonic()-t,3))
