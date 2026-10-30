// k2levers.inc -- K2LEVERS lane (toolkit/module docstring): the generator levers LATE BIRTH and EARLY END as k2 engine move families.  Included by k2search.inc before propose().
// Both are single atomic Edits; every proposal still goes through cleanup + the full (incremental) verifier (frame law, nesting, contract by random evaluation, budgets), so legality is CHECKED,
// and the plans are value-exact by construction where stated.
// move 'lbirth' (K2S_W slot 19): helper h whose first kk stops (kk>=1) hold only READS of its pure version (value e_h; the dim-0 junk loads z += c*h of JOINTFRAMES' rank criterion)
//   is born at G = frame of its stop kk (init := G, MOVEs into stops 1..kk removed).  Every evacuated read z += c*h moves to a gap where h is still pure (before its first write), inside z's
//   write window, with z at G: an existing stop of z at G, or a NEW stop of z at G inserted after z's last event of its current stop (F_z < G < F_next, the Y visit of ylate), or (fallback)
//   re-delivered from another holder (planDeliver).  Value-exact: z receives the same content c*e_h, inside its write window.
// move 'eend' (K2S_W slot 20): helper h ends at its stop j (1 <= j <= ns-2): all later MOVEs/writes of h are deleted, later READS of h are re-delivered from other holders (planDeliver, h excluded),
//   and the deviation e_h - val(h) is cancelled into h at G = frame of stop j after h's last read there (h now stays at G to the end of the program): one holder, a two-term
//   cancellation, an X-main stop inserted at G (X window F_x < G < F_next, the PUREX X split), or a per-write Bennett uncompute (each write h += c*s undone from a holder of c*s).
//   This is the LOCAL end-early; the joint dim-0 junk solve of PUREX (purex2) rewrites the whole dim-0 block and is the python macro move k2/levers.py (route-B words only).
static long LVS[12]={0}; static int LVH=-1, LVJ=-1;   // K2S_LVSEED=h,j forces the register/stop of both families (diagnostics, tests)   // diagnostics: lbirth proposals, planned, moved-in-place, z-stop inserts, fallback deliveries | eend proposals, planned, single, two-term, X-stop, Bennett, reader re-deliveries
static const char*LVN[12]={"lb_prop","lb_plan","lb_place","lb_zins","lb_deliv","ee_prop","ee_plan","ee_one","ee_two","ee_xstop","ee_bennett","ee_redeliv"};
// last event of register r in [a,b) not in the removal set
static int lastTouch(const Index&I,int r,int a,int b,const vector<char>&rm){ int L=-1; const auto&T=I.TOUCH[r]; for(auto it=lower_bound(T.begin(),T.end(),a);it!=T.end()&&*it<b;++it) if(!rm[*it]) L=*it; return L; }
static bool mvLbirth(const Index&I,const State&S,Edit&E,int h=-1,int kk=-1){
  if(h<0&&LVH>=0){ h=LVH; kk=LVJ; }
  if(h<0){ for(int t=0;;t++){ if(t>64) return false; h=rnd(S.init.size()); if(ROLE[h]=='H'&&I.ST[h].size()>=3) break; } }
  LVS[0]++;
  if(ROLE[h]!='H'||I.VR[h].empty()) return false; const auto&STh=I.ST[h]; int ns=STh.size(); if(ns<3) return false;
  const Ver V=I.VR[h][0]; if(V.v!=V0[h]) return false;                                   // pure version e_h
  int kmax=0; for(int k=0;k<ns-2;k++){ const Stop&st=STh[k]; bool ok=true; for(int i:I.TOUCH[h]){ if(i<st.a) continue; if(i>st.b) break; const Ev&e=S.P[i]; if(e.k!='A'||e.s!=h){ ok=false; break; } } if(!ok) break; kmax=k+1; }
  if(kmax<1) return false; if(kk<1||kk>kmax) kk=1+rnd(kmax);
  int G=STh[kk].f; long n=S.P.size();
  vector<int> evs,mvs; for(int k=0;k<kk;k++){ const Stop&st=STh[k]; for(int i:I.TOUCH[h]){ if(i<st.a) continue; if(i>st.b) break; evs.push_back(i); } }
  for(int k=1;k<=kk;k++){ int mi=STh[k].a-1; if(mi<0||S.P[mi].k!='M'||S.P[mi].d!=h) return false; mvs.push_back(mi); }
  if(evs.size()>256) return false;
  vector<char> rm(n+1,0); for(int i:evs) rm[i]=1; for(int i:mvs) rm[i]=1;
  long pb=min((long)V.b,(long)STh[kk].b);                                                  // h pure and at G on gaps [0, pb] of the new program
  // temporary index view: h sits at G from gap 0 to the end of stop kk
  Index&IM=const_cast<Index&>(I); StGuard GD(IM.ST[h]); { vector<Stop> v; Stop x=STh[kk]; x.a=0; v.push_back(x); for(int k=kk+1;k<ns;k++) v.push_back(STh[k]); IM.ST[h]=v; }
  E.rem.clear(); E.ins.clear(); map<int,int> zins;                                             // z -> gap of its inserted MOVE z->G
  for(int i:evs){ const Ev&e=S.P[i]; int z=e.d; int wa,wb; dWin(I,z,i,wa,wb); int a=max(wa,0), b=(int)min((long)wb,pb); if(a>b) return false;
    // (1) z already sits at G inside [a,b]
    { int fo; int g=coloc(IM,z,h,a,b,{},&fo); if(g>=0&&fo==G){ E.ins.push_back({g,{'A',z,h,G,e.c}}); LVS[2]++; continue; } }
    // (2) z's inserted stop (this move) or a new stop of z at G after z's last event of its current stop
    if(ROLE[z]!='O'){ auto f=zins.find(z); bool done=false;
      if(f!=zins.end()){ if(f->second>=a&&f->second<=b){ E.ins.push_back({f->second,{'A',z,h,G,e.c}}); done=true; } }
      else { const auto&STz=I.ST[z]; int nz=STz.size(); vector<int> ks; for(int k=max(0,stopAt(I,z,a));k<nz;k++){ if(STz[k].a>b) break; if(STz[k].b<a) continue; ks.push_back(k); }
        for(size_t q=0;q<ks.size()&&!done;q++){ int k=ks[rnd(ks.size())]; const Stop&sz=STz[k]; if(k+1>=nz) continue; if(!psub(sz.f,G)||!psub(G,STz[k+1].f)) continue;
          int lt=lastTouch(I,z,sz.a,sz.b,rm); int g1=max(max(a,sz.a),lt+1); if(g1>min(b,sz.b)) continue;
          zins[z]=g1; E.ins.push_back({g1,{'M',z,0,G,{0,0}}}); E.ins.push_back({g1,{'A',z,h,G,e.c}}); LVS[3]++; done=true; } }
      if(done){ LVS[2]++; continue; } }
    // (3) fallback: another holder of c*e_h (h itself excluded outside the view)
    { vector<Ins> o; int nt; vector<Excl> ex={{h,(int)pb+1,(int)n}}; if(zins.count(z)) return false; if(!planDeliver(IM,S,i,ex,true,4,o,&nt)) return false; for(auto&x:o) E.ins.push_back(x); LVS[4]++; } }
  for(int i:evs) E.rem.push_back(i); for(int i:mvs) E.rem.push_back(i); E.initCh.push_back({h,G}); E.tag="lbirth"; LVS[1]++; return true; }
