// k2grow.inc -- BLOCKGROW lane (toolkit/module docstring): extra k2net moves.  Included by k2search.inc under #ifdef K2GROW (build with -DK2GROW), after Index/Edit/applyEdit/planDeliver/coloc.
// Every proposal is an Edit (rem + ins) that goes through the same cleanup+verify as the original 9 moves, so exactness/legality is by verification.
//  hubsw  (type 9)  JUNK-INSENSITIVE bracket retarget: all ADDs (d += c*h) of one dest d from one helper h are switched to ANOTHER register g whose X/Y-part (fingerprint with every helper
//                   symbol zeroed) equals h's at each read, coefficients c' = c/mu solved exactly.  This is the "merge sibling crossings onto one hub": g's reader set grows by d, h loses it.
//                   (the ordinary `ret` fingerprints include the helper's own junk symbol and can never find g)
//  relab  (type 10) cluster frame substitution: the connected set of stops/events rendezvousing at one frame (closure over co-located ADD partners) is re-hosted at another frame G with
//                   prev<G<next in every member chain.  Content-neutral; changes dims (R0) when G has another dim, geometry (ports/Ys at the frame) when not.
//  lift   (type 11) dual rung insert: d and s both rise f->G (G strictly above f, below both next stops) before event i; i and any later d<->s events of the stop go to G.
#include <unordered_set>
struct GIdx{ vector<vector<V3>> xv; unordered_map<u64,vector<pair<int,int>>> HX; };
static GIdx GI; static bool GDIRTY=true; static long GN=-1; static int GXMODE=0;
static V3 V0Xof(int r){ V3 z={0,0,0}; return (ROLE[r]=='X'||ROLE[r]=='Y')? V0[r] : z; }
static u64 xkey(const V3&v){ if(v[0]) return mmul(v[1],minv(v[0])); return v[1]? (0x5bd1e995ULL^mmul(v[2],minv(v[1]))) : 0x9e3779b9ULL; }
static void buildGI(const State&S,const Index&I){
  int NR=S.init.size(); GI.xv.assign(NR,{}); GI.HX.clear(); vector<V3> val(NR); for(int r=0;r<NR;r++) val[r]=V0Xof(r);
  for(int r=0;r<NR;r++) if(ROLE[r]=='O') val[r]={0,0,0};
  auto closeVer=[&](int r){ GI.xv[r].push_back(val[r]); };
  for(size_t i=0;i<S.P.size();i++){ const Ev&e=S.P[i]; int d=e.d;
    switch(e.k){
      case 'I': case 'X': closeVer(d); val[d]={0,0,0}; break;
      case 'S': { closeVer(d); u64 q=coMod(e.c); for(auto&x:val[d]) x=mmul(x,q); break; }
      case 'A': case 'C': { closeVer(d); u64 q=coMod(e.c); const V3 sv=val[e.s]; if(e.k=='C'){ for(int k=0;k<KV;k++) val[d][k]=mmul(q,sv[k]); } else for(int k=0;k<KV;k++) val[d][k]=madd(val[d][k],mmul(q,sv[k])); break; }
      default: break; } }
  for(int r=0;r<NR;r++) closeVer(r);
  for(int r=0;r<NR;r++){ if(GI.xv[r].size()!=I.VR[r].size()){ fprintf(stderr,"GI misaligned reg %d %zu vs %zu\n",r,GI.xv[r].size(),I.VR[r].size()); abort(); }
    for(int k=0;k<(int)GI.xv[r].size();k++){ const V3&v=GI.xv[r][k]; if(vzero(v)) continue; GI.HX[xkey(v)].push_back({r,k}); } }
  GDIRTY=false; GN=S.P.size();
}
static void ensureGI(const State&S,const Index&I){ if(GDIRTY||GN!=(long)S.P.size()) buildGI(S,I); }
// ratio mu with x = mu*y (both nonzero, assumed projectively equal): via first nonzero coordinate
static bool xratio(const V3&x,const V3&y,Co*mu){ int c=-1; for(int k=0;k<KV;k++) if(y[k]){ c=k; break; } if(c<0||!x[c]) return false; u64 m=mmul(x[c],minv(y[c])); for(int k=0;k<KV;k++) if(mmul(y[k],m)!=x[k]) return false;
  auto dy=DY.find(m); if(dy==DY.end()) return false; *mu=dy->second; return true; }
