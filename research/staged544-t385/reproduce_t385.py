# SPDX-License-Identifier: Apache-2.0
# Copy-coloring and literal expansion adapt retained PR3605/T45 portable_expand.py
# and integral_network.py. This is not an independent third-party implementation.
"""Solver-free exact integer expansion of the fixed PR3734 T385 proof certificate.
All native supplier words remain unchanged; fresh owner/outer admission is separate.
"""
from pathlib import Path
from array import array
from collections import Counter,defaultdict
from fractions import Fraction as F
import sys,json,gzip,hashlib,time,argparse
if not __debug__ or sys.flags.optimize:raise RuntimeError('Enabled assertions required for exact replay')
P=Path(__file__).parent
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True,help='Authenticated PR3734 staged544-producer-return directory');ap.add_argument('--clock',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--network',type=Path,required=True,help='Retained integral_network.py');ap.add_argument('--out',type=Path,required=True);ap.add_argument('--bounded',type=int,default=0);args=ap.parse_args();start=time.monotonic();SRC=args.source.resolve()
 import importlib.util
 d=read(args.certificate)
 assert hashlib.sha256(args.network.read_bytes()).hexdigest()==d['integral_network_sha256'],'retained network digest'
 spec=importlib.util.spec_from_file_location('retained_integral_network',args.network);net=importlib.util.module_from_spec(spec);spec.loader.exec_module(net);net.INV=(26,2,18,53,96,213)
 for rel,digest in d['source_pins'].items():
  assert not Path(rel).is_absolute()and '..'not in Path(rel).parts,'relative source pin'
  assert hashlib.sha256((SRC/rel).read_bytes()).hexdigest()==digest,('source digest',rel)
 price={'S':d['S'],'profile':d['profile']};S=d['S'];T=77*S;assert d['baseT']==77 and S==5 and d['T']==T;G=d['groups'];order45=d['order'];W=d['widths'];clock_source=read(args.clock);assert hashlib.sha256(args.clock.read_bytes()).hexdigest()==d['clock_sha256'];assert clock_source['order']==order45 and clock_source['baseT']==77,'pinned macroclock';assert sorted(map(tuple,order45))==[(s,r)for s in range(9)for r in range(77)];assert all([s for s,r in order45 if r==o]==list(range(9))for o in range(77));xg=defaultdict(list);zg=defaultdict(list)
 for g,q,n in d['x']:
  assert type(n)is int and n>0;xg[g].append((q,n))
 for g,t,w,n in d['z']:
  assert type(n)is int and n>0;zg[g].append((t,w,n))
 taskwidth=array('B');taskbin=array('I');bingroup=array('H');required=array('b');macro=[array('I')for _ in order45];ranges=[]
 for gi,g in enumerate(G):
  first=len(bingroup);available=defaultdict(lambda:array('I'))
  for q,n in sorted(xg[gi]):
   widths=[w for w,c in zip(W,q)for _ in range(c)]
   for _ in range(n):
    b=len(bingroup);bingroup.append(gi);required.append(-1)
    for w in widths:i=len(taskwidth);taskwidth.append(w);taskbin.append(b);available[w].append(i)
  cursor=Counter()
  for t,w,n in sorted(zg[gi]):
   ids=available[w][cursor[w]:cursor[w]+n];assert len(ids)==n;macro[t].extend(ids);cursor[w]+=n
  assert all(cursor[w]==len(ids)for w,ids in available.items());assert len(bingroup)-first==g[3]*S;ranges.append((first,len(bingroup)))
 assert len(taskwidth)==693*S*408;print('BUILT',len(taskwidth),'tasks',len(bingroup),'bins',round(time.monotonic()-start,2),flush=True)
 actual=[array('I')for _ in range(693*S)];stats=Counter();gn={i:g[3]for i,g in enumerate(G)}
 chosen=list(range(693))if not args.bounded else sorted(set([0,692]+[int(i*692/max(1,args.bounded-1))for i in range(args.bounded)]))
 for t in chosen:
  colors,st=net.copy_colors(sorted(macro[t]),taskbin,taskwidth,bingroup,gn,S)
  for i,cp in colors.items():
   actual[S*t+cp].append(i);b=taskbin[i];gi=bingroup[b]
   if t==G[gi][2]:required[b]=max(required[b],cp)
  stats['flows']+=st['flows'];stats['max_nodes']=max(stats['max_nodes'],st['max_nodes']);stats['max_edges']=max(stats['max_edges'],st['max_edges'])
  if t%20==0 or args.bounded:print('COLORED',t,round(time.monotonic()-start,2),flush=True)
 if args.bounded:
  args.out.mkdir(parents=True,exist_ok=True);(args.out/'COPY-PREFLIGHT.json').write_text(json.dumps({'status':'PASS_BOUNDED_EXACT_COPY_COLORS','macrocalls':chosen,'S':S,'tasks':len(taskwidth),'stats':dict(stats),'seconds':time.monotonic()-start},indent=2)+'\n');return
 assert all(len(x)==408 for x in actual)
 template=read(SRC/'TEMPLATE.json.gz');plan=read(SRC/'PLAN.json.gz');children={c['child']:c['rank']for c in template['idle_children']};clock={tuple(v):i for i,v in enumerate(order45)};groups=defaultdict(list)
 for o in range(77):
  touched={};tm=None
  for ev in template['execution_schedule']:
   kind=ev['kind']
   if kind=='local_cover_sweep':tm=clock[ev['stage'],o];touched[next(x['pair']for x in template['recipe']if x['kind']=='local'and x['stage']==ev['stage'])]=tm
   elif kind=='bridge':touched[ev['src']]=tm;touched[ev['dst']]=tm
   elif kind=='idle_cover_sweep':
    for c in ev['child_indices']:
     if c in children:
      for port in range(112):groups[children[c],touched.get(ev['pair'],-1),tm].append((o,c,port))
 keys=sorted(groups);assert [[*k,len(groups[k])]for k in keys]==G
 owners=array('H',[0])*len(bingroup);childs=array('H',[0])*len(bingroup);ports=array('B',[0])*len(bingroup)
 for gi,(lo,hi)in enumerate(ranges):
  base=groups[keys[gi]];m=len(base)
  for j,b in enumerate(sorted(range(lo,hi),key=lambda b:(required[b],b),reverse=True)):
   cp=S-1-j//m;o,c,p=base[j%m];assert cp>=required[b];owners[b]=o+77*cp;childs[b]=c;ports[b]=p
 order=[[s,r+77*cp]for s,r in order45 for cp in range(S)];old_dispatch={tuple(x[:2]):x[2]for x in clock_source['dispatch']};assert all(pid==old_dispatch[s,r%77]for (s,r),pid in old_dispatch.items());dispatch=[[s,r,old_dispatch[s,r%77]]for s,r in order]
 widths={};pids={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=read(SRC/f'NATIVE-{tag}.json.gz');widths[pid]=[len(w['frames'][w['final'][r]])-len(w['frames'][w['start'][r]])for r in range(224,632)];assert Counter(widths[pid])==dict(zip(W,net.INV))
 out=args.out;out.mkdir(parents=True,exist_ok=False)
 for name,obj in [('ORDER.json',order),('DISPATCH.json',dispatch),('PROFILE.json',price['profile'])]:(out/name).write_text(json.dumps(obj,separators=(',',':'))+'\n')
 offsets=array('B',[0])*len(bingroup);families={c:2*plan['pairs'][str(c)]+plan['sides'][str(c)]for c in children};rolecount=0
 with gzip.open(out/'FILL.json.gz','wt',compresslevel=1)as f:
  f.write('{"columns":["time","helper","owner_replica","child","port","offset"],"dispatch_overrides":[],"rows":[')
  for t,tasks in enumerate(actual):
   pool=defaultdict(list);pid=dispatch[t][2]
   for h,w in enumerate(widths[pid]):pool[w].append(h)
   rows=[];usedfamilies=set()
   for i in sorted(tasks,key=lambda i:(taskwidth[i],i)):
    w=taskwidth[i];h=pool[w].pop();b=taskbin[i];gi=bingroup[b];o=owners[b];c=childs[b];p=ports[b];z=offsets[b];offsets[b]+=w;cap,lo,hi,_=G[gi];cp=o//77
    assert (-1 if lo==-1 else S*lo+cp)<t<=S*hi+cp;assert offsets[b]<=cap
    fam=(o,families[c],p);assert fam not in usedfamilies;usedfamilies.add(fam);rows.append([t,h,o,c,p,z])
   assert not any(pool.values())
   for row in sorted(rows,key=lambda r:r[1]):f.write((','if rolecount else '')+json.dumps(row,separators=(',',':')));rolecount+=1
  f.write(']}\n')
 idle=Counter()
 for b,gi in enumerate(bingroup):
  r=G[gi][0]-offsets[b]
  if r:idle[r]+=1
 profile=Counter({int(k):v*693*S for k,v in d['local_profile'].items()});profile.update(idle);assert dict(profile)=={int(k):v for k,v in price['profile'].items()};assert rolecount==693*S*408
 report={'status':'PASS_EXACT_INTEGER_NETWORK_LITERAL_EXPANSION','replicas':T,'S':S,'roles':rolecount,'physical':896*T+509,'profile':dict(profile),'copy_flow_stats':dict(stats),'seconds':time.monotonic()-start,'scope':'Actual newly generated literalFILL, exact copycirculations, ownerwindows, sharedfamilyuniqueness, prefixcapacity, completeidle invoice checked duringstream. Independent retainedowner and fullouter release stillrequired.','pins':{str(q):hashlib.sha256(q.read_bytes()).hexdigest()for q in[Path(__file__),Path(net.__file__),args.certificate,SRC/'ORDER.json',SRC/'TEMPLATE.json.gz',SRC/'PLAN.json.gz',SRC/'DISPATCH.json',SRC/'NATIVE-base.json.gz',SRC/'NATIVE-extra.json.gz',out/'FILL.json.gz']}}
 (out/'EXPANSION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],rolecount,round(time.monotonic()-start,2),flush=True)
if __name__=='__main__':main()
