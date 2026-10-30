// hubsa.cpp -- SA kernel for synth/hubgen.py (HUBGEN, see ../module docstring).
// Problem: X_i gets a flag f_0 < f_1 < ... < f_{L-1} (f_s = span(q[i][0..s]), q[i][0]=p_i, dim s+1).  Every Y_j (Q_j = p_j^perp) must pick up x_i for the 48 ports i orth to p_j,
// either on its own chain or via private "hubs" (helpers born at frame 0, chain of nested frames, read by Y_j at Q_j, then up to F9).  A chain is a nested sequence of frames;
// port i can be picked at a chain frame f only if f = f_s(i) for some s and f is inside Q_j.  Cost = R0 entropy tax:
//   hub (1 per extra chain):  9 ln 9 - sum r ln r over ranks (d1, d2-d1, ..., 8-dr, 1);   Y chain (the biggest chain): 8 ln 8 - sum r ln r over (d1,...,8-dr)
//   X_i: 8 ln 8 - sum r ln r over the used stops (L_i dim 1 -> used dims -> F9 dim 9).
// usage:  hubsa ports.txt seed iters T0 T1 [init.txt] > out.txt     (ports.txt: n then n ints)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cmath>
#include <vector>
#include <algorithm>
#include <cstring>
#include <array>
using namespace std;
typedef uint64_t u64;
static const int L=7; static double JOINP=0.4;           // levels (dims 1..7)
static int n; static vector<int> P;
static inline int par(int a,int b){return __builtin_popcount(a&b)&1;}
struct Rng{u64 s; u64 next(){s^=s<<13;s^=s>>7;s^=s<<17;return s;} double u(){return (next()>>11)*(1.0/9007199254740992.0);} int r(int m){return next()%m;}};
static Rng rng;
static double RL[64]; // r ln r
static double taxHub(const int*d,int k){ double t=RL[9]; int prev=0; for(int a=0;a<k;a++){t-=RL[d[a]-prev];prev=d[a];} t-=RL[8-prev]; t-=RL[1]; return t;}
static double taxY(const int*d,int k){ double t=RL[8]; int prev=0; for(int a=0;a<k;a++){t-=RL[d[a]-prev];prev=d[a];} t-=RL[8-prev]; return t;}
static double taxX(const int*cntrow){ // used dims among 2..7 (level s>=1)
  double t=RL[8]; int prev=1; for(int s=1;s<L;s++) if(cntrow[s]>0){ int d=s+1; t-=RL[d-prev]; prev=d;} t-=RL[9-prev]; return t;}
