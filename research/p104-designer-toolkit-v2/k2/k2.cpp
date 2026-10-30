// k2.cpp -- KERNEL2 lane: fork of FLAGS/fl.cpp with runtime chain length (env K2_L, default 7; L<=8).  See toolkit/module docstring.
// fl.cpp -- FLAGS lane fork of PARTIALTRIE/pt.cpp: + FL_FREEZE (no X flag moves).
// pt.cpp -- PARTIALTRIE fork of JOINTFEED/jf.cpp: root build as a TRIE of S_k-signed partial roots at frames l_k in F in H_k (virtual tops, type -5),
//   readable by every Y-side register (sign-consistent) and by the root build itself; SA move PT_TRIEP mutates the tries.  env PT=1, PT_TRIE=file, PT_TRIEP, PT_ALLROOT.
// (original header) mainhub.cpp -- SA kernel for synth/mainhub.py (MAINHUB, see ../module docstring).  Extends hubladder.cpp (hub-hub merge ladders, shared hubs) with MAINS AS HUBS:
//  (1) X PACKETS: X_a may ABSORB co-present X_b (same flag frame at stop index sa, sources clean there) with signs sig: from stop sa on X_a carries x_a + sum sig_b x_b and every reader
//      that picks X_a at a stop >= sa gets the whole packet (usable only if all packet ports are in the reader's open target and the relative signs match).  The absorption is a contact at a
//      stop X_a/X_b make anyway (the "free hub"): zero R0 beyond the stops; undone at F9 in reverse order.
//  (2) Y-Y HAAR PAIRS (optional): Y_j,Y_k meet at V = Q_j cap Q_k (dim 7); one collects the agree ports of V, the other the disagree ports; ports of Q_j \ V come from hubs read at Q_j.
// R0 tax: hub 9ln9 - sum r ln r (rungs, then F9); Y 8ln8 - sum (rungs, then 8); X 8ln8 - sum over used stops (picks + absorptions).
// usage: mainhub ports.txt signs.txt seed iters T0 T1 init.txt|- maxdepth pairs.txt|- PAIRP ABSP [absinit.txt|-]
// env: MH_LINES=lines.txt (root copies as carriers)  MH_ROOTTREE=roots_signs.txt (front end as S_k-signed shared trees; roots are readers)  MH_PROV / MH_ROOTS (pricing-only modes, print and exit)
//      MH_VIRT=k (virtual hyperplane rungs, rejected)  MH_PAIRCOPY (copies for paired Ys, experimental, no python glue).  Work dir ext/MAINHUB (runsa.sh, runsa2.sh, realise.sh, plan2init.py, stats.py).
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cmath>
#include <vector>
#include <algorithm>
#include <cstring>
#include <memory>
#include <unordered_map>
#include <array>
#include <functional>
using namespace std;
typedef uint64_t u64; typedef unsigned __int128 M;
static int L=7; static double LINEP=0.0, RLINEP=0.0, COPYPEN=0.0; static int JOINT=0; static vector<int> HM; static vector<vector<int>> cntC; static long NVIOL=0; static vector<vector<int>> LM; static vector<int> ALLL; static double JOINP=0.4, PAIRP=0.0, ABSP=0.0; static int MAXD=100000;
static int FLFREEZE=0; static double FLLAT=0; static int VIRT=0; static int NR=0; static vector<vector<int>> RD; static vector<int> RU; static int n; static vector<int> P; static vector<vector<int>> SG;
static inline int par(int a,int b){return __builtin_popcount(a&b)&1;}
static inline int pc(M x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
static inline int ctz(M x){ u64 lo=(u64)x; if(lo) return __builtin_ctzll(lo); return 64+__builtin_ctzll((u64)(x>>64)); }
static inline M bit(int i){ return ((M)1)<<i; }
struct Rng{u64 s; u64 next(){s^=s<<13;s^=s>>7;s^=s<<17;return s;} double u(){return (next()>>11)*(1.0/9007199254740992.0);} int r(int m){return next()%m;}};
static Rng rng; static double RL[64];
struct Span{u64 m[8];};
static inline bool has(const Span&S,int x){return (S.m[x>>6]>>(x&63))&1;}
static inline void setb(Span&S,int x){S.m[x>>6]|=1ULL<<(x&63);}
static vector<Span> RHS;
static u64 hashSpan(const Span&S){u64 h=1469598103934665603ULL; for(int w=0;w<8;w++){h^=S.m[w]+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2); h*=1099511628211ULL;} return h;}
static vector<vector<int>> Q; static vector<vector<Span>> SP; static vector<vector<u64>> HS; static vector<Span> QS; static vector<u64> QH; static vector<vector<int>> O;
static void buildSpan(int i,int s){
  if(s==0){Span S; memset(&S,0,sizeof S); setb(S,0); setb(S,Q[i][0]); SP[i][0]=S;}
  else {Span S=SP[i][s-1]; int v=Q[i][s]; for(int x=0;x<512;x++) if(has(SP[i][s-1],x)) setb(S,x^v); SP[i][s]=S;}
  HS[i][s]=hashSpan(SP[i][s]);
  if(!LM.empty()){ int msk=0; for(size_t t=0;t<ALLL.size();t++) if(has(SP[i][s],ALLL[t])) msk|=1<<t; LM[i][s]=msk; }
}
static void rebuild(int i,int from){for(int s=from;s<L;s++) buildSpan(i,s);}
static bool indep(int i,int s,int v){ return !has(SP[i][s-1],v); }
// ---- absorption state
static vector<int> absS; static vector<M> absSet; static vector<vector<int>> absSig;   // absSig[a][b] in {+1,-1}
static inline M packet(int a){ return absSet[a]|bit(a); }
static u64 signHash(M T,int j){ if(!T) return 7; u64 h=1469598103934665603ULL; int i0=ctz(T); int s0=SG[j][i0]; for(M B=T;B;B&=B-1){int i=ctz(B); h=(h^(u64)(SG[j][i]*s0+2))*1099511628211ULL;} return h; }
static inline bool pktOK(int a,M T,int sj){ M pk=packet(a); if(pk&~T) return false; for(M B=absSet[a];B;B&=B-1){int b=ctz(B); if(SG[sj][b]*SG[sj][a]!=absSig[a][b]) return false;} return true; }
// TRANSPARENT: every source of X_a's packet is co-present (same frame) and clean at stop s -> a reader can read X_a - sum sig X_b, so X_a acts as a single port there
static inline bool transparent(int a,int s){ for(M B=absSet[a];B;B&=B-1){ int b=ctz(B); if(HS[b][s]!=HS[a][s]) return false; if(absS[b]>=0 && absS[b]<=s) return false; } return true; }
// ---- tax
static double taxChain(const vector<int>&d,bool hub){ double t=RL[hub?9:8]; int prev=0; for(int x:d){t-=RL[x-prev];prev=x;} t-= hub? RL[9-prev] : 0; return t; }
struct NodeS;
struct Kid{ int vi,vs; shared_ptr<NodeS> node; };    // child read at frame (vi,vs)  (vi=-1: parent's top frame; vi=-3: Q_j of a paired Y)
struct NodeS{ u64 Fh; M T; bool strict; M left; bool doTop; int topI,topS,topJ;  // top: flag stop (topI,topS) | Q_topJ (topI=-1) | V of pair (topI=-2, topS=partner, topJ=j)
  vector<int> rd; vector<pair<int,int>> picks; vector<Kid> kids; double taxH,taxY; int depth; vector<int> tb; int lri=-1,lrs=-1; };
