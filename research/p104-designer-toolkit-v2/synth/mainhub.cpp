// mainhub.cpp -- SA kernel for synth/mainhub.py (MAINHUB, see ../module docstring).  Extends hubladder.cpp (hub-hub merge ladders, shared hubs) with MAINS AS HUBS:
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
static const int L=7; static double JOINP=0.4, PAIRP=0.0, ABSP=0.0; static int MAXD=100000;
static int VIRT=0; static int NR=0; static vector<vector<int>> RD; static vector<int> RU; static int n; static vector<int> P; static vector<vector<int>> SG;
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
  vector<int> rd; vector<pair<int,int>> picks; vector<Kid> kids; double taxH,taxY; int depth; vector<int> tb; };
struct MK{ u64 Fh; M T; bool strict; bool dt; u64 sg; bool operator==(const MK&o)const{return Fh==o.Fh&&T==o.T&&strict==o.strict&&dt==o.dt&&sg==o.sg;} };
struct MKH{ size_t operator()(const MK&k)const{ return k.Fh*0x9e3779b97f4a7c15ULL ^ (u64)k.T*1099511628211ULL ^ (u64)(k.T>>64)*0xc2b2ae3d27d4eb4fULL ^ (k.strict?12345:0)^(k.dt?777:0)^k.sg*0x2545F4914F6CDD1DULL;} };
static unordered_map<MK,shared_ptr<NodeS>,MKH> memo;
struct Item{int x; M mask;};
struct Nd{int dim,ri,rs; M pm; vector<Item> it;};
static shared_ptr<NodeS> build(const Span&F,u64 Fh,int dimF,M T,bool strict,int topI,int topS,int topJ,int depth,int sj,bool doTop=true,int lineV=0){
  MK key{Fh,T,strict,doTop,signHash(T,sj)}; auto itm=memo.find(key); if(itm!=memo.end()) return itm->second;
  auto N=make_shared<NodeS>(); N->Fh=Fh; N->T=T; N->strict=strict; N->left=0; N->doTop=doTop; N->topI=topI; N->topS=topS; N->topJ=topJ; N->depth=depth;
  vector<Nd> nodes; vector<u64> hh;
  for(M B=T;B;B&=B-1){ int i=ctz(B);
    for(int s=0;s<L;s++){
      if(s>0 && !has(F,Q[i][s])) break;
      if(strict && s+1==dimF) break;
      if(lineV && !has(SP[i][s],lineV)) continue;
      M mk;
      if(absS[i]>=0 && s>=absS[i] && !transparent(i,s)){ if(!pktOK(i,T,sj)) break; mk=packet(i); } else mk=bit(i);
      u64 h=HS[i][s]; int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==h){id=a;break;}
      if(id<0){ id=nodes.size(); nodes.push_back({s+1,i,s,0,{}}); hh.push_back(h);} nodes[id].pm|=mk; nodes[id].it.push_back({i,mk});
    }
  }
  int Nn=nodes.size();
  if(Nn==0){ N->rd={dimF}; N->taxH=taxChain(N->rd,true); N->taxY=taxChain(N->rd,false); N->left=T; memo[key]=N; return N; }
  vector<int> ord(Nn); for(int a=0;a<Nn;a++) ord[a]=a;
  stable_sort(ord.begin(),ord.end(),[&](int a,int b){return nodes[a].dim<nodes[b].dim;});
  vector<int> bp(Nn,-1); vector<double> best(Nn,0);
  int bestf=-1; double bv=-1;
  for(int x=0;x<Nn;x++){ int f=ord[x]; const Nd&nf=nodes[f]; const Span&sf=SP[nf.ri][nf.rs]; double b=pc(nf.pm); int p=-1;
    for(int y=0;y<x;y++){ int g=ord[y]; const Nd&ng=nodes[g]; if(ng.dim>=nf.dim) break;
      bool ok=has(sf,Q[ng.ri][0]); for(int t=1;t<=ng.rs&&ok;t++) if(!has(sf,Q[ng.ri][t])) ok=false;
      if(ok){ double v=best[g]+pc(nf.pm&~ng.pm); if(v>b){b=v;p=g;} } }
    best[f]=b; bp[f]=p; if(b>bv+1e-9 || (fabs(b-bv)<1e-9 && bestf>=0 && nodes[f].dim>nodes[bestf].dim)){bv=b;bestf=f;}
  }
  vector<int> chain; for(int f=bestf;f>=0;f=bp[f]) chain.push_back(f); reverse(chain.begin(),chain.end());
  M cov=0; vector<M> D(chain.size(),0);
  for(size_t c=0;c<chain.size();c++){ Nd&nd=nodes[chain[c]]; M avail=nd.pm&~cov, got=0;
    stable_sort(nd.it.begin(),nd.it.end(),[](const Item&a,const Item&b){return pc(a.mask)>pc(b.mask);});
    for(auto&itx:nd.it) if(!(itx.mask&~avail) && !(itx.mask&got)){ got|=itx.mask; N->picks.push_back({itx.x,nd.rs}); }
    D[c]=got; cov|=got; }
  vector<int> rd; for(size_t c=0;c<chain.size();c++) if(D[c]) rd.push_back(nodes[chain[c]].dim);
  if(rd.empty() || rd.back()!=dimF) rd.push_back(dimF);
  N->rd=rd; N->taxH=taxChain(rd,true); N->taxY=taxChain(rd,false);
  M left=T&~cov;
  if(left && depth<MAXD){
    vector<M> slot(chain.size()+1,0);
    for(M B=left;B;B&=B-1){ int i=ctz(B); int sl=chain.size();
      for(size_t c=0;c<chain.size();c++){ if(!D[c]) continue; const Nd&nc=nodes[chain[c]]; if(has(SP[nc.ri][nc.rs],P[i])){sl=c;break;} }
      slot[sl]|=bit(i); }
    for(size_t c=0;c<chain.size();c++) if(slot[c]){
      const Nd&nc=nodes[chain[c]]; if(nc.dim<=1){ slot[chain.size()]|=slot[c]; continue; }
      auto ch=build(SP[nc.ri][nc.rs],HS[nc.ri][nc.rs],nc.dim,slot[c],true,nc.ri,nc.rs,-1,depth+1,sj);
      if(ch->T==ch->left){ slot[chain.size()]|=slot[c]; continue; }   // child could place nothing: defer to top
      N->kids.push_back({nc.ri,nc.rs,ch}); slot[chain.size()]|=ch->left; }
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
          if(ch->T!=ch->left){ N->kids.push_back({-5,bq,ch}); N->left=(lf&~Th)|ch->left;
            vector<int> rd2=N->rd; rd2.pop_back(); if(rd2.empty()||rd2.back()!=dimF-1) rd2.push_back(dimF-1); rd2.push_back(dimF); N->rd=rd2; N->taxH=taxChain(rd2,true); N->taxY=taxChain(rd2,false); } } }
    }
    if(doTop){ M tl=N->left; while(tl){ auto sib=build(F,Fh,dimF,tl,true,topI,topS,topJ,depth+1,sj,false); if(sib->T==sib->left){ fprintf(stderr,"FATAL stuck sibling\n"); exit(3);} N->kids.push_back({-1,-1,sib}); tl=sib->left; } N->left=0; }
  } else if(left) N->left=left;
  memo[key]=N; return N;
}
// ---- registry
struct RK{ u64 Fh; M T; u64 sg; bool operator==(const RK&o)const{return Fh==o.Fh&&T==o.T&&sg==o.sg;} };
struct RKH{ size_t operator()(const RK&k)const{ return k.Fh*0x9e3779b97f4a7c15ULL ^ (u64)k.T*1099511628211ULL ^ (u64)(k.T>>64)*0xc2b2ae3d27d4eb4fULL ^ k.sg*0x165667b19e3779f9ULL;} };
struct RE{ int ref; shared_ptr<NodeS> node; };
static unordered_map<RK,RE,RKH> reg;
static vector<vector<int>> cnt; static double Ereg=0;
static void cntAdj(const NodeS*N,int d){ for(auto&pr:N->picks) cnt[pr.first][pr.second]+=d; }
static RK rkOf(const NodeS*c,int j){ return RK{c->Fh,c->T,signHash(c->T,j)^(c->strict?0x5bd1e995ULL:0)^(c->doTop?0x1b873593ULL:0)}; }
typedef pair<RK,shared_ptr<NodeS>> KP;
static void regInc(const RK&k,const shared_ptr<NodeS>&N){ auto it=reg.find(k); if(it==reg.end()){ reg[k]={1,N}; Ereg+=N->taxH; cntAdj(N.get(),+1);} else it->second.ref++; }
static void regDec(const RK&k){ auto it=reg.find(k); if(--it->second.ref==0){ Ereg-=it->second.node->taxH; cntAdj(it->second.node.get(),-1); reg.erase(it);} }
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
static void evalY(int j){
  copyN[j].clear();
  if(j>=n){   // ROOT READER k=j-n: owned root at H_k reads S_k-signed shared hubs; no spine, own cost 0
    M T=0; for(int i=0;i<n;i++) if(SG[j][i]) T|=bit(i);
    auto W=make_shared<NodeS>(); W->Fh=hashSpan(RHS[j-n])^0x77ULL; W->T=T; W->strict=true; W->left=0; W->doTop=true; W->topI=-7; W->topS=RU[j-n]; W->topJ=0; W->depth=0; W->taxH=0; W->taxY=0; W->rd={8};
    M tl=T; while(tl){ auto sib=build(RHS[j-n],hashSpan(RHS[j-n])^0x77ULL,8,tl,true,-7,RU[j-n],0,1,j,false); if(sib->T==sib->left){fprintf(stderr,"FATAL stuck root sibling\n");exit(3);} W->kids.push_back({-1,-1,sib}); tl=sib->left; }
    root[j]=W; cost[j]=0; cntAdj(W.get(),+1); keysY[j].clear(); walk(W,j,keysY[j]); for(auto&kp:keysY[j]) regInc(kp.first,kp.second); return;
  }
  if(pr[j]<0 && !USECOPY){ root[j]=build(QS[j],QH[j],8,fullT(j),false,-1,-1,j,0,j); cost[j]=root[j]->taxY; }
  else if(pr[j]<0){   // COPY CARRIERS: Y spine first, then each root copy u(j,k) (spine through <l_k>, base (1,7,1) already paid), then plain siblings at Q_j
    auto R=build(QS[j],QH[j],8,fullT(j),false,-1,-1,j,0,j,false);
    auto W=make_shared<NodeS>(*R); W->kids=R->kids; double c=R->taxY; M tl=R->left; W->left=0;
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
    if(rd.empty()||rd.back()!=7) rd.push_back(7);
    M tl=Tout; double cc=0;
    /* copies for paired Ys: experimental, MH_PAIRCOPY only (python glue does not support it; init R0 worse on plan B) */
    if(USECOPY && getenv("MH_PAIRCOPY")) for(int l:LN[j]){ if(!tl) break; auto C=build(QS[j],QH[j]^((u64)l*0x9E3779B97F4A7C15ULL),8,tl,true,-4,l,j,1,j,false,l);
      if(C->left==C->T) continue; copyN[j].push_back({l,C}); vector<int> rd2; rd2.push_back(1); for(int x:C->rd) rd2.push_back(x); cc+=taxChain(rd2,true)-COPYBASE; tl=C->left; }
    while(tl){ auto sib=build(QS[j],QH[j],8,tl,true,-1,-1,j,1,j,false); if(sib->T==sib->left){fprintf(stderr,"FATAL stuck Q sibling\n");exit(3);} W->kids.push_back({-3,-3,sib}); tl=sib->left; }
    rd.push_back(8); W->rd=rd; W->taxY=taxChain(rd,false); W->taxH=0; root[j]=W; cost[j]=W->taxY+cc;
  }
  cntAdj(root[j].get(),+1); for(auto&cp:copyN[j]) cntAdj(cp.second.get(),+1);
  keysY[j].clear(); walk(root[j],j,keysY[j]); for(auto&cp:copyN[j]) walk(cp.second,j,keysY[j]); for(auto&kp:keysY[j]) regInc(kp.first,kp.second);
}
static void dropY(int j){ for(auto&kp:keysY[j]) regDec(kp.first); cntAdj(root[j].get(),-1); for(auto&cp:copyN[j]) cntAdj(cp.second.get(),-1); }
static double taxXi(int i){ double t=RL[8]; int prev=1; for(int s=1;s<L;s++){ bool u=cnt[i][s]>0; if(!u && absS[i]==s && absSet[i]) u=true;
    if(!u) for(int a=0;a<n && !u;a++) if(absS[a]==s && (absSet[a]&bit(i))) u=true;
    if(u){int d=s+1; t-=RL[d-prev]; prev=d;} } t-=RL[9-prev]; return t; }