static bool coDiv(Co a,Co b,Co*o){ if(!b.n) return false; if(a.n%b.n) return false; *o=coNorm(a.n/b.n,a.e-b.e); return true; }
static bool mvHubSwitchP(const Index&I,const State&S,Edit&E,bool peel);
static bool mvHubSwitch(const Index&I,const State&S,Edit&E){ return mvHubSwitchP(I,S,E,false); }
static bool mvHubPeel(const Index&I,const State&S,Edit&E){ return mvHubSwitchP(I,S,E,true); }
static bool hubBracket(const Index&I,const State&S,int d,int h,bool peel,Edit&E){
  if(ROLE[h]!='H'||ROLE[d]=='O') return false;
  vector<int> K; for(int j:I.TOUCH[d]) if(S.P[j].k=='A'&&S.P[j].d==d&&S.P[j].s==h) K.push_back(j); if(K.empty()||K.size()>20) return false;
  // pivot: a read with nonzero X/Y part (mid-dim reads); zero-part reads follow
  int piv=-1; for(int j:K){ int vs=verAt(I,h,j); if(vs>=0&&!vzero(GI.xv[h][vs])){ piv=j; break; } } if(piv<0) return false;
  int vp=verAt(I,h,piv); auto f=GI.HX.find(xkey(GI.xv[h][vp])); if(f==GI.HX.end()) return false;
  vector<int> gs; for(auto&rv:f->second){ int g=rv.first; if(g==h||g==d||ROLE[g]=='O') continue; if(find(gs.begin(),gs.end(),g)==gs.end()) gs.push_back(g); }
  if(gs.empty()) return false; int g=gs[rnd(gs.size())];
  Co mu0={1,0}; bool haveMu=false; vector<Excl> ex;
  // process nonzero reads first so mu0 is known, then the zero (junk) reads
  vector<int> ord; for(int j:K){ int vs=verAt(I,h,j); if(vs>=0&&!vzero(GI.xv[h][vs])) ord.push_back(j); } for(int j:K){ int vs=verAt(I,h,j); if(vs<0||vzero(GI.xv[h][vs])) ord.push_back(j); }
  for(int j:ord){ const Ev&e=S.P[j]; int vs=verAt(I,h,j); if(vs<0) return false; const V3&xh=GI.xv[h][vs]; int wa,wb; dWin(I,d,j,wa,wb);
    struct Opt{ int g0,f; Co c; }; vector<Opt> opts;
    for(int v=0;v<(int)I.VR[g].size();v++){ const Ver&V=I.VR[g][v]; if(V.b<wa) continue; if(V.a>wb) break; const V3&xg=GI.xv[g][v];
      Co cn; if(vzero(xh)){ if(!vzero(xg)) continue; cn=e.c; if(haveMu&&rnd(2)){ Co c2; if(coDiv(e.c,mu0,&c2)&&coOK(c2)) cn=c2; } }
      else { if(vzero(xg)) continue; Co mu; if(peel){ break; } if(!xratio(xg,xh,&mu)) continue; if(!coDiv(e.c,mu,&cn)||!coOK(cn)) continue; if(!haveMu){ mu0=mu; } }
      int a=max(V.a,wa), b=min(V.b,wb); if(a>b) continue; int fo; int g0=coloc(I,d,g,a,b,ex,&fo); if(g0<0) continue; opts.push_back({g0,fo,cn}); }
    if(peel&&!vzero(xh)){   // two-term: c1*g + c2*y == c*h on the X/Y part, y a junk-free (X/Y) register co-located with d
      static const Co SC[]={{1,0},{-1,0},{1,1},{-1,1},{1,-1},{-1,-1}};
      for(int v=0;v<(int)I.VR[g].size()&&opts.empty();v++){ const Ver&V=I.VR[g][v]; if(V.b<wa) continue; if(V.a>wb) break; const V3&xg=GI.xv[g][v]; if(vzero(xg)) continue;
        int a=max(V.a,wa), b=min(V.b,wb); if(a>b) continue; V3 T=scaleV(xh,e.c);
        for(int t=0;t<6&&opts.empty();t++){ Co c1=coMul(e.c,SC[t]); if(!coOK(c1)) continue; V3 rest=subV(T,scaleV(xg,c1)); if(vzero(rest)) continue; auto fy=GI.HX.find(xkey(rest)); if(fy==GI.HX.end()) continue;
          for(auto&rv:fy->second){ int y=rv.first; if(y==d||y==g||(ROLE[y]!='X'&&ROLE[y]!='Y')) continue; const Ver&Vy=I.VR[y][rv.second]; int a2=max(a,Vy.a), b2=min(b,Vy.b); if(a2>b2) continue; Co c2; if(!xratio(rest,GI.xv[y][rv.second],&c2)||!coOK(c2)) continue;
            int fo1,fo2; int g1=coloc(I,d,g,a2,b2,ex,&fo1); if(g1<0) continue; int g2=coloc(I,d,y,a2,b2,ex,&fo2); if(g2<0) continue;
            E.rem.push_back(j); E.ins.push_back({g1,{'A',d,g,fo1,c1}}); E.ins.push_back({g2,{'A',d,y,fo2,c2}}); opts.push_back({-1,0,{0,0}}); break; } } }
      if(opts.empty()) return false; haveMu=true; continue; }
    if(opts.empty()) return false; Opt o=opts[rnd(opts.size())]; if(!vzero(xh)) haveMu=true;
    E.rem.push_back(j); E.ins.push_back({o.g0,{'A',d,g,o.f,o.c}}); }
  E.tag="hubsw"; return true; }