struct MK{ u64 Fh; M T; bool strict; bool dt; u64 sg; bool operator==(const MK&o)const{return Fh==o.Fh&&T==o.T&&strict==o.strict&&dt==o.dt&&sg==o.sg;} };
struct MKH{ size_t operator()(const MK&k)const{ return k.Fh*0x9e3779b97f4a7c15ULL ^ (u64)k.T*1099511628211ULL ^ (u64)(k.T>>64)*0xc2b2ae3d27d4eb4fULL ^ (k.strict?12345:0)^(k.dt?777:0)^k.sg*0x2545F4914F6CDD1DULL;} };
static unordered_map<MK,shared_ptr<NodeS>,MKH> memo;
struct Item{int x; M mask;};
struct Nd{int dim,ri,rs; M pm; vector<Item> it; const Span* sp; const vector<int>* bas; u64 h;};
static inline bool ndIn(const Nd&g,const Span&sf){ if(g.bas){ for(int v:*g.bas) if(!has(sf,v)) return false; return true; } if(!has(sf,Q[g.ri][0])) return false; for(int t=1;t<=g.rs;t++) if(!has(sf,Q[g.ri][t])) return false; return true; }
// ---- PARTIALTRIE state
struct TF{ vector<int> bas; Span sp; u64 h; int dim; int cum; M ports; M sup; };
struct TItem{ shared_ptr<NodeS> node; shared_ptr<TF> f; int full; };
static int PT=0, NOTRIE=0, PTALL=0, NORR=0; static vector<vector<shared_ptr<TF>>> TR; static vector<vector<TItem>> TI; static vector<int> LK; static const vector<int>* VTB=nullptr; static long PTREADS=0;
static int LASTR=0; static vector<int> OF, OFR; static int DUAL=0; static long DUALON=0, DUALN=0; static vector<const NodeS*> RNo; static int ROOTY=0;
static void (*ROOTYHOOK)(const Span&,int,M,bool,int,vector<Nd>&,vector<u64>&,vector<shared_ptr<NodeS>>&,vector<char>&)=nullptr; static vector<vector<shared_ptr<NodeS>>> RNc;
static bool spanSub(const Span&a,const Span&b){ for(int w=0;w<8;w++) if(a.m[w]&~b.m[w]) return false; return true; }
static vector<shared_ptr<NodeS>>*ROOTP=nullptr; static int HUBREAD=0; static long HUBREADS=0;
static int rootOfLine(int l){ for(size_t k=0;k<RU.size();k++) if(!par(l,RU[k])) return k; return -1; }
static void collectNodes(const shared_ptr<NodeS>&N,vector<shared_ptr<NodeS>>&out){ for(auto&k:N->kids){ if(find(out.begin(),out.end(),k.node)!=out.end()) continue; out.push_back(k.node); collectNodes(k.node,out);} }
static shared_ptr<NodeS> build(const Span&F,u64 Fh,int dimF,M T,bool strict,int topI,int topS,int topJ,int depth,int sj,bool doTop=true,int lineV=0){
  bool offers=PT && (sj>=n ? OFR[sj-n] : OF[sj]); MK key{Fh,T,strict,doTop,signHash(T,sj)^(offers?0x51ed27ULL:0)}; bool nomemo=lineV || (ROOTY && sj>=n); if(!nomemo){ auto itm=memo.find(key); if(itm!=memo.end()) return itm->second; }
  auto N=make_shared<NodeS>(); N->Fh=Fh; N->T=T; N->strict=strict; N->left=0; N->doTop=doTop; N->topI=topI; N->topS=topS; N->topJ=topJ; N->depth=depth; if(topI==-5 && VTB) N->tb=*VTB;
  vector<Nd> nodes; vector<u64> hh;
  for(M B=T;B;B&=B-1){ int i=ctz(B);
    for(int s=0;s<L;s++){
      if(s>0 && !has(F,Q[i][s])) break;
      if(strict && s+1==dimF) break;
      if(lineV && !has(SP[i][s],lineV)) continue;
      if(JOINT && lineV && s<HM[i]) continue;   // JOINTFEED: copies pick post-root, so only at X stops >= every pre-root (hub/Y/absorb) use of that X
      M mk;
      if(absS[i]>=0 && s>=absS[i] && !transparent(i,s)){ if(!pktOK(i,T,sj)) break; mk=packet(i); } else mk=bit(i);
      u64 h=HS[i][s]; int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==h){id=a;break;}
      if(id<0){ id=nodes.size(); nodes.push_back({s+1,i,s,0,{},&SP[i][s],nullptr,h}); hh.push_back(h);} nodes[id].pm|=mk; nodes[id].it.push_back({i,mk});
    }
  }
  vector<shared_ptr<NodeS>> hubItems;
  if(JOINT && HUBREAD && lineV && ROOTP){   // JOINTFEED: a root copy may READ S_k-signed root-tree hubs of its own root (top holds l_k, inside F, ports sign-consistent with the reader)
    int k=rootOfLine(lineV); int rj=n+k;
    if(k>=0 && rj<(int)ROOTP->size() && (*ROOTP)[rj]){ vector<shared_ptr<NodeS>> all; collectNodes((*ROOTP)[rj],all);
      for(auto&c:all){ if(c->topI<0) continue; if(!has(SP[c->topI][c->topS],lineV)) continue; if(c->left || (c->T&~T)) continue; if(strict && c->topS+1==dimF) continue;
        bool in=true; for(int t=0;t<=c->topS&&in;t++) if(!has(F,Q[c->topI][t])) in=false; if(!in) continue;
        int s0=0; bool cons=true; for(M B=c->T;B&&cons;B&=B-1){ int i=ctz(B); int v=SG[sj][i]*SG[rj][i]; if(!v) cons=false; else if(!s0) s0=v; else if(v!=s0) cons=false; } if(!cons) continue;
        u64 h=HS[c->topI][c->topS]; int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==h){id=a;break;}
        if(id<0){ id=nodes.size(); nodes.push_back({c->topS+1,c->topI,c->topS,0,{},&SP[c->topI][c->topS],nullptr,h}); hh.push_back(h);}
        nodes[id].pm|=c->T; nodes[id].it.push_back({-1-(int)hubItems.size(),c->T}); hubItems.push_back(c); } } }
  vector<char> isTrie(hubItems.size(),0);
  if(offers && !NOTRIE){   // PARTIALTRIE: S_k-signed trie pieces (virtual tops l_k in F in H_k) as items, sign-consistent with reader sj
    for(int k=0;k<(int)TI.size();k++){ int rj=n+k; if(sj>=n && (sj!=rj || NORR)) continue; if(sj<n && par(LK[k],P[sj])) continue;
      for(auto&ti:TI[k]){ const TF&f=*ti.f; M tT=ti.node->T&~ti.node->left; if(!tT || (tT&~T)) continue; if(f.dim>dimF || (strict && f.dim==dimF)) continue; if(!spanSub(f.sp,F)) continue;
        if(sj!=rj){ int s0=0; bool cons=true; for(M B=tT;B&&cons;B&=B-1){ int i=ctz(B); int v=SG[sj][i]*SG[rj][i]; if(!v) cons=false; else if(!s0) s0=v; else if(v!=s0) cons=false; } if(!cons) continue; }
        int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==f.h){id=a;break;}
        if(id<0){ id=nodes.size(); nodes.push_back({f.dim,-5,0,0,{},&f.sp,&f.bas,f.h}); hh.push_back(f.h);}
        nodes[id].pm|=tT; nodes[id].it.push_back({-1-(int)hubItems.size(),tT}); hubItems.push_back(ti.node); isTrie.push_back(1); } } }
  if(offers && PTALL && !NOTRIE && sj<n && ROOTP){   // PT_ALLROOT: every root-tree hub with an X-stop top inside F (any root), sign-consistent with the reader
    for(int k=0;k<NR-n;k++){ int rj=n+k; auto&R=(*ROOTP)[rj]; if(!R) continue;
      if(RNo[k]!=R.get()){ RNc[k].clear(); vector<shared_ptr<NodeS>> all; collectNodes(R,all); for(auto&c:all) if(c->topI>=0 || (LASTR && c->lri>=0)) RNc[k].push_back(c); RNo[k]=R.get(); }
      for(auto&c:RNc[k]) for(int pass=0;pass<2;pass++){   // pass 0: at the hub's top (X stop); pass 1 (PT_LASTRUNG): at its last rung, where its content is already final
        int fi,fs; if(pass==0){ if(c->topI<0) continue; fi=c->topI; fs=c->topS; } else { if(!LASTR || c->lri<0 || (c->topI==c->lri && c->topS==c->lrs)) continue; fi=c->lri; fs=c->lrs; }
        M cT=c->T&~c->left; if(!cT || (cT&~T)) continue; if(strict && fs+1==dimF) continue; if(fs+1>dimF) continue;
        bool in=true; for(int t=0;t<=fs&&in;t++) if(!has(F,Q[fi][t])) in=false; if(!in) continue;
        int s0=0; bool cons=true; for(M B=cT;B&&cons;B&=B-1){ int i=ctz(B); int v=SG[sj][i]*SG[rj][i]; if(!v) cons=false; else if(!s0) s0=v; else if(v!=s0) cons=false; } if(!cons) continue;
        u64 h=HS[fi][fs]; int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==h){id=a;break;}
        if(id<0){ id=nodes.size(); nodes.push_back({fs+1,fi,fs,0,{},&SP[fi][fs],nullptr,h}); hh.push_back(h);}
        nodes[id].pm|=cT; nodes[id].it.push_back({-1-(int)hubItems.size(),cT}); hubItems.push_back(c); isTrie.push_back(2); } } }
  if(PT && ROOTY && !NOTRIE && sj>=n && ROOTYHOOK) ROOTYHOOK(F,dimF,T,strict,sj,nodes,hh,hubItems,isTrie);
  int Nn=nodes.size();
  if(Nn==0){ N->rd={dimF}; N->taxH=taxChain(N->rd,true); N->taxY=taxChain(N->rd,false); N->left=T; if(!nomemo) memo[key]=N; return N; }
  vector<int> ord(Nn); for(int a=0;a<Nn;a++) ord[a]=a;
  stable_sort(ord.begin(),ord.end(),[&](int a,int b){return nodes[a].dim<nodes[b].dim;});
  vector<int> bp(Nn,-1); vector<double> best(Nn,0);
  int bestf=-1; double bv=-1;
  for(int x=0;x<Nn;x++){ int f=ord[x]; const Nd&nf=nodes[f]; const Span&sf=*nf.sp; double b=pc(nf.pm); int p=-1;
    for(int y=0;y<x;y++){ int g=ord[y]; const Nd&ng=nodes[g]; if(ng.dim>=nf.dim) break;
      bool ok=ndIn(ng,sf);
      if(ok){ double v=best[g]+pc(nf.pm&~ng.pm); if(v>b){b=v;p=g;} } }
    best[f]=b; bp[f]=p; if(b>bv+1e-9 || (fabs(b-bv)<1e-9 && bestf>=0 && nodes[f].dim>nodes[bestf].dim)){bv=b;bestf=f;}
  }
  vector<int> chain; for(int f=bestf;f>=0;f=bp[f]) chain.push_back(f); reverse(chain.begin(),chain.end());
  M cov=0; vector<M> D(chain.size(),0);
  for(size_t c=0;c<chain.size();c++){ Nd&nd=nodes[chain[c]]; M avail=nd.pm&~cov, got=0;
    stable_sort(nd.it.begin(),nd.it.end(),[](const Item&a,const Item&b){return pc(a.mask)>pc(b.mask);});
    for(auto&itx:nd.it) if(!(itx.mask&~avail) && !(itx.mask&got)){ got|=itx.mask; if(itx.x>=0) N->picks.push_back({itx.x,nd.rs}); else { int hi=-1-itx.x; if(nd.ri==-5) N->kids.push_back({-5,0,hubItems[hi]}); else N->kids.push_back({nd.ri,nd.rs,hubItems[hi]}); if(isTrie[hi]) PTREADS++; else HUBREADS++; } }
    D[c]=got; cov|=got; }
  vector<int> rd; for(size_t c=0;c<chain.size();c++) if(D[c]) rd.push_back(nodes[chain[c]].dim);
  { int lc=-1; for(size_t c=0;c<chain.size();c++) if(D[c]) lc=c; if(lc>=0 && nodes[chain[lc]].ri>=0){ N->lri=nodes[chain[lc]].ri; N->lrs=nodes[chain[lc]].rs; } }
  if(rd.empty() || rd.back()!=dimF) rd.push_back(dimF);
  N->rd=rd; N->taxH=taxChain(rd,true); N->taxY=taxChain(rd,false);
  M left=T&~cov;
  if(left && depth<MAXD){
    vector<M> slot(chain.size()+1,0);
    for(M B=left;B;B&=B-1){ int i=ctz(B); int sl=chain.size();
      for(size_t c=0;c<chain.size();c++){ if(!D[c]) continue; const Nd&nc=nodes[chain[c]]; if(has(*nc.sp,P[i])){sl=c;break;} }
      slot[sl]|=bit(i); }
    for(size_t c=0;c<chain.size();c++) if(slot[c]){
      const Nd&nc=nodes[chain[c]]; if(nc.dim<=1){ slot[chain.size()]|=slot[c]; continue; }
      shared_ptr<NodeS> ch;
      if(nc.ri==-5){ auto sv=VTB; VTB=nc.bas; ch=build(*nc.sp,nc.h,nc.dim,slot[c],true,-5,0,0,depth+1,sj); VTB=sv; }
      else ch=build(SP[nc.ri][nc.rs],HS[nc.ri][nc.rs],nc.dim,slot[c],true,nc.ri,nc.rs,-1,depth+1,sj);
      if(ch->T==ch->left){ slot[chain.size()]|=slot[c]; continue; }   // child could place nothing: defer to top
      if(nc.ri==-5) N->kids.push_back({-5,0,ch}); else N->kids.push_back({nc.ri,nc.rs,ch}); slot[chain.size()]|=ch->left; }
    N->left=slot[chain.size()];
    if(VIRT && N->left && dimF>=3){   // VIRTUAL RUNG: a hyperplane h of F containing the top spine frame; the register reads a child at h (h need not be an X stop)
      int g=-1; for(size_t c=0;c<chain.size();c++) if(D[c]) g=c;
      vector<int> gb; if(g>=0){ const Nd&ng=nodes[chain[g]]; for(int t=0;t<=ng.rs;t++) gb.push_back(Q[ng.ri][t]); if(ng.dim>=dimF-1) gb.clear(), g=-2; }
      if(g!=-2){ int bq=-1,bs=VIRT-1; M lf=N->left;
        for(int q=1;q<512;q++){ bool ok=true; for(int b:gb) if(par(q,b)){ok=false;break;} if(!ok) continue;
          bool proper=false; for(int x=1;x<512&&!proper;x++) if(has(F,x)&&par(x,q)) proper=true; if(!proper) continue;
          int sc=0; for(M B=lf;B;B&=B-1) if(!par(P[ctz(B)],q)) sc++;
          if(sc>bs){bs=sc;bq=q;} }
        if(bq>0){ Span h; memset(&h,0,sizeof h); for(int x=0;x<512;x++) if(has(F,x)&&!par(x,bq)) setb(h,x);
          M Th=0; for(M B=lf;B;B&=B-1){int i=ctz(B); if(!par(P[i],bq)) Th|=bit(i);}
          auto ch=build(h,hashSpan(h),dimF-1,Th,true,-5,bq,0,depth+1,sj);
          if(ch->tb.empty()){ vector<int> bb; Span sp; memset(&sp,0,sizeof sp); setb(sp,0); for(int x=1;x<512;x++) if(has(h,x)&&!has(sp,x)){ bb.push_back(x); Span nx=sp; for(int y=0;y<512;y++) if(has(sp,y)) setb(nx,y^x); sp=nx; } ch->tb=bb; }
          if(ch->T!=ch->left){ N->lri=-1; N->kids.push_back({-5,bq,ch}); N->left=(lf&~Th)|ch->left;
            vector<int> rd2=N->rd; rd2.pop_back(); if(rd2.empty()||rd2.back()!=dimF-1) rd2.push_back(dimF-1); rd2.push_back(dimF); N->rd=rd2; N->taxH=taxChain(rd2,true); N->taxY=taxChain(rd2,false); } } }
    }
    if(doTop && N->left) N->lri=-1;
    if(doTop){ M tl=N->left; while(tl){ auto sib=build(F,Fh,dimF,tl,true,topI,topS,topJ,depth+1,sj,false); if(sib->T==sib->left){ fprintf(stderr,"FATAL stuck sibling\n"); exit(3);} N->kids.push_back({-1,-1,sib}); tl=sib->left; } N->left=0; }
  } else if(left) N->left=left;
  if(!nomemo) memo[key]=N; return N;
}
// ---- registry
struct RK{ u64 Fh; M T; u64 sg; bool operator==(const RK&o)const{return Fh==o.Fh&&T==o.T&&sg==o.sg;} };
struct RKH{ size_t operator()(const RK&k)const{ return k.Fh*0x9e3779b97f4a7c15ULL ^ (u64)k.T*1099511628211ULL ^ (u64)(k.T>>64)*0xc2b2ae3d27d4eb4fULL ^ k.sg*0x165667b19e3779f9ULL;} };
struct RE{ int ref; shared_ptr<NodeS> node; int rj; };
static int CURJ=-1;
static unordered_map<RK,RE,RKH> reg;
static vector<vector<int>> cnt; static double Ereg=0;
static void cntAdj(const NodeS*N,int d){ for(auto&pr:N->picks) cnt[pr.first][pr.second]+=d; }
static void cntAdjC(const NodeS*N,int d){ for(auto&pr:N->picks){ cnt[pr.first][pr.second]+=d; if(!cntC.empty()) cntC[pr.first][pr.second]+=d; } }
static RK rkOf(const NodeS*c,int j){ return RK{c->Fh,c->T,signHash(c->T,j)^(c->strict?0x5bd1e995ULL:0)^(c->doTop?0x1b873593ULL:0)}; }
typedef pair<RK,shared_ptr<NodeS>> KP;
static void regInc(const RK&k,const shared_ptr<NodeS>&N){ auto it=reg.find(k); if(it==reg.end()){ reg[k]={1,N,CURJ}; Ereg+=N->taxH; cntAdj(N.get(),+1);} else it->second.ref++; }
static void regDec(const RK&k){ auto it=reg.find(k); if(--it->second.ref==0){ Ereg-=it->second.node->taxH; cntAdj(it->second.node.get(),-1); reg.erase(it);} }
static void rootyHook(const Span&F,int dimF,M T,bool strict,int sj,vector<Nd>&nodes,vector<u64>&hh,vector<shared_ptr<NodeS>>&hubItems,vector<char>&isTrie){
  // ROOTY: the root build reads Y-side registry hubs (X-stop top inside H_k, support inside the root's target, content proportional to S_k): residual supply doubling as root build
  for(auto&e:reg){ int rj=e.second.rj; if(rj<0 || rj>=n) continue; const auto&c=e.second.node; if(c->topI<0) continue; M cT=c->T&~c->left; if(!cT || (cT&~T)) continue; if(c->topS+1>dimF || (strict && c->topS+1==dimF)) continue;
    bool in=true; for(int t=0;t<=c->topS&&in;t++) if(!has(F,Q[c->topI][t])) in=false; if(!in) continue;
    int s0=0; bool cons=true; for(M B=cT;B&&cons;B&=B-1){ int i=ctz(B); int v=SG[sj][i]*SG[rj][i]; if(!v) cons=false; else if(!s0) s0=v; else if(v!=s0) cons=false; } if(!cons) continue;
    u64 h=HS[c->topI][c->topS]; int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==h){id=a;break;}
    if(id<0){ id=nodes.size(); nodes.push_back({c->topS+1,c->topI,c->topS,0,{},&SP[c->topI][c->topS],nullptr,h}); hh.push_back(h);}
    nodes[id].pm|=cT; nodes[id].it.push_back({-1-(int)hubItems.size(),cT}); hubItems.push_back(c); isTrie.push_back(3); } }
