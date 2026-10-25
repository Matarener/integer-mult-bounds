"""Rational certificate for the complete mixed profile; inherited enclosure engine.

Cinna Davis with OpenAI Codex assistance, Apache-2.0. PR3945/4076
logarithm and exponential interval arithmetic is imported unchanged.
"""
from fractions import Fraction as Q
import json,sys
from verify import P,read,need,pins,reject
from vendor import exact_root as E

def main():
    pins();r=read(P/'RESULT.json');profile={int(k):n for k,n in r['profile'].items()}
    lower,upper=Q(r['root_lower']),Q(r['root_upper'])
    ml,mh=E.certify_bracket(profile,lower,upper)
    need([list(map(str,x)) for x in [ml,mh]]==[r['lower_moment_interval'],r['upper_moment_interval']],'recorded rational signs')
    predecessor={int(k):n for k,n in read(P/'owner/PR4085-PROFILE.json').items()}
    pl,pu=Q(r['predecessor_lower']),Q(r['predecessor_upper'])
    E.certify_bracket(predecessor,pl,pu)
    claim=read(P/'inputs/PR4085-CLAIM.json')['complex_supplier']
    need(claim['profile']=={str(k):v for k,v in predecessor.items()} and Q(claim['lower'])==pl and Q(claim['upper'])==pu,'pinned PR4085 price')
    need(pl==Q('.001730970419199163702738') and pu==Q('.001730970419199163702739'),'PR4085 predecessor bracket')
    endpoint=lower-Q(1,10**46)-Q(1,10**70)
    need(Q(r['conditional_kappa'])==endpoint and endpoint>pu,'strict conditional improvement')
    need(Q(r['gain_lower_bound'])==endpoint-pu,'gain lower bound')
    need(E.moment(E.signed(profile),endpoint)[1]<0,'padded endpoint')
    prior=read(P/'inputs/PR4088-FIRST-RESULT.json')
    prior_profile={int(k):v for k,v in prior['profile'].items()}
    E.certify_bracket(prior_profile,Q(prior['root_lower']),Q(prior['root_upper']))
    need(Q(r['previous_revision_upper'])==Q(prior['root_upper']),'previous revision bracket')
    need(endpoint>Q(prior['root_upper']) and Q(r['gain_over_previous_revision'])==endpoint-Q(prior['root_upper']),'strict selector improvement')
    need(sum(k*v for k,v in profile.items())==65088*360,'profile mass')
    out=[]
    if '--controls' in sys.argv:
        bad=dict(profile);bad[1]+=1
        out.append(reject('unpaid_extra_rank1',lambda:E.certify_bracket(bad,lower,upper)))
        out.append(reject('old_fill_at_new_root',lambda:E.certify_bracket(predecessor,lower,upper)))
        out.append(reject('unsupported_endpoint',lambda:E.certify_bracket(profile,lower+Q(1,10**12),upper+Q(1,10**12))))
    print(json.dumps({'status':'PASS_MIXED_EXACT_ROOT','root_bracket':[r['root_lower_decimal'],r['root_upper_decimal']],'conditional_kappa':str(endpoint),'gain_lower_bound':r['gain_lower_bound'],'gain_over_previous_revision':r['gain_over_previous_revision'],'controls':out},sort_keys=True))
if __name__=='__main__':main()