static bool mvHubSwitchP(const Index&I,const State&S,Edit&E,bool peel){
  ensureGI(S,I); int i=randADD(S); if(i<0) return false; E.rem.clear(); E.ins.clear(); return hubBracket(I,S,S.P[i].d,S.P[i].s,peel,E); }
// killsw: rung kill of a helper stop that only carries READS of r, evacuated by junk-insensitive bracket switches of every (dest, r) bracket at the stop
static bool mvKillSw(const Index&I,const State&S,Edit&E,int r=-1,int j=-1){
  ensureGI(S,I);
  if(r<0){ for(int t=0;;t++){ if(t>64) return false; r=rnd(S.init.size()); if(ROLE[r]=='H'&&I.ST[r].size()>2) break; } j=1+rnd(I.ST[r].size()-2); }
  const Stop&st=I.ST[r][j]; vector<int> ds; for(int i:I.TOUCH[r]){ if(i<st.a) continue; if(i>st.b) break; const Ev&e=S.P[i]; if(e.k!='A'||e.s!=r) return false; if(find(ds.begin(),ds.end(),(int)e.d)==ds.end()) ds.push_back(e.d); }
  if(ds.empty()||ds.size()>8) return false; E.rem.clear(); E.ins.clear(); for(int d:ds){ if(!hubBracket(I,S,d,r,rnd(3)==0,E)) return false; }
  E.tag="killsw"; return true; }
// ---------------- cluster frame substitution ----------------
static bool clusterOf(const Index&I,const State&S,int r0,int j0,vector<pair<int,int>>&nodes,vector<int>&cev,int maxNodes=40){
  int f=I.ST[r0][j0].f; nodes.clear(); cev.clear(); unordered_set<long long> seen; vector<pair<int,int>> q; q.push_back({r0,j0}); seen.insert((long long)r0*100000+j0); unordered_set<int> evs;
  while(!q.empty()){ auto nd=q.back(); q.pop_back(); nodes.push_back(nd); if((int)nodes.size()>maxNodes) return false; int r=nd.first,j=nd.second; if(ROLE[r]=='O') return false; const Stop&st=I.ST[r][j]; if(st.f!=f) return false;
    for(int i:I.TOUCH[r]){ if(i<st.a) continue; if(i>st.b) break; const Ev&e=S.P[i]; if(e.f!=f) return false; evs.insert(i);
      if(e.k=='A'||e.k=='C'){ int p=(e.d==r)?e.s:e.d; if(ROLE[p]=='O') return false; int jp=stopAt(I,p,i); if(jp<0||I.ST[p][jp].f!=f) return false; long long key=(long long)p*100000+jp; if(!seen.count(key)){ seen.insert(key); q.push_back({p,jp}); } }
      else if(e.k!='S') return false; } }
  for(int i:evs) cev.push_back(i); sort(cev.begin(),cev.end()); return true; }
