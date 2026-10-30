// k2phi.inc -- HEURISTICS lane (toolkit/module docstring): law-derived potentials Phi(s) for SHAPED k2 search.  DEFAULT OFF.
// Included by k2search.inc right before searchMain.  With K2S_PHI unset nothing here runs and no RNG draw is consumed: trajectories are bit-identical.
// Every feature is a cost-law quantity (no reference-word constants):
//   F0 RUNG SLACK   sum over killable stops (r,j) of s_j * p^n_j.  s_j = R0 saved by deleting the stop = taxMask(mask_r) - taxMask(mask_r \ dim_j)
//                   (EXACT under the chain-tax law R0 = D ln D - sum r ln r); n_j = ADD events at the stop (each must be re-delivered by the kill planner);
//                   p = per-event delivery probability (MODEL: independent deliveries, K2S_PHIP, default .5).  = expected R0 saving of one kill attempt at that stop.
//   F1 FREE RUNGS   sum of s_j over killable stops with n_j <= 1 (a rung one delivery away from a kill).
//   F2 BLOCKED      number of non-fixed stops holding a non-ADD event (SCALE/COPY/INIT/CLEAR): mvKill's precondition fails there (EXACT).
//   F3 DRAIN MASS   sum of n_j over killable stops / 100 (delivery obligations standing between the state and its kills).
//   F4 EVENT SLACK  (CAP - nev)/1000: insertion capacity under the event cap (every relay/delivery costs events; EXACT budget).
//   F5 R0/1000      chain tax (MODEL kappa law: kappa ~ 1/(131.2 + .02364 R0)).
// Phi = sum_k w_k F_k (K2S_PHIW, default 1,0,0,0,0,0), in R0 units; converted to SA units (1e-7 kappa) by c = .02364 kappa0^2 1e7 (the same law).
// Shaping (both act only on proposals that are kappa-neutral or worse; best is always tracked on exact kappa):
//   (a) K2S_PHITAU=tau > 0: tie-break on the kappa-neutral manifold: accept with prob NEUTP * min(1, exp(dPhi/tau)).
//   (b) K2S_PHIA=a > 0: dE += a (1 - frac) c dPhi (annealed to 0 at the end of the schedule).
// Logging (no trajectory effect): K2S_FLOG=file, K2S_FLOGN=every (default 1000): "it kappa R0 nev F0..F5 D0..D3"; K2S_FSNAP=every: dumps the current net to <K2S_OUT>.snap<it>.
// Cost: Phi(T) is recomputed from scratch (one O(n) pass) for every legal proposal while shaping is on (the fast path materialises T for it).
static const int NPHI=6; static const int NDEL=4;
struct PhiCtx{ bool on=false, tie=false; double w[NPHI]={1,0,0,0,0,0}; double p=.5, tau=0, a=0, c=2.3; double F[NPHI]={0}, Fc[NPHI]={0}; double phi=0, phic=0;
  FILE*flog=nullptr; long fevery=1000, snap=0, nlog=0, nsnap=0; string snapPre;
  long la=0, nla=0, nref=0, nready=0, nforced=0, ntook=0; int lan=64; vector<pair<int,int>> q; std::unordered_set<u64> miss; double missK=-1; long nskip=0;
  long seg=0, nseg=0, segRev=0, segN=0; double segTau=1, segW[NDEL]={0,0,1,0}, segPhi=0; State anc; Res ancR; bool hasAnc=false; };   // (d) segment tie-break on delivery readiness   // (c) READY-KILL look-ahead: every la its, queue every kill-ready stop (r, frame)
