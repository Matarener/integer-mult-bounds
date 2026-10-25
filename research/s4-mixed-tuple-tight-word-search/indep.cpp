// Second, separately written engine (explicit-matrix representation). Each paid gate is an explicit
// F2 matrix I + (rho(s)+I) (x) u v^T in the natural (4r) and ordered-pair (12r) permutation
// representations; states are products of these matrices (no group-algebra masks). Pruned DFS from
// the target end with the cut windows; prints node counts per depth and full-depth survivors.
#include <bits/stdc++.h>
#include <omp.h>
using namespace std; typedef unsigned long long u64;
int r; vector<array<int,2>> pts[2]; // module 0: natural points (x,-1), module 1: ordered pairs
int dimp[2];
array<int,4> gen[3]={{{2,1,3,4}},{{1,3,2,4}},{{1,2,4,3}}};
int actpt(const array<int,4>&g,int mod,int p){ auto q=pts[mod][p]; array<int,2> img={g[q[0]-1], q[1]<0?-1:g[q[1]-1]}; for(int i=0;i<dimp[mod];i++) if(pts[mod][i]==img) return i; abort(); }
struct M2{ vector<u64> rows; }; // row bitsets, index role*d+point
M2 mul(const M2&A,const M2&B){ M2 C; C.rows.resize(A.rows.size()); for(size_t i=0;i<A.rows.size();i++){ u64 x=A.rows[i],y=0; while(x){ int k=__builtin_ctzll(x); y^=B.rows[k]; x&=x-1;} C.rows[i]=y;} return C; }
int rk(vector<u64> v){ int rnk=0; for(size_t i=0;i<v.size();i++){ u64 p=v[i]; if(!p) continue; rnk++; u64 lb=p&-p; for(size_t j=i+1;j<v.size();j++) if(v[j]&lb) v[j]^=p; } return rnk; }
bool inH(int cut,int p){ auto q= cut==2? pts[1][p] : pts[0][p]; if(cut==0) return q[0]<=1; if(cut==1) return q[0]<=3; return q[0]<q[1]; }
int modOf(int cut){ return cut==2?1:0; }
int brank(const M2&M,int cut,bool fwd){ int mod=modOf(cut), d=dimp[mod]; vector<int> Hr,Cr; for(int i=0;i<r;i++) for(int a=0;a<d;a++) (inH(cut,a)?Hr:Cr).push_back(i*d+a);
  const vector<int>&rs= fwd?Cr:Hr; const vector<int>&cs= fwd?Hr:Cr; vector<u64> sub; for(int q:rs){ u64 x=0; for(size_t t=0;t<cs.size();t++) if(M.rows[q]>>cs[t]&1) x|=1ULL<<t; sub.push_back(x);} return rk(sub); }
int ch[3][3], phiT[3], n[3]; vector<array<int,3>> gates; vector<array<M2,2>> G; array<M2,2> Tm;
long long nodes[20], survivors=0;
bool ok(const array<M2,2>&S,const int m[3]){ for(int c=0;c<3;c++){ int hi=0,tot=0; for(int k=0;k<3;k++){hi+=ch[c][k]*m[k]; tot+=ch[c][k]*n[k];} int lo=phiT[c]-(tot-hi); for(int f=0;f<2;f++){ int ph=brank(S[modOf(c)],c,f); if(ph<lo||ph>hi) return false; } } return true; }
long long nodesT[64][20], survT[64];
void dfs(const array<M2,2>&S,int m[3],int depth,int tot,int tid){ if(depth==tot){ survT[tid]++; return; }
  for(size_t gi=0;gi<gates.size();gi++){ int k=gates[gi][0]; if(!m[k]) continue; array<M2,2> S2={mul(S[0],G[gi][0]),mul(S[1],G[gi][1])}; m[k]--; if(ok(S2,m)){ nodesT[tid][depth+1]++; dfs(S2,m,depth+1,tot,tid);} m[k]++; } }
