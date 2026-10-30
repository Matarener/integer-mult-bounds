#include <unordered_set>
// k2frames.inc -- K2FRAMES lane (toolkit/module docstring): FRAME CREATION and HELPER->OWNED relay moves for the k2net engine.  Included by k2search.inc before propose().
// Both moves are one primitive, DREL (downward cluster relabel with owned relays), read off the swarm edits #5756 / #5802 / #5811:
//   pick a stop (r,j) at frame f and a target frame G strictly below f (G subset f).  The co-location closure of (r,j) BEFORE a time cut (gap index; +inf = whole stops) moves to G:
//   every followed node's entering MOVE/INIT is retargeted to G (or deleted when its previous frame IS G: the stop merges into the previous one), its events before the cut get frame G,
//   and a node whose stop continues past the cut gets MOVE G->f at the cut.  An ADD d += c*s whose dest d is followed but whose source s cannot follow (fixed main stop, frame law) is RELAYED by an
//   owned register o: INIT o@f, o += c*s @f (in place), MOVE o f->G (owned descends), d += 1*o @G, CLEAR o@G (consecutive reads into d share one lifetime: the #5802 / #5811 pattern).
//   value-exact by construction (d's value timeline is unchanged; o is cleared), legality re-checked by the full verifier as every proposal.
// move 'fnew' (K2S_W slot 17): G = a NEW frame = join of the followed nodes' previous frames (+ optional random vectors of f), appended to the frame table (tentative until the edit is accepted).
// move 'own'  (K2S_W slot 18): seed = a helper's or main's stop j>=1 (main final stops only with a cut); G = the helper's previous frame (rung drop, the #5802 P7 role change) or an existing frame between it and f.
// Owned peak is capped at K2S_PEAK (default: the input net's peak, so the profile's peak literal is kept); K2S_OWNNEW=0 forbids new owned ids (reuse idle owned registers only).
static unordered_map<u64,vector<int>> FHASH; static int SNF0=0, TENT=-1; static int PEAKMAX=0, OWNNEW=1; static double PREL=0.0;
static u64 spanKey(const array<u64,8>&s){ u64 h=1469598103934665603ULL; for(int w=0;w<8;w++){ h^=s[w]+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2); h*=1099511628211ULL; } return h; }
static void framesInit(){ SNF0=SNF; FHASH.clear(); for(int f=0;f<SNF;f++) FHASH[spanKey(SSP[f])].push_back(f); TENT=-1; }
static int findFrame(const array<u64,8>&sp){ auto it=FHASH.find(spanKey(sp)); if(it==FHASH.end()) return -1; for(int f:it->second) if(SSP[f]==sp) return f; return -1; }
static array<u64,8> spanOfBasis(const vector<int>&B){ vector<int> sp={0}; for(int v:B){ size_t m=sp.size(); for(size_t a=0;a<m;a++) sp.push_back(sp[a]^v); } array<u64,8> S{}; for(int x:sp) S[x>>6]|=1ULL<<(x&63); return S; }
static inline bool spHas(const array<u64,8>&S,int x){ return (S[x>>6]>>(x&63))&1; }
static bool spSub(const array<u64,8>&a,const array<u64,8>&b){ for(int w=0;w<8;w++) if(a[w]&~b[w]) return false; return true; }
// GF(2) echelon insert (piv[k] has leading bit k); true if v was independent
static bool gfIns(int piv[9],int v){ for(int k=8;k>=0;k--){ if(!(v>>k&1)) continue; if(piv[k]){ v^=piv[k]; continue; } piv[k]=v; return true; } return false; }
static vector<int> gfBasis(const int piv[9]){ vector<int> b; for(int k=8;k>=0;k--) if(piv[k]) b.push_back(piv[k]); return b; }
// frame with this basis' span: existing id, or a new tentative frame (rolled back by frameRollback() unless the proposal is accepted)
static int addFrame(const vector<int>&B){ array<u64,8> sp=spanOfBasis(B); int f=findFrame(sp); if(f>=0) return f;
  f=SNF++; SDIM.push_back((int)B.size()); SSP.push_back(sp); SBAS.push_back(B); FHASH[spanKey(sp)].push_back(f); if(TENT<0) TENT=f; return f; }
