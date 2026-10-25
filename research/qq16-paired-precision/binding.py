"""Literal binding for the conditional fixed-grid reassociation theorem.
Chris R / Clear1nsight with OpenAI assistance. Apache-2.0.
No native implementation or predecessor executable is invoked.
"""
import hashlib,json
QUERY=['Z1','Z2','Z3','Z4','Z5','Z6','Z8','Z9']
def need(ok,why):
 if not ok:raise ValueError(why)
def digest(obj):return hashlib.sha256(json.dumps(obj,separators=(',',':')).encode()).hexdigest()
def cut(word):
 start=word.index(['clear','Z1','query2'])
 response=word.index(['clear','Z10','query2'],start+8)
 restore=word.index(['clear','Z1','current'],response)
 return start,response,restore

def sources(word,start,response):
 captured={}
 for i in range(start,response):
  e=word[i]
  if e[0]=='line':
   _,name,p,sign=e
   expected=[['clear',name,'current'],['add',name,'W'+str(p),'1'],['map',name,2,p,False],['line',name,p,-1]]
   need(sign==-1 and word[i-3:i+1]==expected,'source normalization recipe')
   need(p not in captured,'source acquired twice')
   captured[p]=[v[0:1]+['TEMP']+v[2:] for v in expected]
  need(not(e[0] in ('clear','add','line','map') and e[1].startswith(('X','Y','W'))),'query changes captured source/borrowed value')
 need(len(captured)==104,'all104 actual normalized sources')
 return captured

def audit(baseline,candidate):
 bs,br,bt=cut(baseline);cs,cr,ct=cut(candidate)
 definition=[['clear','Z11','current'],['add','Z11','X11','1']]
 idx=baseline.index(definition[0]);need(baseline[idx:idx+2]==definition and idx+2<=bs,'tenth definition prefix')
 oldprefix=baseline[:idx]+baseline[idx+2:bs]
 need(oldprefix==candidate[:cs],'prefix differs beyond tenth deferral')
 oldsources=sources(baseline,bs,br);newsources=sources(candidate,cs,cr)
 need(oldsources==newsources,'normalized source tags differ')
 need(baseline[br:bt]==candidate[cr:ct],'response arithmetic differs')
 olddefinitions=sum(([['clear',n,'current'],['add',n,'X'+n[1:],'1']] for n in QUERY+['Z10']),[])
 newdefinitions=olddefinitions+definition
 need(baseline[bt:bt+18]==olddefinitions,'nine baseline output definitions')
 need(candidate[ct:ct+20]==newdefinitions,'ten paid candidate output definitions')
 need(baseline[bt+18:]==candidate[ct+20:],'preserved suffix differs')
 # The old tenth host has no numerical consumer before its preserved suffix;
 # otherwise delaying the original copy would need another proof.
 refs=[i for i,e in enumerate(baseline[:bt+18]) if 'Z11' in e[1:3]]
 need(refs==[idx,idx+1],'tenth host live before suffix')
 return {'baseline_cuts':[bs,br,bt],'candidate_cuts':[cs,cr,ct],
         'captured_ports':sorted(oldsources),'captured_recipe_sha256':digest(oldsources),
         'response_sha256':digest(baseline[br:bt]),'suffix_sha256':digest(baseline[bt+18:]),
         'paid_output_definitions':[9,10],
         'premises':'All callbacks same common q/format, bank-independent and deterministic with isolated scratch; exact changed unitADDs and nooverflow. Query integer coefficient identity separately checked on all104 source basis vectors.',
         'conclusion':'Captured normalized values, completed queries, response and final suffix outputs have identical bits under the stated fixed-grid premises; no accuracy or actual native-supplier contract inferred.'}
