"""Exact independent controls for the coprime-grid construction. Apache-2.0."""
import hashlib, itertools, json, random
from fractions import Fraction
from math import gcd, prod
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import grid
import source_guard

HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok: raise RuntimeError(msg)

def rejected(fn):
    try: fn()
    except ValueError: return
    raise RuntimeError('negative control accepted')

def check():
    fixtures=[]
    for k,d in [(8,4),(12,8),(16,16),(32,32),(64,64),(128,128)]:
        moduli,stats=grid.build(k,d)
        need(len(moduli)==d and len(set(moduli))==d,'shape')
        need(all(s%2 and 1<s<1<<k for s in moduli),'range')
        need(all(gcd(a,b)==1 for i,a in enumerate(moduli) for b in moduli[i+1:]),'pairwise gcd')
        certificate=grid.volume_certificate(k,moduli)
        need(Fraction(certificate['target_volume'],certificate['source_volume']) <=
             Fraction(certificate['inflation_upper_numerator'],certificate['inflation_upper_denominator']), 'volume')
        fixtures.append({'k':k,'axes':d,**stats,'moduli_sha256':hashlib.sha256(json.dumps(moduli,separators=(',',':')).encode()).hexdigest()})
    square_fixtures=[]
    for k,d in [(16,4),(32,16),(64,32),(128,64)]:
        moduli,roots,stats=grid.build_squares(k,d)
        need(all(s==a*a and 1<a<s for s,a in zip(moduli,roots)), 'composite witnesses')
        need(all(gcd(a,b)==1 for i,a in enumerate(moduli) for b in moduli[i+1:]),'square gcd')
        grid.volume_certificate(k,moduli)
        square_fixtures.append({'k':k,'axes':d,'maximum_deficit':stats['maximum_deficit'],
                                'sum_deficits':stats['sum_deficits']})
    band_fixtures=[]
    for ell,flags in [(20,[1,0,1]),(20,[0,1,0,1]),(28,[1,0,1,1,0,1,0,1])]:
        targets=[1 << (ell if flag else ell-1) for flag in flags]
        for squares in [False,True]:
            moduli,roots,stats=grid.build_bands(targets,squares=squares)
            need(all(gcd(a,b)==1 for i,a in enumerate(moduli) for b in moduli[i+1:]),'band gcd')
            need(all(3*(len(moduli)+1)*s > (3*(len(moduli)+1)-1)*t and
                     4*(len(moduli)+1)*s <= (4*(len(moduli)+1)-1)*t for s,t in zip(moduli,targets)), 'safe intervals')
            if squares:need(all(s==a*a and a>1 for s,a in zip(moduli,roots)),'band composite witnesses')
            need(2*prod(targets)<3*prod(moduli),'source tensor volume')
            source_guard.check(moduli,targets)
            band_fixtures.append({'ell':ell,'flags':flags,'squares':squares,'moduli':moduli,**stats})
    rejected(lambda:source_guard.check([255,253],[256,256]))
    seen=phase_checks=convolution_checks=0
    rng=random.Random(20261025)
    for moduli in [(3,5),(9,25),(9,25,7),(5,7,11)]:
        g=grid.CRTGrid(moduli)
        forward=list(g.indices(coordinates=True))
        need(g.last_changes < 2*g.size,'odometer bound')
        dual=list(g.indices(dual=True,coordinates=True))
        need(g.last_changes < 2*g.size,'dual odometer bound')
        need(sorted(a for a,_ in forward)==list(range(g.size)),'input permutation')
        need(sorted(a for a,_ in dual)==list(range(g.size)),'output permutation')
        for address,digits in forward:
            need(all(address%s==x for s,x in zip(moduli,digits)),'input residues')
            need(address==g.from_coordinates(digits),'direct input CRT')
        for address,digits in dual:
            need(address==sum(x*(g.size//s) for s,x in zip(moduli,digits))%g.size,'direct dual CRT')
        for _ in range(400):
            j,x=rng.choice(forward);k,y=rng.choice(dual)
            need((j*k-sum(a*b*(g.size//s) for a,b,s in zip(x,y,moduli)))%g.size==0,'Good-Thomas phase')
            phase_checks+=1
        # Independent sparse cyclic convolution versus product-group convolution.
        for _ in range(12):
            a={rng.randrange(g.size):rng.randrange(-9,10) for _ in range(13)}
            b={rng.randrange(g.size):rng.randrange(-9,10) for _ in range(13)}
            ordinary={}; tensor={}
            for j,v in a.items():
                for k,z in b.items():
                    key=(j+k)%g.size;ordinary[key]=ordinary.get(key,0)+v*z
                    coords=tuple((j%s+k%s)%s for s in moduli)
                    key=g.from_coordinates(coords);tensor[key]=tensor.get(key,0)+v*z
            need(ordinary==tensor,'cyclic convolution')
            convolution_checks+=1
        seen+=g.size
    # Full exact DFT, including non-prime tensor lengths 9 and 25.
    g=grid.CRTGrid([9,25]); prime=1801
    # 11 has order 1800 modulo 1801, and its eighth power has order 225.
    root=pow(11,8,prime)
    need(pow(root,225,prime)==1 and pow(root,75,prime)!=1 and pow(root,45,prime)!=1,'root order')
    values=[rng.randrange(prime) for _ in range(g.size)]
    forward=list(g.indices(coordinates=True));dual=list(g.indices(dual=True,coordinates=True))
    for k,coords in dual:
        actual=sum(values[j]*pow(root,j*k,prime) for j in range(g.size))%prime
        tensor=sum(values[j]*pow(root,sum(a*b*(g.size//s) for a,b,s in zip(digits,coords,g.moduli)),prime) for j,digits in forward)%prime
        need(actual==tensor,'complete modular DFT')
    # This mutation uses the input CRT permutation on the frequency side.
    bad=0
    for j,x in forward[:30]:
        for k,y in forward[:30]:
            bad+=(j*k-sum(a*b*(g.size//s) for a,b,s in zip(x,y,g.moduli)))%g.size!=0
    need(bad>0,'wrong dual convention must fail')
    rejected(lambda:grid.CRTGrid([9,15]))
    rejected(lambda:grid.CRTGrid([9,9]))
    rejected(lambda:grid.CRTGrid([2,3]))
    rejected(lambda:grid.CRTGrid([True,3]))
    rejected(lambda:grid.build(8,4,candidate_budget=0))
    rejected(lambda:grid.build(8,4,grid.Words(8)))
    rejected(lambda:grid.build(2,2))
    rejected(lambda:grid.build_squares(7,2))
    rejected(lambda:grid.CRTGrid([3,5]).from_coordinates([3,0]))
    return {'status':'PASS_NATIVE_COPRIME_GRID','new_kappa_claimed':False,
            'source_bound_band_fixtures':band_fixtures,'grid_fixtures':fixtures,'guaranteed_composite_fixtures':square_fixtures,'permutation_entries_each_direction':seen,
            'phase_checks':phase_checks,'sparse_convolution_cases':convolution_checks,
            'exact_modular_dft_outputs':g.size,'wrong_dual_witnesses':bad,
            'rejecting_controls':10,'scope':'exact reference algorithms; no full multiplier, native instruction trace or Lean audit'}

def main():
    manifest=HERE/'MANIFEST.json'
    if manifest.exists():
        for row in json.loads(manifest.read_text())['files']:
            data=(HERE/row['path']).read_bytes()
            need(len(data)==row['size'] and hashlib.sha256(data).hexdigest()==row['sha256'],'source drift: '+row['path'])
    result=check()
    expected=HERE/'RESULT.json'
    if expected.exists():need(result==json.loads(expected.read_text()),'receipt mismatch')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