static double taxXall(){ double t=0; for(int i=0;i<n;i++) t+=taxXi(i); return t; }
static double totE(){ double e=Ereg+taxXall(); for(int j=0;j<NR;j++) e+=cost[j]; return e; }
// valid absorption: sources at the same frame (stop sa) and clean there; a is not a source of an absorption at >= its own stop
static bool absValid(int a){ if(absS[a]<0) return true; int s=absS[a];
  for(M B=absSet[a];B;B&=B-1){ int b=ctz(B); if(HS[b][s]!=HS[a][s]) return false; if(absS[b]>=0 && absS[b]<=s) return false; }
  for(int c=0;c<n;c++) if(absS[c]>=0 && (absSet[c]&bit(a)) && absS[a]<=absS[c]) return false;
  return true; }
static void memoInval(M mask){ for(auto it2=memo.begin();it2!=memo.end();){ if(it2->first.T&mask) it2=memo.erase(it2); else ++it2; } }
int main(int argc,char**argv){
  if(argc<7){fprintf(stderr,"usage\n");return 1;}
  FILE*f=fopen(argv[1],"r"); fscanf(f,"%d",&n); P.resize(n); for(int i=0;i<n;i++) fscanf(f,"%d",&P[i]); fclose(f);
  SG.assign(n,vector<int>(n,0)); f=fopen(argv[2],"r"); for(int j=0;j<n;j++) for(int i=0;i<n;i++) fscanf(f,"%d",&SG[j][i]); fclose(f);
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
  COPYBASE=taxChain(vector<int>{1,8},true); if(getenv("MH_VIRT")) VIRT=atoi(getenv("MH_VIRT"));
  for(int j=0;j<n;j++) if(pr[j]>=0) setV(j);
  if(getenv("MH_PROV")){   // PRICING ONLY (COPYFOLD plan): unsigned frame sums F(V), V=<a,b>^perp, built as shared hubs (signs all +, row n); prints R0 and exits
    SG.push_back(vector<int>(n,1)); FILE*g=fopen(getenv("MH_PROV"),"r"); int a,b,np=0; double top=0; vector<shared_ptr<NodeS>> PR;
    while(fscanf(g,"%d %d",&a,&b)==2){ Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,a)&&!par(x,b)) setb(S,x); M T=0; for(int i=0;i<n;i++) if(has(S,P[i])) T|=bit(i);
      auto R=build(S,hashSpan(S),7,T,false,-6,a,b,0,n); RK key=rkOf(R.get(),n); regInc(key,R); vector<KP> ks; walk(R,n,ks); for(auto&kp:ks) regInc(kp.first,kp.second); np++; }
    fclose(g); double tx=taxXall(); fprintf(stderr,"PROV %d providers: shared hubs %zu (incl. provider roots) tax %.1f, X tax %.1f\n",np,reg.size(),Ereg,tx); printf("PROV %d %.2f %.2f %zu\n",np,Ereg,tx,reg.size()); return 0; }
  for(int j=0;j<NR;j++) evalY(j);
  double E=totE(); fprintf(stderr,"init E %.1f (reg %.1f hubs %zu)\n",E,Ereg,reg.size());
  if(getenv("MH_ROOTS")){   // PRICING ONLY: front end as S_k-signed shared trees read by root k at H_k, in the SAME registry as the Y trees
    FILE*g=fopen(getenv("MH_ROOTS"),"r"); int u; double e0=Ereg, x0=taxXall(); size_t h0=reg.size(); int nk=0;
    while(fscanf(g,"%d",&u)==1){ vector<int> row(n); for(int i=0;i<n;i++) fscanf(g,"%d",&row[i]); SG.push_back(row); int sj=SG.size()-1;
      Span S; memset(&S,0,sizeof S); for(int x=0;x<512;x++) if(!par(x,u)) setb(S,x); M T=0; for(int i=0;i<n;i++) if(row[i]) T|=bit(i);
      auto R=build(S,hashSpan(S)^0x77ULL,8,T,true,-7,u,0,1,sj,true); vector<KP> ks; walk(R,sj,ks); for(auto&kp:ks) regInc(kp.first,kp.second); nk++; }
    fclose(g); fprintf(stderr,"ROOTS %d trees: +%.1f hub tax (+%zu hubs), X tax %+.1f\n",nk,Ereg-e0,reg.size()-h0,taxXall()-x0); return 0; }
  double bestE=E; auto bestQ=Q; auto bestPr=pr, bestRole=agreeRole; auto bestAS=absS; auto bestASet=absSet; auto bestSig=absSig; long acc=0,pacc=0,aacc=0;
  // generic trial: the caller passes the Ys to re-evaluate, setters for the NEW and OLD state, and the memo invalidation mask
  auto trial=[&](vector<int>&aff,const function<void()>&applyNew,const function<void()>&applyOld,M inval,double T)->bool{
    sort(aff.begin(),aff.end()); aff.erase(unique(aff.begin(),aff.end()),aff.end());
    applyOld(); vector<shared_ptr<NodeS>> oldroot; vector<double> oldcost; vector<vector<KP>> oldkeys; vector<vector<pair<int,shared_ptr<NodeS>>>> oldcp;
    for(int a:aff){ oldroot.push_back(root[a]); oldcost.push_back(cost[a]); oldkeys.push_back(keysY[a]); oldcp.push_back(copyN[a]); dropY(a); }
    vector<pair<MK,shared_ptr<NodeS>>> bak; for(auto it2=memo.begin();it2!=memo.end();){ if(it2->first.T&inval){ bak.push_back(*it2); it2=memo.erase(it2);} else ++it2; }
    applyNew(); for(int a:aff) evalY(a);
    double E2=totE(); double d=E2-E;
    if(d<=0 || rng.u()<exp(-d/T)){ E=E2; acc++; if(E<bestE-1e-9){bestE=E; bestQ=Q; bestPr=pr; bestRole=agreeRole; bestAS=absS; bestASet=absSet; bestSig=absSig;} return true; }
    for(int a:aff) dropY(a); memoInval(inval); for(auto&b:bak) memo[b.first]=b.second; applyOld();
    for(size_t a=0;a<aff.size();a++){ int jj=aff[a]; root[jj]=oldroot[a]; cost[jj]=oldcost[a]; keysY[jj]=oldkeys[a]; copyN[jj]=oldcp[a]; cntAdj(root[jj].get(),+1); for(auto&cp:copyN[jj]) cntAdj(cp.second.get(),+1); for(auto&kp:keysY[jj]) regInc(kp.first,kp.second); }
    return false; };
  for(long it=0;it<iters;it++){
    double T=T0*pow(T1/T0,(double)it/iters);
    if(it%2000==0) fprintf(stderr,"it %ld T %.3f E %.1f best %.1f acc %ld pacc %ld aacc %ld pairs %d absorbers %d hubs %zu memo %zu\n",it,T,E,bestE,acc,pacc,aacc,
        (int)count_if(pr.begin(),pr.end(),[](int x){return x>=0;})/2,(int)count_if(absS.begin(),absS.end(),[](int x){return x>=0;}),reg.size(),memo.size());
    if(memo.size()>400000) memo.clear();
    double mvr=rng.u();
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
    int i=rng.r(n); int s=1+rng.r(L-1);
    vector<int> oldq=Q[i]; vector<Span> oldsp=SP[i]; vector<u64> oldh=HS[i];
    bool ok=true;
    if(rng.u()<JOINP){
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
  Q=bestQ; for(int i=0;i<n;i++) rebuild(i,0); pr=bestPr; agreeRole=bestRole; absS=bestAS; absSet=bestASet; absSig=bestSig; for(int j=0;j<n;j++) if(pr[j]>=0) setV(j);
  memo.clear(); reg.clear(); Ereg=0; cnt.assign(n,vector<int>(L,0));
  for(int a=0;a<n;a++) if(!absValid(a)){ fprintf(stderr,"FATAL best absorption invalid %d\n",a); exit(4); }
  for(int j=0;j<NR;j++) evalY(j);
  double tx=taxXall(),tc=0; for(int j=0;j<NR;j++) tc+=cost[j];
  fprintf(stderr,"final E %.1f (Y %.1f hubs %.1f [%zu] X %.1f) best-run %.1f\n",tx+tc+Ereg,tc,Ereg,reg.size(),tx,bestE);
  printf("E %.4f\n",tx+tc+Ereg);
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
