#!/usr/bin/env python3
"""Source-bound exact PR6030 specialization; DLamdata with Codex, Apache-2.0.

No source implementation is imported. Infinite claims are proved in PROOF.md;
these checks certify source bindings, rational substitutions and finite controls.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = 'research/p104-helper470-twin-rung-removal/RESULT.json'
MANIFEST = 'certificates/frontier6030-source.json'
SELECTED_SOURCES = (
    RESULT,
    'research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md',
    'research/kappa-rebuild/transfer-audit/FINITE-TEMPLATE-CLOSURE.md',
    'research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md',
    'research/kappa-observation-integration/release-work/current/package/vendor/pr1673/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md',
    'notes/batched-complex-rows.tex',
    'research/query-thinned-controllers/PROOF.md',
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def reject(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('control accepted: ' + label)


def certify(p, H, atom):
    U,b,a,q,eta = (p[k] for k in ('complex_uniform_saving','b','a','q','stop'))
    sigma,tau,l = 1-b,1-a,1-q
    gamma = sigma+eta*b
    require(0 < sigma < tau < l < 1, 'internal order')
    require(F(1,2) < l, 'phase bound uses l>1/2')
    require(0 < eta < 1 and gamma < tau, 'leaf order')
    require(U>b and H>0, 'compiler gap')
    require(0 < atom < F(1,2), 'stock exponent range for log cubed bound')
    require(atom==F(1,250), 'current atom binding')
    require(p['lambda_prime']==l, 'lambda prime binding')
    out = {
        'sigma_moment_negative_binary_exponent': H*(U-b),
        'tau_moment_negative_binary_exponent': H*(U-a),
        'tau_minus_sigma': tau-sigma,
        'lambda_prime_minus_tau': l-tau,
        'tau_minus_leaf': tau-gamma,
        'lambda_prime_minus_leaf': l-gamma,
        'stock_threshold_power': 1/(1-atom),
        'stock_threshold_log_degree': 3/(1-atom),
    }
    require(out['sigma_moment_negative_binary_exponent']==47005, 'sigma source exponent')
    require(out['tau_moment_negative_binary_exponent']==94010, 'tau source exponent')
    return out


def threshold_exponent(C,L,M):
    """2^t is a safe integer upper envelope of PROOF (4), no float roots."""
    require(all(isinstance(x,int) and x>=1 for x in (C,L,M)), 'threshold domain')
    k=(192*C*L**3).bit_length()
    return max(4,M.bit_length(),2*(192*C).bit_length(),(250*k+248)//249)


def threshold_witness(C,L,M,h):
    require(h>=max(16,M,(192*C)**2), 'logarithmic/base reserve budget')
    require(h**249 >= (192*C*L**3)**250, 'current stock reserve budget')


def main():
    sources=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    pins={x['path']:x for x in sources['files']}
    count=0
    for row in sources['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest()==row['sha256'], 'source hash: '+row['path'])
            count+=1
    manifest=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))['files']
    for path in SELECTED_SOURCES:
        require(manifest.get(path)==pins[path]['sha256'], 'selected manifest binding: '+path)
    raw=json.loads((ROOT/RESULT).read_text(encoding='utf-8'))['complete_cost']
    p={k:F(v) for k,v in raw['outer']['parameters'].items()}
    H=raw['compiler']['H'];atom=F(raw['ordinary_BIT']['atom'])
    require(raw['compiler']['N']==f'2^{H}', 'compressed rank binding')
    require(F(raw['compiler']['uniform_saving'])==p['complex_uniform_saving'], 'compiler saving binding')
    require(raw['compiler']['word_materialized'] is False, 'materialization status')
    exact=certify(p,H,atom)
    require(exact['tau_minus_leaf']==F(6978119347,9800000000000000000), 'leaf certificate')
    require(exact['lambda_prime_minus_leaf']==F(13978119347,9800000000000000000), 'target certificate')
    # Bind the precise selected legacy-to-uniform contract, not just filenames.
    fragments={
        SELECTED_SOURCES[1]: ['Every rank-one leaf becomes the ordinary rank-`f` child.'],
        SELECTED_SOURCES[2]: ['P < W*N^z','exactly `1/W` of its parent','Pad complete rows once'],
        SELECTED_SOURCES[3]: ['q0(h,p) <= C*(log2 h + h^0.003*(log2 p)^3 + 1)', 'prevents an accumulating factor of two per phase'],
        SELECTED_SOURCES[4]: ['do not first apply C','K=128G does not satisfy that literal condition'],
        SELECTED_SOURCES[5]: ['1-c,0','W^{-j}'],
        SELECTED_SOURCES[6]: ['Change the atom power to delta=0.004','digits remain O(w log e)=o(e)'],
    }
    for path, words in fragments.items():
        text=(ROOT/path).read_text(encoding='utf-8')
        for word in words:require(word in text, 'source statement: '+word)
    controls=[]
    for key,value,name in [
        ('complex_uniform_saving',p['b'],'closed uniform gap'),
        ('q',p['a'],'closed internal margin'),
        ('stop',F(1),'linear leaf cost'),
        ('stop',F(0),'invalid stopping endpoint'),
    ]:
        controls.append(reject(lambda k=key,v=value:certify(dict(p,**{k:v}),H,atom),name))
    controls.append(reject(lambda:certify(p,H-1,atom),'changed rank exponent'))
    controls.append(reject(lambda:certify(p,H,F(3,1000)),'stale BIT atom'))
    controls.append(reject(lambda:certify(p,H,F(1)),'linear stock'))
    witnesses=[]
    for C in (1,2,17,1000):
        for L in (1,2,20,100):
            for M in (1,16,10**6):
                t=threshold_exponent(C,L,M);h=1<<t
                threshold_witness(C,L,M,h)
                # At a power of two the log term is exact; separately certify
                # each sufficient inequality used for all larger real h.
                require(C*(t+1)<=F(h,96), 'exact log budget fixture')
                require(F(3,128)+F(1,64)==F(5,128)<F(1,16), 'reservation fraction')
                witnesses.append({'C':C,'L':L,'M':M,'binary_exponent':t})
    controls.append(reject(lambda:threshold_witness(1,100,1,192**2),'insufficient stock threshold'))
    controls.append(reject(lambda:threshold_witness(1,1,10**6,192**2),'missing finite base threshold'))
    # A uniform N=16, P/W=2 fixture: compare squared sigma-mass,
    # sigma=1/2, against mu_sigma^2*e = e/4. Ceiling fails at e=17.
    def child_mass(child):
        require(4*child<=F(17,4), 'floor potential inequality')
    child_mass(17//16)
    controls.append(reject(lambda:child_mass((17+15)//16),'ceiling violates uniform potential'))

    def padded(n,Q):
        require(1<=Q<=n, 'row stock available')
        return ((n+Q-1)//Q)*Q
    padding_cases=0
    for n in range(1,33):
        for Q in range(1,n+1):
            new=padded(n,Q)
            require(n<=new<2*n and new%Q==0, 'whole row padding')
            # An arbitrary original row payload survives identity return;
            # every appended row is identically zero and can be deleted.
            rows=list(range(1,n+1))+[0]*(new-n)
            require(rows[:n]==list(range(1,n+1)) and all(x==0 for x in rows[n:]), 'completed identity return')
            padding_cases+=1
    def phase_volume(v): require(v<2*5,'single-phase volume factor')
    phase_volume(padded(5,4))
    controls.append(reject(lambda:phase_volume(padded(padded(5,4),7)),'padding retained across phases'))
    # Explicit wrong endpoint adds an original row to an appended row.
    def delete_padding(rows,n):
        require(all(x==0 for x in rows[n:]),'padding endpoint is not zero')
        return rows[:n]
    rows=[3,5,7,0]
    require(delete_padding(rows,3)==[3,5,7],'zero padding deletion control')
    rows[3]+=rows[0]
    controls.append(reject(lambda:delete_padding(rows,3),'nonidentity row endpoint'))
    result={
        'status':'PASS_PR6030_DEFERRED_LAYER',
        'source_inputs':count,'selected_manifest_bindings':len(SELECTED_SOURCES),
        'exact':{k:str(v) for k,v in exact.items()},
        'threshold_fixtures':len(witnesses),'padding_fixtures':padding_cases,'rejected_controls':controls,
        'scope':'Conditional source-bound cost specialization; no physical or compiler admission.',
    }
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