static void walk(const shared_ptr<NodeS>&N,int j,vector<KP>&out){ for(auto&k:N->kids){ RK key=rkOf(k.node.get(),j); out.push_back({key,k.node}); walk(k.node,j,out);} }
static vector<shared_ptr<NodeS>> root; static vector<double> cost; static vector<vector<KP>> keysY;
// ---- copies (root signal carriers u(j,k), lines l_k with C_jk != 0)
static int USECOPY=0; static double COPYBASE=0; static vector<vector<int>> LN; static vector<vector<pair<int,shared_ptr<NodeS>>>> copyN;
// ---- pairs
static vector<int> pr; static vector<Span> VS; static vector<u64> VH; static vector<int> agreeRole;
static M fullT(int j){ M T=0; for(int i:O[j]) T|=bit(i); return T; }
static void setV(int j){ int k=pr[j]; Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,P[j])&&!par(x,P[k])) setb(S,x); VS[j]=S; VH[j]=hashSpan(S); }
static M vin(int j){ int k=pr[j]; bool ag=agreeRole[j]; M T=0; for(int i:O[j]) if(!par(P[i],P[k])){ bool a=(SG[j][i]==SG[k][i]); if(a==ag) T|=bit(i); } return T; }
static M vout(int j){ int k=pr[j]; M T=0; for(int i:O[j]) if(par(P[i],P[k])) T|=bit(i); return T; }
static void hmAddTree(const NodeS*N){ for(auto&p:N->picks) if(p.second>HM[p.first]) HM[p.first]=p.second; for(auto&k:N->kids) hmAddTree(k.node.get()); }
static int HMRT=0, HMRTok=0; static vector<int> HMRTc;
static void computeHM(const NodeS*extra){   // highest pre-root stop of every X (hub/Y/root-tree picks, absorptions), + the picks of a tree being built
  HM.assign(n,-1);
  if(HMRT && ROOTP){   // relaxed: only ROOT-TREE hubs are forced pre-root (Y-side hubs may run post-root; glue must phase them)
    if(!HMRTok){ HMRTc.assign(n,-1); for(int r=n;r<NR;r++) if((*ROOTP)[r]){ vector<shared_ptr<NodeS>> all; collectNodes((*ROOTP)[r],all); for(auto&c:all) for(auto&p:c->picks) if(p.second>HMRTc[p.first]) HMRTc[p.first]=p.second; } HMRTok=1; }
    HM=HMRTc; extra=nullptr; }
  else for(int i=0;i<n;i++){ for(int s=L-1;s>=0;s--) if(cnt[i][s]-cntC[i][s]>0){ HM[i]=s; break; } }
  for(int a=0;a<n;a++) if(absS[a]>=0){ if(absS[a]>HM[a]) HM[a]=absS[a]; for(M B=absSet[a];B;B&=B-1){ int b=ctz(B); if(absS[a]>HM[b]) HM[b]=absS[a]; } }
  if(extra) hmAddTree(extra);
}
static int viol(){ if(!JOINT) return 0; computeHM(nullptr); int v=0; for(int i=0;i<n;i++) for(int s=0;s<HM[i];s++) if(cntC[i][s]>0){ v++; break; } return v; }
static double subTax(const NodeS*N,vector<const NodeS*>&seen){ if(find(seen.begin(),seen.end(),N)!=seen.end()) return 0; seen.push_back(N); double t=N->taxH; for(auto&k:N->kids) t+=subTax(k.node.get(),seen); return t; }
// top-level placement of the leftover tl of reader j: optionally root copies first (post-root spines through <l_k>), then plain siblings at Q_j.
// returns copy marginal tax (charged to the reader) in *cm and an APPROXIMATE total (copy marginals + subtree hub taxes, sharing ignored) used to choose copies vs none.
static double sibTax(int j,M tl,int kvi,vector<Kid>*kids){ double tot=0; vector<const NodeS*> seen;
  while(tl){ auto sib=build(QS[j],QH[j],8,tl,true,-1,-1,j,1,j,false); if(sib->T==sib->left){fprintf(stderr,"FATAL stuck sibling (sibTax)\n");exit(3);} if(kids) kids->push_back({kvi,kvi,sib}); tot+=subTax(sib.get(),seen); tl=sib->left; }
  return tot; }