struct Span{u64 m[8];};
static inline bool has(const Span&S,int x){return (S.m[x>>6]>>(x&63))&1;}
static inline void setb(Span&S,int x){S.m[x>>6]|=1ULL<<(x&63);}
static vector<vector<int>> Q;            // Q[i][s]
static vector<vector<Span>> SP;          // span mask of prefix s
static vector<vector<u64>> HS;           // hash of span
static vector<vector<int>> O;            // O[j] list of ports orth to j
static vector<vector<int>> Oinv;         // Oinv[i] = js with i in O[j]  (same set by symmetry)
static vector<vector<int>> lvl;          // lvl[j][pos in O[j]] = assigned level
static vector<vector<int>> chn;          // chain id per pos
static vector<double> cost;              // per j
static vector<vector<int>> cnt;          // cnt[i][s]
static vector<double> xt;
static void buildSpan(int i,int s){
  if(s==0){Span S; memset(&S,0,sizeof S); setb(S,0); setb(S,Q[i][0]); SP[i][0]=S;}
  else {Span S=SP[i][s-1]; int v=Q[i][s]; for(int x=0;x<512;x++) if(has(SP[i][s-1],x)) setb(S,x^v); SP[i][s]=S;}
  u64 h=1469598103934665603ULL; for(int w=0;w<8;w++){h^=SP[i][s].m[w]+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2); h*=1099511628211ULL;} HS[i][s]=h;
}
static void rebuild(int i,int from){for(int s=from;s<L;s++) buildSpan(i,s);}
static bool indep(int i,int s,int v){ return !has(SP[i][s-1],v); }
// ---- cover of Y_j.  Fills lv[pos], ch[pos] and returns cost
struct Node{int dim,rep_i,rep_s; u64 pm;};
static double cover(int j,vector<int>&lv,vector<int>&ch){
  const vector<int>&Oj=O[j]; int m=Oj.size(); int pj=P[j];
  static vector<Node> nodes; nodes.clear();
  static u64 htab[2048]; static int hval[2048]; static bool hinit=false; if(!hinit){hinit=true; for(int a=0;a<2048;a++) hval[a]=-1;}
  static vector<int> touched; touched.clear();
  for(int pos=0;pos<m;pos++){ int i=Oj[pos];
    for(int s=0;s<L;s++){
      if(s>0 && par(Q[i][s],pj)) break;
      u64 h=HS[i][s]; int a=(h>>7)&2047; int id=-1;
      while(hval[a]>=0){ if(htab[a]==h){id=hval[a];break;} a=(a+1)&2047; }
      if(id<0){ id=nodes.size(); nodes.push_back({s+1,i,s,0}); htab[a]=h; hval[a]=id; touched.push_back(a);}
      nodes[id].pm|=1ULL<<pos;
    }
  }
  for(int a:touched) hval[a]=-1;
  int N=nodes.size();
  // order nodes by dim
  static vector<int> ord; ord.resize(N); for(int a=0;a<N;a++) ord[a]=a; stable_sort(ord.begin(),ord.end(),[&](int a,int b){return nodes[a].dim<nodes[b].dim;});
  static vector<vector<int>> pred; if((int)pred.size()<N) pred.resize(N); for(int a=0;a<N;a++) pred[a].clear();
  for(int x=0;x<N;x++){ int f=ord[x]; const Node&nf=nodes[f]; const Span&sf=SP[nf.rep_i][nf.rep_s];
    for(int y=0;y<x;y++){ int g=ord[y]; const Node&ng=nodes[g]; if(ng.dim>=nf.dim) break; // nodes sorted ascending: stop at first with dim>=
      bool ok=true; for(int t=1;t<=ng.rep_s;t++){ if(!has(sf,Q[ng.rep_i][t])){ok=false;break;} } // q0 = port of rep; need also q0
      if(ok && !has(sf,Q[ng.rep_i][0])) ok=false;
      if(ok) pred[f].push_back(g);
    }
  }
  // note the loop above breaks when ng.dim>=nf.dim, but ord is ascending so later y have bigger dim: correct
  u64 unc=(m==64)?~0ULL:((1ULL<<m)-1);
  lv.assign(m,-1); ch.assign(m,-1);
  static vector<double> best; best.resize(N); static vector<int> bp; bp.resize(N);
  double total=0; int cid=0;
  while(unc){
    int bestf=-1; double bv=-1;
    for(int x=0;x<N;x++){ int f=ord[x]; u64 A=nodes[f].pm&unc; double b=__builtin_popcountll(A); int p=-1;
      for(int g:pred[f]){ double v=best[g]+__builtin_popcountll(A&~nodes[g].pm); if(v>b){b=v;p=g;} }
      best[f]=b; bp[f]=p; if(b>bv+1e-9 || (fabs(b-bv)<1e-9 && bestf>=0 && nodes[f].dim>nodes[bestf].dim)){bv=b;bestf=f;}
    }
    // backtrack
    static vector<int> chain; chain.clear(); for(int f=bestf;f>=0;f=bp[f]) chain.push_back(f); reverse(chain.begin(),chain.end());
    int dims[16],k=0;
    for(int f:chain){ u64 A=nodes[f].pm&unc; if(!A) continue; dims[k++]=nodes[f].dim; for(u64 B=A;B;B&=B-1){int pos=__builtin_ctzll(B); lv[pos]=nodes[f].dim-1; ch[pos]=cid;} unc&=~A; }
    total+= (cid==0)? taxY(dims,k):taxHub(dims,k);
    cid++;
  }
  return total;
}
static double energy_full(){ double e=0; for(size_t i=0;i<xt.size();i++) e+=xt[i]; for(double c:cost) e+=c; return e; }
int main(int argc,char**argv){
  if(argc<6){fprintf(stderr,"usage\n");return 1;}
  FILE*f=fopen(argv[1],"r"); fscanf(f,"%d",&n); P.resize(n); for(int i=0;i<n;i++) fscanf(f,"%d",&P[i]); fclose(f);
  u64 seed=atoll(argv[2]); long iters=atol(argv[3]); double T0=atof(argv[4]),T1=atof(argv[5]);
  rng.s=seed*2654435761ULL+88172645463325252ULL; for(int a=0;a<10;a++) rng.next();
  for(int r=1;r<64;r++) RL[r]=r*log((double)r); RL[0]=0;
  Q.assign(n,vector<int>(L,0)); SP.assign(n,vector<Span>(L)); HS.assign(n,vector<u64>(L,0));
  O.assign(n,{}); for(int j=0;j<n;j++) for(int i=0;i<n;i++) if(!par(P[i],P[j])) O[j].push_back(i);
  Oinv=O; // symmetric
  // init flags
  bool haveInit = argc>6;
  if(haveInit){ FILE*g=fopen(argv[6],"r"); for(int i=0;i<n;i++) for(int s=0;s<L;s++) fscanf(g,"%d",&Q[i][s]); fclose(g);
    for(int i=0;i<n;i++){ Q[i][0]=P[i]; rebuild(i,0);} }
  else for(int i=0;i<n;i++){ Q[i][0]=P[i]; buildSpan(i,0); for(int s=1;s<L;s++){ int v; do{ v=P[rng.r(n)]; }while(!indep(i,s,v)); Q[i][s]=v; buildSpan(i,s);} }
  lvl.assign(n,{}); chn.assign(n,{}); cost.assign(n,0); cnt.assign(n,vector<int>(L,0)); xt.assign(n,0);
  for(int j=0;j<n;j++){ cost[j]=cover(j,lvl[j],chn[j]); for(size_t pos=0;pos<O[j].size();pos++) cnt[O[j][pos]][lvl[j][pos]]++; }
  for(int i=0;i<n;i++) xt[i]=taxX(cnt[i].data());
  double E=energy_full(); fprintf(stderr,"init E %.1f\n",E);
  double bestE=E; vector<vector<int>> bestQ=Q;
  vector<int> nl,nc; vector<vector<int>> NL(n),NC(n); vector<double> NCost(n);
  long acc=0;
  for(long it=0;it<iters;it++){
    double T=T0*pow(T1/T0,(double)it/iters);
    int i=rng.r(n); int s=1+rng.r(L-1);
    vector<int> oldq=Q[i]; vector<Span> oldsp=SP[i]; vector<u64> oldh=HS[i];
    bool ok=true;
    if(rng.u()<JOINP){   // JOIN: i adopts the dim-(s+1) frame of another port i2 (needs p_i inside it)
      int i2=-1,s2=s; for(int tr=0;tr<30;tr++){ int c=rng.r(n); if(c!=i && has(SP[c][s],P[i])){i2=c;break;} }
      if(i2<0) continue;
      // chain from p_i up to f using random elements of f
      vector<int> el; for(int x=1;x<512;x++) if(has(SP[i2][s],x)) el.push_back(x);
      Span cur; memset(&cur,0,sizeof cur); setb(cur,0); setb(cur,P[i]);
      bool same=true; vector<int> nq(L); nq[0]=P[i];
      for(int t=1;t<=s;t++){ int v=-1; for(int tr=0;tr<200;tr++){ int c=el[rng.r(el.size())]; if(!has(cur,c)){v=c;break;} } if(v<0){ok=false;break;} nq[t]=v; Span nx=cur; for(int x=0;x<512;x++) if(has(cur,x)) setb(nx,x^v); cur=nx; }
      if(!ok) continue;
      bool ch=false; for(int t=1;t<=s;t++) if(nq[t]!=Q[i][t]) ch=true; if(!ch) continue;
      for(int t=1;t<=s;t++){Q[i][t]=nq[t]; buildSpan(i,t);}
    } else {
      int v=-1,bsc=-1; int TS=6;
      for(int c=0;c<TS;c++){ int w=P[rng.r(n)]; if(!indep(i,s,w)) continue; // tournament on a*b of the new frame
        int a=0,b=0; Span S=SP[i][s-1]; for(int x=0;x<512;x++) if(has(SP[i][s-1],x)) setb(S,x^w);
        for(int q=0;q<n;q++){ if(has(S,P[q])) a++; bool z=true; for(int t=0;t<s&&z;t++) if(par(P[q],Q[i][t])) z=false; if(z && !par(P[q],w)) b++; }
        int sc=a*b+ (int)rng.r(3); if(sc>bsc){bsc=sc;v=w;} }
      if(v<0 || v==Q[i][s]) continue;
      Q[i][s]=v; buildSpan(i,s);
    }
    for(int t=s+1;t<L;t++){ if(has(SP[i][t-1],Q[i][t])){ int w,tr=0; do{ w=P[rng.r(n)]; tr++; }while(has(SP[i][t-1],w)&&tr<50); if(has(SP[i][t-1],w)){ok=false;break;} Q[i][t]=w; } buildSpan(i,t); }
    if(!ok){ Q[i]=oldq; SP[i]=oldsp; HS[i]=oldh; continue; }
    // affected ys
    const vector<int>&aff=Oinv[i];
    double dE=0; vector<int> touchedI;
    for(int j:aff){ NCost[j]=cover(j,NL[j],NC[j]); dE+=NCost[j]-cost[j]; }
    // cnt delta
    static vector<int> mark; if((int)mark.size()<n) mark.assign(n,0);
    vector<array<int,3>> dl; // i', s, delta
    for(int j:aff){ for(size_t pos=0;pos<O[j].size();pos++){ int ip=O[j][pos]; if(lvl[j][pos]!=NL[j][pos]){ cnt[ip][lvl[j][pos]]--; cnt[ip][NL[j][pos]]++; dl.push_back({ip,lvl[j][pos],NL[j][pos]}); } } }
    double dX=0; vector<int> ti; for(auto&a:dl){ if(!mark[a[0]]){mark[a[0]]=1; ti.push_back(a[0]);} }
    vector<double> newxt(ti.size()); for(size_t a=0;a<ti.size();a++){ newxt[a]=taxX(cnt[ti[a]].data()); dX+=newxt[a]-xt[ti[a]]; mark[ti[a]]=0; }
    double d=dE+dX;
    if(d<=0 || rng.u()<exp(-d/T)){
      for(int j:aff){ cost[j]=NCost[j]; lvl[j]=NL[j]; chn[j]=NC[j]; }
      for(size_t a=0;a<ti.size();a++) xt[ti[a]]=newxt[a];
      E+=d; acc++;
      if(E<bestE-1e-9){bestE=E; bestQ=Q;}
    } else {
      for(auto&a:dl){ cnt[a[0]][a[1]]++; cnt[a[0]][a[2]]--; }
      Q[i]=oldq; SP[i]=oldsp; HS[i]=oldh;
    }
    if(it%20000==0) fprintf(stderr,"it %ld T %.3f E %.1f best %.1f acc %ld\n",it,T,E,bestE,acc);
  }
  // restore best and print
  Q=bestQ; for(int i=0;i<n;i++) rebuild(i,0);
  cnt.assign(n,vector<int>(L,0));
  for(int j=0;j<n;j++){ cost[j]=cover(j,lvl[j],chn[j]); for(size_t pos=0;pos<O[j].size();pos++) cnt[O[j][pos]][lvl[j][pos]]++; }
  double tx=0,tc=0; for(int i=0;i<n;i++){xt[i]=taxX(cnt[i].data()); tx+=xt[i];} for(int j=0;j<n;j++) tc+=cost[j];
  fprintf(stderr,"final E %.1f (Y/hub %.1f X %.1f)\n",tx+tc,tc,tx);
  printf("E %.4f\n",tx+tc);
  for(int i=0;i<n;i++){ printf("Q %d",i); for(int s=0;s<L;s++) printf(" %d",Q[i][s]); printf("\n"); }
  for(int j=0;j<n;j++){ printf("Y %d %.4f",j,cost[j]); for(size_t pos=0;pos<O[j].size();pos++) printf(" %d:%d:%d",O[j][pos],lvl[j][pos],chn[j][pos]); printf("\n"); }
  return 0;
}