static void frameRollback(){ if(TENT<0) return; for(int f=SNF-1;f>=TENT;f--){ auto&v=FHASH[spanKey(SSP[f])]; v.erase(remove(v.begin(),v.end(),f),v.end()); if(v.empty()) FHASH.erase(spanKey(SSP[f])); SDIM.pop_back(); SSP.pop_back(); SBAS.pop_back(); } SNF=TENT; TENT=-1; }
static long DRS[8]={0};   // diagnostics: proposals, planned, relays, merges, cuts, new frames
static int inputPeak(const State&S){ int a=0,p=0; for(auto&e:S.P){ if(e.k=='I'){ a++; p=max(p,a); } else if(e.k=='X') a--; } return p; }
// owned lifetimes of S as (INIT pos, CLEAR pos, reg)
static void ownedIntervals(const Index&I,const State&S,vector<array<int,3>>&L){ L.clear(); int NR=S.init.size();
  for(int r=0;r<NR;r++){ if(ROLE[r]!='O') continue; int a=-1; for(int k:I.TOUCH[r]){ char c=S.P[k].k; if(c=='I') a=k; else if(c=='X'&&a>=0){ L.push_back({a,k,r}); a=-1; } } } }
struct DNode{ int r,j; };
// the DREL planner.  mode 0 = fnew (new frame), 1 = own (helper rung drop / existing lower frame)
// round 2: own seeds X/Y main stops too (#5811: main 92 at 267 -> 1091 with a six-read relay)
static bool mvDrel(const Index&I,const State&S,Edit&E,int mode,int r=-1,int j=-1){
  DRS[0]++; int NR=S.init.size();
  static int DS[3]={-2,-1,-1}; if(DS[0]==-2){ DS[0]=-1; if(getenv("K2S_DSEED")) sscanf(getenv("K2S_DSEED"),"%d,%d,%d",&DS[0],&DS[1],&DS[2]); }   // K2S_DSEED=r,j,G: targeted seed (diagnostics)
  if(DS[0]>=0&&r<0){ r=DS[0]; j=DS[1]; }
  if(r<0){ for(int t=0;;t++){ if(t>64) return false; r=rnd(NR); if(ROLE[r]=='O') continue; int ns=I.ST[r].size(); if(mode==1){ if(ns<2) continue; j=1+rnd(ns-1); } else j=rnd(ns); break; } }
  if(ROLE[r]=='O'||j<0||j>=(int)I.ST[r].size()) return false;
  const Stop st0=I.ST[r][j]; int f=st0.f; if(SDIM[f]<1) return false;
  long n=S.P.size(); int cut=INT32_MAX; if(rnd(2)){ if(st0.b-st0.a<1) return false; cut=st0.a+1+rnd(st0.b-st0.a); }   // events with index < cut move to G
  // followability of node (q,jq) for target span Gs (Gsub: G strictly below f); merge = previous frame spans G exactly
  auto followable=[&](int q,int jq,const array<u64,8>&Gs,int Gid,bool&merge)->bool{ merge=false; const auto&Lq=I.ST[q]; int ns=Lq.size(); const Stop&s=Lq[jq]; if(s.f!=f) return false;
    bool crosses=s.b>=cut; char ro=ROLE[q];
    if(ro=='O'){ if(crosses) return false; long ent=s.a-1; if(ent<0) return false; char ek=S.P[ent].k; if(ek!='I'&&ek!='M') return false;
      if(s.b<n&&S.P[s.b].k=='M'){ int B=S.P[s.b].f; if(!spSub(SSP[B],Gs)||SSP[B]==Gs) return false; } return true; }
    if(jq==0){ if(ro!='H') return false; return true; }               // helper birth stop: init moves to G (credit checked by the verifier)
    if((ro=='X'||ro=='Y')&&jq==ns-1&&!crosses) return false;          // fixed final stop must still end at f
    int lo=Lq[jq-1].f; if(!spSub(SSP[lo],Gs)) return false; if(SSP[lo]==Gs) merge=true; (void)Gid; return true; };
  struct Rel{ int i,d,s; Co c; };
  auto plan=[&](const array<u64,8>&Gs,int Gid,vector<DNode>&nodes,vector<char>&mergeV,vector<int>&relab,vector<Rel>&rel,bool collect,int piv[9])->bool{
    nodes.clear(); mergeV.clear(); relab.clear(); rel.clear(); map<long long,int> st;   // node key -> 1 followed, 0 not
    auto key=[](int q,int jq){ return (long long)q*100000+jq; };
    bool mg; if(!followable(r,j,Gs,Gid,mg)) return false; st[key(r,j)]=1; nodes.push_back({r,j}); mergeV.push_back(mg);
    unordered_set<int> seenEv;
    for(size_t h=0;h<nodes.size();h++){ if(nodes.size()>64) return false; int q=nodes[h].r, jq=nodes[h].j; const Stop&s=I.ST[q][jq];
      if(collect&&jq>0&&ROLE[q]!='O'){ for(int v:SBAS[I.ST[q][jq-1].f]) gfIns(piv,v); }
      for(int i:I.TOUCH[q]){ if(i<s.a) continue; if(i>s.b||i>=cut) break; if(!seenEv.insert(i).second) continue; const Ev&e=S.P[i];
        if(e.k=='S'||e.k=='I'||e.k=='X'){ relab.push_back(i); continue; }
        if(e.k!='A'&&e.k!='C') return false;
        int u=(e.d==q)?e.s:e.d; int ju=stopAt(I,u,i); if(ju<0) return false; long long ku=key(u,ju); auto it=st.find(ku); int su;
        if(it!=st.end()) su=it->second;
        else { bool m2=false; bool relayable=(u==e.s&&e.k=='A'&&ROLE[e.d]!='O');
          if(relayable&&PREL>0&&urand()<PREL) su=0; else su=followable(u,ju,Gs,Gid,m2)?1:0;
          st[ku]=su; if(su){ nodes.push_back({u,ju}); mergeV.push_back(m2); } }
        if(su){ relab.push_back(i); continue; }
        if(u==e.s&&e.k=='A'&&ROLE[e.d]!='O'){ rel.push_back({i,e.d,e.s,e.c}); continue; }
        return false; } }
    return true; };
  vector<DNode> nodes; vector<char> mergeV; vector<int> relab; vector<Rel> rel; int G=-1;
  if(mode==1){   // own: G = previous frame (rung drop) or an existing frame between it and f
    if(j<1) return false; int lo=I.ST[r][j-1].f; G=lo;
    if(DS[2]>=0) G=DS[2]; else if(rnd(2)){ vector<int> c; for(int g=0;g<SNF;g++) if(g!=lo&&psub(g,f)&&sub(lo,g)&&SDIM[g]>SDIM[lo]) c.push_back(g); if(!c.empty()) G=c[rnd(c.size())]; }
    if(!psub(G,f)) return false;
    if(!plan(SSP[G],G,nodes,mergeV,relab,rel,false,nullptr)) return false;
  } else {      // fnew: pass 1 with G = f (collect the join J of the followed nodes' previous frames), then G = J (+ random vectors of f), new frame if its span is new
    int piv[9]={0}; if(!plan(SSP[f],f,nodes,mergeV,relab,rel,true,piv)) return false;
    vector<int> B=gfBasis(piv); if((int)B.size()>=SDIM[f]) return false;
    int extra=0; int room=SDIM[f]-1-(int)B.size(); if(room>0&&rnd(3)==0) extra=1+rnd(room);
    if(B.empty()&&extra==0) extra=room>0?1:0; if(B.empty()&&extra==0) return false;
    for(int k=0;k<extra;k++){ array<u64,8> cs=spanOfBasis(gfBasis(piv)); vector<int> xs; for(int x=1;x<512;x++) if(spHas(SSP[f],x)&&!spHas(cs,x)) xs.push_back(x); if(xs.empty()) break; gfIns(piv,xs[rnd(xs.size())]); }
    B=gfBasis(piv); array<u64,8> Gs=spanOfBasis(B); if(!spSub(Gs,SSP[f])||Gs==SSP[f]) return false;
    if(!plan(Gs,-1,nodes,mergeV,relab,rel,false,nullptr)) return false;
    G=addFrame(B); if(G>=SNF0&&G==SNF-1&&TENT==G) DRS[5]++;
  }
  if(G==f) return false;
  for(size_t h=0;h<nodes.size();h++) if(mergeV[h]&&I.ST[nodes[h].r][nodes[h].j-1].f!=G) return false;   // duplicate-span frames: a merge must reuse the previous stop's frame id
  // relay groups: consecutive relayed reads into the same dest with no other event of d in between share one owned lifetime
  sort(rel.begin(),rel.end(),[](const Rel&a,const Rel&b){ return a.i<b.i; });
  vector<vector<int>> groups; { map<int,vector<int>> byD; for(int k=0;k<(int)rel.size();k++) byD[rel[k].d].push_back(k);
    for(auto&kv:byD){ int d=kv.first; vector<int> cur; for(int k:kv.second){ if(!cur.empty()){ int a=rel[cur.back()].i, b=rel[k].i; const auto&T=I.TOUCH[d]; auto it=upper_bound(T.begin(),T.end(),a); bool other=false;
          for(;it!=T.end()&&*it<b;++it){ bool isRel=false; for(int k2:kv.second) if(rel[k2].i==*it) isRel=true; if(!isRel){ other=true; break; } }
          if(other){ groups.push_back(cur); cur.clear(); } } cur.push_back(k); } if(!cur.empty()) groups.push_back(cur); } }
  if(groups.size()>8) return false;
  // owned ids + peak
  vector<array<int,3>> L; if(!groups.empty()) ownedIntervals(I,S,L);
  vector<int> gid(groups.size(),-1); vector<array<int,2>> gint; int nextNew=NR;
  for(size_t g=0;g<groups.size();g++){ int a=rel[groups[g].front()].i, b=rel[groups[g].back()].i; gint.push_back({a,b});
    // peak: existing lifetimes + earlier groups overlapping, at every start point inside [a,b]
    vector<int> pts={a}; for(auto&x:L) if(x[0]>=a&&x[0]<=b) pts.push_back(x[0]); for(size_t h=0;h<g;h++) if(gint[h][0]>=a&&gint[h][0]<=b) pts.push_back(gint[h][0]);
    for(int t:pts){ int c=1; for(auto&x:L) if(x[0]<=t&&t<=x[1]) c++; for(size_t h=0;h<g;h++) if(gint[h][0]<=t&&t<=gint[h][1]) c++; if(PEAKMAX>0&&c>PEAKMAX) return false; }
    vector<int> idle; { set<int> busy; for(auto&x:L) if(x[0]<=b+1&&x[1]>=a-1) busy.insert(x[2]); for(size_t h=0;h<g;h++) if(gint[h][0]<=b+1&&gint[h][1]>=a-1) busy.insert(gid[h]);
      for(int q=0;q<NR;q++) if(ROLE[q]=='O'&&!busy.count(q)) idle.push_back(q); }
    if(!idle.empty()&&(!OWNNEW||rnd(2))) gid[g]=idle[rnd(idle.size())]; else if(OWNNEW) gid[g]=nextNew++; else return false; }
  // ---- build the edit.  E.ins order matters at equal gaps: relay events first, then relabelled events, then the cut MOVEs (all stable-sorted by gap)
  E.rem.clear(); E.ins.clear(); E.initCh.clear(); E.newO.clear(); for(int q=NR;q<nextNew;q++) E.newO.push_back(q);
  for(size_t g=0;g<groups.size();g++){ int o=gid[g]; const auto&gr=groups[g]; int d=rel[gr[0]].d;
    E.ins.push_back({rel[gr[0]].i,{'I',o,0,f,{0,0}}});
    for(int k:gr){ E.rem.push_back(rel[k].i); E.ins.push_back({rel[k].i,{'A',o,rel[k].s,f,rel[k].c}}); }
    int t=rel[gr.back()].i+1; E.ins.push_back({t,{'M',o,0,G,{0,0}}}); E.ins.push_back({t,{'A',d,o,G,{1,0}}}); E.ins.push_back({t,{'X',o,0,G,{0,0}}}); DRS[2]++; }
  int nmerge=0, ncut=0;
  for(size_t h=0;h<nodes.size();h++){ int q=nodes[h].r, jq=nodes[h].j; const Stop&s=I.ST[q][jq];
    if(ROLE[q]=='O'){ long ent=s.a-1; Ev x=S.P[ent]; x.f=G; E.rem.push_back(ent); E.ins.push_back({(int)ent,x}); }
    else if(jq==0) E.initCh.push_back({q,G});
    else { long ent=s.a-1; if(ent<0||S.P[ent].k!='M'||S.P[ent].d!=q) return false; E.rem.push_back(ent); if(mergeV[h]) nmerge++; else E.ins.push_back({(int)ent,{'M',q,0,G,{0,0}}}); } }
  for(int i:relab){ Ev x=S.P[i]; x.f=G; E.rem.push_back(i); E.ins.push_back({i,x}); }
  for(size_t h=0;h<nodes.size();h++){ int q=nodes[h].r, jq=nodes[h].j; const Stop&s=I.ST[q][jq]; if(s.b>=cut&&cut<INT32_MAX){ E.ins.push_back({cut,{'M',q,0,f,{0,0}}}); ncut++; } }
  if(nmerge) DRS[3]++; if(ncut) DRS[4]++; DRS[1]++;
  E.tag=mode?"own":"fnew"; return true; }