int main(int argc,char**argv){ r=atoi(argv[1]); for(int k=0;k<3;k++) n[k]=atoi(argv[2+k]); vector<array<int,4>> tg; for(int i=0;i<r;i++){ array<int,4> g; for(int j=0;j<4;j++) g[j]=argv[5+i][j]-'0'; tg.push_back(g);} 
  for(int x=1;x<=4;x++) pts[0].push_back({x,-1}); for(int x=1;x<=4;x++) for(int y=1;y<=4;y++) if(x!=y) pts[1].push_back({x,y}); dimp[0]=4; dimp[1]=12;
  if(12*r>64){ fprintf(stderr,"r too large\n"); return 2; }
  auto rho=[&](const array<int,4>&g,int mod){ int d=dimp[mod]; vector<vector<int>> A(d,vector<int>(d,0)); for(int b=0;b<d;b++) A[actpt(g,mod,b)][b]=1; return A; };
  for(int c=0;c<3;c++) for(int k=0;k<3;k++){ int cnt=0, mod=modOf(c); for(int p=0;p<dimp[mod];p++) if(inH(c,p) && !inH(c,actpt(gen[k],mod,p))) cnt++; ch[c][k]=cnt; }
  for(int u=1;u<(1<<r);u++) for(int v=1;v<(1<<r);v++) if(__builtin_popcount(u&v)&1) for(int k=0;k<3;k++) gates.push_back({k,u,v});
  for(auto&g:gates){ array<M2,2> pr; for(int mod=0;mod<2;mod++){ int d=dimp[mod]; auto A=rho(gen[g[0]],mod); for(int a=0;a<d;a++) A[a][a]^=1; M2 M; M.rows.assign(r*d,0);
      for(int i=0;i<r;i++) for(int a=0;a<d;a++){ u64 x=0; for(int j=0;j<r;j++) for(int b=0;b<d;b++){ int val=(i==j&&a==b) ^ (A[a][b] & (g[1]>>i&1) & (g[2]>>j&1)); if(val) x|=1ULL<<(j*d+b);} M.rows[i*d+a]=x; } pr[mod]=M; } G.push_back(pr); }
  for(int mod=0;mod<2;mod++){ int d=dimp[mod]; M2 M; M.rows.assign(r*d,0); for(int i=0;i<r;i++){ auto A=rho(tg[i],mod); for(int a=0;a<d;a++){ u64 x=0; for(int b=0;b<d;b++) if(A[a][b]) x|=1ULL<<(i*d+b); M.rows[i*d+a]=x; } } Tm[mod]=M; }
  int tot=n[0]+n[1]+n[2];
  for(int c=0;c<3;c++){ int a=brank(Tm[modOf(c)],c,true), b=brank(Tm[modOf(c)],c,false); if(a!=b) abort(); phiT[c]=a; int t=0; for(int k=0;k<3;k++) t+=ch[c][k]*n[k]; printf("cut%d charges=(%d,%d,%d) PhiT=%d n.c=%d\n",c,ch[c][0],ch[c][1],ch[c][2],a,t); if(t<a){ printf("INFEASIBLE_BY_CUT\n"); return 0; } }
  // first level: optional list of first-letter gate indices (comma list) to restrict, else all
  vector<int> first; if(argc>5+r && string(argv[5+r])!="all"){ string s=argv[5+r]; stringstream ss(s); string t; while(getline(ss,t,',')) first.push_back(stoi(t)); } else for(size_t g=0;g<gates.size();g++) first.push_back(g);
  memset(nodesT,0,sizeof nodesT); memset(survT,0,sizeof survT);
  #pragma omp parallel for schedule(dynamic,1)
  for(size_t fi=0;fi<first.size();fi++){ int tid=omp_get_thread_num(); int gi=first[fi]; int m[3]={n[0],n[1],n[2]}; int k=gates[gi][0]; if(!m[k]) continue; array<M2,2> S2={mul(Tm[0],G[gi][0]),mul(Tm[1],G[gi][1])}; m[k]--; if(ok(S2,m)){ nodesT[tid][1]++; dfs(S2,m,1,tot,tid);} }
  for(int t=0;t<64;t++){ for(int d=0;d<20;d++) nodes[d]+=nodesT[t][d]; survivors+=survT[t]; }
  printf("gates=%zu first_letters=%zu nodes_per_depth=",gates.size(),first.size()); for(int d=1;d<=tot;d++) printf("%lld,",nodes[d]); printf(" full_depth_survivors=%lld\n",survivors);
}
