// k2search.inc -- K2SEARCH lane (toolkit/module docstring): exact-delta SA/LNS moves on k2net rendezvous event programs.
// Included by k2.cpp after k2net.inc; run with K2_NET=<net> K2_SEARCH=<census|walk|sa>.  Every proposal = an EDIT (removals, insertions at gaps, register renames, init changes)
// applied to a copy of the program, then CLEANUP (empty stops deleted: middle rungs, helper births/ends; idle helpers -> single jump) and a FULL VERIFY:
// frame law, nesting (public ascend / owned descend), dyadic |q|+1<2^16, COPY into cleared owned, owned exits, fixed main ends, helper credit > 0, scalar budget, event cap,
// and the value contract (final register = e_r, Y = e_r + e_{r-112}, owned 0) by random evaluation mod 2^61-1 (KV=3).  Objective: exact invoice kappa (double); R0 reported.
// env: K2S_SEED K2S_ITERS K2S_T0 K2S_T1 (temperatures in 1e-7 kappa units) K2S_OUT (best net) K2S_CAP (event cap, default 26000) K2S_W (move weights "shift,mshift,ret,cadd,cdel,kill,ins,split")
//      K2S_LOG (trajectory file) K2S_DUMPEVERY.  Mode walk: accept every legal proposal (validation of python == C++); census: local-optimality census from the input state.
#include <unordered_map>
#include <string>
#include <map>
#include <set>
#include <chrono>
static double TPR[8]={0}; static inline double nowS(){ return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static const u64 PM=(1ULL<<61)-1;
static inline u64 mred(unsigned __int128 x){ u64 r=(u64)(x&PM)+(u64)(x>>61); r=(r&PM)+(r>>61); if(r>=PM) r-=PM; return r; }
static inline u64 mmul(u64 a,u64 b){ return mred((unsigned __int128)a*b); }
static inline u64 madd(u64 a,u64 b){ u64 r=a+b; if(r>=PM) r-=PM; return r; }
static inline u64 msub(u64 a,u64 b){ return a>=b? a-b : a+PM-b; }
static u64 mpow(u64 a,u64 e){ u64 r=1; while(e){ if(e&1) r=mmul(r,a); a=mmul(a,a); e>>=1; } return r; }
static inline u64 minv(u64 a){ return mpow(a,PM-2); }
const int KV=3; typedef array<u64,KV> V3;
static inline bool vzero(const V3&a){ return !a[0]&&!a[1]&&!a[2]; }
struct Co{ long long n; int e; };            // n*2^e, n odd (or 0)
static Co coNorm(long long n,int e){ if(!n) return {0,0}; while(!(n&1)){ n>>=1; e++; } return {n,e}; }
static Co coFromD(double c){ if(c==0) return {0,0}; int ex; double m=frexp(c,&ex); long long n=(long long)ldexp(m,53); return coNorm(n,ex-53); }
static inline u64 p2(int e){ int t=((e%61)+61)%61; return 1ULL<<t; }
static u64 coMod(Co c){ if(!c.n) return 0; u64 m=(u64)(c.n<0?-c.n:c.n)%PM; if(c.n<0&&m) m=PM-m; return mmul(m,p2(c.e)); }
static bool coOK(Co c){ if(!c.n) return false; long double a=fabsl((long double)c.n)*powl(2.0L,c.e); return a+1<65536.0L && c.e>-40; }
static string coStr(Co c){ char b[64]; if(c.e>=0) snprintf(b,64,"%lld",c.n<<c.e); else snprintf(b,64,"%lld/%lld",c.n,1LL<<(-c.e)); return b; }
static int bitlen(unsigned long long x){ return x?64-__builtin_clzll(x):0; }
static unordered_map<u64,Co> DY;             // residue -> dyadic rational (|n| odd <= 4095, e in [-16,16])
static void buildDY(){ for(long long n=1;n<=4095;n+=2) for(int e=-16;e<=16;e++) for(int sg=-1;sg<=1;sg+=2){ Co c{sg*n,e}; if(!coOK(c)) continue; DY.emplace(coMod(c),c); } }
struct Ev{ char k; int d,s,f; Co c; };
// ---------------- global static data ----------------
static int SNF, SN0, SNO;                        // frames, public count of the input net, owned count
static vector<int> SDIM; static vector<array<u64,8>> SSP; static vector<vector<int>> SBAS;
static vector<char> ROLE; static vector<int> FIXFIN; static vector<V3> V0; static u64 RSEED=1;
static long CAP=26000; static int FREEB=0;
static inline bool sub(int a,int b){ for(int w=0;w<8;w++) if(SSP[a][w]&~SSP[b][w]) return false; return true; }   // span(a) subset span(b)
static inline bool psub(int a,int b){ return a!=b && SDIM[a]<SDIM[b] && sub(a,b); }
static u64 rng64(){ RSEED^=RSEED<<13; RSEED^=RSEED>>7; RSEED^=RSEED<<17; return RSEED; }
static inline int rnd(int n){ return n<=0?0:(int)(rng64()%(u64)n); }
static inline double urand(){ return (rng64()>>11)*(1.0/9007199254740992.0); }
static V3 randV(){ V3 v; for(int k=0;k<KV;k++) v[k]=rng64()%PM; return v; }
static void ensureReg(int r){ while((int)ROLE.size()<=r){ ROLE.push_back('H'); FIXFIN.push_back(-1); V0.push_back(randV()); } }
struct State{ vector<Ev> P; vector<int> init; long p0=-1, q=0; };   // p0/q: change hints (events [0,p0) and the last q events equal the state the edit was applied to; p0<0 = unknown)
struct Res{ bool ok; const char*why; long at; double kap,R0,R0x,R0y,R0h,obj; long nev,scalar,nhel; long paid[16]; long hel[16]; long lt,budget; };   // lt = owned lifetimes (INITs), budget = scalar + routes (price_exact.budgets)
static const int TOUTr[]={145,73,17,25,33,41,49,57,65}; static const long TOUTn[]={208,208,416,416,416,416,416,416,416};
static const int POUTr[]={1,72,16,24,32,40,48,56,64}; static const long POUTn[]={15*104,208,416,416,416,416,416,416,416};
static int COSTR0=0;   // K2S_COST=r0: SA objective = -R0 (dE in R0 units); default exact invoice kappa
static double kapOf(const long*paid,const long*hel){
  double Tr[32],Tn[32],Pr[32],Pn[32]; int nt=0,np=0;
  for(int i=0;i<9;i++){ Tr[nt]=TOUTr[i]; Tn[nt++]=TOUTn[i]; Pr[np]=POUTr[i]; Pn[np++]=POUTn[i]; }
  for(int r=1;r<16;r++){ if(hel[r]){ Tr[nt]=r; Tn[nt++]=18.0*hel[r]; } if(paid[r]){ Pr[np]=r; Pn[np++]=18.0*paid[r]; } }
  auto f=[&](double k){ double e=1-k,s=0; for(int i=0;i<nt;i++) s+=Tn[i]*pow(Tr[i],e); for(int i=0;i<np;i++) s-=Pn[i]*pow(Pr[i],e); return s; };
  double lo=1e-5,hi=0.02; for(int it=0;it<100;it++){ double m=(lo+hi)/2; if(f(m)>0) lo=m; else hi=m; } return lo;
}
static double taxMask(int m){ if(!m) return 0; int lo=__builtin_ctz(m), hi=31-__builtin_clz(m); double t=RL[hi-lo]; int prev=lo; for(int d=lo+1;d<=hi;d++) if(m>>d&1){ t-=RL[d-prev]; prev=d; } return t; }
// ---------------- full verifier ----------------
// simEvent: ONE copy of the per-event legality + value semantics, shared by verify() (whole program), verifyInc() (checkpoint resume) and buildIndex().
static inline long scalOfEv(const Ev&e){
  switch(e.k){ case 'I': case 'X': return 2;
    case 'S': { int nb=e.c.e>=0?1+e.c.e:1, db=e.c.e>=0?1:1-e.c.e; return 2*(abs(nb-db)+(e.c.n<0)); }
    case 'A': case 'C': { unsigned long long an=(unsigned long long)(e.c.n<0?-e.c.n:e.c.n); int dbm1; if(e.c.e>=0){ an<<=e.c.e; dbm1=0; } else dbm1=-e.c.e; int nb=bitlen(an), pcnt=__builtin_popcountll(an); return 2*(3+nb-1+pcnt+dbm1); } }
  return 0; }
static inline const char* simEvent(const Ev&e,int NR,vector<int>&cur,vector<char>&act,vector<V3>&val,int&nact,long*paid,long&scal){
  int d=e.d; if(d<0||d>=NR) return "reg index";
  switch(e.k){
  case 'M': { int c=cur[d]; if(c<0) return "MOVE unlocated";
    if(ROLE[d]=='O'){ if(!act[d]||!psub(e.f,c)) return "owned MOVE not descending"; }
    else if(!psub(c,e.f)) return "MOVE not ascending";
    paid[abs(SDIM[e.f]-SDIM[c])]++; cur[d]=e.f; return nullptr; }
  case 'I': if(ROLE[d]!='O'||act[d]) return "INIT"; act[d]=1; nact++; for(auto&x:val[d]) x=0; cur[d]=e.f; scal+=2; return nullptr;
  case 'X': if(!act[d]||cur[d]!=e.f) return "CLEAR"; act[d]=0; nact--; for(auto&x:val[d]) x=0; cur[d]=-1; scal+=2; return nullptr;
  case 'S': { if(cur[d]!=e.f) return "SCALE frame"; if(!(e.c.n==1||e.c.n==-1)||!coOK(e.c)) return "SCALE coef";
    u64 q=coMod(e.c); for(auto&x:val[d]) x=mmul(x,q); scal+=scalOfEv(e); return nullptr; }
  case 'A': case 'C': { int s=e.s; if(s<0||s>=NR||s==d) return "source";
    if(cur[d]!=e.f||cur[s]!=e.f) return "rendezvous";
    if(!coOK(e.c)) return "coef";
    u64 q=coMod(e.c);
    if(e.k=='C'){ if(!(ROLE[d]=='O'&&act[d]&&vzero(val[d]))) return "COPY into uncleared"; for(int k=0;k<KV;k++) val[d][k]=mmul(q,val[s][k]); }
    else for(int k=0;k<KV;k++) val[d][k]=madd(val[d][k],mmul(q,val[s][k]));
    scal+=scalOfEv(e); return nullptr; }
  default: return "opcode"; }
}
// end-of-program checks (+ helper credit histogram); false => R.why/R.at set
static bool finalChecks(const State&S,const vector<int>&cur,const vector<V3>&val,int nact,Res&R){
  int NR=S.init.size();
  if(nact){ R.why="owned not cleared"; return false; }
  long nhel=0;
  for(int r=0;r<NR;r++){ char ro=ROLE[r];
    if(ro=='X'||ro=='Y'){ if(cur[r]!=FIXFIN[r]){ R.why="main final frame"; R.at=r; return false; } }
    if(ro=='H'){ int cr=SDIM[cur[r]]-SDIM[S.init[r]]; if(cr<=0){ R.why="helper credit 0"; R.at=r; return false; } R.hel[cr]++; nhel++; }
    V3 ex; if(ro=='O') ex={0,0,0}; else { ex=V0[r]; if(ro=='Y') for(int k=0;k<KV;k++) ex[k]=madd(ex[k],V0[r-112][k]); }
    if(val[r]!=ex){ R.why="contract"; R.at=r; return false; }
  }
  R.nhel=nhel; return true;
}
static void sumTax(const vector<double>&tax,Res&R){ R.R0x=R.R0y=R.R0h=0; int NR=tax.size(); for(int r=0;r<NR;r++){ char ro=ROLE[r]; if(ro=='X') R.R0x+=tax[r]; else if(ro=='Y') R.R0y+=tax[r]; else if(ro=='H') R.R0h+=tax[r]; } }
static bool budgetOK(long n,long scal,const Res&R,long nhel){   // event cap + scalar budget (not under K2S_FREE)
  long pj=0; for(int r=0;r<16;r++) pj+=R.paid[r];
  if(!FREEB&&n>=CAP) return false;
  return true; }
static Res verify(const State&S){
  Res R; memset(&R,0,sizeof R); R.ok=false; R.at=-1; int NR=S.init.size();
  vector<int> cur(NR,-1); vector<char> act(NR,0); vector<V3> val(V0.begin(),V0.begin()+NR); vector<int> mask(NR,0);
  for(int r=0;r<NR;r++){ if(ROLE[r]!='O'){ cur[r]=S.init[r]; if(cur[r]<0){ R.why="public without frame"; return R; } mask[r]=1<<SDIM[cur[r]]; } else for(auto&x:val[r]) x=0; }
  int nact=0; long scal=0; const vector<Ev>&P=S.P; long n=P.size();
  for(long i=0;i<n;i++){ const Ev&e=P[i]; const char*w=simEvent(e,NR,cur,act,val,nact,R.paid,scal); if(w){ R.why=w; R.at=i; return R; } if(e.k=='M') mask[e.d]|=1<<SDIM[e.f]; else if(e.k=='I') R.lt++; }
  if(!finalChecks(S,cur,val,nact,R)) return R;
  vector<double> tax(NR,0.0); for(int r=0;r<NR;r++) if(ROLE[r]!='O') tax[r]=taxMask(mask[r]);
  sumTax(tax,R);
  long pj=0; for(int r=0;r<16;r++) pj+=R.paid[r];
  if(!FREEB&&n>=CAP){ R.why="event cap"; return R; }
  R.budget=scal+1000*(pj+2*R.nhel+2*104+4*104+4*R.lt);   // K2FRAMES: routes count the ACTUAL owned lifetimes (was a fixed 4*8)
  if(!FREEB&&R.budget>=10000000){ R.why="scalar budget"; return R; }
  R.nev=n; R.scalar=scal; R.R0=R.R0x+R.R0y+R.R0h; R.kap=kapOf(R.paid,R.hel); R.obj=COSTR0?-R.R0*1e-7:R.kap; R.ok=true; R.why="ok"; return R;
}
// ---------------- cleanup: delete empty stops ----------------
// cleanup: A (optional) restricts the rules to the registers flagged in A -- exact when every other register is already clean (the accepted state S is, see SCLEAN), because the rules act per
// register.  With A the rules run on the list of events touching A only (one O(n) gather, then O(|A events|)); compaction happens only if something is deleted.
static void cleanup(State&S,const vector<char>*A=nullptr){
  int NR=S.init.size(); const vector<Ev>&P=S.P; long n=P.size();
  auto in=[&](int r){ return !A||(*A)[r]; };
  static vector<long> ids; ids.clear();
  if(A){ for(long i=0;i<n;i++){ const Ev&e=P[i]; if((*A)[e.d]||((e.k=='A'||e.k=='C')&&(*A)[e.s])) ids.push_back(i); } } else { ids.resize(n); for(long i=0;i<n;i++) ids[i]=i; }
  vector<int> totE(NR,0), totM(NR,0), delM(NR,0);
  for(long i:ids){ const Ev&e=P[i]; if(e.k=='M'){ if(in(e.d)) totM[e.d]++; continue; } if(in(e.d)) totE[e.d]++; if((e.k=='A'||e.k=='C')&&in(e.s)) totE[e.s]++; }
  static vector<char> del; if((long)del.size()<n) del.resize(n,0); static vector<long> dl; dl.clear();
  auto setDel=[&](long i){ if(!del[i]){ del[i]=1; dl.push_back(i); } };
  vector<long> enter(NR,-1); vector<int> cnt(NR,0), nmv(NR,0), nev(NR,0);
  for(long i:ids){ const Ev&e=P[i];
    if(e.k=='M'){ int r=e.d; if(!in(r)) continue; char ro=ROLE[r];
      if(cnt[r]==0){
        if(enter[r]>=0){ setDel(enter[r]); delM[r]++; }                     // middle stop empty: drop its entering MOVE
        else if(ro=='H'&&enter[r]==-1&&nev[r]==0&&totE[r]>0&&totM[r]-delM[r]>=2){ S.init[r]=e.f; setDel(i); delM[r]++; enter[r]=-1; cnt[r]=0; continue; }   // helper birth shift
      }
      enter[r]=i; cnt[r]=0; nmv[r]++; continue; }
    if(e.k=='I'){ if(in(e.d)){ enter[e.d]=-2; cnt[e.d]=1; nev[e.d]++; } continue; }
    if(in(e.d)){ cnt[e.d]++; nev[e.d]++; if(e.k=='X'){ enter[e.d]=-2; } }
    if((e.k=='A'||e.k=='C')&&in(e.s)){ cnt[e.s]++; nev[e.s]++; }
  }
  for(int r=0;r<NR;r++){ if(ROLE[r]!='H'||!in(r)) continue;
    if(nev[r]==0){ continue; }
    if(cnt[r]==0&&enter[r]>=0){ // last stop empty: drop unless it is the only remaining MOVE
      int alive=0; for(long i:ids) if(P[i].k=='M'&&P[i].d==r&&!del[i]) alive++;
      if(alive>1) setDel(enter[r]); }
  }
  // idle helpers (no events): exactly one MOVE init -> original final
  vector<int> fin(NR,-1); for(int r=0;r<NR;r++) fin[r]=S.init[r]; for(long i:ids) if(P[i].k=='M'&&!del[i]&&in(P[i].d)) fin[P[i].d]=P[i].f;
  vector<char> idleKeep(NR,0); vector<long> fchg;
  for(long k=(long)ids.size()-1;k>=0;k--){ long i=ids[k]; const Ev&e=P[i]; if(e.k=='M'&&ROLE[e.d]=='H'&&in(e.d)&&nev[e.d]==0){ if(!idleKeep[e.d]&&!del[i]){ idleKeep[e.d]=1; if(e.f!=fin[e.d]) fchg.push_back(i); } else setDel(i); } }
  if(dl.empty()&&fchg.empty()) return;
  long cmin=n, cmax=-1; for(long i:dl){ cmin=min(cmin,i); cmax=max(cmax,i); } for(long i:fchg){ cmin=min(cmin,i); cmax=max(cmax,i); }
  vector<Ev>&PM=S.P; for(long i:fchg) PM[i].f=fin[PM[i].d];
  if(!dl.empty()){ long w=0; for(long i=0;i<n;i++){ if(del[i]) continue; if(w!=i) PM[w]=PM[i]; w++; } PM.resize(w); for(long i:dl) del[i]=0; }
  if(S.p0>=0){ long hsT=max(n-S.q,cmax+1); S.p0=min(S.p0,cmin); S.q=n-hsT; if(S.q<0) S.q=0; if((long)PM.size()-S.q<S.p0) S.q=(long)PM.size()-S.p0; }
}
// ---------------- planning index ----------------
struct Stop{ int f,a,b; }; struct Ver{ int a,b; V3 v; u64 iv; int hsid=-1; };
struct HSTab{   // flat chained hash (key -> (reg,version) list); entries die lazily (val.first = -1) and are appended incrementally; candidates are sorted by (reg,version) by the reader
  vector<int> head,nxt; vector<u64> key; vector<pair<int,int>> val; u64 mask=0; long dead=0; bool ok=false;
  void reset(size_t n){ size_t b=16; while(b<2*n) b<<=1; head.assign(b,-1); mask=b-1; nxt.clear(); key.clear(); val.clear(); nxt.reserve(n+n/2); key.reserve(n+n/2); val.reserve(n+n/2); dead=0; ok=true; }
  inline int add(u64 k,int r,int v){ size_t h=(k*0x9E3779B97F4A7C15ULL>>20)&mask; int id=nxt.size(); nxt.push_back(head[h]); key.push_back(k); val.push_back({r,v}); head[h]=id; return id; }
  inline void kill(int id){ if(id>=0&&val[id].first>=0){ val[id].first=-1; dead++; } }
  inline int first(u64 k) const { int p=head[(k*0x9E3779B97F4A7C15ULL>>20)&mask]; while(p>=0&&(key[p]!=k||val[p].first<0)) p=nxt[p]; return p; }
  inline int next(int p) const { u64 k=key[p]; p=nxt[p]; while(p>=0&&(key[p]!=k||val[p].first<0)) p=nxt[p]; return p; }
};
static const int CKN=1024;   // simulation checkpoint spacing (events); checkpoints carry their own position (they shift with the program)
struct Ck{ long pos; vector<int> cur,sa,va; vector<char> act; vector<V3> val; long paid[16]; long scal; };
struct Index{
  vector<vector<Stop>> ST; vector<vector<Ver>> VR; vector<vector<int>> BAR, WR, TOUCH; vector<vector<array<int,3>>> OCC;
  HSTab HS; long n; int nr=0;
  vector<Ck> CKS;                                   // checkpoints of the verify simulation (sorted by pos): incremental verify + index resume/splice
  vector<array<uint16_t,32>> CNT; vector<double> TAX; // per register: visits per frame dim (MOVEs + init), chain tax (R0 contribution)
};
static inline u64 pkey(const V3&v,u64 iv){ return v[0]? mmul(v[1],iv) : (v[1]? 0x5bd1e995ULL^mmul(v[2],minv(v[1])) : 0x9e3779b9ULL); }
static double TBI[6]={0};
static long FB[6]={0}; static long BR_RES=0,BR_FULL=0,BR_SPL=0,BR_EV=0;
static int RESUME=1, SPLICE=1, HSINC=1;   // K2S_NORESUME=1: always rebuild from event 0; K2S_NOSPLICE=1: resume to the end instead of splicing at the convergence checkpoint
static inline int ckFloor(const Index&I,long p){ int lo=0,hi=(int)I.CKS.size()-1,ans=0; while(lo<=hi){ int m=(lo+hi)/2; if(I.CKS[m].pos<=p){ ans=m; lo=m+1; } else hi=m-1; } return ans; }
static inline int ckExact(const Index&I,long p){ int lo=0,hi=(int)I.CKS.size()-1; while(lo<=hi){ int m=(lo+hi)/2; if(I.CKS[m].pos<p) lo=m+1; else if(I.CKS[m].pos>p) hi=m-1; else return m; } return -1; }
struct GenL{ vector<Stop> ST; vector<Ver> VR; vector<int> BAR,WR,TOUCH; };
static vector<GenL> GEN;
// buildIndex(S,I,P0,jS,delta): P0 >= 0 = first event position differing from the state I was built for (resume at the checkpoint at or below P0); P0 < 0 = full build.
// jS >= 0 additionally says: T[jS+delta ..] is event-identical to the OLD state's [jS ..) and the simulation state equals the old checkpoint at jS => keep the old index entries after jS (shifted by delta) and only re-simulate [resume, jS+delta).
static void buildIndex(const State&S,Index&I,long P0=-1,long jS=-1,long delta=0,const vector<char>*oldTouched=nullptr){
  double tb0=nowS();
  int NR=S.init.size(); long n=S.P.size();
  bool res=RESUME&&P0>=0&&I.nr==NR&&!I.CKS.empty()&&(int)I.ST.size()==NR;
  int c0=0; if(res) c0=ckFloor(I,P0);
  long P=res?I.CKS[c0].pos:0; int kS=-1; if(res&&SPLICE&&jS>=P){ kS=ckExact(I,jS); if(kS<=c0) kS=-1; }   // K2FRAMES fix: kS == c0 would keep a moved-from checkpoint (empty vectors) in the prefix -> no splice
  bool splice=kS>=0; long jT=splice?jS+delta:n; long iend=splice?jT:n;
  if(res){ if(splice) BR_SPL++; else BR_RES++; BR_EV+=iend-P; } else { BR_FULL++; BR_EV+=n; }
  I.n=n; I.nr=NR; if(getenv("K2S_DBG")) fprintf(stderr,"build res %d splice %d P0 %ld P %ld jS %ld delta %ld jT %ld n %ld c0 %d kS %d\n",(int)res,(int)splice,P0,P,jS,delta,jT,n,c0,kS);
  vector<int> cur,sa,va; vector<char> act; vector<V3> val; long paid[16]; long scal; long lastCk;
  if((int)GEN.size()!=NR){ GEN.clear(); GEN.resize(NR); }
  vector<int> touched; touched.reserve(256); vector<char> tmark(NR,0);
  auto touch=[&](int r){ if(!tmark[r]){ tmark[r]=1; touched.push_back(r); } };
  vector<Ck> newCK;
  if(!res){
    auto rs=[&](auto&V,int m){ if((int)V.size()!=m){ V.clear(); V.resize(m); } else for(auto&x:V) x.clear(); }; rs(I.ST,NR); rs(I.VR,NR); rs(I.BAR,NR); rs(I.WR,NR); rs(I.TOUCH,NR);
    cur.assign(NR,-1); sa.assign(NR,0); va.assign(NR,0); act.assign(NR,0); val.assign(V0.begin(),V0.begin()+NR); memset(paid,0,sizeof paid); scal=0;
    for(int r=0;r<NR;r++) if(ROLE[r]!='O') cur[r]=S.init[r]; else for(auto&x:val[r]) x=0;
    I.CKS.clear(); lastCk=-CKN-1;
  } else {
    const Ck&K=I.CKS[c0]; cur=K.cur; sa=K.sa; va=K.va; act=K.act; val=K.val; memcpy(paid,K.paid,sizeof paid); scal=K.scal; lastCk=K.pos;
  }
  auto closeStop=[&](int r,int b){ if(cur[r]>=0){ GEN[r].ST.push_back({cur[r],sa[r],b}); touch(r); } };
  auto closeVer=[&](int r,int b){ GEN[r].VR.push_back({va[r],b,val[r],0}); touch(r); };
  for(long i=P;i<iend;i++){ const Ev&e=S.P[i]; int d=e.d;
    if(i-lastCk>=CKN&&(i>P||!res)){ newCK.emplace_back(); Ck&K=newCK.back(); K.pos=i; K.cur=cur; K.sa=sa; K.va=va; K.act=act; K.val=val; memcpy(K.paid,paid,sizeof paid); K.scal=scal; lastCk=i; }
    switch(e.k){
    case 'M': closeStop(d,i); paid[abs(SDIM[e.f]-SDIM[cur[d]])]++; cur[d]=e.f; sa[d]=i+1; touch(d); break;
    case 'I': closeVer(d,i); for(auto&x:val[d]) x=0; va[d]=i+1; cur[d]=e.f; act[d]=1; sa[d]=i+1; GEN[d].BAR.push_back(i); GEN[d].TOUCH.push_back(i); scal+=2; break;
    case 'X': closeStop(d,i); cur[d]=-1; act[d]=0; closeVer(d,i); for(auto&x:val[d]) x=0; va[d]=i+1; GEN[d].BAR.push_back(i); GEN[d].TOUCH.push_back(i); scal+=2; break;
    case 'S': { closeVer(d,i); u64 q=coMod(e.c); for(auto&x:val[d]) x=mmul(x,q); va[d]=i+1; GEN[d].BAR.push_back(i); GEN[d].TOUCH.push_back(i); scal+=scalOfEv(e); break; }
    case 'A': case 'C': { int s=e.s; closeVer(d,i); u64 q=coMod(e.c);
      if(e.k=='C'){ for(int k=0;k<KV;k++) val[d][k]=mmul(q,val[s][k]); GEN[d].BAR.push_back(i); } else for(int k=0;k<KV;k++) val[d][k]=madd(val[d][k],mmul(q,val[s][k]));
      va[d]=i+1; GEN[d].WR.push_back(i); touch(s); GEN[s].BAR.push_back(i); GEN[d].TOUCH.push_back(i); GEN[s].TOUCH.push_back(i); scal+=scalOfEv(e); break; }
    }
    if(e.k!='M'&&e.k!='A'&&e.k!='C') touch(d);
  }
  double tq0=nowS(); TBI[4]+=tq0-tb0;
  if(!splice) for(int r=0;r<NR;r++){ closeStop(r,n); closeVer(r,n); }
  // ---- merge generated entries into the index lists: [first entry >= P, first entry >= jS) is replaced by the generated entries, later entries shift by delta
  vector<int> vr0(NR,0), vrNew(NR,0), vrDrop(NR,0); bool incHS=HSINC&&res&&I.HS.ok&&I.HS.dead*2<(long)I.HS.nxt.size();
  auto mergeList=[&](auto&L,auto&G,auto keyf,auto shiftf)->size_t{
    typedef typename std::remove_reference<decltype(L)>::type::value_type T_;
    size_t i1=lower_bound(L.begin(),L.end(),P,[&](const T_&x,long v){ return (long)keyf(x)<v; })-L.begin();
    size_t i2=splice? (size_t)(lower_bound(L.begin(),L.end(),jS,[&](const T_&x,long v){ return (long)keyf(x)<v; })-L.begin()) : L.size();
    if(i2<i1) i2=i1;
    size_t g=G.size();
    if(g==i2-i1){ for(size_t k=0;k<g;k++) L[i1+k]=G[k]; }
    else { L.erase(L.begin()+i1,L.begin()+i2); L.insert(L.begin()+i1,G.begin(),G.end()); }
    if(splice&&delta!=0) for(size_t k=i1+g;k<L.size();k++) shiftf(L[k]);
    G.clear(); return i1+g; };
  for(int r=0;r<NR;r++){
    if(!tmark[r]&&delta==0&&splice&&oldTouched&&!(*oldTouched)[r]) continue;   // untouched by the old AND the new changed region (delta 0: nothing to shift either)
    { size_t f=mergeList(I.ST[r],GEN[r].ST,[](const Stop&x){return x.b;},[&](Stop&x){ x.a+=delta; x.b+=delta; });
      if(splice&&cur[r]>=0&&f<I.ST[r].size()) I.ST[r][f].a=sa[r]; }
    { size_t i1=lower_bound(I.VR[r].begin(),I.VR[r].end(),P,[](const Ver&x,long v){return (long)x.b<v;})-I.VR[r].begin(); vr0[r]=i1; vrNew[r]=GEN[r].VR.size();
      size_t i2v=splice? (size_t)(lower_bound(I.VR[r].begin(),I.VR[r].end(),jS,[](const Ver&x,long v){return (long)x.b<v;})-I.VR[r].begin()) : I.VR[r].size(); if(i2v<i1) i2v=i1; vrDrop[r]=i2v-i1; if(incHS) for(size_t k=i1;k<i2v;k++) I.HS.kill(I.VR[r][k].hsid);
      size_t f=mergeList(I.VR[r],GEN[r].VR,[](const Ver&x){return x.b;},[&](Ver&x){ x.a+=delta; x.b+=delta; });
      if(splice&&f<I.VR[r].size()) I.VR[r][f].a=va[r]; }
    mergeList(I.BAR[r],GEN[r].BAR,[](int x){return x;},[&](int&x){ x+=delta; });
    mergeList(I.WR[r],GEN[r].WR,[](int x){return x;},[&](int&x){ x+=delta; });
    mergeList(I.TOUCH[r],GEN[r].TOUCH,[](int x){return x;},[&](int&x){ x+=delta; });
  }
  double tq1=nowS(); TBI[5]+=tq1-tq0;
  // checkpoints: kept prefix, generated, shifted suffix
  { vector<Ck> suff; if(splice) suff.assign(make_move_iterator(I.CKS.begin()+kS),make_move_iterator(I.CKS.end()));
    I.CKS.resize(res?c0+1:0); for(auto&k:newCK) I.CKS.push_back(std::move(k));
    if(splice){ long dp[16]; for(int k=0;k<16;k++) dp[k]=paid[k]-suff[0].paid[k]; long ds=scal-suff[0].scal;
      // sa/va == jS means the stop/version began at jS-1, inside the changed region: the simulated state is the truth
      for(size_t q2=0;q2<suff.size();q2++){ Ck&k=suff[q2]; for(int q=0;q<16;q++) k.paid[q]+=dp[q]; k.scal+=ds;
        if(q2==0){ k.sa=sa; k.va=va; } else for(int r=0;r<NR;r++){ k.sa[r]=(k.sa[r]>jS)?k.sa[r]+(int)delta:sa[r]; k.va[r]=(k.va[r]>jS)?k.va[r]+(int)delta:va[r]; }
        k.pos+=delta; }
      for(auto&k:suff) I.CKS.push_back(std::move(k)); } }
  double tb1=nowS(); TBI[0]+=tb1-tb0;
  { if((int)I.OCC.size()!=SNF) I.OCC.assign(SNF,{}); else for(auto&x:I.OCC) x.clear();
    for(int r=0;r<NR;r++) for(auto&s2:I.ST[r]) I.OCC[s2.f].push_back({r,s2.a,s2.b}); }
  // chain visits / tax
  I.CNT.assign(NR,array<uint16_t,32>{}); for(int r=0;r<NR;r++) if(ROLE[r]!='O') I.CNT[r][SDIM[S.init[r]]]++;
  for(long i=0;i<n;i++){ const Ev&e=S.P[i]; if(e.k=='M'&&ROLE[e.d]!='O') I.CNT[e.d][SDIM[e.f]]++; }
  I.TAX.assign(NR,0.0); for(int r=0;r<NR;r++) if(ROLE[r]!='O'){ int m=0; for(int d=0;d<32;d++) if(I.CNT[r][d]) m|=1<<d; I.TAX[r]=taxMask(m); }
  double tb2=nowS(); TBI[1]+=tb2-tb1;
  // batch inverse of v[0] for the NEW versions only (kept versions carry their inverse)
  vector<u64*> ptr; vector<u64> pre,vals; u64 acc=1;
  for(int r=0;r<NR;r++) for(size_t k=vr0[r];k<(size_t)vr0[r]+vrNew[r];k++){ auto&v=I.VR[r][k]; if(v.v[0]){ pre.push_back(acc); vals.push_back(v.v[0]); acc=mmul(acc,v.v[0]); ptr.push_back(&v.iv); } }
  if(!ptr.empty()){ u64 ia=minv(acc); for(long j=(long)ptr.size()-1;j>=0;j--){ *ptr[j]=mmul(ia,pre[j]); ia=mmul(ia,vals[j]); } }
  double tb3=nowS(); TBI[2]+=tb3-tb2;
  if(!incHS){ size_t tot=0; for(int r=0;r<NR;r++) tot+=I.VR[r].size(); I.HS.reset(tot);
    for(int r=NR-1;r>=0;r--) for(int k=(int)I.VR[r].size()-1;k>=0;k--){ auto&v=I.VR[r][k]; if(vzero(v.v)){ v.hsid=-1; continue; } v.hsid=I.HS.add(pkey(v.v,v.iv),r,k); } }
  else for(int r=0;r<NR;r++){ if(!vrNew[r]&&!vrDrop[r]) continue; auto&L=I.VR[r];
    for(size_t k=vr0[r];k<(size_t)vr0[r]+vrNew[r];k++){ auto&v=L[k]; if(vzero(v.v)) v.hsid=-1; else v.hsid=I.HS.add(pkey(v.v,v.iv),r,k); }
    if(vrNew[r]!=vrDrop[r]) for(size_t k=vr0[r]+vrNew[r];k<L.size();k++) if(L[k].hsid>=0) I.HS.val[L[k].hsid].second=k; }
  TBI[3]+=nowS()-tb3;
}
// FULLVERIFY oracle: every checkpoint of I equals a from-scratch simulation of S at the same position
static bool ckValid(const State&S,const Index&I,const char**what){
  int NR=S.init.size(); long n=S.P.size(); *what="ckpt";
  vector<int> cur(NR,-1),sa(NR,0),va(NR,0); vector<char> act(NR,0); vector<V3> val(V0.begin(),V0.begin()+NR); long paid[16]={0}; long scal=0;
  for(int r=0;r<NR;r++) if(ROLE[r]!='O') cur[r]=S.init[r]; else for(auto&x:val[r]) x=0;
  size_t kc=0;
  for(long i=0;i<=n;i++){
    while(kc<I.CKS.size()&&I.CKS[kc].pos<i) kc++;
    if(kc<I.CKS.size()&&I.CKS[kc].pos==i){ const Ck&K=I.CKS[kc]; if(K.cur!=cur||K.act!=act||K.val!=val||K.sa!=sa||K.va!=va||K.scal!=scal||memcmp(K.paid,paid,sizeof paid)){ *what="ckpt-state"; if(getenv("K2S_DBG")){ fprintf(stderr,"ckpt pos %ld: cur %d act %d val %d sa %d va %d scal %d(%ld vs %ld) paid %d\n",i,K.cur==cur,K.act==act,K.val==val,K.sa==sa,K.va==va,K.scal==scal,K.scal,scal,!memcmp(K.paid,paid,sizeof paid)); if(K.sa!=sa) for(int r=0;r<NR;r++) if(K.sa[r]!=sa[r]){ fprintf(stderr,"  sa[%d] stored %d fresh %d (role %c cur %d)\n",r,K.sa[r],sa[r],ROLE[r],cur[r]); break; } if(K.va!=va) for(int r=0;r<NR;r++) if(K.va[r]!=va[r]){ fprintf(stderr,"  va[%d] stored %d fresh %d (role %c)\n",r,K.va[r],va[r],ROLE[r]); break; } } return false; } kc++; }
    if(i==n) break;
    const Ev&e=S.P[i]; int d=e.d;
    switch(e.k){
    case 'M': paid[abs(SDIM[e.f]-SDIM[cur[d]])]++; cur[d]=e.f; sa[d]=i+1; break;
    case 'I': for(auto&x:val[d]) x=0; va[d]=i+1; cur[d]=e.f; act[d]=1; sa[d]=i+1; scal+=2; break;
    case 'X': cur[d]=-1; act[d]=0; for(auto&x:val[d]) x=0; va[d]=i+1; scal+=2; break;
    case 'S': { u64 q=coMod(e.c); for(auto&x:val[d]) x=mmul(x,q); va[d]=i+1; scal+=scalOfEv(e); break; }
    case 'A': case 'C': { int s2=e.s; u64 q=coMod(e.c); if(e.k=='C'){ for(int k=0;k<KV;k++) val[d][k]=mmul(q,val[s2][k]); } else for(int k=0;k<KV;k++) val[d][k]=madd(val[d][k],mmul(q,val[s2][k])); va[d]=i+1; scal+=scalOfEv(e); break; }
    } }
  return true; }
static bool indexEqual(const Index&A,const Index&B,const char**what){
  int NR=A.ST.size(); *what="size"; if((int)B.ST.size()!=NR||A.n!=B.n||A.nr!=B.nr) return false;
  for(int r=0;r<NR;r++){
    *what="ST"; if(A.ST[r].size()!=B.ST[r].size()) return false; for(size_t k=0;k<A.ST[r].size();k++){ auto&x=A.ST[r][k]; auto&y=B.ST[r][k]; if(x.f!=y.f||x.a!=y.a||x.b!=y.b) return false; }
    *what="VR"; if(A.VR[r].size()!=B.VR[r].size()) return false; for(size_t k=0;k<A.VR[r].size();k++){ auto&x=A.VR[r][k]; auto&y=B.VR[r][k]; if(x.a!=y.a||x.b!=y.b||x.v!=y.v||x.iv!=y.iv) return false; }
    *what="BAR"; if(A.BAR[r]!=B.BAR[r]) return false; *what="WR"; if(A.WR[r]!=B.WR[r]) return false; *what="TOUCH"; if(A.TOUCH[r]!=B.TOUCH[r]) return false; }
  *what="OCC"; if(A.OCC!=B.OCC) return false; *what="CNT"; if(A.CNT!=B.CNT) return false; *what="TAX"; if(A.TAX!=B.TAX) return false;
  *what="CKS-pos"; if(A.CKS.empty()||A.CKS[0].pos!=0) return false; for(size_t c=1;c<A.CKS.size();c++) if(A.CKS[c].pos<=A.CKS[c-1].pos) return false;
  *what="HS"; { auto ents=[&](const Index&X,vector<array<long,3>>&o){ for(size_t id=0;id<X.HS.val.size();id++){ if(X.HS.val[id].first<0) continue; o.push_back({(long)X.HS.key[id],(long)X.HS.val[id].first,(long)X.HS.val[id].second}); } sort(o.begin(),o.end()); };
    vector<array<long,3>> ea,eb; ents(A,ea); ents(B,eb); if(ea!=eb) return false;
    for(auto&x:ea){ const Ver&v=A.VR[x[1]][x[2]]; if((long)pkey(v.v,v.iv)!=x[0]||v.hsid<0||A.HS.val[v.hsid].second!=x[2]||A.HS.val[v.hsid].first!=x[1]) return false; } }
  return true; }
// ---------------- incremental verifier ----------------
// Resume the verification simulation of the ACCEPTED state S (checkpoints every CKN events, taken by buildIndex) at the checkpoint below the first changed event, simulate the changed
// region of T, and stop as soon as the full simulation state (frames, owned liveness, ALL register value vectors) equals S's checkpoint again: the rest of T is event-identical to the rest of S,
// which is legal and ends in the right values, so it is skipped.  Totals (paid ranks, scalar budget) = S totals - S[checkpoints] + simulated; chain taxes from per-register dim visit counts.
// Exact by construction (same simEvent); K2S_FULLVERIFY=1 compares every call with verify(); K2S_NOINC=1 disables.
static long LCV_j=-1, LCV_delta=0; static int LOCALCL=1; static int INCV=1, FULLV=0, FASTCL=1, SCLEAN=0; static long PERIODIC=5000; static long BIGREG=12000, NFAST=0; static long VI_FULL=0, VI_INC=0, VI_CONV=0, VI_SIMEV=0;
static int stopAt(const Index&I,int r,int g){ const auto&v=I.ST[r]; int lo=0,hi=(int)v.size()-1; while(lo<=hi){ int m=(lo+hi)/2; if(v[m].b<g) lo=m+1; else if(v[m].a>g) hi=m-1; else return m; } return -1; }
static int verAt(const Index&I,int r,int g){ const auto&v=I.VR[r]; int lo=0,hi=(int)v.size()-1; while(lo<=hi){ int m=(lo+hi)/2; if(v[m].b<g) lo=m+1; else if(v[m].a>g) hi=m-1; else return m; } return -1; }
static void dWin(const Index&I,int d,long i,int&wa,int&wb){ const auto&B=I.BAR[d]; auto it=lower_bound(B.begin(),B.end(),(int)i); wb=(it==B.end())?I.n:*it; wa=(it==B.begin())?0:*(it-1)+1; }
struct Cand{ int s; Co c; int g; int f; };
struct Excl{ int r,x,y; };   // forbid gaps [x,y] whenever register r is involved (as source or destination)
// pick a gap in [a,b] minus forbidden intervals
static int pickGap(int a,int b,const vector<pair<int,int>>&forb){
  vector<pair<int,int>> seg={{a,b}};
  for(auto&f:forb){ vector<pair<int,int>> ns; for(auto&s:seg){ if(f.second<s.first||f.first>s.second){ ns.push_back(s); continue; } if(s.first<f.first) ns.push_back({s.first,f.first-1}); if(f.second<s.second) ns.push_back({f.second+1,s.second}); } seg.swap(ns); }
  long tot=0; for(auto&s:seg) tot+=s.second-s.first+1; if(tot<=0) return -1; long k=rng64()%tot; for(auto&s:seg){ long L=s.second-s.first+1; if(k<L) return s.first+k; k-=L; } return -1;
}
// co-located gap of d and s inside [a,b] (excluding forbidden); returns gap or -1, frame in *fo
static int coloc(const Index&I,int d,int s,int a,int b,const vector<Excl>&ex,int*fo,int avoidF=-1){
  const auto&A=I.ST[d]; const auto&B=I.ST[s]; int ia=stopAt(I,d,a), ib=stopAt(I,s,a);
  if(ia<0){ ia=0; while(ia<(int)A.size()&&A[ia].b<a) ia++; } if(ib<0){ ib=0; while(ib<(int)B.size()&&B[ib].b<a) ib++; }
  vector<array<int,3>> opts;
  while(ia<(int)A.size()&&ib<(int)B.size()){ const Stop&x=A[ia]; const Stop&y=B[ib]; if(x.a>b||y.a>b) break;
    int lo=max(max(x.a,y.a),a), hi=min(min(x.b,y.b),b);
    if(x.f==y.f&&lo<=hi&&x.f!=avoidF){ vector<pair<int,int>> fb; for(auto&e:ex) if(e.r==d||e.r==s) fb.push_back({e.x,e.y}); int g=pickGap(lo,hi,fb); if(g>=0) opts.push_back({g,x.f,0}); }
    if(x.b<y.b) ia++; else ib++; }
  if(opts.empty()) return -1; auto&o=opts[rnd(opts.size())]; *fo=o[1]; return o[0];
}
static void findSources(const Index&I,const V3&t,int d,int wa,int wb,const vector<Excl>&ex,vector<Cand>&out,int maxOut,int skipS=-1,int skipV=-1){
  if(vzero(t)) return;
  static vector<pair<int,int>> hc; hc.clear(); for(int hp=I.HS.first(t[0]?mmul(t[1],minv(t[0])):pkey(t,0)); hp>=0; hp=I.HS.next(hp)) hc.push_back(I.HS.val[hp]); sort(hc.begin(),hc.end());
  for(auto&rv:hc){ int s=rv.first; if(s==d) continue; if(s==skipS&&rv.second==skipV) continue; const Ver&V=I.VR[s][rv.second];
    if(!V.v[0]&&t[0]) continue; u64 lam= t[0]? mmul(t[0],V.iv) : 0; if(!t[0]){ if(!V.v[1]) continue; lam=mmul(t[1],minv(V.v[1])); }
    bool okp=true; for(int k=0;k<KV;k++) if(mmul(V.v[k],lam)!=t[k]){ okp=false; break; } if(!okp) continue;
    auto dy=DY.find(lam); if(dy==DY.end()) continue; Co c=dy->second; if(!coOK(c)) continue;
    int a=max(V.a,wa), b=min(V.b,wb); if(a>b) continue; int fo; int g=coloc(I,d,s,a,b,ex,&fo); if(g<0) continue;
    out.push_back({s,c,g,fo}); if((int)out.size()>=maxOut) return; }
}
// ---------------- edits ----------------
struct Ins{ int g; Ev e; };
struct Edit{ vector<int> rem; vector<Ins> ins; vector<pair<int,int>> initCh; int splitReg=-1, splitGap=-1, splitNew=-1, splitInit=-1; vector<int> newO; const char*tag=""; };   // newO: new owned registers (K2FRAMES)
static State applyEdit(const State&S,const Edit&E){
  State T; T.init=S.init; long n=S.P.size();
  vector<Ins> ins=E.ins; stable_sort(ins.begin(),ins.end(),[](const Ins&a,const Ins&b){return a.g<b.g;}); vector<int> remS=E.rem; sort(remS.begin(),remS.end());
  long lo=n, hs=0; for(int i:E.rem){ lo=min(lo,(long)i); hs=max(hs,(long)i+1); } for(auto&x:E.ins){ lo=min(lo,(long)x.g); hs=max(hs,(long)x.g); }
  if(E.splitReg>=0){ lo=0; hs=n; }        // renaming touches every later event: element-wise path
  if(lo>hs) lo=hs; if(E.rem.empty()&&E.ins.empty()){ lo=hs=n; }
  T.P.reserve(n+ins.size()); T.P.assign(S.P.begin(),S.P.begin()+lo);
  size_t k=0, ri=0; while(k<ins.size()&&ins[k].g<lo) k++; while(ri<remS.size()&&remS[ri]<lo) ri++;
  for(long i=lo;i<=min(hs,n);i++){ while(k<ins.size()&&ins[k].g==i) T.P.push_back(ins[k++].e);
    if(i<n&&i<hs){ if(ri<remS.size()&&remS[ri]==i){ ri++; while(ri<remS.size()&&remS[ri]==i) ri++; continue; } Ev e=S.P[i];
      if(E.splitReg>=0&&i>=E.splitGap){ if(e.d==E.splitReg) e.d=E.splitNew; if((e.k=='A'||e.k=='C')&&e.s==E.splitReg) e.s=E.splitNew; }
      T.P.push_back(e); } }
  if(hs<n) T.P.insert(T.P.end(),S.P.begin()+hs,S.P.end());
  if(E.splitNew>=0){ ensureReg(E.splitNew); if((int)T.init.size()<=E.splitNew) T.init.resize(E.splitNew+1,-1); T.init[E.splitNew]=E.splitInit; ROLE[E.splitNew]='H'; }
  for(int q:E.newO){ ensureReg(q); if((int)T.init.size()<=q) T.init.resize(q+1,-1); T.init[q]=-1; ROLE[q]='O'; }
  for(auto&p:E.initCh) T.init[p.first]=p.second;
  if(E.splitReg<0){   // change hints: prefix [0,lo) and suffix S[hs..) are untouched
    long nT=T.P.size(); long q=nT-(hs+(long)(nT-n)); if(q<0) q=0; if(nT-q<lo) q=nT-lo; T.p0=lo; T.q=q; }
  return T;
}
// event source for a virtual T = S with removals/insertions applied (no copy); also iterates a materialised event vector (ins = rem = null)
struct TGen{ const vector<Ev>&B; const vector<Ins>*ins; const vector<int>*rem; size_t ii=0, ri=0; long si;
  TGen(const vector<Ev>&b,const vector<Ins>*in,const vector<int>*rm,long start):B(b),ins(in),rem(rm),si(start){ if(rem) while(ri<rem->size()&&(*rem)[ri]<start) ri++; if(ins) while(ii<ins->size()&&(*ins)[ii].g<start) ii++; }
  const Ev* next(){ for(;;){ if(ins&&ii<ins->size()&&(*ins)[ii].g==si) return &(*ins)[ii++].e; if(si>=(long)B.size()) return nullptr;
      if(rem&&ri<rem->size()&&(*rem)[ri]==si){ ri++; si++; continue; } return &B[si++]; } } };
// Tb/ins/rem describe T (see TGen); p0/q = change hints against S; Tinit = T's initial frames
static Res verifyIncV(const State&S,const Index&I,const Res&SR,const vector<Ev>&Tb,const vector<Ins>*ins,const vector<int>*rem,long nT,const vector<int>&Tinit,long p0,long q,const State*Tfull){
  int NR=Tinit.size(); long nS=S.P.size();
  auto fullFallback=[&](int why)->Res{ VI_FULL++; FB[why]++; if(Tfull) return verify(*Tfull); State X; X.P=Tb; X.init=Tinit; if(ins||rem){ Edit E2; for(size_t a=0;a<rem->size();a++) E2.rem.push_back((*rem)[a]); E2.ins=*ins; X=applyEdit(S,E2); } return verify(X); };
  LCV_j=-1; if(!INCV||p0<0) return fullFallback(0);
  if((int)S.init.size()!=NR||I.nr!=NR||I.CKS.empty()||I.n!=nS||Tinit!=S.init) return fullFallback(1);
  if(p0>nS||p0>nT||q<0||q>nS-p0||q>nT-p0||(nS-q-p0)+(nT-q-p0)>BIGREG) return fullFallback(3);
  LCV_j=-1; VI_INC++; long delta=nT-nS; int c0=ckFloor(I,p0); const Ck&K0=I.CKS[c0]; int kc=c0;
  vector<int> cur=K0.cur; vector<char> act=K0.act; vector<V3> val=K0.val; long paid[16]; memcpy(paid,K0.paid,sizeof paid); long scal=K0.scal; int nact=0; for(int r=0;r<NR;r++) nact+=act[r];
  Res R; memset(&R,0,sizeof R); R.ok=false; R.at=-1; bool conv=false; long i=K0.pos; long cS=0;
  TGen g(Tb,ins,rem,i);
  for(;;i++){
    if(i>=nT-q){ long j=i-delta; while(kc<(int)I.CKS.size()&&I.CKS[kc].pos<j) kc++; if(kc<(int)I.CKS.size()&&I.CKS[kc].pos==j){ const Ck&K=I.CKS[kc]; if(cur==K.cur&&act==K.act&&val==K.val){ conv=true; cS=kc; break; } } }
    const Ev*e=g.next(); if(!e) break;
    const char*w=simEvent(*e,NR,cur,act,val,nact,paid,scal); if(w){ R.why=w; R.at=i; VI_SIMEV+=i-K0.pos; return R; }
  }
  VI_SIMEV+=i-K0.pos;
  if(conv){ VI_CONV++; LCV_j=I.CKS[cS].pos; LCV_delta=delta; const Ck&K=I.CKS[cS]; for(int k=0;k<16;k++){ R.paid[k]=SR.paid[k]-K.paid[k]+paid[k]; R.hel[k]=SR.hel[k]; } scal=SR.scalar-K.scal+scal; R.nhel=SR.nhel; }
  else { for(int k=0;k<16;k++) R.paid[k]=paid[k]; State Tt; Tt.init=Tinit; if(!finalChecks(Tt,cur,val,nact,R)) return R; }
  // chain taxes: dim visit counts of the registers whose MOVEs lie in the changed regions
  long dlt=0; vector<double> tax=I.TAX; { map<int,int> dd; for(long a=p0;a<nS-q;a++){ const Ev&e=S.P[a]; if(e.k=='M'&&ROLE[e.d]!='O') dd[e.d*32+SDIM[e.f]]--; if(e.k=='I') dlt--; }
    { TGen g2(Tb,ins,rem,p0); for(long a=p0;a<nT-q;a++){ const Ev*e=g2.next(); if(e->k=='M'&&ROLE[e->d]!='O') dd[e->d*32+SDIM[e->f]]++; if(e->k=='I') dlt++; } }
    int last=-1; for(auto&kv:dd){ int r=kv.first/32; if(r==last) continue; last=r; int m=0; for(int d=0;d<32;d++){ auto f=dd.find(r*32+d); int c=(int)I.CNT[r][d]+(f==dd.end()?0:f->second); if(c>0) m|=1<<d; } tax[r]=taxMask(m); } }
  sumTax(tax,R);
  long pj=0; for(int r=0;r<16;r++) pj+=R.paid[r];
  if(!FREEB&&nT>=CAP){ R.why="event cap"; return R; }
  R.lt=SR.lt+dlt; R.budget=scal+1000*(pj+2*R.nhel+2*104+4*104+4*R.lt);
  if(!FREEB&&R.budget>=10000000){ R.why="scalar budget"; return R; }
  R.nev=nT; R.scalar=scal; R.R0=R.R0x+R.R0y+R.R0h; R.kap=kapOf(R.paid,R.hel); R.obj=COSTR0?-R.R0*1e-7:R.kap; R.ok=true; R.why="ok"; return R;
}
static Res verifyInc(const State&T,const State&S,const Index&I,const Res&SR){ return verifyIncV(S,I,SR,T.P,nullptr,nullptr,T.P.size(),T.init,T.p0,T.q,&T); }
// fast path legality: the edit only removes/inserts ADDs, never empties a stop of a public register, so cleanup() is the identity (S is clean)
static bool fastOK(const Index&I,const State&S,const Edit&E){
  if(!E.initCh.empty()||E.splitReg>=0) return false;
  for(auto&x:E.ins) if(x.e.k!='A') return false;
  vector<array<int,3>> rm;   // (reg, stop, removed)
  for(int i:E.rem){ const Ev&e=S.P[i]; if(e.k!='A') return false;
    for(int t=0;t<2;t++){ int r=t?e.s:e.d; if(ROLE[r]=='O') return false; int j=stopAt(I,r,i); if(j<0) return false; bool f=false; for(auto&x:rm) if(x[0]==r&&x[1]==j){ x[2]++; f=true; break; } if(!f) rm.push_back({r,j,1}); } }
  for(auto&x:rm){ const Stop&st=I.ST[x[0]][x[1]]; const auto&T=I.TOUCH[x[0]]; long c=lower_bound(T.begin(),T.end(),st.b)-lower_bound(T.begin(),T.end(),st.a); if(c-x[2]<=0) return false; }
  return true; }
static V3 scaleV(const V3&v,Co c){ u64 q=coMod(c); V3 o; for(int k=0;k<KV;k++) o[k]=mmul(v[k],q); return o; }
static V3 subV(const V3&a,const V3&b){ V3 o; for(int k=0;k<KV;k++) o[k]=msub(a[k],b[k]); return o; }
static V3 addV(const V3&a,const V3&b){ V3 o; for(int k=0;k<KV;k++) o[k]=madd(a[k],b[k]); return o; }
static const Co CSET[]={{1,0},{-1,0},{1,1},{-1,1},{1,-1},{-1,-1},{1,2},{-1,2},{1,-2},{-1,-2}};
static int PEELK=0, PEELV=3; static double NEUTP=1.0; static double EVPEN=0; static long EVT=0;   // peel delivery: max constituent terms (0 = off), version radius
static Co coMul(Co a,Co b){ return coNorm(a.n*b.n,a.e+b.e); }
// PEEL: read s at ANOTHER version k (co-located with d in the window) and correct by the writes into s between the two versions (each delivered from any holder), or by their sum
static bool planPeel(const Index&I,const State&S,long i,const vector<Excl>&ex,vector<Ins>&out,int*nterms){
  if(PEELK<=0) return false; const Ev&e=S.P[i]; int d=e.d,s=e.s; int vs=verAt(I,s,i); if(vs<0) return false; int wa,wb; dWin(I,d,i,wa,wb);
  vector<int> ks; for(int k=max(0,vs-PEELV);k<=min((int)I.VR[s].size()-1,vs+PEELV);k++) if(k!=vs) ks.push_back(k);
  for(size_t q=0;q<ks.size();q++) swap(ks[q],ks[q+rnd(ks.size()-q)]);
  V3 t=scaleV(I.VR[s][vs].v,e.c);
  for(int k:ks){ const Ver&V=I.VR[s][k]; if(vzero(V.v)) continue; int a=max(V.a,wa), b=min(V.b,wb); if(a>b) continue; int fo; int g=coloc(I,d,s,a,b,ex,&fo); if(g<0) continue;
    V3 res=subV(t,scaleV(V.v,e.c)); vector<Ins> tmp; tmp.push_back({g,{'A',d,s,fo,e.c}});
    if(vzero(res)){ out.insert(out.end(),tmp.begin(),tmp.end()); *nterms=1; return true; }
    { vector<Cand> c; findSources(I,res,d,wa,wb,ex,c,8); if(!c.empty()){ auto&x=c[rnd(c.size())]; if(x.s!=s){ tmp.push_back({x.g,{'A',d,x.s,x.f,x.c}}); out.insert(out.end(),tmp.begin(),tmp.end()); *nterms=2; return true; } } }
    int lo=min(k,vs), hi=max(k,vs); if(hi-lo>PEELK) continue; bool okc=true; int sg=(k<vs)?1:-1;
    for(int m=lo+1;m<=hi&&okc;m++){ int w=I.VR[s][m].a-1; const Ev&x=S.P[w]; if(x.k!='A'||x.d!=s){ okc=false; break; }
      int vx=verAt(I,x.s,w); if(vx<0){ okc=false; break; } Co cc=coMul(e.c,x.c); cc.n*=sg; V3 tv=scaleV(I.VR[x.s][vx].v,cc);
      vector<Cand> c; findSources(I,tv,d,wa,wb,ex,c,8); if(c.empty()){ okc=false; break; } auto&y=c[rnd(c.size())]; tmp.push_back({y.g,{'A',d,y.s,y.f,y.c}}); }
    if(okc){ out.insert(out.end(),tmp.begin(),tmp.end()); *nterms=tmp.size(); return true; } }
  return false; }
// replacement plan for ADD i: deliver target into d inside its write window, avoiding exclusions.  single source first, then two-term (cancellation) if allowed
static bool planDeliver(const Index&I,const State&S,long i,const vector<Excl>&ex,bool allowSame,int maxTwo,vector<Ins>&out,int*nterms){
  const Ev&e=S.P[i]; int d=e.d,s=e.s; int vs=verAt(I,s,i); if(vs<0) return false; V3 t=scaleV(I.VR[s][vs].v,e.c);
  int wa,wb; dWin(I,d,i,wa,wb);
  vector<Cand> c1; findSources(I,t,d,wa,wb,ex,c1,24,allowSame?-1:s,allowSame?-1:vs);
  if(!c1.empty()){ auto&c=c1[rnd(c1.size())]; out.push_back({c.g,{'A',d,c.s,c.f,c.c}}); *nterms=1; return true; }
  if(maxTwo<=0) return planPeel(I,S,i,ex,out,nterms);
  // two-term: enumerate co-located registers of d inside the window
  vector<array<int,4>> pool; // (s1, ver, a, b)
  for(int si=max(0,stopAt(I,d,wa));si<(int)I.ST[d].size();si++){ const Stop&st=I.ST[d][si]; if(st.a>wb) break; int A=max(st.a,wa),B=min(st.b,wb); if(A>B) continue;
    for(auto&o:I.OCC[st.f]){ int r=o[0]; if(r==d) continue; int a=max(A,o[1]),b=min(B,o[2]); if(a>b) continue;
      bool bad=false; for(auto&x:ex) if((x.r==r||x.r==d)&&x.x<=a&&b<=x.y) bad=true; if(bad) continue;
      int v0=verAt(I,r,a); for(int v=v0;v>=0&&v<(int)I.VR[r].size()&&I.VR[r][v].a<=b;v++){ if(vzero(I.VR[r][v].v)) continue; pool.push_back({r,v,max(a,I.VR[r][v].a),min(b,I.VR[r][v].b)}); } } }
  for(int tries=0;tries<maxTwo&&!pool.empty();tries++){ auto&p=pool[rnd(pool.size())]; Co c=CSET[rnd(10)];
    V3 rest=subV(t,scaleV(I.VR[p[0]][p[1]].v,c)); if(vzero(rest)) continue;
    int fo; int g1=coloc(I,d,p[0],p[2],p[3],ex,&fo); if(g1<0) continue; int f1=fo;
    vector<Cand> c2; findSources(I,rest,d,wa,wb,ex,c2,8); if(c2.empty()) continue; auto&q=c2[rnd(c2.size())];
    if(q.s==p[0]) continue;
    out.push_back({g1,{'A',d,p[0],f1,c}}); out.push_back({q.g,{'A',d,q.s,q.f,q.c}}); *nterms=2; return true; }
  return planPeel(I,S,i,ex,out,nterms);
}
static vector<char> FOC; static double FOCP=0;   // K2PUSH focus: registers whose events/stops are proposed with prob FOCP
static bool foc(int r){ return r>=0&&r<(int)FOC.size()&&FOC[r]; }
static int focusPick(const State&S,char k){ vector<int> c; for(long i=0;i<(long)S.P.size();i++){ const auto&e=S.P[i]; if(e.k!=k) continue; if(foc(e.d)||(k=='A'&&foc(e.s))) c.push_back(i); } return c.empty()?-1:c[rnd(c.size())]; }
static int focusReg(){ vector<int> c; for(int r=0;r<(int)FOC.size();r++) if(FOC[r]) c.push_back(r); return c.empty()?-1:c[rnd(c.size())]; }
static int randADD(const State&S){ if(FOCP>0&&urand()<FOCP){ int i=focusPick(S,'A'); if(i>=0) return i; } for(int t=0;t<64;t++){ long i=rnd(S.P.size()); if(S.P[i].k=='A') return i; } return -1; }
static bool fixedStop(int r,int j,int nst){ char ro=ROLE[r]; if(ro=='X'||ro=='Y') return j==0||j==nst-1; return false; }
// ---- move generators ----
static bool mvShift(const Index&I,const State&S,Edit&E){ int i=randADD(S); if(i<0) return false; const Ev&e=S.P[i]; int wa,wb; dWin(I,e.d,i,wa,wb);
  int vs=verAt(I,e.s,i); int a=max(wa,I.VR[e.s][vs].a), b=min(wb,I.VR[e.s][vs].b); int fo; int g=coloc(I,e.d,e.s,a,b,{},&fo, urand()<0.7?e.f:-1); if(g<0||g==i||g==i+1) return false;
  E.rem={i}; E.ins={{g,{'A',e.d,e.s,fo,e.c}}}; E.tag="shift"; return true; }
static bool mvMShift(const Index&I,const State&S,Edit&E){ long i; if(FOCP>0&&urand()<FOCP){ i=focusPick(S,'M'); if(i<0) return false; } else for(int t=0;;t++){ if(t>64) return false; i=rnd(S.P.size()); if(S.P[i].k=='M') break; }
  int r=S.P[i].d; int g=i+(rnd(2)?1:-1)*(1+rnd(40)); if(g<0||g>(long)S.P.size()) return false;
  long lo=min((long)g,i),hi=max((long)g,i); for(long j=lo;j<hi;j++) if(j!=i&&S.P[j].k=='M'&&S.P[j].d==r) return false;
  E.rem={(int)i}; E.ins={{g,S.P[i]}}; E.tag="mshift"; return true; }
static bool mvRet(const Index&I,const State&S,Edit&E){ int i=randADD(S); if(i<0) return false; vector<Ins> o; int nt;
  if(!planDeliver(I,S,i,{},false,0,o,&nt)) return false; E.rem={i}; E.ins=o; E.tag="ret"; return true; }
static bool mvCadd(const Index&I,const State&S,Edit&E){ int i=randADD(S); if(i<0) return false; vector<Ins> o; int nt;
  const Ev&e=S.P[i]; int vs=verAt(I,e.s,i); V3 t=scaleV(I.VR[e.s][vs].v,e.c); int wa,wb; dWin(I,e.d,i,wa,wb);
  // force a two-term plan
  vector<array<int,4>> pool; for(int si=max(0,stopAt(I,e.d,wa));si<(int)I.ST[e.d].size();si++){ const Stop&st=I.ST[e.d][si]; if(st.a>wb) break; int A=max(st.a,wa),B=min(st.b,wb); if(A>B) continue;
    for(auto&oc:I.OCC[st.f]){ int r=oc[0]; if(r==e.d) continue; int a=max(A,oc[1]),b=min(B,oc[2]); if(a>b) continue; int v=verAt(I,r,a); if(v<0||vzero(I.VR[r][v].v)) continue; pool.push_back({r,v,a,min(b,I.VR[r][v].b)}); } }
  for(int tries=0;tries<16&&!pool.empty();tries++){ auto&p=pool[rnd(pool.size())]; Co c=CSET[rnd(10)]; V3 rest=subV(t,scaleV(I.VR[p[0]][p[1]].v,c)); if(vzero(rest)) continue;
    vector<Cand> c2; findSources(I,rest,e.d,wa,wb,{},c2,8); if(c2.empty()) continue; auto&q=c2[rnd(c2.size())]; if(q.s==p[0]) continue;
    int fo; int g1=coloc(I,e.d,p[0],p[2],p[3],{},&fo); if(g1<0) continue;
    E.rem={i}; E.ins={{g1,{'A',e.d,p[0],fo,c}},{q.g,{'A',e.d,q.s,q.f,q.c}}}; E.tag="cadd"; return true; }
  return false; }
static bool mvCdel(const Index&I,const State&S,Edit&E){ int i=randADD(S); if(i<0) return false; const Ev&e=S.P[i]; int wa,wb; dWin(I,e.d,i,wa,wb);
  const auto&W=I.WR[e.d]; vector<int> js; for(auto it=lower_bound(W.begin(),W.end(),wa);it!=W.end()&&*it<wb;++it) if(*it!=i&&S.P[*it].k=='A') js.push_back(*it); if(js.empty()) return false;
  int j=js[rnd(js.size())]; const Ev&f=S.P[j]; V3 t=addV(scaleV(I.VR[e.s][verAt(I,e.s,i)].v,e.c),scaleV(I.VR[f.s][verAt(I,f.s,j)].v,f.c));
  if(vzero(t)){ E.rem={i,j}; E.tag="cdel0"; return true; }
  vector<Cand> c; findSources(I,t,e.d,wa,wb,{},c,8); if(c.empty()) return false; auto&q=c[rnd(c.size())]; E.rem={i,j}; E.ins={{q.g,{'A',e.d,q.s,q.f,q.c}}}; E.tag="cdel"; return true; }
// K2PUSH hop-delivery (kill fallback): deliver ADD i's content into d beyond ONE adjacent reader of d, compensating that reader
static int HOPKILL=0;
static bool hopDeliver(const Index&I,const State&S,long i,const vector<Excl>&ex,vector<Ins>&out){
  const Ev&e=S.P[i]; int d=e.d,s=e.s; if(ROLE[d]=='O') return false; int vs=verAt(I,s,i); if(vs<0) return false; V3 t=scaleV(I.VR[s][vs].v,e.c);
  int wa,wb; dWin(I,d,i,wa,wb);
  for(int side=0;side<2;side++){ bool fwd=(side==0)^(rnd(2)==1); int j=fwd?wb:wa-1; if(j<0||j>=(long)S.P.size()) continue; const Ev&x=S.P[j]; if(x.k!='A'||x.s!=d) continue; int r2=x.d; if(r2==d) continue;
    int a2,b2; if(fwd){ dWin(I,d,j+1,a2,b2); a2=j+1; } else { int p,q; dWin(I,d,j,p,q); a2=p; b2=j; }
    vector<Cand> c; findSources(I,t,d,a2,b2,ex,c,16); vector<Cand> ok; for(auto&q:c) if(q.s!=d&&q.s!=r2) ok.push_back(q); if(ok.empty()) continue; auto q=ok[rnd(ok.size())];
    Co cc=coMul(x.c,e.c); if(!fwd) cc.n=-cc.n; if(!coOK(cc)) continue; V3 t2=scaleV(I.VR[s][vs].v,cc);
    int ra,rb; dWin(I,r2,j,ra,rb); vector<Cand> c2; findSources(I,t2,r2,ra,rb,ex,c2,16); vector<Cand> ok2; for(auto&z:c2) if(z.s!=d&&z.s!=r2) ok2.push_back(z); if(ok2.empty()) continue; auto z=ok2[rnd(ok2.size())];
    out.push_back({q.g,{'A',d,q.s,q.f,q.c}}); out.push_back({z.g,{'A',r2,z.s,z.f,z.c}}); return true; }
  return false; }
// K2PUSH multi-hop delivery: deliver ADD i's content into d after crossing up to HOPK readers of d (forward only), compensating each reader from any holder in its window
static int HOPK=0, HDBG=0;
// recursive content delivery: put t into d inside [wa,wb] from any holder; else cross up to XR readers of d forward (window ends at wb), each reader compensated recursively (depth-1)
static int XR=4;
static bool deliverRec(const Index&I,const State&S,int d,const V3&t,int wa,int wb,const vector<Excl>&ex,int depth,vector<Ins>&out,int skipA=-1){
  { vector<Cand> c; findSources(I,t,d,wa,wb,ex,c,16); vector<Cand> ok; for(auto&q:c) if(q.s!=skipA) ok.push_back(q); if(!ok.empty()){ auto q=ok[rnd(ok.size())]; out.push_back({q.g,{'A',d,q.s,q.f,q.c}}); return true; } }
  if(depth<=0||ROLE[d]=='O') return false; int j=wb; vector<Ins> comp;
  for(int k=0;k<XR;k++){ if(j<0||j>=(long)S.P.size()) return false; const Ev&x=S.P[j]; if(x.k!='A'||x.s!=d||x.d==d) return false; int r2=x.d;
    u64 q=coMod(x.c); V3 t2; for(int m=0;m<KV;m++) t2[m]=mmul(t[m],q); int ra,rb; dWin(I,r2,j,ra,rb);
    if(!deliverRec(I,S,r2,t2,ra,rb,ex,depth-1,comp,d)) return false;
    int a2,b2; dWin(I,d,j+1,a2,b2); a2=j+1;
    vector<Cand> c; findSources(I,t,d,a2,b2,ex,c,16); vector<Cand> ok; for(auto&z:c) if(z.s!=skipA) ok.push_back(z);
    if(!ok.empty()){ auto z=ok[rnd(ok.size())]; out.push_back({z.g,{'A',d,z.s,z.f,z.c}}); out.insert(out.end(),comp.begin(),comp.end()); return true; }
    j=b2; }
  return false; }
static bool hopDeliverK(const Index&I,const State&S,long i,const vector<Excl>&ex,vector<Ins>&out){
  if(getenv("K2S_REC")){ const Ev&e=S.P[i]; int vs=verAt(I,e.s,i); if(vs<0) return false; V3 t=scaleV(I.VR[e.s][vs].v,e.c); int wa,wb; dWin(I,e.d,i,wa,wb); vector<Ins> o; if(deliverRec(I,S,e.d,t,wa,wb,ex,HOPK,o)){ out.insert(out.end(),o.begin(),o.end()); return true; } return false; }
  const Ev&e=S.P[i]; int d=e.d,s=e.s; if(ROLE[d]=='O') return false; int vs=verAt(I,s,i); if(vs<0) return false; V3 t=scaleV(I.VR[s][vs].v,e.c);
  int wa,wb; dWin(I,d,i,wa,wb); int j=wb; vector<Ins> comp; int kmax=1+rnd(HOPK);
  for(int k=0;k<kmax;k++){ if(j<0||j>=(long)S.P.size()) return false; const Ev&x=S.P[j]; if(x.k!='A'||x.s!=d||x.d==d) return false; int r2=x.d;
    Co cc=coMul(x.c,e.c); if(!coOK(cc)) return false; V3 t2=scaleV(I.VR[s][vs].v,cc);
    int ra,rb; dWin(I,r2,j,ra,rb); vector<Cand> c2; findSources(I,t2,r2,ra,rb,ex,c2,16); vector<Cand> ok2; for(auto&z:c2) if(z.s!=d&&z.s!=r2) ok2.push_back(z); if(ok2.empty()){ if(HDBG) printf("  hopK i=%ld k=%d reader %d at %d [%d,%d]: no comp source (cands %zu)\n",i,k,r2,j,ra,rb,c2.size()); return false; } auto z=ok2[rnd(ok2.size())];
    comp.push_back({z.g,{'A',r2,z.s,z.f,z.c}}); if(HDBG) printf("  hopK i=%ld k=%d reader %d at %d comp from %d\n",i,k,r2,j,z.s);
    int a2,b2; dWin(I,d,j+1,a2,b2); a2=j+1;
    vector<Cand> c; findSources(I,t,d,a2,b2,ex,c,16); vector<Cand> ok; for(auto&q:c) if(q.s!=d) ok.push_back(q);
    if(!ok.empty()&&(k+1>=kmax||rnd(2))){ auto q=ok[rnd(ok.size())]; out.push_back({q.g,{'A',d,q.s,q.f,q.c}}); out.insert(out.end(),comp.begin(),comp.end()); return true; }
    j=b2; }
  return false; }
struct KD{ int nonadd,nev,ok,full; }; static KD KDIAG={0,0,0,0};
// rung kill: evacuate every event of (r, stop j) and let cleanup delete the rung
static bool mvKill(const Index&I,const State&S,Edit&E,int r=-1,int j=-1,int maxTwo=12){
  if(r<0){ if(FOCP>0&&urand()<FOCP){ r=focusReg(); if(r<0||ROLE[r]=='O'||I.ST[r].size()<2) return false; } else for(int t=0;;t++){ if(t>64) return false; r=rnd(S.init.size()); if(ROLE[r]!='O'&&I.ST[r].size()>1) break; } j=rnd(I.ST[r].size()); }
  const Stop&st=I.ST[r][j]; if(fixedStop(r,j,I.ST[r].size())) return false;
  vector<Excl> ex={{r,st.a,st.b}}; vector<int> evs; KDIAG.nonadd=0; KDIAG.nev=0; KDIAG.ok=0;
  for(int i:I.TOUCH[r]){ if(i<st.a) continue; if(i>st.b) break; if(S.P[i].k!='A'){ KDIAG.nonadd++; continue; } evs.push_back(i); }
  KDIAG.nev=evs.size(); if(KDIAG.nonadd) return false; if(evs.empty()) return false; if(evs.size()>64) return false;
  vector<Ins> all; bool okall=true; for(int i:evs){ int nt; if(!planDeliver(I,S,i,ex,true,maxTwo,all,&nt)&&!(HOPKILL&&hopDeliver(I,S,i,ex,all))&&!(HOPK&&hopDeliverK(I,S,i,ex,all))){ okall=false; if(!KDIAG.full) return false; } else KDIAG.ok++; }
  if(!okall) return false;
  E.rem=evs; E.ins=all; E.tag="kill"; return true; }
// rung re-host: kill (r, stop j); deliverable events go elsewhere, the rest (and the stop's SCALEs) move with the rung onto a NEW frame G of r (prev < G < next), where their partners are
static int RH_U=0, RH_G=0, RH_WANT=-1;
static bool mvRehost(const Index&I,const State&S,Edit&E,int r=-1,int j=-1,int maxU=3,int maxTwo=8){
  if(r<0){ if(FOCP>0&&urand()<FOCP){ r=focusReg(); if(r<0||ROLE[r]=='O'||I.ST[r].size()<2) return false; } else for(int t=0;;t++){ if(t>64) return false; r=rnd(S.init.size()); if(ROLE[r]!='O'&&I.ST[r].size()>1) break; } j=rnd(I.ST[r].size()); }
  if(ROLE[r]=='O') return false; const auto&STr=I.ST[r]; int ns=STr.size(); if(fixedStop(r,j,ns)) return false;
  if((j==0||j==ns-1)&&ROLE[r]!='H') return false;
  const Stop&st=STr[j]; int Fprev=j>0?STr[j-1].f:-1, Fnext=j+1<ns?STr[j+1].f:-1;
  vector<int> evs,sc; int lo=0;
  for(int i:I.TOUCH[r]){ if(i<st.a){ lo=i+1; continue; } if(i>st.b) break; char k=S.P[i].k; if(k=='A') evs.push_back(i); else if(k=='S') sc.push_back(i); else return false; }
  if(evs.empty()) return false;
  vector<Excl> ex={{r,st.a,st.b}}; vector<int> U,D; 
  for(int i:evs){ vector<Ins> tmp; int nt; if(planDeliver(I,S,i,ex,true,maxTwo,tmp,&nt)||(HOPKILL&&hopDeliver(I,S,i,ex,tmp))||(HOPK&&hopDeliverK(I,S,i,ex,tmp))) D.push_back(i); else U.push_back(i); }
  RH_U=U.size(); if((int)U.size()>maxU) return false;
  vector<int> hosted=U; if(hosted.empty()){ if(sc.empty()&&rnd(2)) return false; hosted.push_back(evs[rnd(evs.size())]); }  // pure rung move: carry one event
  auto okG=[&](int G){ if(G==st.f) return false; if(Fprev>=0&&!psub(Fprev,G)) return false; if(Fnext>=0&&!psub(G,Fnext)) return false; if(Fprev<0&&Fnext<0) return false; return true; };
  // candidate frames from the first hosted event's partner, then check the others
  map<int,vector<pair<int,int>>> cand;  // G -> per hosted event gap range
  for(size_t h=0;h<hosted.size();h++){ int i=hosted[h]; const Ev&e=S.P[i]; int p=(e.d==r)?e.s:e.d; if(ROLE[p]=='O') return false;
    int wa,wb; dWin(I,e.d,i,wa,wb); int vs=verAt(I,e.s,i); int a=max(max(wa,I.VR[e.s][vs].a),lo), b=min(min(wb,I.VR[e.s][vs].b),st.b); if(a>b) return false;
    map<int,pair<int,int>> here; for(int k=max(0,stopAt(I,p,a));k<(int)I.ST[p].size();k++){ const Stop&q=I.ST[p][k]; if(q.a>b) break; int A=max(a,q.a),B=min(b,q.b); if(A>B) continue; if(!okG(q.f)) continue; here[q.f]={A,B}; }
    if(h==0){ for(auto&x:here) cand[x.first]={x.second}; }
    else { for(auto it=cand.begin();it!=cand.end();){ auto f=here.find(it->first); if(f==here.end()) it=cand.erase(it); else { it->second.push_back(f->second); ++it; } } }
    if(cand.empty()) return false; }
  auto it=cand.begin(); if(RH_WANT>=0){ it=cand.find(RH_WANT); if(it==cand.end()) return false; } else advance(it,rnd(cand.size())); int G=it->first; RH_G=G;
  vector<int> gaps; int g0=INT32_MAX; for(auto&rg:it->second){ int g=rg.first+rnd(rg.second-rg.first+1); gaps.push_back(g); g0=min(g0,g); } for(int i:sc) g0=min(g0,i);
  if(g0<lo) return false;
  E.rem.clear(); E.ins.clear();
  if(j>0){ int mi=st.a-1; if(mi<0||S.P[mi].k!='M'||S.P[mi].d!=r) return false; E.rem.push_back(mi); E.ins.push_back({g0,{'M',r,0,G,{0,0}}}); }
  else E.initCh.push_back({r,G});
  vector<char> isHost(S.P.size()+1,0); for(int i:hosted) isHost[i]=1;
  vector<Excl> ex2={{r,min(g0,st.a),st.b}};
  for(size_t h=0;h<hosted.size();h++){ int i=hosted[h]; const Ev&e=S.P[i]; E.rem.push_back(i); E.ins.push_back({gaps[h],{'A',e.d,e.s,G,e.c}}); }
  for(int i:sc){ Ev e=S.P[i]; e.f=G; E.rem.push_back(i); E.ins.push_back({i,e}); }
  for(int i:evs){ if(isHost[i]) continue; vector<Ins> tmp; int nt; if(!planDeliver(I,S,i,ex2,true,maxTwo,tmp,&nt)&&!(HOPKILL&&hopDeliver(I,S,i,ex2,tmp))&&!(HOPK&&hopDeliverK(I,S,i,ex2,tmp))) return false; E.rem.push_back(i); for(auto&x:tmp) E.ins.push_back(x); }
  E.tag="rehost"; return true; }
// rung insert + pull: event i moves onto a new stop of r at its partner's frame G (strictly between r's neighbouring stops)
static bool mvIns(const Index&I,const State&S,Edit&E){ int i=randADD(S); if(i<0) return false; const Ev&e=S.P[i]; int r=rnd(2)?e.d:e.s, p=(r==e.d)?e.s:e.d; if(ROLE[r]=='O'||ROLE[p]=='O') return false;
  int wa,wb; dWin(I,e.d,i,wa,wb); int vs=verAt(I,e.s,i); int a=max(wa,I.VR[e.s][vs].a), b=min(wb,I.VR[e.s][vs].b);
  for(int t=0;t<8;t++){ int g=a+rnd(b-a+1); int jr=stopAt(I,r,g), jp=stopAt(I,p,g); if(jr<0||jp<0) continue; int G=I.ST[p][jp].f; const Stop&sr=I.ST[r][jr]; if(G==sr.f) continue;
    bool last=(jr==(int)I.ST[r].size()-1); if(!psub(sr.f,G)) continue; if(!last&&!psub(G,I.ST[r][jr+1].f)) continue; if(last&&ROLE[r]!='H') continue;
    // r must have no events at its stop after gap g (they would land on G)
    bool clash=false; for(int k:I.TOUCH[r]) if(k>=g&&k<=sr.b&&k!=i){ clash=true; break; } if(clash) continue;
    E.rem={i}; E.ins={{g,{'M',r,0,G,{0,0}}},{g,{'A',e.d,e.s,G,e.c}}}; E.tag="ins"; return true; }
  return false; }
// helper split at a restored point (value == e_h): later events go to a fresh helper born at h's frame there
static bool mvSplit(const Index&I,const State&S,Edit&E){ int h; for(int t=0;;t++){ if(t>64) return false; h=rnd(S.init.size()); if(ROLE[h]=='H'&&I.VR[h].size()>2) break; }
  vector<int> cands; for(int k=1;k+1<(int)I.VR[h].size();k++) if(I.VR[h][k].v==V0[h]) cands.push_back(k); if(cands.empty()) return false;
  const Ver&V=I.VR[h][cands[rnd(cands.size())]]; int g=V.a+rnd(V.b-V.a+1); int js=stopAt(I,h,g); if(js<0) return false; int F=I.ST[h][js].f;
  int nr=S.init.size(); E.splitReg=h; E.splitGap=g; E.splitNew=nr; E.splitInit=F; E.tag="split"; return true; }

// K2PUSH hop: move ADD d+=c*s across ONE adjacent reader r+=a*d of d (later or earlier), compensating the reader with r+=(+-a*c)*val(s) from any holder in r's write window
static int HOP=0;
static bool mvHop(const Index&I,const State&S,Edit&E){ int i=randADD(S); if(i<0) return false; const Ev&e=S.P[i]; int d=e.d,s=e.s; if(ROLE[d]=='O') return false;
  int vs=verAt(I,s,i); if(vs<0) return false; const Ver&V=I.VR[s][vs]; int wa,wb; dWin(I,d,i,wa,wb); bool fwd=rnd(2);
  int j=fwd?wb:wa-1; if(j<0||j>=(long)S.P.size()) return false; const Ev&x=S.P[j]; if(x.k!='A'||x.s!=d) return false; int r=x.d; if(r==s||r==d) return false;
  // new window of d beyond j
  int a2,b2; if(fwd){ dWin(I,d,j+1,a2,b2); a2=j+1; } else { int p,q; dWin(I,d,j,p,q); a2=p; b2=j; }
  int a=max(a2,V.a), b=min(b2,V.b); if(a>b) return false; int fo; int g=coloc(I,d,s,a,b,{},&fo); if(g<0) return false;
  Co cc=coMul(x.c,e.c); if(!fwd) cc.n=-cc.n; if(!coOK(cc)) return false; V3 t=scaleV(V.v,cc);
  int ra,rb; dWin(I,r,j,ra,rb); vector<Cand> c; findSources(I,t,r,ra,rb,{},c,24);
  vector<Cand> ok; for(auto&q:c) if(q.s!=d&&q.s!=r) ok.push_back(q); if(ok.empty()) return false; auto&q=ok[rnd(ok.size())];
  // the source read must not sit between i and g on the wrong side of d's change: sources other than d are unaffected
  E.rem={i}; E.ins={{g,{'A',d,s,fo,e.c}},{q.g,{'A',r,q.s,q.f,q.c}}}; E.tag="hop"; return true; }
static void diagStop(const Index&I,const State&S,int r,int j){
  const Stop&st=I.ST[r][j]; printf("DIAG reg %d role %c stop %d/%zu frame %d dim %d gaps [%d,%d]\n",r,ROLE[r],j,I.ST[r].size(),st.f,SDIM[st.f],st.a,st.b);
  for(int i:I.TOUCH[r]){ if(i<st.a) continue; if(i>st.b) break; const Ev&e=S.P[i]; if(e.k!='A'){ printf("  ev %d kind %c\n",i,e.k); continue; }
    int wa,wb; dWin(I,e.d,i,wa,wb); int vs=verAt(I,e.s,i); const Ver&V=I.VR[e.s][vs];
    printf("  ev %d ADD %d(%c) += %s * %d(%c)  r is %s | d-window [%d,%d] s-version %d/%zu [%d,%d]\n",i,e.d,ROLE[e.d],coStr(e.c).c_str(),e.s,ROLE[e.s],e.d==r?"DEST":"SRC",wa,wb,vs,I.VR[e.s].size(),V.a,V.b);
    int other=e.d==r?e.s:e.d; printf("    stops of d %d in window:",e.d); for(auto&x:I.ST[e.d]) if(x.b>=wa&&x.a<=wb) printf(" f%d(d%d)[%d,%d]",x.f,SDIM[x.f],x.a,x.b); printf("\n");
    printf("    stops of s %d in window:",e.s); for(auto&x:I.ST[e.s]) if(x.b>=wa&&x.a<=wb) printf(" f%d(d%d)[%d,%d]",x.f,SDIM[x.f],x.a,x.b); printf("\n");
    u64 hk=mmul(scaleV(V.v,e.c)[1],minv(scaleV(V.v,e.c)[0])); int nh=0; for(int hp=I.HS.first(hk);hp>=0;hp=I.HS.next(hp)) nh++; printf("    holders of the content (any time): %d\n",nh);
    for(int hp=I.HS.first(hk);hp>=0;hp=I.HS.next(hp)){ auto rv=I.HS.val[hp]; const Ver&W=I.VR[rv.first][rv.second]; printf("      reg %d(%c) ver [%d,%d]\n",rv.first,ROLE[rv.first],W.a,W.b); }
    (void)other; }
}
// ---------------- net dump ----------------
static int SNFI=-1;   // frame count of the input net (frames >= SNFI were created by the search; unused ones are not written)
static void dumpNet(const State&S,const char*path,const Res&R){
  int NR=S.init.size(); int nf0=SNFI<0?SNF:SNFI; vector<int> fm(SNF,-1); for(int i=0;i<nf0;i++) fm[i]=i;
  if(nf0<SNF){ vector<char> used(SNF,0); for(int r=0;r<NR;r++) if(ROLE[r]!='O'&&S.init[r]>=0) used[S.init[r]]=1; for(auto&e:S.P) used[e.f]=1; int k=nf0; for(int i=nf0;i<SNF;i++) if(used[i]) fm[i]=k++; }
  int nfo=0; for(int i=0;i<SNF;i++) if(fm[i]>=0) nfo++;
  FILE*f=fopen(path,"w"); fprintf(f,"NET %d %d %d %zu\n",SN0,SNO,nfo,S.P.size());
  fprintf(f,"#K2S kappa %.15f R0 %.6f X %.6f Y %.6f H %.6f nev %ld nhel %ld regs %d\n",R.kap,R.R0,R.R0x,R.R0y,R.R0h,R.nev,R.nhel,NR);
  for(int i=0;i<SNF;i++){ if(fm[i]<0) continue; fprintf(f,"F %d %d",fm[i],SDIM[i]); for(int v:SBAS[i]) fprintf(f," %d",v); fprintf(f,"\n"); }
  for(int r=0;r<NR;r++) fprintf(f,"R %d %c %d\n",r,ROLE[r],ROLE[r]=='O'?-1:fm[S.init[r]]);
  for(auto&e:S.P){ int ff=fm[e.f]; switch(e.k){ case 'M': fprintf(f,"M %d %d\n",e.d,ff); break; case 'A': case 'C': fprintf(f,"%c %d %d %s %d\n",e.k,e.d,e.s,coStr(e.c).c_str(),ff); break;
    case 'S': fprintf(f,"S %d %s %d\n",e.d,coStr(e.c).c_str(),ff); break; case 'I': fprintf(f,"I %d %d\n",e.d,ff); break; case 'X': fprintf(f,"X %d %d\n",e.d,ff); break; } }
  fclose(f);
}
#include "k2grow.inc"
#include "k2frames.inc"
static int HOPSLOT7=0;
// every net the search writes is re-verified from scratch first: the header always carries the full verifier's kappa/R0
static void dumpBest(const State&B,const char*path,const Res&R){ Res F=verify(B); if(!F.ok||F.kap!=R.kap){ printf("DUMP VERIFY MISMATCH: full ok=%d (%s) kap %.15f vs tracked %.15f\n",F.ok,F.why,F.kap,R.kap); fflush(stdout); abort(); } dumpNet(B,path,F); }
// K2BACKTEST spec "kslide" (#5811 -> #5827 class): rung kill of helper r's middle stop j where the NEXT MOVE of r (into stop j+1) may also slide EARLIER (to just after r's previous stop's last event),
// so that r sits at the next frame already while the evacuated events are re-delivered (single source or two-term: one term at the previous frame, one at the next frame).  The intermediates are illegal
// as single moves (the slide alone breaks the stop's reads; the delivery alone needs r at the next frame first), hence one atomic Edit: rem = stop events + M(j) + M(j+1); ins = M(j+1)@g_s + deliveries.
struct StGuard{ vector<Stop>*p; vector<Stop> saved; StGuard(vector<Stop>&v):p(&v),saved(v){} ~StGuard(){ *p=saved; } };
static int SLIDEK=40;
static bool mvKillSlide(const Index&I,const State&S,Edit&E,int r=-1,int j=-1,int maxTwo=12){
  if(r<0){ for(int t=0;;t++){ if(t>64) return false; r=rnd(S.init.size()); if(ROLE[r]=='H'&&I.ST[r].size()>2) break; } j=1+rnd(I.ST[r].size()-2); }
  const auto&STr=I.ST[r]; int ns=STr.size(); if(ROLE[r]!='H'||j<1||j+1>=ns) return false;
  const Stop st=STr[j], nx=STr[j+1], pv=STr[j-1];
  long mj=st.a-1, mj1=st.b; if(mj<0||mj1>=(long)S.P.size()||S.P[mj].k!='M'||S.P[mj].d!=r||S.P[mj1].k!='M'||S.P[mj1].d!=r) return false;
  vector<int> evs; long prevLast=pv.a-1; for(int i:I.TOUCH[r]){ if(i<st.a){ if(i>prevLast) prevLast=i; continue; } if(i>st.b) break; if(S.P[i].k!='A') return false; evs.push_back(i); }
  if(evs.empty()||evs.size()>64) return false;
  long lo=max(prevLast+1,mj1-SLIDEK); long gs=lo+rnd((int)(mj1-lo+1)); if(gs>mj1) gs=mj1;     // new position of the MOVE into stop j+1 (gap index in S coordinates)
  // temporary Index view: r is at the previous frame until gs, at the next frame from gs; stop j does not exist
  Index&IM=const_cast<Index&>(I); StGuard G(IM.ST[r]); { vector<Stop> v; for(int k=0;k<ns;k++){ if(k==j) continue; Stop x=STr[k]; if(k==j-1) x.b=(int)gs-1; if(k==j+1) x.a=(int)gs; v.push_back(x); } IM.ST[r]=v; }
  vector<Ins> all; vector<Excl> ex; for(int i:evs){ int nt; if(!planDeliver(IM,S,i,ex,true,maxTwo,all,&nt)) return false; }
  E.rem=evs; E.rem.push_back((int)mj); E.rem.push_back((int)mj1); E.ins.clear(); E.ins.push_back({(int)gs,{'M',r,0,nx.f,{0,0}}}); for(auto&x:all) E.ins.push_back(x);
  E.tag="kslide"; return true; }
#include "k2levers.inc"   // K2LEVERS: late birth / early end move families (default weight 0)
static bool propose(int type,const Index&I,const State&S,Edit&E){
  frameRollback();   // K2FRAMES: frames created by the previous (rejected) proposal are dropped
  switch(type){ case 0: return mvShift(I,S,E); case 1: return mvMShift(I,S,E); case 2: return mvRet(I,S,E); case 3: return mvCadd(I,S,E); case 4: return mvCdel(I,S,E);
    case 5: return mvKill(I,S,E); case 6: return mvIns(I,S,E); case 7: return HOPSLOT7?mvHop(I,S,E):mvSplit(I,S,E); case 8: return mvRehost(I,S,E);
    case 9: return mvHubSwitch(I,S,E); case 10: return mvRelabel(I,S,E); case 11: return mvLift(I,S,E); case 12: return mvHubPeel(I,S,E); case 13: return mvKillSw(I,S,E); case 14: return mvHop(I,S,E); case 15: return mvKillSlide(I,S,E); case 16: return mvDrel(I,S,E,0); case 17: return mvDrel(I,S,E,1); case 18: return mvLbirth(I,S,E); case 19: return mvEend(I,S,E); } return false; }
static const int NMV=20; static const char*MVN[NMV]={"shift","mshift","ret","cadd","cdel","kill","ins","split","rehost","hubsw","relab","lift","hubpl","killsw","hop","kslide","fnew","own","lbirth","eend"};
#include "k2phi.inc"   // HEURISTICS lane: potentials + shaped acceptance (default OFF)
static int searchMain(const char*path,const char*mode){
  Net N; if(!loadNet(path,N)){ fprintf(stderr,"cannot load %s\n",path); return 1; }
  for(int r=1;r<64;r++) RL[r]=r*log((double)r); RL[0]=0; buildDY();
  if(getenv("K2S_SEED")) RSEED=atoll(getenv("K2S_SEED"))*2654435761ULL+12345; for(int k=0;k<20;k++) rng64();
  if(getenv("K2S_CAP")) CAP=atol(getenv("K2S_CAP")); if(getenv("K2S_FREE")) FREEB=1; if(getenv("K2S_NORESUME")) RESUME=0; if(getenv("K2S_NOINC")) INCV=0; if(getenv("K2S_NOLOCALCL")) LOCALCL=0; if(getenv("K2S_NOHSINC")) HSINC=0; if(getenv("K2S_PERIODIC")) PERIODIC=max(1L,atol(getenv("K2S_PERIODIC"))); if(getenv("K2S_NOFAST")) FASTCL=0; if(getenv("K2S_BIGREG")) BIGREG=atol(getenv("K2S_BIGREG")); if(getenv("K2S_FULLVERIFY")) FULLV=1; if(getenv("K2S_COST")&&!strcmp(getenv("K2S_COST"),"r0")) COSTR0=1; if(getenv("K2S_PEEL")) PEELK=atoi(getenv("K2S_PEEL")); if(getenv("K2S_PEELV")) PEELV=atoi(getenv("K2S_PEELV")); if(getenv("K2S_NEUT")) NEUTP=atof(getenv("K2S_NEUT")); if(getenv("K2S_EVPEN")) EVPEN=atof(getenv("K2S_EVPEN")); if(getenv("K2S_HOP")){ HOP=1; HOPSLOT7=1; MVN[7]="hop7"; } if(getenv("K2S_HOPKILL")) HOPKILL=1; if(getenv("K2S_HOPK")) HOPK=atoi(getenv("K2S_HOPK")); if(getenv("K2S_HDBG")) HDBG=1; if(getenv("K2S_XR")) XR=atoi(getenv("K2S_XR")); if(getenv("K2S_FOCUS")){ FOC.assign(100000,0); const char*q=getenv("K2S_FOCUS"); while(*q){ FOC[atoi(q)]=1; while(*q&&*q!=',') q++; if(*q) q++; } FOCP=getenv("K2S_FOCUSP")?atof(getenv("K2S_FOCUSP")):0.5; } if(getenv("K2S_EVT")) EVT=atol(getenv("K2S_EVT")); if(getenv("K2S_EEDBG")) EEDBG=1; if(getenv("K2S_EEMAXR")) EEMAXR=atoi(getenv("K2S_EEMAXR")); if(getenv("K2S_EEXR")) EEXR=atoi(getenv("K2S_EEXR")); if(getenv("K2S_LVSEED")) sscanf(getenv("K2S_LVSEED"),"%d,%d",&LVH,&LVJ);
  SNF=N.nf; SDIM=N.dim; SSP=N.spn; SBAS=N.basis; SN0=N.n; SNO=N.nown; int NR=N.n+N.nown; for(int r=0;r<(int)N.reg.size();r++) if(N.reg[r].role!='?') NR=max(NR,r+1);
  { u64 sv=RSEED; RSEED=0x243F6A8885A308D3ULL; ROLE.assign(NR,'?'); FIXFIN.assign(NR,-1); V0.resize(NR); for(int r=0;r<NR;r++){ ROLE[r]=N.reg[r].role; V0[r]=randV(); } RSEED=sv; }
  State S; S.init.assign(NR,-1); for(int r=0;r<NR;r++) if(ROLE[r]!='O') S.init[r]=N.reg[r].init;
  for(auto&e:N.ev){ Ev x{e.k,e.d,e.s,e.f,{0,0}}; if(e.k=='X') x.k='X'; if(e.k=='A'||e.k=='C'||e.k=='S') x.c=coFromD(e.c); S.P.push_back(x); }
  { vector<int> cur(S.init); for(auto&e:S.P) if(e.k=='M') cur[e.d]=e.f; for(int r=0;r<NR;r++) if(ROLE[r]=='X'||ROLE[r]=='Y') FIXFIN[r]=cur[r]; }
  // V0 for registers created later must be reproducible: derive from a separate stream
  SNFI=SNF; framesInit(); PEAKMAX=getenv("K2S_PEAK")?atoi(getenv("K2S_PEAK")):inputPeak(S); if(getenv("K2S_OWNNEW")) OWNNEW=atoi(getenv("K2S_OWNNEW")); if(getenv("K2S_PREL")) PREL=atof(getenv("K2S_PREL"));
  Res R=verify(S); printf("INPUT ok=%d why=%s at=%ld kappa %.13f R0 %.4f (X %.4f Y %.4f H %.4f) nev %ld helpers %ld scalar %ld lifetimes %ld budget %ld\n",R.ok,R.why,R.at,R.kap,R.R0,R.R0x,R.R0y,R.R0h,R.nev,R.nhel,R.scalar,R.lt,R.budget);
  if(!R.ok){ return 2; }
  { State C=S; cleanup(C); Res Rc=verify(C); printf("CLEANUP of input: events %zu -> %zu  kappa %.13f R0 %.4f ok=%d why=%s at=%ld\n",S.P.size(),C.P.size(),Rc.kap,Rc.R0,Rc.ok,Rc.why,Rc.at);
    if(getenv("K2S_DBG")) for(size_t i=0,j=0;i<S.P.size();i++){ if(j<C.P.size()&&C.P[j].k==S.P[i].k&&C.P[j].d==S.P[i].d&&C.P[j].f==S.P[i].f){ j++; continue; } printf("  cleanup dropped %zu %c d=%d f=%d role %c\n",i,S.P[i].k,S.P[i].d,S.P[i].f,ROLE[S.P[i].d]); } }
  const char*out=getenv("K2S_OUT"); long iters=getenv("K2S_ITERS")?atol(getenv("K2S_ITERS")):10000;
  double W[32]={1,1,1,0.5,0.5,2,0.5,0.2,2,0,0,0,0,0,0,0,0,0}; if(getenv("K2S_W")){ const char*q=getenv("K2S_W"); for(int k=0;k<NMV&&*q;k++){ W[k]=atof(q); while(*q&&*q!=',') q++; if(*q) q++; } }
  double Wt=0; for(int k=0;k<NMV;k++) Wt+=W[k];
  Index I; buildIndex(S,I);
  if(getenv("K2S_GROW")) growCensus(I,S,R);
  if(getenv("K2S_DIAG")){ int r,j; sscanf(getenv("K2S_DIAG"),"%d,%d",&r,&j); diagStop(I,S,r,j); return 0; }
  if(!strcmp(mode,"census")){
    // (a) rung-kill census over every non-fixed stop; (b) per-event neutral move counts for shift/ret/cadd/cdel (random samples)
    long tried=0,planned=0,legal=0,impr=0,neut=0,rhLegal=0,rhImp=0,rhNeu=0,rhWor=0; map<string,long> rhWhy; double best=R.kap; map<string,long> why; FILE*lg=getenv("K2S_LOG")?fopen(getenv("K2S_LOG"),"w"):nullptr;
    int tries=getenv("K2S_KTRIES")?atoi(getenv("K2S_KTRIES")):3;
    for(int r=0;r<NR;r++) for(int j=0;j<(int)I.ST[r].size();j++){ if(fixedStop(r,j,I.ST[r].size())) continue; if(ROLE[r]=='O'&&I.ST[r].size()<=1) continue; tried++;
      bool pl=false,lgl=false; double bk=-1; const char*w0="noplan";
      for(int t=0;t<tries;t++){ Edit E; if(!mvKill(I,S,E,r,j,24)) continue; pl=true; State T=applyEdit(S,E); cleanup(T); Res Q=verify(T); if(!Q.ok){ w0=Q.why; continue; } lgl=true; if(Q.kap>bk) bk=Q.kap;
        if(Q.kap>R.kap+1e-13&&Q.kap>best){ best=Q.kap; if(out){ dumpNet(T,out,Q); } } }
      if(pl) planned++; if(lgl){ legal++; if(bk>R.kap+1e-13) impr++; else if(fabs(bk-R.kap)<=1e-13) neut++; } else why[pl?w0:"noplan"]++;
      { Edit E2; KDIAG.full=1; mvKill(I,S,E2,r,j,24); KDIAG.full=0; }
      { double rb=-1,r0b=0; int rl=0; for(int t=0;t<tries*3;t++){ Edit E3; if(!mvRehost(I,S,E3,r,j,3,12)) continue; State T=applyEdit(S,E3); cleanup(T); Res Q=verify(T); if(!Q.ok){ rhWhy[Q.why]++; continue; } rl++; if(Q.kap>rb){ rb=Q.kap; r0b=Q.R0; }
          if(Q.kap>best+1e-13){ best=Q.kap; if(out) dumpNet(T,out,Q); } }
        if(rl){ rhLegal++; if(rb>R.kap+1e-13) rhImp++; else if(rb>=R.kap-1e-13) rhNeu++; else rhWor++; if(lg) fprintf(lg,"REHOST %d %c %d legal %d best dk %.3e dR0 %.4f\n",r,ROLE[r],j,rl,rb-R.kap,r0b-R.R0); } }
      if(lg) fprintf(lg,"%d %c %d dim %d nev %d nonadd %d deliverable %d plan %d legal %d dk %.3e\n",r,ROLE[r],j,SDIM[I.ST[r][j].f],KDIAG.nev,KDIAG.nonadd,KDIAG.ok,pl,lgl,lgl?bk-R.kap:0.0);
    }
    printf("KILL census: stops %ld planned %ld legal %ld improving %ld neutral %ld best kappa %.13f (dk %.3e)\n",tried,planned,legal,impr,neut,best,best-R.kap);
    for(auto&p:why) printf("  reject %s %ld\n",p.first.c_str(),p.second);
    printf("REHOST census: stops with a legal re-host %ld (improving %ld neutral %ld worse %ld) best kappa %.13f |",rhLegal,rhImp,rhNeu,rhWor,best); for(auto&p:rhWhy) printf(" %s:%ld",p.first.c_str(),p.second); printf("\n");
    long ns=getenv("K2S_SAMPLES")?atol(getenv("K2S_SAMPLES")):20000;
    for(int ty=0;ty<NMV;ty++){ if(ty==5) continue; long pl=0,lg2=0,im=0,ne=0,wo=0; double bb=R.kap; map<string,long> wy;
      for(long it=0;it<ns;it++){ Edit E; if(!propose(ty,I,S,E)) continue; pl++; State T=applyEdit(S,E); cleanup(T); Res Q=verify(T); if(!Q.ok){ wy[Q.why]++; continue; } lg2++;
        if(Q.kap>R.kap+1e-13){ im++; if(Q.kap>bb){ bb=Q.kap; if(out){ string o=string(out)+"."+MVN[ty]; dumpNet(T,o.c_str(),Q);} } } else if(Q.kap>=R.kap-1e-13) ne++; else wo++; }
      printf("MOVE %-6s samples %ld planned %ld legal %ld improving %ld neutral %ld worse %ld best dk %.3e |",MVN[ty],ns,pl,lg2,im,ne,wo,bb-R.kap); for(auto&p:wy) printf(" %s:%ld",p.first.c_str(),p.second); printf("\n"); }
    if(lg) fclose(lg); return 0;
  }
  // K2PUSH target mode: K2S_TLIST file of "r f g" (kill stop of r at frame f if g<0, else rehost it to frame g); K2S_TTRIES attempts each; greedy apply if dk >= K2S_TMIN (1e-7 units)
  if(!strcmp(mode,"target")){ FILE*g=fopen(getenv("K2S_TLIST"),"r"); vector<array<int,3>> L; int a1,b1,c1; while(fscanf(g,"%d %d %d",&a1,&b1,&c1)==3) L.push_back({a1,b1,c1}); fclose(g);
    int tries=getenv("K2S_TTRIES")?atoi(getenv("K2S_TTRIES")):40; double tmin=getenv("K2S_TMIN")?atof(getenv("K2S_TMIN")):1e9; const char*out=getenv("K2S_OUT"); Res cur=R;
    State S0=S; Res R0s=R; Index I0=I; double bestG=-1e18;
    for(int pass=0;pass<(getenv("K2S_TPASS")?atoi(getenv("K2S_TPASS")):1);pass++) for(auto&t:L){ int r=t[0]; int j=-1;
      if(r<0){ double gd=(cur.kap-R0s.kap)*1e7; printf("GROUP dk %.4f kappa %.13f nev %ld\n",gd,cur.kap,cur.nev); if(gd>bestG&&gd>1e-6){ bestG=gd; if(out){ string o=string(out)+".best"; dumpNet(S,o.c_str(),cur);} } S=S0; cur=R0s; I=I0; continue; } for(size_t k=0;k<I.ST[r].size();k++) if(I.ST[r][k].f==t[1]) j=k; if(j<0){ printf("T %d %d %d: no stop\n",r,t[1],t[2]); continue; }
      double bd=-1e18; State bS; Res bR; map<string,long> wy; int nl=0;
      for(int k=0;k<tries;k++){ Edit E; RH_WANT=t[2]; bool okp=t[2]<0?mvKill(I,S,E,r,j):mvRehost(I,S,E,r,j); RH_WANT=-1; if(!okp){ wy["plan"]++; continue; }
        State T=applyEdit(S,E); cleanup(T); Res Q=verify(T); if(!Q.ok){ wy[Q.why]++; continue; } nl++; double d=(Q.kap-cur.kap)*1e7; if(d>bd){ bd=d; bS=T; bR=Q; } }
      printf("T %d %d %d: legal %d/%d best dk %.4f (1e-7)",r,t[1],t[2],nl,tries,nl?bd:0.0); for(auto&p:wy) printf(" %s:%ld",p.first.c_str(),p.second);
      if(nl&&bd>=tmin){ S=bS; cur=bR; buildIndex(S,I); printf("  APPLIED kappa %.13f nev %ld",cur.kap,cur.nev); } printf("\n"); fflush(stdout); }
    printf("FINAL kappa %.13f R0 %.4f nev %ld\n",cur.kap,cur.R0,cur.nev); if(out) dumpNet(S,out,cur); return 0; }
  // walk / sa
  bool walk=!strcmp(mode,"walk"); double T0=getenv("K2S_T0")?atof(getenv("K2S_T0")):1.0, T1=getenv("K2S_T1")?atof(getenv("K2S_T1")):0.01;
  FILE*lg=getenv("K2S_LOG")?fopen(getenv("K2S_LOG"),"w"):nullptr; long acc[32]={0},prop[32]={0},lgl[32]={0},imp[32]={0}; Res cur=R; State best=S; Res bestR=R; long dumpEvery=getenv("K2S_DUMPEVERY")?atol(getenv("K2S_DUMPEVERY")):0;
  double SECS=getenv("K2S_SECS")?atof(getenv("K2S_SECS")):0, tStart=nowS();   // K2S_SECS: wall-clock budget, temperature schedule follows elapsed time (not reproducible); iters then only caps
  long stall=0, lastDump=-1000000; int dirty=0; map<string,long> rej;
  PhiCtx PH; if(getenv("K2S_PHI")||getenv("K2S_FLOG")||getenv("K2S_FSNAP")||getenv("K2S_PHILA")||getenv("K2S_PHISEG")) phiInit(PH,S,cur,I);   // HEURISTICS
  for(long it=0;it<iters;it++){
    double frac=(double)it/max(1L,iters); if(SECS>0){ frac=(nowS()-tStart)/SECS; if(frac>=1) break; }
    if(it%PERIODIC==0&&it>0){ Res F=verify(S); if(!F.ok||F.kap!=cur.kap||F.nev!=cur.nev||F.scalar!=cur.scalar||F.budget!=cur.budget||F.lt!=cur.lt||memcmp(F.paid,cur.paid,sizeof F.paid)||memcmp(F.hel,cur.hel,sizeof F.hel)||fabs(F.R0-cur.R0)>1e-6){ printf("PERIODIC FULL VERIFY MISMATCH at it %ld: full ok=%d (%s) kap %.15f nev %ld | incremental kap %.15f nev %ld\n",it,F.ok,F.why,F.kap,F.nev,cur.kap,cur.nev); fflush(stdout); abort(); } else cur=F; }   // periodic exact re-anchoring
    if(PH.la&&it>=PH.nla&&phiLookahead(PH,it,I,S,cur,best,bestR,lg)) dirty=1;
    if(PH.seg&&it>=PH.nseg) phiSegment(PH,it,I,S,cur);   // HEURISTICS (d) segment tie-break   // HEURISTICS (c) ready-kill look-ahead
    double u=urand()*Wt; int ty=0; while(ty<NMV-1&&u>=W[ty]){ u-=W[ty]; ty++; }
    double tp0=nowS(); Edit E; bool pr=propose(ty,I,S,E); double tp1=nowS(); TPR[0]+=tp1-tp0; if(!pr) continue; prop[ty]++;
    // fast path: the edit only moves ADDs and empties no stop (S clean) => cleanup is the identity: verify the virtual T without materialising it
    State T; Res Q; bool fast=SCLEAN&&FASTCL&&fastOK(I,S,E); double tp2;
    if(fast){ NFAST++; vector<Ins> insS=E.ins; stable_sort(insS.begin(),insS.end(),[](const Ins&a,const Ins&b){return a.g<b.g;}); vector<int> remS=E.rem; sort(remS.begin(),remS.end());
      long n0=S.P.size(), lo=n0, hs=0; for(int i:E.rem){ lo=min(lo,(long)i); hs=max(hs,(long)i+1); } for(auto&x:E.ins){ lo=min(lo,(long)x.g); hs=max(hs,(long)x.g); }
      long nT=n0+(long)E.ins.size()-(long)E.rem.size(); long q=n0-hs; if(lo>hs) lo=hs; if(q<0) q=0; if(nT-q<lo) q=nT-lo;
      tp2=nowS(); TPR[1]+=tp2-tp1; if(!FREEB&&nT>=CAP&&!FULLV){ memset(&Q,0,sizeof Q); Q.ok=false; Q.why="event cap"; } else Q=verifyIncV(S,I,cur,S.P,&insS,&remS,nT,S.init,lo,q,nullptr); TPR[2]+=nowS()-tp2;
      if(FULLV){ T=applyEdit(S,E); State C=T; cleanup(C); bool same=C.P.size()==T.P.size()&&C.init==T.init; for(size_t a=0;same&&a<C.P.size();a++){ const Ev&x=C.P[a],&y=T.P[a]; same=x.k==y.k&&x.d==y.d&&x.f==y.f&&(x.k!='A'||x.s==y.s)&&(x.k=='M'||x.k=='I'||x.k=='X'||(x.c.n==y.c.n&&x.c.e==y.c.e)); } if(!same){ printf("FAST PATH MISMATCH: cleanup not identity (%s)\n",MVN[ty]); fflush(stdout); abort(); } }
    } else { T=applyEdit(S,E); if(SCLEAN&&LOCALCL&&E.splitReg<0){ vector<char> inA(T.init.size(),0); for(int i:E.rem){ const Ev&e=S.P[i]; inA[e.d]=1; if(e.k=='A'||e.k=='C') inA[e.s]=1; } for(auto&x:E.ins){ inA[x.e.d]=1; if(x.e.k=='A'||x.e.k=='C') inA[x.e.s]=1; } for(auto&p:E.initCh) inA[p.first]=1; if(FULLV){ State T2=T; cleanup(T2); cleanup(T,&inA); bool same=T2.P.size()==T.P.size()&&T2.init==T.init; for(size_t a=0;same&&a<T.P.size();a++){ const Ev&x=T.P[a],&y=T2.P[a]; same=x.k==y.k&&x.d==y.d&&x.f==y.f&&(x.k!='A'&&x.k!='C'||x.s==y.s)&&(x.k=='M'||x.k=='I'||x.k=='X'||(x.c.n==y.c.n&&x.c.e==y.c.e)); } if(!same||T2.p0!=T.p0||T2.q!=T.q){ printf("LOCAL CLEANUP MISMATCH (%s)\n",MVN[ty]); fflush(stdout); abort(); } } else cleanup(T,&inA); } else cleanup(T); tp2=nowS(); TPR[1]+=tp2-tp1; if(!FREEB&&(long)T.P.size()>=CAP&&!FULLV){ memset(&Q,0,sizeof Q); Q.ok=false; Q.why="event cap"; } else Q=verifyInc(T,S,I,cur); TPR[2]+=nowS()-tp2; }
    if(FULLV){ if(fast&&T.P.empty()) T=applyEdit(S,E); Res F=verify(T); bool bad=F.ok!=Q.ok; if(!bad&&F.ok) bad=!(F.kap==Q.kap&&F.nev==Q.nev&&F.scalar==Q.scalar&&F.budget==Q.budget&&F.lt==Q.lt&&F.nhel==Q.nhel&&fabs(F.R0-Q.R0)<1e-9&&!memcmp(F.paid,Q.paid,sizeof F.paid)&&!memcmp(F.hel,Q.hel,sizeof F.hel)); if(bad){ for(int k=0;k<16;k++) if(F.paid[k]!=Q.paid[k]||F.hel[k]!=Q.hel[k]) printf("  rank %d paid full %ld inc %ld hel full %ld inc %ld (S paid %ld)\n",k,F.paid[k],Q.paid[k],F.hel[k],Q.hel[k],cur.paid[k]); printf("FULLVERIFY MISMATCH it %ld move %s fast %d: full ok=%d (%s) kap %.15f nev %ld scal %ld R0 %.6f | inc ok=%d (%s) kap %.15f nev %ld scal %ld R0 %.6f\n",it,MVN[ty],(int)fast,F.ok,F.why,F.kap,F.nev,F.scalar,F.R0,Q.ok,Q.why,Q.kap,Q.nev,Q.scalar,Q.R0); fflush(stdout); abort(); } }
    if(!Q.ok){ rej[string(MVN[ty])+":"+Q.why]++; continue; } lgl[ty]++;
    double dE=(Q.obj-cur.obj)*1e7; double Tm=T0*pow(T1/T0,frac);
    double dK=dE; if(EVPEN>0&&dK<=1e-9){ auto ov=[&](long v){ return (double)max(0L,v-EVT); }; dE-=EVPEN*(ov(Q.nev)-ov(cur.nev)); }   // never penalise a real kappa gain   // K2PUSH: soft event pressure above EVT (search bias only; best tracked on exact kappa)
    double dPhi=0; bool tieN=false; if(PH.on){ if(fast&&T.P.empty()) T=applyEdit(S,E); dPhi=phiDelta(PH,T,Q); tieN=PH.tie&&!walk&&fabs(dE)<=1e-9; if(!tieN&&PH.a>0&&dK<=1e-9) dE+=PH.a*(1-frac)*PH.c*dPhi; }   // HEURISTICS (a) tie-break / (b) annealed shaping
    bool ok=tieN?phiTieAcc(PH,dPhi,NEUTP):(walk||dE>1e-9||(dE>=-1e-9&&urand()<NEUTP)||(dE<-1e-9&&urand()<exp(dE/Tm)));
    if(ok&&PH.on) phiAccepted(PH);
    if(dK>1e-6) imp[ty]++;
    if(ok){ acc[ty]++; if(fast&&T.P.empty()) T=applyEdit(S,E); long hp0=(T.init==S.init)?T.p0:-1; long cj=LCV_j, cdl=LCV_delta; vector<char> otch; if(hp0>=0&&cj>=0&&cdl==0){ otch.assign(S.init.size(),0); for(long a=hp0;a<cj&&a<(long)S.P.size();a++){ const Ev&e=S.P[a]; otch[e.d]=1; if(e.k=='A'||e.k=='C') otch[e.s]=1; } } TENT=-1; SCLEAN=true; S.P.swap(T.P); S.init.swap(T.init); cur=Q; { double tb=nowS(); buildIndex(S,I,hp0,(hp0>=0)?cj:-1,cdl,otch.empty()?nullptr:&otch); TPR[3]+=nowS()-tb; } GDIRTY=true;
      if(FULLV){ Index J; buildIndex(S,J); const char*wh; if(!indexEqual(I,J,&wh)||!ckValid(S,I,&wh)){ printf("INDEX MISMATCH after accepted %s at it %ld: %s (hp0 %ld)\n",MVN[ty],it,wh,hp0); fflush(stdout); abort(); } }
      if(cur.obj>bestR.obj+1e-14){ best=S; bestR=cur; if(out&&(it-lastDump>20000||urand()<0.001)){ dumpBest(best,out,bestR); lastDump=it; dirty=0; } else dirty=1;
        if(lg){ fprintf(lg,"%ld %s kappa %.13f R0 %.4f nev %ld nhel %ld T %.4g\n",it,MVN[ty],cur.kap,cur.R0,cur.nev,cur.nhel,Tm); fflush(lg); } } }
    if(dirty&&out&&it-lastDump>20000){ dumpBest(best,out,bestR); lastDump=it; dirty=0; }
    if(PH.flog||PH.snap) phiTick(PH,it,S,cur,I);
    if(dumpEvery&&it%dumpEvery==0){ string o=string(out?out:"walk.net")+".cur"; dumpNet(S,o.c_str(),cur); }
    if(it%20000==0){ printf("it %ld kappa %.13f R0 %.4f nev %ld best %.13f |",it,cur.kap,cur.R0,cur.nev,bestR.kap); for(int k=0;k<NMV;k++) printf(" %s %ld/%ld/%ld",MVN[k],acc[k],lgl[k],prop[k]); printf("\n"); fflush(stdout); }
    (void)stall;
  }
  if(dirty&&out) dumpBest(best,out,bestR);
  if(getenv("K2S_PROFILE")){ printf("BUILDPH sim %.2f merge %.2f rest(ckpt..) %.2f\n",TBI[4],TBI[5],TBI[0]-TBI[4]-TBI[5]); printf("BUILDS resumed %ld spliced %ld full %ld\n",BR_RES,BR_SPL,BR_FULL); printf("FALLBACKS nohint %ld init %ld other %ld bigregion %ld | builds resumed %ld full %ld avg events/build %.0f\n",FB[0],FB[1],FB[2],FB[3],BR_RES,BR_FULL,(double)BR_EV/max(1L,BR_RES+BR_FULL)); printf("VERIFYINC full %ld inc %ld converged %ld simulated events/call %.0f\n",VI_FULL,VI_INC,VI_CONV,VI_INC?(double)VI_SIMEV/VI_INC:0.0); printf("BUILD sec events %.2f occ %.2f inv %.2f hash %.2f\n",TBI[0],TBI[1],TBI[2],TBI[3]); printf("PROFILE sec propose %.2f apply+cleanup %.2f verify %.2f buildIndex %.2f\n",TPR[0],TPR[1],TPR[2],TPR[3]); }
  if(PH.seg) printf("PHISEG segments %ld reverted %ld\n",PH.segN,PH.segRev);
  if(PH.la) printf("PHILA refreshes %ld ready-stops %ld kills-tried %ld cached %ld taken %ld\n",PH.nref,PH.nready,PH.nforced,PH.nskip,PH.ntook);
  printf("FINAL kappa %.13f R0 %.4f nev %ld | best kappa %.13f R0 %.4f\n",cur.kap,cur.R0,cur.nev,bestR.kap,bestR.R0);
  for(int k=0;k<NMV;k++) printf("  %-6s proposed %ld legal %ld improving %ld accepted %ld\n",MVN[k],prop[k],lgl[k],imp[k],acc[k]);
  for(auto&p:rej) printf("  reject %s %ld\n",p.first.c_str(),p.second);
  printf("DREL proposals %ld planned %ld relay-lifetimes %ld merges %ld cuts %ld newframes %ld | frames %d (input %d) peak cap %d regs %zu\n",DRS[0],DRS[1],DRS[2],DRS[3],DRS[4],DRS[5],SNF,SNF0,PEAKMAX,S.init.size());
  if(LVS[0]||LVS[5]){ printf("LEVERS"); for(int k=0;k<12;k++) printf(" %s %ld",LVN[k],LVS[k]); printf(" ee_hopback %ld\n",LVHB); }
  if(walk&&out){ dumpNet(S,out,cur); }
  if(lg) fclose(lg); return 0;
}