static bool mvRelabel(const Index&I,const State&S,Edit&E,int r=-1,int j=-1,int G=-1){
  if(r<0){ for(int t=0;;t++){ if(t>64) return false; r=rnd(S.init.size()); if(ROLE[r]!='O'&&I.ST[r].size()>1) break; } j=rnd(I.ST[r].size()); }
  if(ROLE[r]=='O') return false; int f=I.ST[r][j].f; if(SDIM[f]==0||SDIM[f]>=9) return false;
  vector<pair<int,int>> nodes; vector<int> cev; if(!clusterOf(I,S,r,j,nodes,cev)) return false;
  vector<int> cand; for(int g=0;g<SNF;g++){ if(g==f) continue; bool ok=true;
    for(auto&nd:nodes){ int rr=nd.first,jj=nd.second; int ns=I.ST[rr].size(); if(fixedStop(rr,jj,ns)){ ok=false; break; } int lo=jj>0?I.ST[rr][jj-1].f:-1, hi=jj+1<ns?I.ST[rr][jj+1].f:-1; if(lo<0&&hi<0){ ok=false; break; }
      if(lo>=0&&!psub(lo,g)){ ok=false; break; } if(hi>=0&&!psub(g,hi)){ ok=false; break; } }
    if(ok) cand.push_back(g); }
  if(cand.empty()) return false; if(G<0) G=cand[rnd(cand.size())]; else if(find(cand.begin(),cand.end(),G)==cand.end()) return false;
  E.rem.clear(); E.ins.clear(); E.initCh.clear();
  for(auto&nd:nodes){ int rr=nd.first,jj=nd.second; const Stop&st=I.ST[rr][jj]; if(jj>0){ int mi=st.a-1; if(mi<0||S.P[mi].k!='M'||S.P[mi].d!=rr) return false; E.rem.push_back(mi); E.ins.push_back({mi,{'M',rr,0,G,{0,0}}}); } else E.initCh.push_back({rr,G}); }
  for(int i:cev){ Ev x=S.P[i]; x.f=G; E.rem.push_back(i); E.ins.push_back({i,x}); }
  E.tag="relab"; return true; }
// ---------------- lift: dual rung insert ----------------
static bool mvLift(const Index&I,const State&S,Edit&E){
  int i=randADD(S); if(i<0) return false; const Ev&e=S.P[i]; int d=e.d,s=e.s; if(ROLE[d]=='O'||ROLE[s]=='O') return false; int f=e.f; if(SDIM[f]>=8) return false;
  int jd=stopAt(I,d,i), js=stopAt(I,s,i); if(jd<0||js<0) return false; const Stop&sd=I.ST[d][jd]; const Stop&ss=I.ST[s][js];
  int nd=I.ST[d].size(), ns=I.ST[s].size(); int hd=jd+1<nd?I.ST[d][jd+1].f:-1, hs=js+1<ns?I.ST[s][js+1].f:-1;
  if(hd<0&&ROLE[d]!='H') return false; if(hs<0&&ROLE[s]!='H') return false;
  vector<int> later; for(int k:I.TOUCH[d]){ if(k<i) continue; if(k>sd.b) break; later.push_back(k); }
  for(int k:I.TOUCH[s]){ if(k<i) continue; if(k>ss.b) break; later.push_back(k); }
  sort(later.begin(),later.end()); later.erase(unique(later.begin(),later.end()),later.end());
  for(int k:later){ const Ev&x=S.P[k]; if(x.k=='S'){ continue; } if(x.k!='A'||!((x.d==d&&x.s==s)||(x.d==s&&x.s==d))) return false; }
  vector<int> cand; for(int g=0;g<SNF;g++){ if(!psub(f,g)) continue; if(hd>=0&&!psub(g,hd)) continue; if(hs>=0&&!psub(g,hs)) continue; cand.push_back(g); }
  if(cand.empty()) return false; int G=cand[rnd(cand.size())];
  E.rem.clear(); E.ins.clear(); E.ins.push_back({i,{'M',d,0,G,{0,0}}}); E.ins.push_back({i,{'M',s,0,G,{0,0}}});
  for(int k:later){ Ev x=S.P[k]; x.f=G; E.rem.push_back(k); E.ins.push_back({k,x}); }
  E.tag="lift"; return true; }