static void phiFeat(const State&S,long nev,double R0,double p,double*F){
  int NR=S.init.size(); struct SR{ int r,dim,n; char blk; };
  static vector<SR> recs; recs.clear(); static vector<int> cd,cn,cb,nst,mask; cd.assign(NR,-1); cn.assign(NR,0); cb.assign(NR,0); nst.assign(NR,0); mask.assign(NR,0);
  for(int r=0;r<NR;r++) if(ROLE[r]!='O'&&S.init[r]>=0) cd[r]=SDIM[S.init[r]];
  auto close=[&](int r){ if(cd[r]>=0){ recs.push_back({r,cd[r],cn[r],(char)cb[r]}); nst[r]++; mask[r]|=1<<cd[r]; } cn[r]=0; cb[r]=0; };
  for(const Ev&e:S.P){ int d=e.d; if(ROLE[d]=='O'&&(e.k!='A'&&e.k!='C')) continue;
    switch(e.k){ case 'M': close(d); cd[d]=SDIM[e.f]; break;
      case 'A': if(ROLE[d]!='O') cn[d]++; if(ROLE[e.s]!='O') cn[e.s]++; break;
      case 'C': if(ROLE[d]!='O') cb[d]=1; if(ROLE[e.s]!='O') cb[e.s]=1; break;
      default: cb[d]=1; } }
  for(int r=0;r<NR;r++) if(ROLE[r]!='O') close(r);
  for(int k=0;k<NPHI;k++) F[k]=0;
  static vector<int> seen; seen.assign(NR,0);   // stop ordinal per register (records are in closing order = chain order per register)
  for(auto&x:recs){ int j=seen[x.r]++; int ns=nst[x.r]; if(ns<2) continue; if(fixedStop(x.r,j,ns)) continue;
    if(x.blk){ F[2]+=1; continue; } if(x.n<=0) continue;
    double s=taxMask(mask[x.r])-taxMask(mask[x.r]&~(1<<x.dim)); F[0]+=s*pow(p,x.n); if(x.n<=1) F[1]+=s; F[3]+=x.n*.01; }
  F[4]=(double)(CAP-nev)*1e-3; F[5]=R0*1e-3;
}
static double phiOf(const PhiCtx&P,const double*F){ double s=0; for(int k=0;k<NPHI;k++) s+=P.w[k]*F[k]; return s; }
// candidate T (cleaned, legal, result Q): dPhi = Phi(T) - Phi(S)
static double phiDelta(PhiCtx&P,const State&T,const Res&Q){ phiFeat(T,Q.nev,Q.R0,P.p,P.Fc); P.phic=phiOf(P,P.Fc); return P.phic-P.phi; }
static inline bool phiTieAcc(const PhiCtx&P,double dPhi,double neutp){ double u=urand(); return dPhi>=-1e-12 ? u<neutp : u<neutp*exp(dPhi/P.tau); }
static void phiAccepted(PhiCtx&P){ memcpy(P.F,P.Fc,sizeof P.F); P.phi=P.phic; }
// DELIVERY READINESS (needs the Index of an ACCEPTED state; RNG state saved/restored, so logging never changes a trajectory):
//   for every killable stop (r,j) (non-fixed, ADD-only, r has >= 2 stops), d_j = number of its ADD events with NO single-term re-delivery (findSources with the stop excluded, exactly
//   mvKill's first planner attempt).  d_j = 0 => the rung kill is plannable now (EXACT lower bound: two-term/peel deliveries are not counted).
//   D0 = sum s_j [d_j = 0]   D1 = sum s_j [d_j = 1]   D2 = sum s_j .1^d_j   D3 = deliverable events / 100   (s_j = R0 saved by the rung, as F0)

static void phiDeliv(const Index&I,const State&S,double*D,vector<pair<int,int>>*ready=nullptr){   // D == nullptr: readiness list only (early exit per stop)
  u64 sv=RSEED; if(D) for(int k=0;k<NDEL;k++) D[k]=0; int NR=S.init.size();
  for(int r=0;r<NR;r++){ if(ROLE[r]=='O') continue; const auto&ST=I.ST[r]; int ns=ST.size(); if(ns<2) continue; int mask=0; for(auto&st:ST) mask|=1<<SDIM[st.f];
    size_t ti=0; const auto&TO=I.TOUCH[r];
    for(int j=0;j<ns;j++){ const Stop&st=ST[j]; while(ti<TO.size()&&TO[ti]<st.a) ti++; if(fixedStop(r,j,ns)) continue;
      int n=0,dl=0; bool blk=false; vector<Excl> ex={{r,st.a,st.b}};
      for(size_t k=ti;k<TO.size()&&TO[k]<=st.b;k++){ const Ev&e=S.P[TO[k]]; if(e.k!='A'){ blk=true; break; } n++; }
      if(blk||!n) continue;
      for(size_t k=ti;k<TO.size()&&TO[k]<=st.b;k++){ long i=TO[k]; const Ev&e=S.P[i]; int vs=verAt(I,e.s,i); if(vs<0) continue; V3 t=scaleV(I.VR[e.s][vs].v,e.c); int wa,wb; dWin(I,e.d,i,wa,wb);
        vector<Cand> c1; findSources(I,t,e.d,wa,wb,ex,c1,1); if(!c1.empty()) dl++; else if(ready&&!D) break; }
      double sj=taxMask(mask)-taxMask(mask&~(1<<SDIM[st.f])); int dj=n-dl; if(!dj&&ready) ready->push_back({r,st.f}); if(D){ if(!dj) D[0]+=sj; if(dj==1) D[1]+=sj; D[2]+=sj*pow(.1,dj); D[3]+=dl*.01; } } }
  RSEED=sv; }