static bool propVer(const V3&t,const V3&v,Co*c){ if(vzero(v)) return false; u64 lam; if(v[0]){ lam=mmul(t[0],minv(v[0])); } else if(v[1]){ if(t[0]) return false; lam=mmul(t[1],minv(v[1])); } else { if(t[0]||t[1]) return false; lam=mmul(t[2],minv(v[2])); }
  for(int k=0;k<KV;k++) if(mmul(v[k],lam)!=t[k]) return false; auto dy=DY.find(lam); if(dy==DY.end()||!coOK(dy->second)) return false; *c=dy->second; return true; }
static int EEMAXR=64, EEDBG=0, EEXR=4; static long LVHB=0;
static bool mvEend(const Index&I,const State&S,Edit&E,int h=-1,int j=-1){
  if(h<0&&LVH>=0){ h=LVH; j=LVJ; }
  if(h<0){ for(int t=0;;t++){ if(t>64) return false; h=rnd(S.init.size()); if(ROLE[h]=='H'&&I.ST[h].size()>=3) break; } }
  LVS[5]++;
  if(ROLE[h]!='H') return false; const auto&STh=I.ST[h]; int ns=STh.size(); if(ns<3) return false; if(j<1||j>ns-2) j=1+rnd(ns-2);
  int G=STh[j].f; long n=S.P.size(); const Stop stj=STh[j];
  vector<int> rem,reads; for(int k=j+1;k<ns;k++){ int mi=STh[k].a-1; if(mi<0||S.P[mi].k!='M'||S.P[mi].d!=h) return false; rem.push_back(mi); }
  for(int i:I.TOUCH[h]){ if(i<=stj.b) continue; const Ev&e=S.P[i]; if(e.k=='A'&&e.d==h){ rem.push_back(i); continue; } if(e.k=='S'&&e.d==h){ rem.push_back(i); continue; } if(e.k=='A'&&e.s==h){ reads.push_back(i); continue; } return false; }
  if((int)reads.size()>EEMAXR) return false;
  int vs=verAt(I,h,stj.b); if(vs<0) return false; V3 t=subV(V0[h],I.VR[h][vs].v);
  // cleanup window: after h's last barrier (read/scale) in stop j, to the end of the program (h stays at G)
  int wa,wb; dWin(I,h,stj.b,wa,wb); int a=max(wa,stj.a), b=(int)n;
  Index&IM=const_cast<Index&>(I); StGuard GD(IM.ST[h]); { vector<Stop> v(STh.begin(),STh.begin()+j+1); v.back().b=(int)n; IM.ST[h]=v; }
  vector<Ins> ins; vector<Excl> exR={{h,stj.a,(int)n}};
  // readers after stop j: the same content from another holder
  for(int i:reads){ int nt; if(!planDeliver(IM,S,i,exR,true,8,ins,&nt)) return false; LVS[11]++; }
  if(EEDBG){ long np=0; for(int k=0;k<KV;k++) np+=t[k]!=0; vector<Cand> c; findSources(IM,t,h,0,(int)n,{},c,4); printf("EEDBG h %d j %d/%d dim %d reads %zu ok, dev-zero %d, holders(any gap, co-located) %zu, window [%d,%ld) stop [%d,%d]",h,j,ns,SDIM[G],reads.size(),(int)vzero(t),c.size(),a,n,stj.a,stj.b); for(auto&q:c) printf(" holder %d(%c) gap %d f %d",q.s,ROLE[q.s],q.g,q.f); printf(" | h barriers in stop:"); for(int i:I.BAR[h]) if(i>=stj.a&&i<=stj.b) printf(" %d:%c->%d",i,S.P[i].k,S.P[i].d); printf("\n"); }
  bool done=vzero(t);
  if(!done){ vector<Cand> c; findSources(IM,t,h,a,b,{},c,16); if(!c.empty()){ auto&q=c[rnd(c.size())]; ins.push_back({q.g,{'A',h,q.s,q.f,q.c}}); done=true; LVS[7]++; } }
  if(!done){ // hop-back: cancel EARLIER (before up to EEXR reads of h in stop j); each crossed reader r += c*h then receives c*(e_h - v) too, compensated by r -= c*(e_h - v) from a holder in r's window
    vector<Ins> comp; int jx=a-1;
    for(int k=0;k<EEXR&&!done;k++){ if(jx<stj.a) break; const Ev&x=S.P[jx]; if(x.k!='A'||x.s!=h||x.d==h||ROLE[x.d]=='O') break; int r2=x.d;
      V3 t2=scaleV(t,x.c); for(auto&y:t2) y=y?PM-y:0; int ra,rb; dWin(I,r2,jx,ra,rb); vector<Cand> c2; findSources(IM,t2,r2,ra,rb,{},c2,16); vector<Cand> ok2; for(auto&z:c2) if(z.s!=h) ok2.push_back(z); if(ok2.empty()) break;
      auto z=ok2[rnd(ok2.size())]; comp.push_back({z.g,{'A',r2,z.s,z.f,z.c}});
      int pa,pb; dWin(I,h,jx,pa,pb); pa=max(pa,stj.a); vector<Cand> c; findSources(IM,t,h,pa,jx,{},c,16);
      if(!c.empty()){ auto&q=c[rnd(c.size())]; ins.push_back({q.g,{'A',h,q.s,q.f,q.c}}); for(auto&y:comp) ins.push_back(y); done=true; LVS[7]++; LVHB++; break; }
      jx=pa-1; } }
  if(!done){ // two-term: one co-located register (any coefficient of CSET), the rest from a holder
    vector<array<int,4>> pool; for(auto&o:IM.OCC[G]){ int r=o[0]; if(r==h) continue; int A=max(a,o[1]),B=min(b,o[2]); if(A>B) continue; int v=verAt(I,r,A); for(;v>=0&&v<(int)I.VR[r].size()&&I.VR[r][v].a<=B;v++){ if(vzero(I.VR[r][v].v)) continue; pool.push_back({r,v,max(A,I.VR[r][v].a),min(B,I.VR[r][v].b)}); } }
    for(int tr=0;tr<24&&!pool.empty()&&!done;tr++){ auto&p=pool[rnd(pool.size())]; Co cc=CSET[rnd(10)]; V3 rest=subV(t,scaleV(I.VR[p[0]][p[1]].v,cc)); if(vzero(rest)) continue;
      vector<Cand> c2; findSources(IM,rest,h,a,b,{},c2,8); if(c2.empty()) continue; auto&q=c2[rnd(c2.size())]; if(q.s==p[0]) continue;
      int g1=p[2]+rnd(p[3]-p[2]+1); ins.push_back({g1,{'A',h,p[0],G,cc}}); ins.push_back({q.g,{'A',h,q.s,q.f,q.c}}); done=true; LVS[8]++; } }
  if(!done){ // X-main stop at G: X x with F_x < G < F_next, after x's last event of its stop; its value (alone, or plus one holder) cancels the deviation
    vector<char> rm0(n+1,0); vector<int> xs; for(int r=0;r<(int)S.init.size();r++) if(ROLE[r]=='X') xs.push_back(r);
    for(size_t q=0;q<xs.size();q++) swap(xs[q],xs[q+rnd(xs.size()-q)]);
    for(int x:xs){ if(done) break; const auto&STx=I.ST[x]; int nx=STx.size();
      for(int k=max(0,stopAt(I,x,a));k+1<nx&&!done;k++){ const Stop&sx=STx[k]; if(sx.b<a) continue; if(!psub(sx.f,G)||!psub(G,STx[k+1].f)) continue;
        int lt=lastTouch(I,x,sx.a,sx.b,rm0); int g1=max(max(a,sx.a),lt+1); if(g1>min(b,sx.b)) continue; int vx=verAt(I,x,g1); if(vx<0) continue; const V3&xv=I.VR[x][vx].v;
        Co cc; if(propVer(t,xv,&cc)){ ins.push_back({g1,{'M',x,0,G,{0,0}}}); ins.push_back({g1,{'A',h,x,G,cc}}); done=true; LVS[9]++; break; }
        for(int tr=0;tr<10&&!done;tr++){ Co c1=CSET[tr]; V3 rest=subV(t,scaleV(xv,c1)); if(vzero(rest)) continue; vector<Cand> c2; findSources(IM,rest,h,a,b,{},c2,8); vector<Cand> ok; for(auto&z:c2) if(z.s!=x) ok.push_back(z); if(ok.empty()) continue;
          auto&z=ok[rnd(ok.size())]; ins.push_back({g1,{'M',x,0,G,{0,0}}}); ins.push_back({g1,{'A',h,x,G,c1}}); ins.push_back({z.g,{'A',h,z.s,z.f,z.c}}); done=true; LVS[9]++; } } } }
  if(!done){ // Bennett: undo every write into h (before the end of stop j) from a holder of its content; no SCALE of h allowed
    for(int i:I.BAR[h]) if(i<=stj.b&&S.P[i].k=='S'&&S.P[i].d==h) return false;
    vector<Ins> o; bool ok=true; for(int i:I.WR[h]){ if(i>stj.b) break; const Ev&e=S.P[i]; if(e.k!='A'){ ok=false; break; } int v2=verAt(I,e.s,i); if(v2<0){ ok=false; break; } V3 tw=scaleV(I.VR[e.s][v2].v,e.c); for(auto&x:tw) x=x?PM-x:0;
      vector<Cand> c; findSources(IM,tw,h,a,b,{},c,8); if(c.empty()){ ok=false; break; } auto&q=c[rnd(c.size())]; o.push_back({q.g,{'A',h,q.s,q.f,q.c}}); if(o.size()>64){ ok=false; break; } }
    if(ok&&!o.empty()){ for(auto&x:o) ins.push_back(x); done=true; LVS[10]++; } }
  if(!done) return false;
  for(int i:reads) rem.push_back(i);
  E.rem=rem; E.ins=ins; E.tag="eend"; LVS[6]++; return true; }