// top-level placement of reader j's leftover tl: the root copies switched on in CU[j] (SA state; post-root spines through <l_k>) take ports first, then plain siblings at Q_j.
static vector<int> CU;
static void chooseTop(int j,M tl,int kvi,vector<Kid>&kids,double*cm){
  double c=0;
  for(size_t t=0;t<LN[j].size();t++){ if(!tl) break; if(!((CU[j]>>t)&1)) continue; int l=LN[j][t]; auto C=build(QS[j],QH[j]^((u64)l*0x9E3779B97F4A7C15ULL),8,tl,true,-4,l,j,1,j,false,l);
      if(C->left==C->T) continue;
      vector<int> rd2; rd2.push_back(1); for(int x:C->rd) rd2.push_back(x); c+=taxChain(rd2,true)-COPYBASE+COPYPEN; copyN[j].push_back({l,C}); tl=C->left; }
  sibTax(j,tl,kvi,&kids); *cm=c; }
static shared_ptr<TF> mkTF(const vector<int>&bas,int cum,int k){ auto f=make_shared<TF>(); f->bas=bas; f->cum=cum; Span S; memset(&S,0,sizeof S); setb(S,0);
  for(int v:bas){ if(has(S,v)) return nullptr; Span nx=S; for(int x=0;x<512;x++) if(has(S,x)) setb(nx,x^v); S=nx; }
  for(int x=1;x<512;x++) if(has(S,x) && par(x,RU[k])) return nullptr;   // must lie in H_k
  f->sp=S; f->h=hashSpan(S); f->dim=bas.size(); f->sup=0; f->ports=0; for(int i=0;i<n;i++) if(has(S,P[i])) f->ports|=bit(i); return f; }
static void buildTrie(int k){   // trie nodes: shell S(F) = ports(F) minus ports(parent) built from X stops under virtual top F; cumulative C(F) = full(parent)@parent + S(F)@F
  TI[k].clear(); auto&V=TR[k]; vector<int> ord(V.size()); for(size_t a=0;a<V.size();a++) ord[a]=a; stable_sort(ord.begin(),ord.end(),[&](int a,int b){return V[a]->dim<V[b]->dim;});
  vector<shared_ptr<NodeS>> full(V.size()), shell(V.size()); vector<int> pa(V.size(),-1);
  for(int a:ord){ const TF&f=*V[a]; int p=-1; if(!f.sup) for(int b:ord){ if(V[b]->dim>=f.dim) break; if(V[b]->sup) continue; if(spanSub(V[b]->sp,f.sp) && (p<0 || V[b]->dim>V[p]->dim)) p=b; } pa[a]=p;
    M sh=f.sup? f.sup : f.ports&~(p>=0?V[p]->ports:(M)0);
    if(sh){ auto sv=VTB; VTB=&f.bas; NOTRIE=1; auto S=build(f.sp,f.h,f.dim,sh,true,-5,0,0,1,n+k,true); NOTRIE=0; VTB=sv; shell[a]=S; TI[k].push_back({S,V[a],p<0}); if(p<0) full[a]=S; }
    if(p>=0 && f.cum && sh && full[p]){ auto C=make_shared<NodeS>(); C->Fh=f.h; C->T=f.ports; C->strict=true; C->left=0; C->doTop=true; C->topI=-5; C->topS=0; C->topJ=0; C->depth=1; C->tb=f.bas;
      C->kids.push_back({-5,0,full[p]}); C->kids.push_back({-5,0,shell[a]}); C->rd={V[p]->dim,f.dim}; C->taxH=taxChain(C->rd,true); C->taxY=taxChain(C->rd,false); full[a]=C; TI[k].push_back({C,V[a],1}); } } }
static void evalY0(int j){
  copyN[j].clear(); if(j>=n) HMRTok=0;
  if(j>=n){   // ROOT READER k=j-n: owned root at H_k reads S_k-signed shared hubs; no spine, own cost 0
    if(PT) buildTrie(j-n);
    M T=0; for(int i=0;i<n;i++) if(SG[j][i]) T|=bit(i);
    auto W=make_shared<NodeS>(); W->Fh=hashSpan(RHS[j-n])^0x77ULL; W->T=T; W->strict=true; W->left=0; W->doTop=true; W->topI=-7; W->topS=RU[j-n]; W->topJ=0; W->depth=0; W->taxH=0; W->taxY=0; W->rd={8};
    M tl=T; while(tl){ auto sib=build(RHS[j-n],hashSpan(RHS[j-n])^0x77ULL,8,tl,true,-7,RU[j-n],0,1,j,false); if(sib->T==sib->left){fprintf(stderr,"FATAL stuck root sibling\n");exit(3);} W->kids.push_back({-1,-1,sib}); tl=sib->left; }
    root[j]=W; cost[j]=0; cntAdj(W.get(),+1); keysY[j].clear(); walk(W,j,keysY[j]); CURJ=j; for(auto&kp:keysY[j]) regInc(kp.first,kp.second); return;
  }
  if(pr[j]<0 && !USECOPY){ root[j]=build(QS[j],QH[j],8,fullT(j),false,-1,-1,j,0,j); cost[j]=root[j]->taxY; }
  else if(pr[j]<0){   // COPY CARRIERS: Y spine first, then each root copy u(j,k) (spine through <l_k>, base (1,7,1) already paid), then plain siblings at Q_j
    auto R=build(QS[j],QH[j],8,fullT(j),false,-1,-1,j,0,j,false);
    if(JOINT) computeHM(R.get());
    auto W=make_shared<NodeS>(*R); W->kids=R->kids; double c=R->taxY; M tl=R->left; W->left=0;
    if(JOINT){ double cm; chooseTop(j,tl,-1,W->kids,&cm); c+=cm; tl=0; }
    for(int l:LN[j]){ if(!tl) break; auto C=build(QS[j],QH[j]^((u64)l*0x9E3779B97F4A7C15ULL),8,tl,true,-4,l,j,1,j,false,l);
      if(C->left==C->T) continue; copyN[j].push_back({l,C}); vector<int> rd2; rd2.push_back(1); for(int x:C->rd) rd2.push_back(x); c+=taxChain(rd2,true)-COPYBASE; tl=C->left; }
    while(tl){ auto sib=build(QS[j],QH[j],8,tl,true,-1,-1,j,1,j,false); if(sib->T==sib->left){fprintf(stderr,"FATAL stuck Y sibling\n");exit(3);} W->kids.push_back({-1,-1,sib}); tl=sib->left; }
    root[j]=W; cost[j]=c;
  }
  else {
    int k=pr[j]; M Tin=vin(j), Tout=vout(j);
    auto W=make_shared<NodeS>(); W->Fh=VH[j]; W->T=Tin|Tout; W->strict=false; W->left=0; W->doTop=true; W->topI=-2; W->topS=k; W->topJ=j; W->depth=0;
    vector<int> rd;
    if(Tin){ auto R=build(VS[j],VH[j],7,Tin,false,-2,k,j,0,j); W->picks=R->picks; W->kids=R->kids; rd=R->rd; }
    if(JOINT) computeHM(W.get());
    if(rd.empty()||rd.back()!=7) rd.push_back(7);
    M tl=Tout; double cc=0;
    if(JOINT){ chooseTop(j,tl,-3,W->kids,&cc); tl=0; }
    /* copies for paired Ys: experimental, MH_PAIRCOPY only (python glue does not support it; init R0 worse on plan B) */
    if(USECOPY && (JOINT || getenv("MH_PAIRCOPY"))) for(int l:LN[j]){ if(!tl) break; auto C=build(QS[j],QH[j]^((u64)l*0x9E3779B97F4A7C15ULL),8,tl,true,-4,l,j,1,j,false,l);
      if(C->left==C->T) continue; copyN[j].push_back({l,C}); vector<int> rd2; rd2.push_back(1); for(int x:C->rd) rd2.push_back(x); cc+=taxChain(rd2,true)-COPYBASE; tl=C->left; }
    while(tl){ auto sib=build(QS[j],QH[j],8,tl,true,-1,-1,j,1,j,false); if(sib->T==sib->left){fprintf(stderr,"FATAL stuck Q sibling\n");exit(3);} W->kids.push_back({-3,-3,sib}); tl=sib->left; }
    rd.push_back(8); W->rd=rd; W->taxY=taxChain(rd,false); W->taxH=0; root[j]=W; cost[j]=W->taxY+cc;
  }
  cntAdj(root[j].get(),+1); for(auto&cp:copyN[j]) cntAdjC(cp.second.get(),+1);
  keysY[j].clear(); walk(root[j],j,keysY[j]); for(auto&cp:copyN[j]) walk(cp.second,j,keysY[j]); CURJ=j; for(auto&kp:keysY[j]) regInc(kp.first,kp.second);
}
static int chkNode(const NodeS*N,int depth){ M c=0; for(auto&p:N->picks){ int i=p.first,s=p.second; M mk=(absS[i]>=0 && s>=absS[i] && !transparent(i,s))?packet(i):bit(i); c|=mk; } for(auto&k:N->kids) c|=k.node->T&~k.node->left;
  if(c!=(N->T&~N->left)){ fprintf(stderr,"CHK node mismatch depth %d topI %d T %d cov %d picks %zu kids %zu left %d\n",depth,N->topI,pc(N->T),pc(c),N->picks.size(),N->kids.size(),pc(N->left)); return 1; }
  for(auto&k:N->kids) if(chkNode(k.node.get(),depth+1)) return 1; return 0; }