static void phiInit(PhiCtx&P,const State&S,const Res&R,const Index&I){
  if(getenv("K2S_FLOG")){ P.flog=fopen(getenv("K2S_FLOG"),"w"); if(getenv("K2S_FLOGN")) P.fevery=max(1L,atol(getenv("K2S_FLOGN"))); }
  if(getenv("K2S_FSNAP")){ P.snap=atol(getenv("K2S_FSNAP")); P.snapPre=getenv("K2S_FSNAPPRE")?getenv("K2S_FSNAPPRE"):(getenv("K2S_OUT")?getenv("K2S_OUT"):"phi.net"); }
  if(getenv("K2S_PHIP")) P.p=atof(getenv("K2S_PHIP")); if(getenv("K2S_PHILA")) P.la=max(0L,atol(getenv("K2S_PHILA"))); if(getenv("K2S_PHILAN")) P.lan=atoi(getenv("K2S_PHILAN"));
  if(getenv("K2S_PHISEG")) P.seg=max(0L,atol(getenv("K2S_PHISEG"))); if(getenv("K2S_PHISEGTAU")) P.segTau=atof(getenv("K2S_PHISEGTAU"));
  if(getenv("K2S_PHISEGW")){ const char*q=getenv("K2S_PHISEGW"); for(int k=0;k<NDEL&&*q;k++){ P.segW[k]=atof(q); while(*q&&*q!=',') q++; if(*q) q++; } }
  if(getenv("K2S_PHIW")){ const char*q=getenv("K2S_PHIW"); for(int k=0;k<NPHI&&*q;k++){ P.w[k]=atof(q); while(*q&&*q!=',') q++; if(*q) q++; } }
  P.on=getenv("K2S_PHI")&&atoi(getenv("K2S_PHI"))!=0; if(getenv("K2S_PHITAU")) P.tau=atof(getenv("K2S_PHITAU")); if(getenv("K2S_PHIA")) P.a=atof(getenv("K2S_PHIA"));
  if(!(P.tau>0)&&!(P.a>0)) P.on=false; P.tie=P.on&&P.tau>0;
  P.c=.02364*R.kap*R.kap*1e7;
  phiFeat(S,R.nev,R.R0,P.p,P.F); P.phi=phiOf(P,P.F);
  printf("PHI on=%d tau %g a %g la %ld p %g c %.4f w",(int)P.on,P.tau,P.a,P.la,P.p,P.c); for(int k=0;k<NPHI;k++) printf(" %g",P.w[k]); printf(" | F"); for(int k=0;k<NPHI;k++) printf(" %.6f",P.F[k]); printf(" Phi %.6f",P.phi); { double D[NDEL]; phiDeliv(I,S,D); printf(" | D"); for(int k=0;k<NDEL;k++) printf(" %.6f",D[k]); } printf("\n"); fflush(stdout);
}
static void phiTick(PhiCtx&P,long it,const State&S,const Res&cur,const Index&I){
  if(P.flog&&it>=P.nlog){ P.nlog=(it/P.fevery+1)*P.fevery; if(!P.on){ phiFeat(S,cur.nev,cur.R0,P.p,P.F); } double D[NDEL]; phiDeliv(I,S,D);
    fprintf(P.flog,"%ld %.13f %.4f %ld",it,cur.kap,cur.R0,cur.nev); for(int k=0;k<NPHI;k++) fprintf(P.flog," %.6f",P.F[k]); for(int k=0;k<NDEL;k++) fprintf(P.flog," %.6f",D[k]); fprintf(P.flog,"\n"); fflush(P.flog); }
  if(P.snap>0&&it>=P.nsnap){ P.nsnap=(it/P.snap+1)*P.snap; char b[1024]; snprintf(b,sizeof b,"%s.snap%ld",P.snapPre.c_str(),it); dumpNet(S,b,cur); }
}
// (c) READY-KILL look-ahead (K2S_PHILA=every; K2S_PHILAN = max kills tried per refresh, default 64).  Every `every` its: list the stops whose rung kill is plannable NOW
// (d_j = 0, phiDeliv), plan each kill, verify it exactly (verifyInc), and take it ONLY if it raises exact kappa (greedy look-ahead on the one-step value).
// Rejected look-aheads restore the RNG and leave S untouched, so the run is bit-identical to the blind run until the look-ahead first fires an improvement.
// Rationale (MEASURED, h1 seed 501): the twin rung became kill-ready at it ~16.4k, blind SA proposed it at 24.1k (a blind kill picks one of ~3800 stops uniformly).
static bool phiLookahead(PhiCtx&P,long it,Index&I,State&S,Res&cur,State&best,Res&bestR,FILE*lg){
  P.nla=it+P.la; u64 sv=RSEED; P.q.clear(); phiDeliv(I,S,nullptr,&P.q); P.nref++; P.nready+=P.q.size(); bool took=false; int tried=0;
  if(P.missK!=cur.obj){ P.miss.clear(); P.missK=cur.obj; }   // cache of non-improving kills: the kill's kappa change depends on r's chain and the global invoice only
  for(auto&rf:P.q){ if(tried>=P.lan) break; int r=rf.first; int j=-1; u64 key=(u64)r*1000003ULL+(u64)rf.second; for(int k=0;k<(int)I.ST[r].size();k++){ key=key*1315423911ULL+(u64)I.ST[r][k].f; if(I.ST[r][k].f==rf.second) j=k; } if(j<0) continue;
    if(P.miss.count(key)){ P.nskip++; continue; }
    Edit E; if(!mvKill(I,S,E,r,j)) continue; tried++; P.nforced++; State T=applyEdit(S,E); cleanup(T); if(!FREEB&&(long)T.P.size()>=CAP) continue; Res Q=verifyInc(T,S,I,cur);
    if(!Q.ok||Q.obj<=cur.obj+1e-14){ if(Q.ok) P.miss.insert(key); continue; }
    TENT=-1; SCLEAN=true; S.P.swap(T.P); S.init.swap(T.init); cur=Q; buildIndex(S,I); GDIRTY=true; took=true; P.ntook++; if(P.on){ phiFeat(S,cur.nev,cur.R0,P.p,P.F); P.phi=phiOf(P,P.F); }
    if(cur.obj>bestR.obj+1e-14){ best=S; bestR=cur; if(lg){ fprintf(lg,"%ld lookahead kappa %.13f R0 %.4f nev %ld nhel %ld T 0\n",it,cur.kap,cur.R0,cur.nev,cur.nhel); fflush(lg); } }
    break; }   // the stop list is stale after an accepted kill: refresh next time
  if(!took) RSEED=sv; return took; }
