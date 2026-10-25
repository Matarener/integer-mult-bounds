// Exact MITM search for words W = L1...Ln (paid gates D=I+([s]+1)uv^T, v.u=1) on r roles with
// prescribed label counts, equal to T=diag([t1],..,[tr]) in M_r(F2[S4]). Free GL_r(F2) is absorbed
// (conjugated into the idempotents; the trailing scalar is forced to I by augmentation).
// Usage: search R KA KC n1 n2 n3 t1..tR logslots. KA=0 gives a pure DFS from the target end (used
// for all recorded runs). Env SYM=1 SYM_A=i SYM_B=j [SYM_D=1] restricts the first peeled letter to
// orbit representatives (see PROOF.md section 5); STOP_FIRST=1 stops at the first verified word.
// Pruning: necessary cut windows Phi(T)-c.(n-m) <= Phi(P_m) <= c.m for every prefix P_m and for
// the inv (ordered-pair), c1 and c3 (natural) coordinate cuts, both crossing blocks.
#include <bits/stdc++.h>
#include <omp.h>
using namespace std;
typedef array<int,4> P4; typedef unsigned u32; typedef unsigned long long u64;
int R; // roles
vector<P4> el; map<P4,int> idx;
P4 comp(const P4&a,const P4&b){P4 c; for(int i=0;i<4;i++) c[i]=a[b[i]]; return c;}
P4 parse(const string&s){P4 q; for(int i=0;i<4;i++) q[i]=s[i]-'1'; return q;}
u32 RT[3][3][256]; // right multiplication by s_k: g -> g s_k
struct Mat{ u32 e[6][6]; };
int ng; vector<array<int,3>> gates; // (label k, u, v)
u32 mulR(int k,u32 a){ return RT[k][0][a&255]|RT[k][1][(a>>8)&255]|RT[k][2][(a>>16)&255]; }
inline void apply(Mat&M,int gi){ int k=gates[gi][0],u=gates[gi][1],v=gates[gi][2];
  for(int i=0;i<R;i++){ u32 w=0; for(int j=0;j<R;j++) if(u>>j&1) w^=M.e[i][j]; w=mulR(k,w)^w; if(w) for(int j=0;j<R;j++) if(v>>j&1) M.e[i][j]^=w; } }
// modules
u32 NM[4][4]; // g with g(b)=a
vector<pair<int,int>> pairs; u32 PM[12][12];
int rankrows(vector<u32>& rows){ int rk=0; for(size_t i=0;i<rows.size();i++){ u32 x=rows[i]; if(!x) continue; rk++; u32 lb=x&-x; for(size_t j=i+1;j<rows.size();j++) if(rows[j]&lb) rows[j]^=x; } return rk; }
struct Cut{ int mod; vector<int> H, Hc; int ch[3]; };
vector<Cut> cuts;
int blockrank(const Mat&M,const Cut&c,bool fwd){ // fwd: rows Hc <- cols H ; else rows H <- cols Hc
  const vector<int>&rowsP= fwd?c.Hc:c.H; const vector<int>&colsP= fwd?c.H:c.Hc;
  vector<u32> rows; rows.reserve(R*rowsP.size());
  for(int i=0;i<R;i++) for(int a:rowsP){ u32 m=0; int bit=0; for(int j=0;j<R;j++) for(int b:colsP){ u32 mask= c.mod==0? NM[a][b] : PM[a][b]; if(__builtin_popcount(M.e[i][j]&mask)&1) m|=1u<<bit; bit++; } rows.push_back(m);} 
  return rankrows(rows);
}
int n[3]; int phiT[16]; Mat T;
bool windows_ok(const Mat&M,const int m[3]){
  for(size_t ci=0;ci<cuts.size();ci++){ const Cut&c=cuts[ci]; int hi=0,tot=0; for(int k=0;k<3;k++){hi+=c.ch[k]*m[k]; tot+=c.ch[k]*n[k];} int lo=phiT[ci]-(tot-hi);
    for(int f=0;f<2;f++){ int ph=blockrank(M,c,f); if(ph<lo||ph>hi) return false; } }
  return true; }
