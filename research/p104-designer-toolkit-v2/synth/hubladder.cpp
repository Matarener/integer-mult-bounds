// hubladder.cpp -- SA kernel for synth/hubladder.py (HUBLADDER, see ../module docstring).  Extends hubsa.cpp with HUB-HUB MERGE LADDERS:
// every register (Y main or hub) has a SPINE = nested chain of frames inside its read frame F.  It picks X_i directly at spine frames (i's flag stop), and the ports it cannot pick on the spine
// are delivered by CHILD hubs that are read at a spine frame V (child top = V, child spine strictly inside V) -- recursively.  A hub is identified by (top frame, port set, normalized signs);
// identical hubs are SHARED by every parent that needs them (registry refcount) and are priced once:  R0 hub tax = 9ln9 - sum r ln r over rank increments of its rungs (spine dims + top), final jump to F9.
// Y root: 8ln8 - sum r ln r over (spine dims + 8).  X_i: 8ln8 - sum over used stops.   usage: hubladder ports.txt signs.txt seed iters T0 T1 [init.txt] [maxdepth]
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
static const int L=7; static double JOINP=0.4; static int MAXD=100000;
static int n; static vector<int> P; static vector<vector<int>> SG;
static inline int par(int a,int b){return __builtin_popcount(a&b)&1;}
static inline int pc(M x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
static inline int ctz(M x){ u64 lo=(u64)x; if(lo) return __builtin_ctzll(lo); return 64+__builtin_ctzll((u64)(x>>64)); }
struct Rng{u64 s; u64 next(){s^=s<<13;s^=s>>7;s^=s<<17;return s;} double u(){return (next()>>11)*(1.0/9007199254740992.0);} int r(int m){return next()%m;}};
static Rng rng; static double RL[64];
struct Span{u64 m[8];};
static inline bool has(const Span&S,int x){return (S.m[x>>6]>>(x&63))&1;}
static inline void setb(Span&S,int x){S.m[x>>6]|=1ULL<<(x&63);}
static u64 hashSpan(const Span&S){u64 h=1469598103934665603ULL; for(int w=0;w<8;w++){h^=S.m[w]+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2); h*=1099511628211ULL;} return h;}
static vector<vector<int>> Q; static vector<vector<Span>> SP; static vector<vector<u64>> HS; static vector<Span> QS; static vector<u64> QH; static vector<vector<int>> O;
static void buildSpan(int i,int s){
  if(s==0){Span S; memset(&S,0,sizeof S); setb(S,0); setb(S,Q[i][0]); SP[i][0]=S;}
  else {Span S=SP[i][s-1]; int v=Q[i][s]; for(int x=0;x<512;x++) if(has(SP[i][s-1],x)) setb(S,x^v); SP[i][s]=S;}
  HS[i][s]=hashSpan(SP[i][s]);
}
static void rebuild(int i,int from){for(int s=from;s<L;s++) buildSpan(i,s);}
static bool indep(int i,int s,int v){ return !has(SP[i][s-1],v); }
static inline int dimOfSpan(const Span&S){int c=0; for(int w=0;w<8;w++) c+=__builtin_popcountll(S.m[w]); int d=0; while((1<<d)<c) d++; return d;}
// ---- tax
static double taxChain(const vector<int>&d,bool hub){ double t=RL[hub?9:8]; int prev=0; for(int x:d){t-=RL[x-prev];prev=x;} t-= hub? RL[9-prev] : 0; return t; }
// ---- cover node
struct NodeS;
struct Kid{ int vi,vs; shared_ptr<NodeS> node; };    // child read at frame (vi,vs)  (vi=-1: parent's top frame)
struct NodeS{ u64 Fh; M T; bool strict; M left; bool doTop; int topI,topS,topJ;  // top spec: port-flag stop (topI,topS) or hyperplane Q_topJ (topI=-1)
  vector<int> rd; vector<pair<int,int>> picks; vector<Kid> kids; double taxH,taxY; int depth; };
