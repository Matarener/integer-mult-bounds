"""Independent exact arithmetic and complete conditional transfer ledger.

Apache-2.0; substantial OpenAI Codex assistance. Reuses credited PR3342
outward interval engine; integer-root enclosures are independent.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r437_intervals',HERE/'sources/intervals.py')
intervals=importlib.util.module_from_spec(spec); spec.loader.exec_module(intervals)
OLD={1:381024,2:400416,3:22752,4:26880,5:29376,6:17376,7:26784,42:288}
NEW={1:380160,2:400864,3:22176,4:26592,5:29376,6:17376,7:26496,34:64,42:352}
T360={1:7980120,2:2345760,3:755730,4:330480,5:69930,8:25920,48:137790}
C=F(1,576); A=C*(1-C); B=10**6
COMPARATOR=F('0.001730418899766071163804')-F(1,10**46)-F(1,10**70)


def need(ok,message):
    if not ok: raise ValueError(message)


def power(rank,dimension,saving,bits=140):
    t=1-saving; n,d=t.numerator,t.denominator; scale=1<<bits
    target=rank**n*scale**d; divisor=dimension**n; lo,hi=0,scale
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**d*divisor<=target:lo=mid
        else:hi=mid
    need(lo**d*divisor<=target<hi**d*divisor,'integer power enclosure')
    return F(lo,scale),F(hi,scale)


def direct(hist,saving):
    lo=hi=F(0)
    for rank,count in hist.items():
        a,b=power(rank,64,saving); lo+=count*a;hi+=count*b
    fallback=F(32*64**2*sum(hist.values()),10**16)
    a,b=power(1,64,saving)
    return (lo+fallback*a)/28416,(hi+fallback*b)/28416


def display(bound,digits=28):
    lo,hi=bound; scale=10**digits
    return [lo.numerator*scale//lo.denominator,-(-hi.numerator*scale//hi.denominator),scale]


def run():
    expected=json.loads((HERE/'sources/r437/EXPECTED.json').read_bytes())
    need(NEW=={int(r):n for r,n in expected['profile'].items()},'actual source profile')
    results={}
    for label,hist in [('old',OLD),('R437',NEW)]:
        integer=direct(hist,C); series=intervals.moment(hist,64,28416,C,True)
        need(max(integer[0],series[0])<=min(integer[1],series[1]),'two engine intersection')
        need(display(integer)==display(series),'same exact decimal enclosure')
        results[label]={'complete_mu':display(integer),'E':sum(hist.values()),
                        'F':32*64**2*sum(hist.values())}
    need(direct(OLD,C)[0]>1>direct(NEW,C)[1],'old FAIL and R437 PASS')
    mu1=F(sum(r*n for r,n in NEW.items()),64*28416)+F(32*64*sum(NEW.values()),10**16*28416)
    mu=direct(NEW,C)
    need(200*(1-mu1)>1 and B*(1-mu[1])>1,'complete finite majorants')
    need(F(17,10000)<C<F(1,512) and C<F(expected['BIT_c']),'history and BIT premise')
    need(17**128>32*16**128 and 696575<2**20,'eventual original-width stock fit')
    wrapper=33584+F(17,4)*B
    need(wrapper==4283584,'both padded C0 calls and complete wrapper bill')
    strict=json.loads((HERE/'sources/t360-STRICT-RESULT.json').read_bytes())['independent']
    release=json.loads((HERE/'sources/t360-RESULT.json').read_bytes())
    invoice=json.loads((HERE/'sources/t360-PREFIX-AND-INVOICE.json').read_bytes())
    need({int(r):n for r,n in strict['profile'].items()}==T360
         and {int(r):n for r,n in release['profile'].items()}==T360,'same actual T360 profile')
    need((strict['live'],strict['physical'],strict['calls'],strict['roles'])
         ==(322560,323069,3240,1321920),'complete T360 source stock and controller')
    need(F(release['kappa'])==COMPARATOR,'exact strongest compatible public comparator')
    need((invoice['global_prefix_bits'],invoice['charged_prefix_bits'],
          invoice['finite']['physical_row_coefficient'])==(1478,2048,19549),'same complete finite invoice')
    sigma=F('0.9982695812'); eta=F(1,10**6); alpha=F('0.998269582931'); tau=1-A
    moment=intervals.moment(T360,73,322560,1-sigma,False)
    need(moment[1]<1 and tau<sigma,'T360 complete moment and stronger ordinary')
    internal=sigma-eta*(sigma-tau); leaf=sigma+eta*(1-sigma)
    need(max(internal,leaf,F(499,500))<alpha,'prospective stopped-tree powers')
    synthetic=F(997,1000)*min(1-alpha,A)
    need(synthetic<COMPARATOR<A,'ordinary gain is not outer multiplication gain')
    # Source-relative limitation in this fixed normalized T360 profile.
    fail=intervals.moment(T360,73,322560,F('0.001730418899766071163805'),False)
    need(fail[0]>1,'next T360 root grid point still fails after R437')
    return {'status':'PASS_R437_COMPLETE_RECURRENCE_AND_FIXED_T360_LEDGER',
      'c':str(C),'ordinary_saving':str(A),'ordinary_gain_over_public_comparator':str(A-COMPARATOR),
      'mu':results,'mu1':str(mu1),'C0_majorant':{'linear':200,'power':B},
      'ordinary_complete_coefficient':int(wrapper),'fit_from':2**20,
      'stock':'[269241600*|GL64(Fq)|*q^(4096(w-1))]^D(e), D(e)=1+D(42 floor(e/64)) above cutoff64',
      'T360':{'profile':T360,'live':322560,'physical':323069,'sigma':str(sigma),
               'moment':display(moment),'tau':str(tau),'internal_power':str(internal),
               'leaf_power':str(leaf),'alpha':str(alpha),'uniform_height':'UNRESOLVED',
               'physical_stock':'323069*|O(73,2)|','online_precision':'P+2*B_T*g+3; B_T unresolved',
               'fixed_root_next_grid_mu':display(fail)},
      'synthetic_two_term_saving_ceiling_for_chosen_alpha':str(synthetic),
      'public_comparator':str(COMPARATOR),'multiplication_kappa_claim':None,
      'scope':'Exact substituted recurrence and prospective full two-term transfer. New physical supplier/all-size join unproved.'}


if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