// targeted census: every helper mid stop that carries only reads of the helper -> killsw; plus per-bracket switch plans
static void growCensus(const Index&I,const State&S,const Res&R){
  ensureGI(S,I); int NR=S.init.size(); long stops=0,srconly=0,planned=0,legal=0,impr=0,neut=0,brk=0,brkPlan=0,brkLegal=0,brkNeut=0,brkImpr=0; map<string,long> why; double best=R.kap;
  const char*out=getenv("K2S_OUT"); int tries=getenv("K2S_KTRIES")?atoi(getenv("K2S_KTRIES")):12;
  for(int r=0;r<NR;r++){ if(ROLE[r]!='H') continue; for(int j=1;j+1<(int)I.ST[r].size();j++){ stops++;
      const Stop&st=I.ST[r][j]; bool so=true; int nev=0; for(int i:I.TOUCH[r]){ if(i<st.a) continue; if(i>st.b) break; nev++; const Ev&e=S.P[i]; if(e.k!='A'||e.s!=r){ so=false; break; } } if(!so||!nev) continue; srconly++;
      bool pl=false,lg=false; double bk=-1;
      for(int t=0;t<tries;t++){ Edit E; if(!mvKillSw(I,S,E,r,j)) continue; pl=true; State T=applyEdit(S,E); cleanup(T); Res Q=verify(T); if(!Q.ok){ why[Q.why]++; continue; } lg=true; if(Q.kap>bk) bk=Q.kap;
        if(Q.kap>best+1e-13){ best=Q.kap; if(out){ string o=string(out)+".killsw"; dumpNet(T,o.c_str(),Q); } } }
      if(pl) planned++; if(lg){ legal++; if(bk>R.kap+1e-13) impr++; else if(bk>=R.kap-1e-13) neut++; } } }
  // per (dest, helper) bracket: any plan / legal / improving
  set<pair<int,int>> seen; for(size_t i=0;i<S.P.size();i++){ const Ev&e=S.P[i]; if(e.k!='A'||ROLE[e.s]!='H'||ROLE[e.d]=='O') continue; if(SDIM[e.f]==0||SDIM[e.f]>=9) continue; if(!seen.insert({e.d,e.s}).second) continue; brk++;
    bool pl=false,lg=false,nt=false,im=false; for(int t=0;t<tries;t++){ Edit E; if(!hubBracket(I,S,e.d,e.s,false,E)) continue; pl=true; State T=applyEdit(S,E); cleanup(T); Res Q=verify(T); if(!Q.ok) continue; lg=true; if(Q.kap>R.kap+1e-13) im=true; else if(Q.kap>=R.kap-1e-13) nt=true; }
    if(pl) brkPlan++; if(lg) brkLegal++; if(nt) brkNeut++; if(im) brkImpr++; }
  printf("GROW census: helper mid stops %ld, reads-only %ld: killsw planned %ld legal %ld improving %ld neutral %ld best kappa %.13f |",stops,srconly,planned,legal,impr,neut,best); for(auto&p:why) printf(" %s:%ld",p.first.c_str(),p.second); printf("\n");
  printf("GROW census: (dest,helper) mid-bracket pairs %ld: switch planned %ld legal %ld neutral %ld improving %ld\n",brk,brkPlan,brkLegal,brkNeut,brkImpr);
}
