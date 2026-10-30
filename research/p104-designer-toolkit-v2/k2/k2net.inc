// k2net.inc -- KERNEL2 explicit-network engine (included by k2.cpp; run with K2_NET=<net file>).
// STATE = rendezvous event program: per register a MOVE chain (nested frames), events at the frame where all their registers are located.
// Energy = sum over registers of tax(distinct chain dims) = D ln D - sum r ln r (owned reported apart).  Replay = exact content in doubles (dyadic coefficients).
struct NReg{ char role; int init; };
struct NEv{ char k; int d,s,f; double c; };
struct Net{
  int n=0,nown=0,nf=0,ne=0; vector<int> dim; vector<vector<int>> basis; vector<array<u64,8>> spn; vector<NReg> reg; vector<NEv> ev;
  vector<double> cdbl;
};
static double parseCoef(const char*s){ const char*sl=strchr(s,'/'); if(sl) return atof(s)/atof(sl+1); return atof(s); }
static bool loadNet(const char*path,Net&N){
  FILE*g=fopen(path,"r"); if(!g) return false; char buf[1<<16];
  while(fgets(buf,sizeof buf,g)){
    char t=buf[0];
    if(!strncmp(buf,"NET",3)){ sscanf(buf+3,"%d %d %d %d",&N.n,&N.nown,&N.nf,&N.ne); N.dim.assign(N.nf,0); N.basis.assign(N.nf,{}); N.reg.assign(N.n+4096,{'?',-1}); }
    else if(t=='F'){ int id,d; int off; sscanf(buf+1,"%d %d%n",&id,&d,&off); N.dim[id]=d; char*p=buf+1+off; for(int a=0;a<d;a++){ int v=strtol(p,&p,10); N.basis[id].push_back(v);} }
    else if(t=='R'){ int r,f; char ro; sscanf(buf+1,"%d %c %d",&r,&ro,&f); if(r>=(int)N.reg.size()) N.reg.resize(r+1,{'?',-1}); N.reg[r]={ro,f}; }
    else if(t=='M'){ NEv e{'M',0,0,0,0}; sscanf(buf+1,"%d %d",&e.d,&e.f); N.ev.push_back(e); }
    else if(t=='A'||t=='C'){ NEv e{t,0,0,0,0}; char cs[64]; sscanf(buf+1,"%d %d %63s %d",&e.d,&e.s,cs,&e.f); e.c=parseCoef(cs); N.ev.push_back(e); }
    else if(t=='S'){ NEv e{'S',0,0,0,0}; char cs[64]; sscanf(buf+1,"%d %63s %d",&e.d,cs,&e.f); e.c=parseCoef(cs); N.ev.push_back(e); }
    else if(t=='I'||t=='X'){ NEv e{t,0,0,0,0}; sscanf(buf+1,"%d %d",&e.d,&e.f); N.ev.push_back(e); }
  }
  fclose(g);
  N.spn.assign(N.nf,{}); for(int f=0;f<N.nf;f++){ array<u64,8> S{}; S[0]=1; vector<int> sp={0}; for(int v:N.basis[f]){ size_t m=sp.size(); for(size_t a=0;a<m;a++) sp.push_back(sp[a]^v); } for(int x:sp) S[x>>6]|=1ULL<<(x&63); N.spn[f]=S; }
  return true;
}
static bool nSub(const array<u64,8>&a,const array<u64,8>&b){ for(int w=0;w<8;w++) if(a[w]&~b[w]) return false; return true; }
static double taxDims(vector<int> ds){ sort(ds.begin(),ds.end()); ds.erase(unique(ds.begin(),ds.end()),ds.end()); int D=ds.back()-ds[0]; if(D<=0) return 0; double t=RL[D]; for(size_t a=1;a<ds.size();a++) t-=RL[ds[a]-ds[a-1]]; return t; }
// energy by role from chains; returns total over X,Y,H (owned printed apart)
static double netEnergy(const Net&N,double*byRole /*X,Y,H,O*/){
  vector<vector<int>> ch(N.reg.size()); for(size_t r=0;r<N.reg.size();r++) if(N.reg[r].role!='?' && N.reg[r].init>=0) ch[r].push_back(N.dim[N.reg[r].init]);
  for(auto&e:N.ev){ if(e.k=='M'||e.k=='I') ch[e.d].push_back(N.dim[e.f]); }
  double tot[4]={0,0,0,0};
  for(size_t r=0;r<N.reg.size();r++){ if(ch[r].empty()) continue; char ro=N.reg[r].role; int k=ro=='X'?0:ro=='Y'?1:ro=='H'?2:3; tot[k]+=taxDims(ch[r]); }
  if(byRole) for(int k=0;k<4;k++) byRole[k]=tot[k];
  return tot[0]+tot[1]+tot[2];
}
// legality: co-presence at every event, nested chain; returns violations
static long netLegal(const Net&N,long*nonNested){
  vector<int> cur(N.reg.size(),-1); for(size_t r=0;r<N.reg.size();r++) if(N.reg[r].init>=0) cur[r]=N.reg[r].init; long bad=0,nn=0;
  for(auto&e:N.ev){
    if(e.k=='M'){ if(cur[e.d]>=0 && !nSub(N.spn[cur[e.d]],N.spn[e.f])) nn++; cur[e.d]=e.f; }
    else if(e.k=='I'){ cur[e.d]=e.f; }
    else if(e.k=='A'||e.k=='C'){ bad+=(cur[e.d]!=e.f)+(cur[e.s]!=e.f); }
    else if(e.k=='S'||e.k=='X'){ bad+=cur[e.d]!=e.f; }
  }
  if(nonNested) *nonNested=nn; return bad;
}
static double netSignature(const Net&N){
  int n=N.n; vector<vector<double>> V(N.reg.size()); for(int r=0;r<n;r++){ V[r].assign(n,0); V[r][r]=1; }
  for(auto&e:N.ev){
    if(e.k=='A'||e.k=='C'){ auto&D=V[e.d]; if(D.empty()) D.assign(n,0); if(e.k=='C') fill(D.begin(),D.end(),0.0); const auto&S=V[e.s]; if(S.empty()) continue; double c=e.c; for(int i=0;i<n;i++) D[i]+=c*S[i]; }
    else if(e.k=='S'){ for(auto&x:V[e.d]) x*=e.c; }
    else if(e.k=='I'||e.k=='X'){ V[e.d].assign(n,0); }
  }
  double s=0; for(size_t r=0;r<V.size();r++) for(int c=0;c<(int)V[r].size();c++) if(V[r][c]!=0) s+=V[r][c]*(double)((r*7919ULL+c*104729ULL)%1000003ULL);
  return s;
}
static int netMain(const char*path){
  Net N; if(!loadNet(path,N)){ fprintf(stderr,"cannot load %s\n",path); return 1; }
  for(int r=1;r<64;r++) RL[r]=r*log((double)r); RL[0]=0;
  double by[4]; double E=netEnergy(N,by); long nn; long bad=netLegal(N,&nn);
  printf("NET n=%d owned=%d frames=%d events=%zu\n",N.n,N.nown,N.nf,N.ev.size());
  printf("R0 X %.4f Y %.4f H %.4f total %.4f (owned chains %.4f)\n",by[0],by[1],by[2],E,by[3]);
  printf("rendezvous violations %ld non-nested chain steps %ld\n",bad,nn);
  printf("signature %.6f\n",netSignature(N));
  return 0;
}