static void dropY(int j);
static void evalY(int j){   // PT_DUAL: cost-aware use of the partial-root offers: build with and without, keep the lower marginal R0 (own cost + new registry tax)
  if(!PT || !DUAL){ evalY0(j); return; }
  int&o=(j>=n)?OFR[j-n]:OF[j]; double e0=Ereg;
  o=1; evalY0(j); double c1=Ereg-e0+cost[j]; dropY(j);
  o=0; evalY0(j); double c0=Ereg-e0+cost[j];
  DUALN++; if(c1<c0-1e-9){ dropY(j); o=1; evalY0(j); DUALON++; } }
static void dropY(int j){ if(j>=n) HMRTok=0; for(auto&kp:keysY[j]) regDec(kp.first); cntAdj(root[j].get(),-1); for(auto&cp:copyN[j]) cntAdjC(cp.second.get(),-1); }
static double taxXi(int i){ double t=RL[8]; int prev=1; for(int s=1;s<L;s++){ bool u=cnt[i][s]>0; if(!u && absS[i]==s && absSet[i]) u=true;
    if(!u) for(int a=0;a<n && !u;a++) if(absS[a]==s && (absSet[a]&bit(i))) u=true;
    if(u){int d=s+1; t-=RL[d-prev]; prev=d;} } t-=RL[9-prev]; return t; }
static double taxXall(){ double t=0; for(int i=0;i<n;i++) t+=taxXi(i); return t; }
static double totE(){ double e=Ereg+taxXall(); for(int j=0;j<NR;j++) e+=cost[j]; if(JOINT) e+=1e4*viol(); return e; }
// valid absorption: sources at the same frame (stop sa) and clean there; a is not a source of an absorption at >= its own stop
static bool absValid(int a){ if(absS[a]<0) return true; int s=absS[a];
  for(M B=absSet[a];B;B&=B-1){ int b=ctz(B); if(HS[b][s]!=HS[a][s]) return false; if(absS[b]>=0 && absS[b]<=s) return false; }
  for(int c=0;c<n;c++) if(absS[c]>=0 && (absSet[c]&bit(a)) && absS[a]<=absS[c]) return false;
  return true; }