u64 hashm(const Mat&M,const int m[3]){ u64 h=1469598103934665603ULL^(m[0]*49+m[1]*7+m[2]); for(int i=0;i<R;i++) for(int j=0;j<R;j++){ h^=M.e[i][j]+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2); h*=0xff51afd7ed558ccdULL; h^=h>>33;} return h|1ULL<<63; }
int KA,KC; vector<u64> table; u64 tmask; long long nodesA[16],nodesC[16],inserted=0,hits=0,verified=0;
vector<int> wordA(16),wordC(16);
void insert(u64 h){ u64 s=h&tmask; while(table[s]){ if(table[s]==h) return; s=(s+1)&tmask;} table[s]=h; inserted++; }
bool lookup(u64 h){ u64 s=h&tmask; while(table[s]){ if(table[s]==h) return true; s=(s+1)&tmask;} return false; }
void dfsA(Mat M,int d,int m[3]){ if(d==KA){ insert(hashm(M,m)); return; }
  for(int gi=0;gi<ng;gi++){ int k=gates[gi][0]; if(m[k]==n[k]) continue; Mat N2=M; apply(N2,gi); m[k]++; if(windows_ok(N2,m)){ nodesA[d+1]++; dfsA(N2,d+1,m);} m[k]--; } }
// verification: re-enumerate A words matching target matrix
bool findA(Mat M,int d,int m[3],const Mat&tgt,const int tm[3],vector<int>&w){ if(d==KA){ if(memcmp(m,tm,sizeof(int)*3)) return false; for(int i=0;i<R;i++) for(int j=0;j<R;j++) if(M.e[i][j]!=tgt.e[i][j]) return false; return true; }
  for(int gi=0;gi<ng;gi++){ int k=gates[gi][0]; if(m[k]==n[k]) continue; Mat N2=M; apply(N2,gi); m[k]++; w[d]=gi; if(windows_ok(N2,m) && findA(N2,d+1,m,tgt,tm,w)){ m[k]--; return true;} m[k]--; } return false; }
vector<vector<int>> found;
long long nodesCt[64][16],hitst[64],vert[64];
void dfsC(Mat M,int d,int m[3],vector<int>&wc,int tid){ // M = prefix P with counts m (= n - peeled)
  for(int gi=0;gi<ng;gi++){ int k=gates[gi][0]; if(m[k]==0) continue; Mat N2=M; apply(N2,gi); m[k]--; wc[d]=gi;
    if(d+1==KC){ nodesCt[tid][d+1]++; if(lookup(hashm(N2,m))){ hitst[tid]++; Mat I; memset(&I,0,sizeof I); for(int i=0;i<R;i++) I.e[i][i]=1u<<idx[P4{0,1,2,3}]; int z[3]={0,0,0}; vector<int> w(KA);
        if(findA(I,0,z,N2,m,w)){ vert[tid]++; vector<int> full=w; for(int t=KC-1;t>=0;t--) full.push_back(wc[t]);
          #pragma omp critical
          { found.push_back(full); if(getenv("STOP_FIRST")){ printf("FIRST_WORD"); for(int gi:full) printf(" s%d:u%d:v%d",gates[gi][0]+1,gates[gi][1],gates[gi][2]); printf("\n"); fflush(stdout); _exit(0);} } } } }
    else if(windows_ok(N2,m)){ nodesCt[tid][d+1]++; dfsC(N2,d+1,m,wc,tid);} m[k]++; } }
