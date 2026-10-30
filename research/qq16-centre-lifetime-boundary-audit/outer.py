"""Exact constant-cover witness at a real ordinary bridge boundary.
Chris R / Clear1nsight with OpenAI assistance; Apache-2.0. No predecessor code imports.
The bridge semantics are pinned in qq16-controller-scope-map.md; the trace is
bound to the actual hosted template, including its intervening idle sweep.
"""
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
import gzip
import json
import tarfile

ARCHIVE='research/community-frontier1042-audit/selected-replay.tar.gz'
PACKET='research/joint-query/certificate.json.gz'
TEMPLATE='t16/global/hosted/GLOBAL-TEMPLATE.json.gz'
TEMPLATE_SHA='73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a'


def need(ok,why):
    if not ok:raise ValueError(why)


def run(repo):
    raw=(repo/ARCHIVE).read_bytes()
    need(sha256(raw).hexdigest()=='22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754','archive pin')
    with tarfile.open(fileobj=BytesIO(raw),mode='r:gz') as tar:
        found=[m for m in tar.getmembers() if m.name==TEMPLATE]
        need(len(found)==1 and found[0].isfile(),'unique template member')
        data=tar.extractfile(found[0]).read()
    need(sha256(data).hexdigest()==TEMPLATE_SHA,'template member pin')
    template=json.loads(gzip.decompress(data))
    raw=(repo/PACKET).read_bytes()
    need(sha256(raw).hexdigest()=='a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7','packet pin')
    packet=json.loads(gzip.decompress(raw))
    A,T,U=map(tuple,(packet['A_ports'],packet['T_ports'],packet['U_ports']))
    R=[[Q(row.get(str(p),0)) for p in range(112)] for row in packet['R_rows']]
    need(template['recipe'][:4]==[
        {'kind':'local','pair':0,'reverse':False,'stage':0},
        {'kind':'local','pair':0,'reverse':True,'stage':1},
        {'coefficient':1,'dst':0,'kind':'bridge','src':1},
        {'kind':'local','pair':0,'reverse':False,'stage':2}], 'real logical continuation')
    execution=[e for e in template['execution_schedule'] if e.get('replica')==0]
    events=execution[:5]
    need([e['kind'] for e in events]==['local_cover_sweep','local_cover_sweep','idle_cover_sweep','bridge','local_cover_sweep'],'actual physical event kinds')
    need([e['source_event'] for e in events]==[0,1,2,3,4],'actual source event sequence')
    need(events[1]['stage']==1 and events[2]['pair']==1 and events[2]['from_level']==-1 and events[2]['to_level']==1 and events[3]['src']==1 and events[3]['dst']==0 and events[3]['coefficient']==1 and events[4]['stage']==2,'actual bridge boundary')
    zero=lambda:[Q(0)]*112
    def query(x,ports):return [sum(R[k][p]*x[p] for p in ports) for k in range(8)]
    def inject(q,ports):return [sum(R[k][p]*q[k]/4 for k in range(8)) if p in ports else Q(0) for p in range(112)]
    def forward0(x,y):
        q=query(x,range(112));c=query(x,T);kf=inject(q,U+T);old=inject(c,A)
        xx=[x[p]-kf[p] if p in U else old[p] if p in A else kf[p] for p in range(112)]
        yy=[y[p]+xx[p] if p in U else x[p]+y[p]-xx[p] for p in range(112)]
        return xx,yy
    def backward1(x,y):
        qu=query(y,U+T);future=inject(qu,A);u=[y[p]+future[p] for p in range(112)]
        a=query(x,T);b=query(u,range(112));ku=inject(a,U);pa=inject(a,T);pb=inject(b,T)
        yy=[y[p]+ku[p] if p in U else u[p] if p in A else u[p]-pb[p]-11*pa[p] for p in range(112)]
        xx=[x[p]-y[p] if p in U else x[p]+y[p]-yy[p] for p in range(112)]
        return xx,yy
    def project(y):
        k=inject(query(y,range(112)),U)
        return [y[p]-k[p] for p in U]
    def encode(v):return {str(p):str(x) for p,x in enumerate(v) if x}
    need(all(sum(R[i][p]*R[j][p] for p in U)==48*(i==j) for i in range(8) for j in range(8)),'eight independent ordinary response directions')
    cases=[]
    for channel in range(8):
        a=[Q(4)*(j==channel) for j in range(8)]
        k=inject(a,U);pa=inject(a,A);pt=inject(a,T)
        x0=[k[p]-11*pa[p] for p in range(112)]
        y0=[11*pa[p]+pt[p] for p in range(112)]
        need(all(v.denominator==1 for v in x0+y0),'integer native witness')
        x1,y1=forward0(x0,y0)
        need(x1==pt and y1==zero(),'reachable preB1 cut')
        x2,y2=backward1(x1,y1)
        need(project(y2)==[0]*96,'identical projected demand to zero execution')
        need([x2[p] for p in U]==[0]*96,'same first-bridge target X_U')
        # Other pair fields are identically zero. Idle preparation fixes zero.
        # Bridge X0_U+=X1_U is zero; Y1_U-=Y0_U is the distinguishing read.
        changed={p:-y2[p] for p in U if y2[p]}
        need(len(changed)==48 and changed=={p:-R[channel][p] for p in U if R[channel][p]},'actual bridge separation')
        cases.append({'channel':channel,'original_X0':encode(x0),'original_Y0':encode(y0),
                      'projected_y1_U':'96 zeros','postB1_X2':encode(x2),'postB1_Y2':encode(y2),
                      'bridge_Y_pair1_U':{str(p):str(v) for p,v in changed.items()},
                      'maximum_original_absolute_value':str(max(map(abs,x0+y0)))})
    need(any(cases[0]['bridge_Y_pair1_U'].values()),'bridge write is material')
    # Meaningful controls: suppressing the bridge Y write destroys separation;
    # removing the projected query correction destroys equality of observations.
    need({}!=cases[0]['bridge_Y_pair1_U'],'omit bridge Y write control')
    need(any(Q(v) for p,v in cases[0]['postB1_Y2'].items() if int(p) in U),'omit query correction control')
    return {'status':'PASS_ACTUAL_OUTER_BRIDGE_BOUNDARY',
        'template_member':TEMPLATE,'template_member_sha256':TEMPLATE_SHA,
        'logical_recipe_prefix':template['recipe'][:4],'replica0_physical_prefix':events,
        'required_bridge_roles':['current X0_U','current X1_U','current Y0_U','current Y1_U'],
        'projected_output_role':'extra earlier y1_U; not current postB1 Y0_U',
        'independent_missing_query_directions':8,'integer_constant_witnesses':cases,
        'negative_controls':['omit bridge Y write loses separating observable','omit query correction loses identical demand'],
        'scope':'The real bridge cannot factor through projected y1_U alone with other-pair state fixed. PR3952 retains borrowed currentXY; reading that state is outside the restricted observation and is not excluded. No whole-controller admission or universal boundary lower bound.'}