static void memoInval(M mask){ for(auto it2=memo.begin();it2!=memo.end();){ if(it2->first.T&mask) it2=memo.erase(it2); else ++it2; } }
#include "k2net.inc"
#include "k2search.inc"
int main(int argc,char**argv){
  if(getenv("K2_NET")&&getenv("K2_SEARCH")) return searchMain(getenv("K2_NET"),getenv("K2_SEARCH"));
  if(getenv("K2_NET")) return netMain(getenv("K2_NET"));
  if(argc<7){fprintf(stderr,"usage\n");return 1;}
  FILE*f=fopen(argv[1],"r"); fscanf(f,"%d",&n); P.resize(n); for(int i=0;i<n;i++) fscanf(f,"%d",&P[i]); fclose(f);
  SG.assign(n,vector<int>(n,0)); f=fopen(argv[2],"r"); for(int j=0;j<n;j++) for(int i=0;i<n;i++) fscanf(f,"%d",&SG[j][i]); fclose(f);
  if(getenv("K2_L")) L=atoi(getenv("K2_L"));
  if(getenv("FL_FREEZE")) FLFREEZE=1; if(getenv("FL_LATP")) FLLAT=atof(getenv("FL_LATP"));
  u64 seed=atoll(argv[3]); long iters=atol(argv[4]); double T0=atof(argv[5]),T1=atof(argv[6]);
  if(argc>8) MAXD=atoi(argv[8]);
  rng.s=seed*2654435761ULL+88172645463325252ULL; for(int a=0;a<10;a++) rng.next();
  for(int r=1;r<64;r++) RL[r]=r*log((double)r); RL[0]=0;
  Q.assign(n,vector<int>(L,0)); SP.assign(n,vector<Span>(L)); HS.assign(n,vector<u64>(L,0));
  O.assign(n,{}); for(int j=0;j<n;j++) for(int i=0;i<n;i++) if(!par(P[i],P[j])) O[j].push_back(i);
  QS.resize(n); QH.resize(n); for(int j=0;j<n;j++){ Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,P[j])) setb(S,x); QS[j]=S; QH[j]=hashSpan(S); }
  if(argc>7 && strcmp(argv[7],"-")){ FILE*g=fopen(argv[7],"r"); for(int i=0;i<n;i++) for(int s=0;s<L;s++) fscanf(g,"%d",&Q[i][s]); fclose(g); for(int i=0;i<n;i++){Q[i][0]=P[i]; rebuild(i,0);} }
  else for(int i=0;i<n;i++){ Q[i][0]=P[i]; buildSpan(i,0); for(int s=1;s<L;s++){ int v; do{ v=P[rng.r(n)]; }while(!indep(i,s,v)); Q[i][s]=v; buildSpan(i,s);} }
  NR=n; RD.assign(n,{}); for(int i=0;i<n;i++) RD[i]=O[i];
  if(getenv("MH_ROOTTREE")){ FILE*g=fopen(getenv("MH_ROOTTREE"),"r"); int u; while(fscanf(g,"%d",&u)==1){ vector<int> row(n); for(int i=0;i<n;i++) fscanf(g,"%d",&row[i]); SG.push_back(row);
      Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,u)) setb(S,x); RU.push_back(u); RHS.push_back(S); for(int i=0;i<n;i++) if(row[i]) RD[i].push_back(NR); NR++; } fclose(g); }
  cnt.assign(n,vector<int>(L,0)); root.assign(NR,nullptr); cost.assign(NR,0); keysY.assign(NR,{});
  pr.assign(NR,-1); VS.resize(NR); VH.assign(NR,0); agreeRole.assign(NR,0);
  absS.assign(n,-1); absSet.assign(n,0); absSig.assign(n,vector<int>(n,1));
  if(argc>9 && strcmp(argv[9],"-")){ FILE*g=fopen(argv[9],"r"); int a,b,r; while(fscanf(g,"%d %d %d",&a,&b,&r)==3){ pr[a]=b; pr[b]=a; agreeRole[a]=r; agreeRole[b]=!r; } fclose(g); }
  if(argc>10) PAIRP=atof(argv[10]);
  if(argc>11) ABSP=atof(argv[11]);
  if(argc>12 && strcmp(argv[12],"-")){ FILE*g=fopen(argv[12],"r"); int a,s,k; while(fscanf(g,"%d %d %d",&a,&s,&k)==3){ absS[a]=s; for(int t=0;t<k;t++){int b,sg; fscanf(g," %d:%d",&b,&sg); absSet[a]|=bit(b); absSig[a][b]=sg;} } fclose(g);
    for(int a=0;a<n;a++) if(!absValid(a)){ fprintf(stderr,"init absorption %d invalid, dropped\n",a); absS[a]=-1; absSet[a]=0; } }
  copyN.assign(NR,{}); LN.assign(NR,{});
  if(getenv("MH_LINES")){ USECOPY=1; FILE*g=fopen(getenv("MH_LINES"),"r"); for(int j=0;j<n;j++){ int c; fscanf(g,"%d",&c); for(int t=0;t<c;t++){int l; fscanf(g,"%d",&l); LN[j].push_back(l);} } fclose(g); }
  if(getenv("JF_JOINT")){ JOINT=1; for(int j=0;j<n;j++) for(int l:LN[j]) if(find(ALLL.begin(),ALLL.end(),l)==ALLL.end()) ALLL.push_back(l); LM.assign(n,vector<int>(L,0)); for(int i=0;i<n;i++) rebuild(i,0);
    for(int a=0;a<n;a++) if(absS[a]>=0 && LM[a][absS[a]]){ absS[a]=-1; absSet[a]=0; } fprintf(stderr,"JOINT mode: %zu lines\n",ALLL.size()); }
  COPYBASE=taxChain(vector<int>{1,8},true); if(getenv("MH_VIRT")) VIRT=atoi(getenv("MH_VIRT")); if(getenv("JF_LINEP")) LINEP=atof(getenv("JF_LINEP")); if(getenv("JF_RLINEP")) RLINEP=atof(getenv("JF_RLINEP")); if(getenv("JF_COPYPEN")) COPYPEN=atof(getenv("JF_COPYPEN"));
  for(int j=0;j<n;j++) if(pr[j]>=0) setV(j);
  if(getenv("MH_PROV")){   // PRICING ONLY (COPYFOLD plan): unsigned frame sums F(V), V=<a,b>^perp, built as shared hubs (signs all +, row n); prints R0 and exits
    SG.push_back(vector<int>(n,1)); FILE*g=fopen(getenv("MH_PROV"),"r"); int a,b,np=0; double top=0; vector<shared_ptr<NodeS>> PR;
    while(fscanf(g,"%d %d",&a,&b)==2){ Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,a)&&!par(x,b)) setb(S,x); M T=0; for(int i=0;i<n;i++) if(has(S,P[i])) T|=bit(i);
      auto R=build(S,hashSpan(S),7,T,false,-6,a,b,0,n); RK key=rkOf(R.get(),n); regInc(key,R); vector<KP> ks; walk(R,n,ks); for(auto&kp:ks) regInc(kp.first,kp.second); np++; }
    fclose(g); double tx=taxXall(); fprintf(stderr,"PROV %d providers: shared hubs %zu (incl. provider roots) tax %.1f, X tax %.1f\n",np,reg.size(),Ereg,tx); printf("PROV %d %.2f %.2f %zu\n",np,Ereg,tx,reg.size()); return 0; }
  if(JOINT) cntC.assign(n,vector<int>(L,0));
  CU.assign(NR,0); if(getenv("JF_CUINIT")){ FILE*g=fopen(getenv("JF_CUINIT"),"r"); int j,m; while(fscanf(g,"%d %d",&j,&m)==2) CU[j]=m; fclose(g); }
  double COPYP=getenv("JF_COPYP")?atof(getenv("JF_COPYP")):0.0;
  ROOTP=&root; if(getenv("JF_HUBREAD")) HUBREAD=1; if(getenv("JF_HMRT")) HMRT=1;
  double LIFTP=getenv("PT_LIFTP")?atof(getenv("PT_LIFTP")):0.0; int LIFTMIN=getenv("PT_LIFTMIN")?atoi(getenv("PT_LIFTMIN")):2; int NK=NR-n; double TRIEP=getenv("PT_TRIEP")?atof(getenv("PT_TRIEP")):0.0; int TRIEMAXD=getenv("PT_MAXD")?atoi(getenv("PT_MAXD")):5;
  vector<vector<int>> RDK(NK);   // Ys that can read root k's trie (l_k in Q_j)
  OF.assign(n,getenv("PT_OFINIT")?atoi(getenv("PT_OFINIT")):1); OFR.assign(NR-n,1); if(getenv("PT_DUAL")) DUAL=1; double OFP=getenv("PT_OFP")?atof(getenv("PT_OFP")):0.0;
  if(getenv("PT_ALLROOT")) PTALL=1; if(getenv("PT_NORR")) NORR=1; if(getenv("PT_LASTRUNG")) LASTR=1; RNo.assign(NR-n,nullptr); RNc.assign(NR-n,{});
  if(getenv("PT")){ PT=1; TR.assign(NK,{}); TI.assign(NK,{}); LK.assign(NK,0);
    for(int j=0;j<n;j++) for(int l:LN[j]){ int k=rootOfLine(l); if(k>=0) LK[k]=l; }
    for(int k=0;k<NK;k++){ if(!LK[k]){ fprintf(stderr,"FATAL no line for root %d\n",k); exit(5);} for(int j=0;j<n;j++) if(!par(LK[k],P[j])) RDK[k].push_back(j); }
    if(getenv("PT_TRIE")){ FILE*g=fopen(getenv("PT_TRIE"),"r"); char buf[4096]; int nf=0; while(fgets(buf,sizeof buf,g)){ int k,c; int off=0; if(sscanf(buf,"%d %d%n",&k,&c,&off)<2) continue; vector<int> b; int v,o2; char*p=buf+off; while(sscanf(p,"%d%n",&v,&o2)==1){ b.push_back(v); p+=o2; }
        auto f=mkTF(b,c,k); if(!f){ fprintf(stderr,"trie frame rejected (dependent or not in H_k)\n"); continue; } bool dup=false; for(auto&x:TR[k]) if(x->h==f->h) dup=true; if(!dup){ TR[k].push_back(f); nf++; } } fclose(g); fprintf(stderr,"PT: %d trie frames loaded\n",nf); }
    fprintf(stderr,"PT mode: %d roots, TRIEP %.3f\n",NK,TRIEP); }
  if(getenv("PT_ROOTY")){ ROOTY=1; ROOTYHOOK=rootyHook; }
  if(ROOTY){ for(int j=0;j<n;j++) evalY(j); for(int j=n;j<NR;j++) evalY(j); } else { for(int j=n;j<NR;j++) evalY(j); for(int j=0;j<n;j++) evalY(j); }
  for(int pass=0;JOINT && pass<8;pass++){ int v=viol(); fprintf(stderr,"repair pass %d: %d violating X\n",pass,v); if(!v) break;
    computeHM(nullptr); vector<int> bad; for(int j=0;j<n;j++){ bool b=false; for(auto&cp:copyN[j]) for(auto&p:cp.second->picks) if(p.second<HM[p.first]) b=true; if(b) bad.push_back(j); }
    for(int j:bad){ dropY(j); evalY(j); } }
  double E=totE(); fprintf(stderr,"init E %.1f (reg %.1f hubs %zu) viol %d\n",E,Ereg,reg.size(),viol());
  if(getenv("MH_ROOTS")){   // PRICING ONLY: front end as S_k-signed shared trees read by root k at H_k, in the SAME registry as the Y trees
    FILE*g=fopen(getenv("MH_ROOTS"),"r"); int u; double e0=Ereg, x0=taxXall(); size_t h0=reg.size(); int nk=0;
    while(fscanf(g,"%d",&u)==1){ vector<int> row(n); for(int i=0;i<n;i++) fscanf(g,"%d",&row[i]); SG.push_back(row); int sj=SG.size()-1;
      Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,u)) setb(S,x); M T=0; for(int i=0;i<n;i++) if(row[i]) T|=bit(i);
      auto R=build(S,hashSpan(S)^0x77ULL,8,T,true,-7,u,0,1,sj,true); vector<KP> ks; walk(R,sj,ks); for(auto&kp:ks) regInc(kp.first,kp.second); nk++; }
    fclose(g); fprintf(stderr,"ROOTS %d trees: +%.1f hub tax (+%zu hubs), X tax %+.1f\n",nk,Ereg-e0,reg.size()-h0,taxXall()-x0); return 0; }
  double bestE=E; auto bestQ=Q; auto bestPr=pr, bestRole=agreeRole; auto bestAS=absS; auto bestASet=absSet; auto bestSig=absSig; auto bestCU=CU; auto bestTR=TR; auto bestOF=OF; long acc=0,pacc=0,aacc=0,tacc=0;
  // generic trial: the caller passes the Ys to re-evaluate, setters for the NEW and OLD state, and the memo invalidation mask
  auto trial=[&](vector<int>&aff,const function<void()>&applyNew,const function<void()>&applyOld,M inval,double T)->bool{
    sort(aff.begin(),aff.end()); aff.erase(unique(aff.begin(),aff.end()),aff.end()); stable_partition(aff.begin(),aff.end(),[](int a){return ROOTY? a<n : a>=n;});   // roots first: copies may read their trees
    vector<vector<TItem>> oldTI; if(PT) oldTI=TI;
    applyOld(); vector<shared_ptr<NodeS>> oldroot; vector<double> oldcost; vector<vector<KP>> oldkeys; vector<vector<pair<int,shared_ptr<NodeS>>>> oldcp;
    for(int a:aff){ oldroot.push_back(root[a]); oldcost.push_back(cost[a]); oldkeys.push_back(keysY[a]); oldcp.push_back(copyN[a]); dropY(a); }
    vector<pair<MK,shared_ptr<NodeS>>> bak; for(auto it2=memo.begin();it2!=memo.end();){ if(it2->first.T&inval){ bak.push_back(*it2); it2=memo.erase(it2);} else ++it2; }
    applyNew(); for(int a:aff) evalY(a);
    double E2=totE(); double d=E2-E;
    if(d<=0 || rng.u()<exp(-d/T)){ E=E2; acc++; if(E<bestE-1e-9){bestE=E; bestQ=Q; bestPr=pr; bestRole=agreeRole; bestAS=absS; bestASet=absSet; bestSig=absSig; bestCU=CU; bestTR=TR; bestOF=OF;} return true; }
    for(int a:aff) dropY(a); memoInval(inval); for(auto&b:bak) memo[b.first]=b.second; applyOld();
    if(PT) TI=oldTI;
    for(size_t a=0;a<aff.size();a++){ int jj=aff[a]; root[jj]=oldroot[a]; cost[jj]=oldcost[a]; keysY[jj]=oldkeys[a]; copyN[jj]=oldcp[a]; cntAdj(root[jj].get(),+1); for(auto&cp:copyN[jj]) cntAdjC(cp.second.get(),+1); CURJ=jj; for(auto&kp:keysY[jj]) regInc(kp.first,kp.second); }
    return false; };
  for(long it=0;it<iters;it++){
    double T=T0*pow(T1/T0,(double)it/iters);
    if(it%2000==0) if(PT && it%2000==0){ int nf=0; for(auto&v:TR) nf+=v.size(); fprintf(stderr,"   trie frames %d tacc %ld ptreads(cum) %ld\n",nf,tacc,PTREADS); }
    if(it%2000==0) fprintf(stderr,"it %ld T %.3f E %.1f best %.1f acc %ld pacc %ld aacc %ld pairs %d absorbers %d hubs %zu memo %zu\n",it,T,E,bestE,acc,pacc,aacc,
        (int)count_if(pr.begin(),pr.end(),[](int x){return x>=0;})/2,(int)count_if(absS.begin(),absS.end(),[](int x){return x>=0;}),reg.size(),memo.size());
    if(memo.size()>400000) memo.clear();
    double mvr=rng.u();
    if(PT && rng.u()<OFP){ int j=rng.r(n); int o=OF[j]; vector<int> aff{j}; trial(aff,[&]{OF[j]=!o;},[&]{OF[j]=o;},0,T); continue; }
    if(PT && rng.u()<TRIEP){   // ---- PARTIALTRIE move: add / drop / mutate / cum-toggle one frame of root k's trie
      int k=rng.r(NK); auto oldT=TR[k]; auto newT=oldT; double mv=rng.u(); vector<shared_ptr<TF>> ch;
      auto Vports=[&](int j){ vector<int> v; for(int i:O[j]) if(SG[n+k][i]) v.push_back(i); return v; };
      if(LIFTP>=1.0) mv=0.45+rng.u()*(LIFTP+0.30);   // lift-only mode: no free frames (lift / drop only)
      if(LIFTP<1.0 && (mv<0.45 || newT.empty())){
        int j=RDK[k][rng.r(RDK[k].size())]; auto vp=Vports(j); vector<int> b;
        vector<int> ext; for(size_t a=0;a<newT.size();a++){ bool in=true; for(int v:newT[a]->bas) if(par(v,P[j])){in=false;break;} if(in && newT[a]->dim<TRIEMAXD) ext.push_back(a); }
        if(!ext.empty() && rng.u()<0.6){ b=newT[ext[rng.r(ext.size())]]->bas; } else b={LK[k]};
        int add=1+((b.size()==1)?rng.r(3):0); bool okb=true;
        for(int t=0;t<add && okb;t++){ int tr=0; while(tr<30){ int i=vp[rng.r(vp.size())]; vector<int> b2=b; b2.push_back(P[i]); if(mkTF(b2,0,k)){ b=b2; break;} tr++; } if(tr>=30) okb=false; }
        if(!okb || (int)b.size()>TRIEMAXD) continue;
        auto f=mkTF(b,rng.r(2),k); if(!f) continue; bool dup=false; for(auto&x:newT) if(x->h==f->h) dup=true; if(dup) continue;
        newT.push_back(f); ch.push_back(f); }
      else if(mv<0.45+LIFTP){   // LIFT: an X meeting frame G (co-present X stops) inside H_k, l_k not in G -> piece = the co-present root-k ports, virtual top G+l_k
        vector<int> hp; for(int i=0;i<n;i++) if(SG[n+k][i]) hp.push_back(i); int i=hp[rng.r(hp.size())]; int st=1+rng.r(4);
        bool in=true; for(int t=0;t<=st&&in;t++) if(par(Q[i][t],RU[k])) in=false; if(!in || has(SP[i][st],LK[k])) continue;
        M co=0; for(int b:hp) if(HS[b][st]==HS[i][st]) co|=bit(b); if(pc(co)<LIFTMIN) continue;
        vector<int> b(Q[i].begin(),Q[i].begin()+st+1); b.push_back(LK[k]); auto f=mkTF(b,0,k); if(!f) continue; f->sup=co; f->ports=co;
        bool dup=false; for(auto&x:newT) if(x->h==f->h) dup=true; if(dup) continue; newT.push_back(f); ch.push_back(f); }
      else if(mv<0.75+LIFTP){ if(newT.empty()) continue; int a=rng.r(newT.size()); ch.push_back(newT[a]); newT.erase(newT.begin()+a); }
      else if(mv<0.9){ if(newT.empty()) continue; int a=rng.r(newT.size()); auto b=newT[a]->bas; if(b.size()<2) continue; int t=1+rng.r(b.size()-1);
        vector<int> hp; for(int i=0;i<n;i++) if(SG[n+k][i]) hp.push_back(i); b[t]=P[hp[rng.r(hp.size())]];
        auto f=mkTF(b,newT[a]->cum,k); if(!f) continue; bool dup=false; for(auto&x:newT) if(x->h==f->h) dup=true; if(dup) continue; ch.push_back(newT[a]); ch.push_back(f); newT[a]=f; }
      else { if(newT.empty()) continue; int a=rng.r(newT.size()); auto f=make_shared<TF>(*newT[a]); f->cum=!f->cum; ch.push_back(f); newT[a]=f; }
      M inv=0; vector<int> aff{n+k};
      for(auto&f:ch){ inv|=f->ports; for(int j:RDK[k]){ bool in=true; for(int v:f->bas) if(par(v,P[j])){in=false;break;} if(in) aff.push_back(j); } }
      if(trial(aff,[&]{TR[k]=newT;},[&]{TR[k]=oldT;},inv,T)) tacc++;
      continue; }
    if(JOINT && rng.u()<COPYP){   // ---- copy toggle (reader-local)
      int j=rng.r(n); if(LN[j].empty()) continue; int t=rng.r(LN[j].size()); int oc=CU[j], nc=CU[j]^(1<<t); vector<int> aff{j};
      trial(aff,[&]{CU[j]=nc;},[&]{CU[j]=oc;},0,T); continue; }
    if(mvr<PAIRP){
      int j=rng.r(n), k=pr[j]; vector<int> aff; auto opr=pr; auto orole=agreeRole; double mv=rng.u();
      auto unp=[&](int a){ if(a>=0 && pr[a]>=0){ int b=pr[a]; pr[a]=-1; pr[b]=-1; aff.push_back(a); aff.push_back(b);} };
      if(k>=0 && mv<0.15){ unp(j); }
      else if(k>=0 && mv<0.3){ agreeRole[j]=!agreeRole[j]; agreeRole[k]=!agreeRole[k]; aff.push_back(j); aff.push_back(k); }
      else { int l=rng.r(n); if(l==j || l==k){ pr=opr; continue; } int m2=pr[l]; unp(j); unp(l);
        pr[j]=l; pr[l]=j; agreeRole[j]=rng.r(2); agreeRole[l]=!agreeRole[j]; aff.push_back(j); aff.push_back(l);
        if(k>=0 && m2>=0 && rng.u()<0.8){ pr[k]=m2; pr[m2]=k; agreeRole[k]=rng.r(2); agreeRole[m2]=!agreeRole[k]; } }
      if(aff.empty()){ pr=opr; agreeRole=orole; continue; }
      auto npr=pr; auto nrole=agreeRole;
      if(trial(aff,[&]{pr=npr;agreeRole=nrole;for(int a:aff) if(pr[a]>=0) setV(a);},[&]{pr=opr;agreeRole=orole;for(int a:aff) if(pr[a]>=0) setV(a);},0,T)) pacc++;
      continue;
    }
    if(mvr<PAIRP+ABSP){   // ---- absorption move
      int a=rng.r(n); auto oS=absS; auto oSet=absSet; auto oSig=absSig[a];
      if(absS[a]>=0 && rng.u()<0.3){ absS[a]=-1; absSet[a]=0; }
      else {
        int s=1+rng.r(5);   // absorb at dims 2..6
        M cand=0; for(int b=0;b<n;b++) if(b!=a && HS[b][s]==HS[a][s] && (absS[b]<0||absS[b]>s)) cand|=bit(b);
        if(!cand) continue;
        vector<int> rds; for(int j:O[a]){ bool ok=true; for(int t=0;t<=s&&ok;t++) if(par(Q[a][t],P[j])) ok=false; if(ok) rds.push_back(j); }
        if(rds.empty()) continue;
        int j=rds[rng.r(rds.size())]; M S=0;
        for(M B=cand;B;B&=B-1){ int b=ctz(B); if(rng.u()<0.85){ S|=bit(b); absSig[a][b]=SG[j][b]*SG[j][a]; } }
        if(!S){ absSig[a]=oSig; continue; }
        absS[a]=s; absSet[a]=S;
        if(!absValid(a)){ absS=oS; absSet=oSet; absSig[a]=oSig; continue; }
      }
      auto nS=absS; auto nSet=absSet; auto nSig=absSig[a];
      M inv=bit(a); for(int c=0;c<n;c++) if((oS[c]>=0 && (oSet[c]&bit(a))) || (nS[c]>=0 && (nSet[c]&bit(a)))) inv|=bit(c);   // a's absorb stop changes transparency of packets it is a source of
      vector<int> aff; for(M B=inv;B;B&=B-1){ int c=ctz(B); for(int j:RD[c]) aff.push_back(j); }
      if(trial(aff,[&]{absS=nS;absSet=nSet;absSig[a]=nSig;},[&]{absS=oS;absSet=oSet;absSig[a]=oSig;},inv,T)) aacc++;
      continue;
    }
    // ---- X flag move (as hubladder)
    if(FLFREEZE) continue;   // FLAGS lane: flags fixed (helpers-only optimisation)
    int i=rng.r(n); int s=1+rng.r(L-1);
    vector<int> oldq=Q[i]; vector<Span> oldsp=SP[i]; vector<u64> oldh=HS[i];
    bool ok=true;
    if(JOINT && NR>n && rng.u()<RLINEP){   // JOINTFEED ROOT-LINE MOVE: put l_k into X_i's flag right above its largest prefix inside H_k (p_i in H_k): root-k tree hubs can then sit on frames holding l_k
      vector<int> ks; for(int k=0;k<NR-n;k++) if(SG[n+k][i]) ks.push_back(k); if(ks.empty()) continue; int k=ks[rng.r(ks.size())];
      int l=-1; for(int x:ALLL) if(rootOfLine(x)==k) l=x; if(l<0) continue;
      int s0=0; while(s0+1<L){ bool in=true; for(int t=0;t<=s0+1&&in;t++) if(par(Q[i][t],RU[k])) in=false; if(!in) break; s0++; }
      if(s0+1>=L || has(SP[i][s0],l)) continue;
      s=1+rng.r(s0+1); if(has(SP[i][s-1],l)) continue; Q[i][s]=l; buildSpan(i,s);
    } else if(USECOPY && rng.u()<LINEP){   // JOINTFEED LINE MOVE: put a reader's root line l_k into X_i's flag right above the largest prefix inside Q_j (frame stays inside Q_j)
      int j=O[i][rng.r(O[i].size())]; if(LN[j].empty()) continue;
      int s0=0; while(s0+1<L){ bool in=true; for(int t=0;t<=s0+1&&in;t++) if(par(Q[i][t],P[j])) in=false; if(!in) break; s0++; }
      if(s0+1>=L) continue;
      int l=LN[j][rng.r(LN[j].size())]; if(has(SP[i][s0],l)) continue;
      s=s0+1; Q[i][s]=l; buildSpan(i,s);
    } else if(FLLAT>0 && rng.u()<FLLAT){   // FLAGS LATTICE MOVE (G1): stop s<=4 re-drawn inside the intersection of |K_i|-s of X_i's own root hyperplanes (port preferred)
      vector<int> K; for(int k=0;k<NR-n;k++) if(SG[n+k][i]) K.push_back(k); if(K.empty()) continue;
      s=1+rng.r(min(4,L-1)); int m=max(1,(int)K.size()-s); for(int a2=K.size()-1;a2>0;a2--){ int b2=rng.r(a2+1); swap(K[a2],K[b2]); } K.resize(m);
      vector<int> cand,candP; for(int v=1;v<512;v++){ if(has(SP[i][s-1],v)) continue; bool in=true; for(int k:K) if(par(v,RU[k])){in=false;break;} if(!in) continue; cand.push_back(v); }
      if(cand.empty()) continue; for(int v:cand) for(int q=0;q<n;q++) if(P[q]==v){ candP.push_back(v); break; }
      int v=(!candP.empty() && rng.u()<0.8)? candP[rng.r(candP.size())] : cand[rng.r(cand.size())]; if(v==Q[i][s]) continue;
      Q[i][s]=v; buildSpan(i,s);
    } else if(rng.u()<JOINP){
      int i2=-1; for(int tr=0;tr<30;tr++){ int c=rng.r(n); if(c!=i && has(SP[c][s],P[i])){i2=c;break;} }
      if(i2<0) continue;
      vector<int> el; for(int x=1;x<512;x++) if(has(SP[i2][s],x)) el.push_back(x);
      Span cur; memset(&cur,0,sizeof cur); setb(cur,0); setb(cur,P[i]); vector<int> nq(L); nq[0]=P[i];
      for(int t=1;t<=s;t++){ int v=-1; for(int tr=0;tr<200;tr++){ int c=el[rng.r(el.size())]; if(!has(cur,c)){v=c;break;} } if(v<0){ok=false;break;} nq[t]=v; Span nx=cur; for(int x=0;x<512;x++) if(has(cur,x)) setb(nx,x^v); cur=nx; }
      if(!ok) continue;
      bool ch=false; for(int t=1;t<=s;t++) if(nq[t]!=Q[i][t]) ch=true; if(!ch) continue;
      for(int t=1;t<=s;t++){Q[i][t]=nq[t]; buildSpan(i,t);}
    } else {
      int v=-1,bsc=-1; int TS=6;
      for(int c=0;c<TS;c++){ int w=P[rng.r(n)]; if(!indep(i,s,w)) continue;
        int a2=0,b2=0; Span S=SP[i][s-1]; for(int x=0;x<512;x++) if(has(SP[i][s-1],x)) setb(S,x^w);
        for(int q=0;q<n;q++){ if(has(S,P[q])) a2++; bool z=true; for(int t=0;t<s&&z;t++) if(par(P[q],Q[i][t])) z=false; if(z && !par(P[q],w)) b2++; }
        int sc=a2*b2+(int)rng.r(3); if(sc>bsc){bsc=sc;v=w;} }
      if(v<0 || v==Q[i][s]) continue;
      Q[i][s]=v; buildSpan(i,s);
    }
    for(int t=s+1;t<L;t++){ if(has(SP[i][t-1],Q[i][t])){ int w,tr=0; do{ w=P[rng.r(n)]; tr++; }while(has(SP[i][t-1],w)&&tr<50); if(has(SP[i][t-1],w)){ok=false;break;} Q[i][t]=w; } buildSpan(i,t); }
    if(!ok){ Q[i]=oldq; SP[i]=oldsp; HS[i]=oldh; continue; }
    auto nq=Q[i]; auto nsp=SP[i]; auto nh=HS[i];
    auto oS=absS; auto oSet=absSet; M touchedA=bit(i);
    int s0=L; for(int t=1;t<L;t++) if(nh[t]!=oldh[t]){ s0=t; break; }   // lowest stop whose frame changed (JOIN rewrites stops 1..s)
    if(absS[i]>=s0){ absS[i]=-1; absSet[i]=0; }
    for(int a=0;a<n;a++) if(absS[a]>=s0 && (absSet[a]&bit(i))){ absSet[a]&=~bit(i); if(!absSet[a]) absS[a]=-1; touchedA|=bit(a); }
    for(int a=0;a<n;a++) if(absS[a]>=0 && (absSet[a]&bit(i))) touchedA|=bit(a);   // transparency of a's packet depends on the source's frames
    auto nS=absS; auto nSet=absSet;
    vector<int> aff; for(M B=touchedA;B;B&=B-1){ int a=ctz(B); for(int j:RD[a]) aff.push_back(j); }
    trial(aff,[&]{Q[i]=nq;SP[i]=nsp;HS[i]=nh;absS=nS;absSet=nSet;},[&]{Q[i]=oldq;SP[i]=oldsp;HS[i]=oldh;absS=oS;absSet=oSet;},touchedA,T);
  }
  for(int j=0;j<NR;j++) dropY(j);
  Q=bestQ; for(int i=0;i<n;i++) rebuild(i,0); pr=bestPr; agreeRole=bestRole; absS=bestAS; absSet=bestASet; absSig=bestSig; CU=bestCU; if(PT){ TR=bestTR; OF=bestOF; } for(int j=0;j<n;j++) if(pr[j]>=0) setV(j);
  memo.clear(); reg.clear(); Ereg=0; cnt.assign(n,vector<int>(L,0)); if(JOINT) cntC.assign(n,vector<int>(L,0));
  for(int a=0;a<n;a++) if(!absValid(a)){ fprintf(stderr,"FATAL best absorption invalid %d\n",a); exit(4); }
  HUBREADS=0; PTREADS=0; if(ROOTY){ for(int j=0;j<n;j++) evalY(j); for(int j=n;j<NR;j++) evalY(j); } else { for(int j=n;j<NR;j++) evalY(j); for(int j=0;j<n;j++) evalY(j); } fprintf(stderr,"final trie-item reads (build calls) %ld\n",PTREADS); if(getenv("PT_CHECK")) for(int j=0;j<NR;j++){ if(chkNode(root[j].get(),0)) fprintf(stderr,"  ^ reader %d pair %d\n",j,j<n?pr[j]:-9); }
  for(int pass=0;JOINT && pass<8;pass++){ int v=viol(); if(!v) break; fprintf(stderr,"final repair pass %d: %d violating X\n",pass,v);
    computeHM(nullptr); vector<int> bad; for(int j=0;j<n;j++){ bool b=false; for(auto&cp:copyN[j]) for(auto&p:cp.second->picks) if(p.second<HM[p.first]) b=true; if(b) bad.push_back(j); }
    for(int j:bad){ dropY(j); evalY(j); } }
  if(JOINT && viol()){ fprintf(stderr,"final violations remain: switching the violating copies off\n");
    for(int pass=0;pass<20 && viol();pass++){ computeHM(nullptr); for(int j=0;j<n;j++){ bool b=false; for(auto&cp:copyN[j]) for(auto&p:cp.second->picks) if(p.second<HM[p.first]) b=true; if(b){ dropY(j); CU[j]=0; evalY(j);} } } }
  double tx=taxXall(),tc=0; for(int j=0;j<NR;j++) tc+=cost[j];
  fprintf(stderr,"final E %.1f (Y %.1f hubs %.1f [%zu] X %.1f) best-run %.1f viol %d\n",tx+tc+Ereg,tc,Ereg,reg.size(),tx,bestE,viol());
  { int nc=0,np=0; for(int j=0;j<n;j++) for(auto&cp:copyN[j]){ nc++; np+=cp.second->picks.size(); } fprintf(stderr,"copies used %d, copy picks %d, copy reads of root-tree hubs %ld\n",nc,np,HUBREADS); }
  if(PT){ int no=0; for(int j=0;j<n;j++) no+=OF[j]; int nr=0; for(int k=0;k<NR-n;k++) nr+=OFR[k]; fprintf(stderr,"Ys with offers on: %d, roots %d (dual on %ld of %ld)\n",no,nr,DUALON,DUALN); for(int k=0;k<NK;k++) for(auto&f:TR[k]){ printf("TRIE %d %d",k,f->cum); for(int v:f->bas) printf(" %d",v); printf("\n"); } }
  printf("E %.4f\n",tx+tc+Ereg);
  for(int j=0;j<n;j++) if(CU[j]) printf("U %d %d\n",j,CU[j]);
  for(int j=0;j<n;j++) if(pr[j]>j) printf("P %d %d %d\n",j,pr[j],agreeRole[j]);
  for(int a=0;a<n;a++) if(absS[a]>=0){ printf("A %d %d",a,absS[a]); for(M B=absSet[a];B;B&=B-1){int b=ctz(B); printf(" %d:%d",b,absSig[a][b]);} printf("\n"); }
  for(int i=0;i<n;i++){ printf("Q %d",i); for(int s=0;s<L;s++) printf(" %d",Q[i][s]); printf("\n"); }
  int nid=0; unordered_map<RK,int,RKH> sid;
  function<void(const NodeS*,int)> dump=[&](const NodeS*N,int j){ for(auto&k:N->kids){ const NodeS*c=k.node.get(); RK key=rkOf(c,j); if(sid.count(key)) continue; dump(c,j); sid[key]=nid++;
      printf("H %d top %d %d %d tb %d",sid[key],c->topI,c->topS,c->topJ,(int)c->tb.size()); for(int b:c->tb) printf(" %d",b); printf(" T %llu %llu picks",(unsigned long long)(c->T>>64),(unsigned long long)c->T); for(auto&p:c->picks) printf(" %d:%d",p.first,p.second); printf(" kids"); for(auto&kk:c->kids) printf(" %d:%d:%d",kk.vi,kk.vs,sid[rkOf(kk.node.get(),j)]); printf("\n"); } };
  for(int j=0;j<n;j++) for(auto&cp:copyN[j]){ dump(cp.second.get(),j); }
  for(int j=0;j<n;j++){ for(auto&cp:copyN[j]){ const NodeS*c=cp.second.get(); printf("C %d %d picks",j,cp.first); for(auto&p:c->picks) printf(" %d:%d",p.first,p.second); printf(" kids"); for(auto&kk:c->kids) printf(" %d:%d:%d",kk.vi,kk.vs,sid[rkOf(kk.node.get(),j)]); printf("\n"); } }
  for(int j=n;j<NR;j++){ dump(root[j].get(),j); printf("R %d %d picks",j-n,RU[j-n]); printf(" kids"); for(auto&kk:root[j]->kids) printf(" %d:%d:%d",kk.vi,kk.vs,sid[rkOf(kk.node.get(),j)]); printf("\n"); }
  for(int j=0;j<n;j++){ dump(root[j].get(),j); printf("Y %d picks",j); for(auto&p:root[j]->picks) printf(" %d:%d",p.first,p.second); printf(" kids"); for(auto&kk:root[j]->kids) printf(" %d:%d:%d",kk.vi,kk.vs,sid[rkOf(kk.node.get(),j)]); printf("\n"); }
  return 0;
}