int main(int argc,char**argv){
  // usage: mitm R KA KC n1 n2 n3 t1 t2 ... tR logslots
  // shortcut: blockrank packs block rows into 32-bit words and the inv block has 6R columns, so R<=5;
  // widen rows/rankrows to u64 (and the guard to R<=6) before any r=6 run.
  R=atoi(argv[1]); if(R<1||R>5){fprintf(stderr,"R out of range (1..5)\n");return 2;} KA=atoi(argv[2]); KC=atoi(argv[3]); for(int k=0;k<3;k++) n[k]=atoi(argv[4+k]);
  vector<string> tg; for(int i=0;i<R;i++) tg.push_back(argv[7+i]); int logs=atoi(argv[7+R]);
  if(n[0]+n[1]+n[2]!=KA+KC){ fprintf(stderr,"bad split\n"); return 2; }
  P4 p={0,1,2,3}; do el.push_back(p); while(next_permutation(p.begin(),p.end())); for(int i=0;i<24;i++) idx[el[i]]=i;
  const char* sn[3]={"2134","1324","1243"};
  for(int k=0;k<3;k++){ P4 s=parse(sn[k]); for(int b=0;b<3;b++) for(int v=0;v<256;v++){ u32 m=0; for(int j=0;j<8;j++) if(v>>j&1) m|=1u<<idx[comp(el[8*b+j],s)]; RT[k][b][v]=m; } }
  for(int a=0;a<4;a++) for(int b=0;b<4;b++){ u32 m=0; for(int g=0;g<24;g++) if(el[g][b]==a) m|=1u<<g; NM[a][b]=m; }
  for(int a=0;a<4;a++) for(int b=0;b<4;b++) if(a!=b) pairs.push_back({a,b});
  for(int p1=0;p1<12;p1++) for(int q=0;q<12;q++){ u32 m=0; for(int g=0;g<24;g++) if(el[g][pairs[q].first]==pairs[p1].first && el[g][pairs[q].second]==pairs[p1].second) m|=1u<<g; PM[p1][q]=m; }
  // cuts: c1 (natural H={1}), c3 (natural H={1,2,3}), inv (ordered pairs H={(a,b):a<b})
  auto mkcut=[&](int mod,vector<int>H){ Cut c; c.mod=mod; c.H=H; int np= mod==0?4:12; for(int x=0;x<np;x++) if(!count(H.begin(),H.end(),x)) c.Hc.push_back(x);
     for(int k=0;k<3;k++){ P4 s=parse(sn[k]); int cc=0; for(int x:H){ int y; if(mod==0) y=s[x]; else { auto pr=pairs[x]; pair<int,int> q={s[pr.first],s[pr.second]}; y=find(pairs.begin(),pairs.end(),q)-pairs.begin(); } if(!count(H.begin(),H.end(),y)) cc++; } c.ch[k]=cc; } return c; };
  cuts.push_back(mkcut(0,{0})); cuts.push_back(mkcut(0,{0,1,2})); vector<int> inc; for(int x=0;x<12;x++) if(pairs[x].first<pairs[x].second) inc.push_back(x); cuts.push_back(mkcut(1,inc));
  for(int u=1;u<(1<<R);u++) for(int v=1;v<(1<<R);v++) if(__builtin_popcount(u&v)&1) for(int k=0;k<3;k++) gates.push_back({k,u,v});
  ng=gates.size();
  memset(&T,0,sizeof T); for(int i=0;i<R;i++) T.e[i][i]=1u<<idx[parse(tg[i])];
  for(size_t ci=0;ci<cuts.size();ci++){ int a=blockrank(T,cuts[ci],true), b=blockrank(T,cuts[ci],false); if(a!=b){fprintf(stderr,"asym\n");} phiT[ci]=a;
    int tot=0; for(int k=0;k<3;k++) tot+=cuts[ci].ch[k]*n[k]; fprintf(stderr,"cut%zu charges(%d,%d,%d) PhiT=%d n.c=%d %s\n",ci,cuts[ci].ch[0],cuts[ci].ch[1],cuts[ci].ch[2],phiT[ci],tot,tot==phiT[ci]?"TIGHT":(tot<phiT[ci]?"INFEASIBLE":"slack")); if(tot<phiT[ci]){ printf("RESULT infeasible-by-cut words=0\n"); return 0;} }
  fprintf(stderr,"gates=%d\n",ng);
  table.assign(1ULL<<logs,0); tmask=(1ULL<<logs)-1;
  Mat I; memset(&I,0,sizeof I); for(int i=0;i<R;i++) I.e[i][i]=1u<<idx[P4{0,1,2,3}];
  int m[3]={0,0,0}; auto t0=chrono::steady_clock::now();
  dfsA(I,0,m);
  double tA=chrono::duration<double>(chrono::steady_clock::now()-t0).count();
  fprintf(stderr,"A side done: inserted=%lld (load %.3f) time=%.1fs nodes:",inserted,(double)inserted/(1ULL<<logs),tA); for(int d=1;d<=KA;d++) fprintf(stderr," %lld",nodesA[d]); fprintf(stderr,"\n");
  memset(nodesCt,0,sizeof nodesCt); memset(hitst,0,sizeof hitst); memset(vert,0,sizeof vert);
  // optional symmetry reduction of the first peeled letter: conjugation by GL_2(F2) on two roles
  // holding the same target element, and the diagram automorphism s1<->s3 when every target is
  // w0-invariant. Both are ring automorphisms of M_r(F2[S4]) fixing T and preserving counts (n1=n3).
  vector<int> rep(ng); for(int g=0;g<ng;g++) rep[g]=g;
  int symA=-1,symB=-1; bool symD=false;
  if(getenv("SYM")){ symA=atoi(getenv("SYM_A")); symB=atoi(getenv("SYM_B")); symD=getenv("SYM_D")!=nullptr;
    if(tg[symA]!=tg[symB]){ fprintf(stderr,"SYM roles differ\n"); return 3; }
    if(symD){ if(n[0]!=n[2]){fprintf(stderr,"SYM_D needs n1=n3\n");return 3;} P4 w0=parse("4321"); for(auto&t:tg){ P4 g=parse(t); if(comp(comp(w0,g),w0)!=g){ fprintf(stderr,"target not w0-invariant\n"); return 3; } } }
    int Gs[6][4]={{1,0,0,1},{0,1,1,0},{1,1,0,1},{1,0,1,1},{0,1,1,1},{1,1,1,0}};
    map<array<int,3>,int> gidx; for(int g=0;g<ng;g++) gidx[gates[g]]=g;
    auto tr=[&](int x,int a,int b,int c,int d){ int x0=x>>symA&1, x1=x>>symB&1; int y0=(a&x0)^(b&x1), y1=(c&x0)^(d&x1); x&=~((1<<symA)|(1<<symB)); return x|(y0<<symA)|(y1<<symB); };
    for(int g=0;g<ng;g++) for(int gi=0;gi<6;gi++) for(int dd=0;dd<(symD?2:1);dd++){ int a=Gs[gi][0],b=Gs[gi][1],c=Gs[gi][2],d=Gs[gi][3];
      int k=gates[g][0]; if(dd) k=2-k; int u2=tr(gates[g][1],a,b,c,d); int v2=tr(gates[g][2],d,c,b,a); // u->Gu, v->G^{-T}v
      int h=gidx.at({k,u2,v2}); rep[g]=min(rep[g],h); }
    int nr=0; for(int g=0;g<ng;g++) nr+=rep[g]==g; fprintf(stderr,"SYM on roles %d,%d D=%d: %d first-letter orbit representatives of %d gates\n",symA,symB,(int)symD,nr,ng); }
  { int surv=0, survrep=0; for(int g0=0;g0<ng;g0++){ int mc[3]={n[0],n[1],n[2]}; int k=gates[g0][0]; if(mc[k]==0) continue; Mat N2=T; apply(N2,g0); mc[k]--; if(windows_ok(N2,mc)){ surv++; if(rep[g0]==g0) survrep++; } }
    fprintf(stderr,"depth-1 survivors=%d, representatives to search=%d\n",surv,survrep); }
  #pragma omp parallel for schedule(dynamic,1)
  for(int g0=0;g0<ng;g0++){ int tid=omp_get_thread_num(); if(rep[g0]!=g0) continue; int mc[3]={n[0],n[1],n[2]}; int k=gates[g0][0]; if(mc[k]==0) continue; Mat N2=T; apply(N2,g0); mc[k]--; vector<int> wc(16); wc[0]=g0;
    if(KC==1){ nodesCt[tid][1]++; if(lookup(hashm(N2,mc))){ hitst[tid]++; } continue; }
    if(windows_ok(N2,mc)){ long long before=0; for(int d=0;d<16;d++) before+=nodesCt[tid][d]; nodesCt[tid][1]++; dfsC(N2,1,mc,wc,tid); long long after=0; for(int d=0;d<16;d++) after+=nodesCt[tid][d];
      #pragma omp critical
      { fprintf(stderr,"BRANCH g0=%d subtree_nodes=%lld\n",g0,after-before); fflush(stderr);} } }
  for(int t=0;t<64;t++){ for(int d=0;d<16;d++) nodesC[d]+=nodesCt[t][d]; hits+=hitst[t]; verified+=vert[t]; }
  double tC=chrono::duration<double>(chrono::steady_clock::now()-t0).count();
  fprintf(stderr,"C side done time=%.1fs nodes:",tC); for(int d=1;d<=KC;d++) fprintf(stderr," %lld",nodesC[d]); fprintf(stderr,"\n");
  printf("RESULT R=%d n=(%d,%d,%d) split=%d+%d hits=%lld verified_words=%lld Anodes=",R,n[0],n[1],n[2],KA,KC,hits,verified); for(int d=1;d<=KA;d++) printf("%lld,",nodesA[d]); printf(" Cnodes="); for(int d=1;d<=KC;d++) printf("%lld,",nodesC[d]); printf(" Ainserted=%lld\n",inserted);
  for(size_t f=0;f<found.size()&&f<5;f++){ printf("WORD"); for(int gi:found[f]) printf(" s%d:u%d:v%d",gates[gi][0]+1,gates[gi][1],gates[gi][2]); printf("\n"); }
}