// (d) SEGMENT tie-break on DELIVERY READINESS (K2S_PHISEG=L its, K2S_PHISEGTAU=tau, K2S_PHISEGW=w over D0..D3, default D2 = sum s_j .1^d_j).
// Phi_D needs the Index of the state, which only accepted states have, so the tie-break acts on SEGMENTS: every L its, if exact kappa did not change over the segment
// and Phi_D fell, the segment is undone with probability 1 - exp(dPhi/tau) (state and index restored to the segment start).  Segments that changed kappa are always kept,
// so true optima are untouched; best is tracked on exact kappa as always.
static double phiSegVal(PhiCtx&P,const Index&I,const State&S){ double D[NDEL]; phiDeliv(I,S,D); double v=0; for(int k=0;k<NDEL;k++) v+=P.segW[k]*D[k]; return v; }
static bool phiSegment(PhiCtx&P,long it,Index&I,State&S,Res&cur){
  P.nseg=it+P.seg; double v=phiSegVal(P,I,S); bool rev=false; P.segN++;
  if(P.hasAnc&&cur.obj==P.ancR.obj&&v<P.segPhi&&urand()>=exp((v-P.segPhi)/P.segTau)){ S=P.anc; cur=P.ancR; TENT=-1; SCLEAN=true; buildIndex(S,I); GDIRTY=true; v=P.segPhi; rev=true; P.segRev++;
    if(P.on){ phiFeat(S,cur.nev,cur.R0,P.p,P.F); P.phi=phiOf(P,P.F); } }
  if(!rev){ P.anc=S; P.ancR=cur; P.segPhi=v; P.hasAnc=true; }
  return rev; }