struct MK{ u64 Fh; M T; bool strict; bool dt; bool operator==(const MK&o)const{return Fh==o.Fh&&T==o.T&&strict==o.strict&&dt==o.dt;} };
struct MKH{ size_t operator()(const MK&k)const{ return k.Fh*0x9e3779b97f4a7c15ULL ^ (u64)k.T*1099511628211ULL ^ (u64)(k.T>>64)*0xc2b2ae3d27d4eb4fULL ^ (k.strict?12345:0)^(k.dt?777:0);} };
static unordered_map<MK,shared_ptr<NodeS>,MKH> memo;
struct Nd{int dim,ri,rs; M pm;};
static shared_ptr<NodeS> build(const Span&F,u64 Fh,int dimF,M T,bool strict,int topI,int topS,int topJ,int depth,bool doTop=true){
  MK key{Fh,T,strict,doTop}; auto it=memo.find(key); if(it!=memo.end()) return it->second;
  auto N=make_shared<NodeS>(); N->Fh=Fh; N->T=T; N->strict=strict; N->left=0; N->doTop=doTop; N->topI=topI; N->topS=topS; N->topJ=topJ; N->depth=depth;
  // nodes
  vector<Nd> nodes; vector<u64> hh; 
  for(M B=T;B;B&=B-1){ int i=ctz(B);
    for(int s=0;s<L;s++){
      if(s>0 && !has(F,Q[i][s])) break;
      if(strict && s+1==dimF) break;
      u64 h=HS[i][s]; int id=-1; for(size_t a=0;a<hh.size();a++) if(hh[a]==h){id=a;break;}
      if(id<0){ id=nodes.size(); nodes.push_back({s+1,i,s,0}); hh.push_back(h);} nodes[id].pm|=((M)1)<<i;
    }
  }
  int Nn=nodes.size(); vector<int> ord(Nn); for(int a=0;a<Nn;a++) ord[a]=a;
  stable_sort(ord.begin(),ord.end(),[&](int a,int b){return nodes[a].dim<nodes[b].dim;});
  vector<vector<int>> pred(Nn); vector<int> bp(Nn,-1); vector<double> best(Nn,0);
  int bestf=-1; double bv=-1;
  for(int x=0;x<Nn;x++){ int f=ord[x]; const Nd&nf=nodes[f]; const Span&sf=SP[nf.ri][nf.rs]; double b=pc(nf.pm); int p=-1;
    for(int y=0;y<x;y++){ int g=ord[y]; const Nd&ng=nodes[g]; if(ng.dim>=nf.dim) break;
      bool ok=has(sf,Q[ng.ri][0]); for(int t=1;t<=ng.rs&&ok;t++) if(!has(sf,Q[ng.ri][t])) ok=false;
      if(ok){ double v=best[g]+pc(nf.pm&~ng.pm); if(v>b){b=v;p=g;} } }
    best[f]=b; bp[f]=p; if(b>bv+1e-9 || (fabs(b-bv)<1e-9 && bestf>=0 && nodes[f].dim>nodes[bestf].dim)){bv=b;bestf=f;}
  }
  if(bestf<0){ fprintf(stderr,"FATAL no node\n"); exit(2);} 
  vector<int> chain; for(int f=bestf;f>=0;f=bp[f]) chain.push_back(f); reverse(chain.begin(),chain.end());
  M cov=0; vector<M> D(chain.size(),0);
  for(size_t c=0;c<chain.size();c++){ M A=nodes[chain[c]].pm&~cov; D[c]=A; cov|=A; for(M B=A;B;B&=B-1) N->picks.push_back({ctz(B),nodes[chain[c]].rs}); }
  // rungs
  vector<int> rd; for(size_t c=0;c<chain.size();c++) if(D[c]) rd.push_back(nodes[chain[c]].dim);
  if(rd.empty() || rd.back()!=dimF) rd.push_back(dimF);
  N->rd=rd; N->taxH=taxChain(rd,true); N->taxY=taxChain(rd,false);
  M left=T&~cov;
  if(left && depth<MAXD){
    vector<M> slot(chain.size()+1,0);
    for(M B=left;B;B&=B-1){ int i=ctz(B); int sl=chain.size();
      for(size_t c=0;c<chain.size();c++){ if(!D[c]) continue; const Nd&nc=nodes[chain[c]]; if(has(SP[nc.ri][nc.rs],P[i])){sl=c;break;} }
      slot[sl]|=((M)1)<<i; }
    for(size_t c=0;c<chain.size();c++) if(slot[c]){
      const Nd&nc=nodes[chain[c]]; if(nc.dim<=1){ slot[chain.size()]|=slot[c]; continue; }
      auto ch=build(SP[nc.ri][nc.rs],HS[nc.ri][nc.rs],nc.dim,slot[c],true,nc.ri,nc.rs,-1,depth+1); N->kids.push_back({nc.ri,nc.rs,ch}); }
    N->left=slot[chain.size()];
    if(doTop){ M tl=N->left; while(tl){ auto sib=build(F,Fh,dimF,tl,true,topI,topS,topJ,depth+1,false); N->kids.push_back({-1,-1,sib}); tl=sib->left; } N->left=0; }
  }
  memo[key]=N; return N;
}
// ---- registry
struct RK{ u64 Fh; M T; u64 sg; bool operator==(const RK&o)const{return Fh==o.Fh&&T==o.T&&sg==o.sg;} };
struct RKH{ size_t operator()(const RK&k)const{ return k.Fh*0x9e3779b97f4a7c15ULL ^ (u64)k.T*1099511628211ULL ^ (u64)(k.T>>64)*0xc2b2ae3d27d4eb4fULL ^ k.sg*0x165667b19e3779f9ULL;} };
struct RE{ int ref; shared_ptr<NodeS> node; };
static unordered_map<RK,RE,RKH> reg;
static vector<vector<int>> cnt; static vector<double> xt; static double Ereg=0; static vector<int> touchedX;
static void cntAdj(const NodeS*N,int d){ for(auto&pr:N->picks){ cnt[pr.first][pr.second]+=d; touchedX.push_back(pr.first);} }
static u64 signHash(M T,int j){ u64 h=1469598103934665603ULL; int i0=ctz(T); int s0=SG[j][i0]; for(M B=T;B;B&=B-1){int i=ctz(B); h=(h^(u64)(SG[j][i]*s0+2))*1099511628211ULL;} return h; }
static RK rkOf(const NodeS*c,int j){ return RK{c->Fh,c->T,signHash(c->T,j)^(c->strict?0x5bd1e995ULL:0)^(c->doTop?0x1b873593ULL:0)}; }
typedef pair<RK,shared_ptr<NodeS>> KP;
static void regInc(const RK&k,const shared_ptr<NodeS>&N){ auto it=reg.find(k); if(it==reg.end()){ reg[k]={1,N}; Ereg+=N->taxH; cntAdj(N.get(),+1);} else it->second.ref++; }
static void regDec(const RK&k){ auto it=reg.find(k); if(--it->second.ref==0){ Ereg-=it->second.node->taxH; cntAdj(it->second.node.get(),-1); reg.erase(it);} }
static void walk(const shared_ptr<NodeS>&N,int j,vector<KP>&out){ for(auto&k:N->kids){ RK key=rkOf(k.node.get(),j); out.push_back({key,k.node}); walk(k.node,j,out);} }
static vector<shared_ptr<NodeS>> root; static vector<double> cost; static vector<vector<KP>> keysY;
static void evalY(int j){   // (re)compute tree of Y_j and apply to registry
  root[j]=build(QS[j],QH[j],8,[&]{M T=0; for(int i:O[j]) T|=((M)1)<<i; return T;}(),false,-1,-1,j,0);
  cost[j]=root[j]->taxY; cntAdj(root[j].get(),+1);
  keysY[j].clear(); walk(root[j],j,keysY[j]); for(auto&kp:keysY[j]) regInc(kp.first,kp.second);
}
static void dropY(int j){ for(auto&kp:keysY[j]) regDec(kp.first); cntAdj(root[j].get(),-1); }
static double taxX(const int*c){ double t=RL[8]; int prev=1; for(int s=1;s<L;s++) if(c[s]>0){int d=s+1; t-=RL[d-prev]; prev=d;} t-=RL[9-prev]; return t; }
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
  cnt.assign(n,vector<int>(L,0)); xt.assign(n,0); root.assign(n,nullptr); cost.assign(n,0); keysY.assign(n,{});
  for(int j=0;j<n;j++) evalY(j);
  auto fullE=[&](){ double e=Ereg; for(int j=0;j<n;j++) e+=cost[j]; for(int i=0;i<n;i++) e+=xt[i]; return e; };
  for(int i=0;i<n;i++) xt[i]=taxX(cnt[i].data());
  double E=fullE(); fprintf(stderr,"init E %.1f (reg %.1f Y %.1f hubs %zu)\n",E,Ereg,E-Ereg,reg.size());
  double bestE=E; vector<vector<int>> bestQ=Q; touchedX.clear(); long acc=0;
  for(long it=0;it<iters;it++){
    double T=T0*pow(T1/T0,(double)it/iters);
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
        int a=0,b=0; Span S=SP[i][s-1]; for(int x=0;x<512;x++) if(has(SP[i][s-1],x)) setb(S,x^w);
        for(int q=0;q<n;q++){ if(has(S,P[q])) a++; bool z=true; for(int t=0;t<s&&z;t++) if(par(P[q],Q[i][t])) z=false; if(z && !par(P[q],w)) b++; }
        int sc=a*b+(int)rng.r(3); if(sc>bsc){bsc=sc;v=w;} }
      if(v<0 || v==Q[i][s]) continue;
      Q[i][s]=v; buildSpan(i,s);
    }
    for(int t=s+1;t<L;t++){ if(has(SP[i][t-1],Q[i][t])){ int w,tr=0; do{ w=P[rng.r(n)]; tr++; }while(has(SP[i][t-1],w)&&tr<50); if(has(SP[i][t-1],w)){ok=false;break;} Q[i][t]=w; } buildSpan(i,t); }
    if(!ok){ Q[i]=oldq; SP[i]=oldsp; HS[i]=oldh; continue; }
    // invalidate memo entries whose target contains i
    vector<pair<MK,shared_ptr<NodeS>>> bak; { M bi=((M)1)<<i; for(auto it2=memo.begin();it2!=memo.end();){ if(it2->first.T&bi){ bak.push_back(*it2); it2=memo.erase(it2);} else ++it2; } }
    const vector<int>&aff=O[i];
    vector<shared_ptr<NodeS>> oldroot; vector<double> oldcost; vector<vector<KP>> oldkeys; double Ereg0=Ereg; 
    touchedX.clear(); touchedX.push_back(i);
    // snapshot cnt for touched later via journal: store full copy of rows of ports in affected set (cheap): record changes by diff
    for(int j:aff){ oldroot.push_back(root[j]); oldcost.push_back(cost[j]); oldkeys.push_back(keysY[j]); dropY(j); evalY(j); }
    sort(touchedX.begin(),touchedX.end()); touchedX.erase(unique(touchedX.begin(),touchedX.end()),touchedX.end());
    double dX=0; vector<double> nxt(touchedX.size()); for(size_t a=0;a<touchedX.size();a++){ nxt[a]=taxX(cnt[touchedX[a]].data()); dX+=nxt[a]-xt[touchedX[a]]; }
    double dY=0; for(size_t a=0;a<aff.size();a++) dY+=cost[aff[a]]-oldcost[a];
    double d=(Ereg-Ereg0)+dY+dX;
    if(d<=0 || rng.u()<exp(-d/T)){
      for(size_t a=0;a<touchedX.size();a++) xt[touchedX[a]]=nxt[a];
      E+=d; acc++; if(E<bestE-1e-9){bestE=E; bestQ=Q;}
    } else {
      // rollback: drop new trees, restore old
      for(int j:aff) dropY(j);
      { M bi=((M)1)<<i; for(auto it2=memo.begin();it2!=memo.end();){ if(it2->first.T&bi) it2=memo.erase(it2); else ++it2; } }
      for(auto&b:bak) memo[b.first]=b.second;
      Q[i]=oldq; SP[i]=oldsp; HS[i]=oldh;
      for(size_t a=0;a<aff.size();a++){ int j=aff[a]; root[j]=oldroot[a]; cost[j]=oldcost[a]; keysY[j]=oldkeys[a]; cntAdj(root[j].get(),+1); for(auto&kp:keysY[j]) regInc(kp.first,kp.second); }
      touchedX.clear();
    }
    if(it%2000==0) fprintf(stderr,"it %ld T %.3f E %.1f best %.1f acc %ld hubs %zu memo %zu\n",it,T,E,bestE,acc,reg.size(),memo.size());
  }
  // final: restore best
  Q=bestQ; for(int i=0;i<n;i++) rebuild(i,0);
  for(int j=0;j<n;j++) dropY(j);
  memo.clear(); reg.clear(); Ereg=0; cnt.assign(n,vector<int>(L,0));
  for(int j=0;j<n;j++) evalY(j);
  double tx=0,tc=0; for(int i=0;i<n;i++){xt[i]=taxX(cnt[i].data()); tx+=xt[i];} for(int j=0;j<n;j++) tc+=cost[j];
  fprintf(stderr,"final E %.1f (Y %.1f hubs %.1f [%zu] X %.1f)\n",tx+tc+Ereg,tc,Ereg,reg.size(),tx);
  printf("E %.4f\n",tx+tc+Ereg);
  for(int i=0;i<n;i++){ printf("Q %d",i); for(int s=0;s<L;s++) printf(" %d",Q[i][s]); printf("\n"); }
  // print registry nodes with ids
  int nid=0;
  unordered_map<RK,int,RKH> sid;
  auto KEY=[&](const NodeS*c,int j){ return rkOf(c,j); };
  function<void(const NodeS*,int)> dump=[&](const NodeS*N,int j){ for(auto&k:N->kids){ const NodeS*c=k.node.get(); RK key=KEY(c,j); if(sid.count(key)) continue; sid[key]=nid++; dump(c,j);
      printf("H %d top %d %d %d T %llu %llu picks",sid[key],c->topI,c->topS,c->topJ,(unsigned long long)(c->T>>64),(unsigned long long)c->T); for(auto&p:c->picks) printf(" %d:%d",p.first,p.second); printf(" kids"); for(auto&kk:c->kids) printf(" %d:%d:%d",kk.vi,kk.vs,sid[KEY(kk.node.get(),j)]); printf("\n"); } };
  for(int j=0;j<n;j++){ dump(root[j].get(),j); printf("Y %d picks",j); for(auto&p:root[j]->picks) printf(" %d:%d",p.first,p.second); printf(" kids"); for(auto&kk:root[j]->kids) printf(" %d:%d:%d",kk.vi,kk.vs,sid[KEY(kk.node.get(),j)]); printf("\n"); }
  return 0;
}
