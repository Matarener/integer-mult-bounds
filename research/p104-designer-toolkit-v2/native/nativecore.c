/* nativecore.c -- C replay kernel for incr.IncrWord._run (NATIVECORE; notes ../module docstring).
 * Line-for-line port of IncrWord._run (itself a copy of infra/legal.check's event loop).  Exact integer arithmetic only (mod 2^61-1 via __int128).
 * State blob layout (little endian, NR registers, K=2 value vectors):  cur int32[NR] (INT32_MIN = None) | owned uint8[NR] | pad to 8 | val uint64[K][NR].
 * Violation record = 4 x int32: (event index, code, cur[r] or cur[s] as seen by the check, 0).  Codes -> rule names live in nincr.py.
 * Return: 0 ok;  -1 frame index out of range (Python IndexError);  -2 violation buffer full. */
#include <stdint.h>
#include <string.h>
#define PM ((1ULL<<61)-1)
#define NONE ((int32_t)INT32_MIN)
#define KV 2
typedef unsigned __int128 u128;
typedef struct { int32_t op,r,s,a,b,pv,f,ci; } Ev;
typedef struct { uint64_t qm; int64_t cs,ca; uint8_t zero,dy,grow,unit,_p[4]; } Coef;
enum { OP_MOVE=0,OP_INIT,OP_CLEAR,OP_SCALE,OP_COPY,OP_ADD,OP_OTHER };
enum { V_ROLE=0,V_SRC,V_NEST,V_OINIT,V_OERASE,V_DEST,V_DYAD,V_GROW,V_UNIT,V_CHART,V_COPY,V_OPC };
static inline uint64_t red(u128 x){ uint64_t t=(uint64_t)(x&PM)+(uint64_t)(x>>61); t=(t&PM)+(t>>61); if(t>=PM) t-=PM; return t; }
long nc_state_size(int NR){ long o=4L*NR+NR; o=(o+7)&~7L; return o+8L*KV*NR; }
static inline int rsv(int f,int nf){ if(f<0) f+=nf; return (f<0||f>=nf)?-1:f; }
/* proper subset A<B of 512-bit sets */
static inline int psub(const uint64_t*A,const uint64_t*B){ int ne=0; for(int i=0;i<8;i++){ if(A[i]&~B[i]) return 0; if(A[i]!=B[i]) ne=1; } return ne; }
int nc_run(int NR,const uint8_t*own,int nf,const uint64_t*span,const int32_t*dim,const Ev*ev,int nev,const Coef*ct,
           const uint8_t*st_in,uint8_t*st,int32_t*viol,int vcap,int*nviol,int64_t*out)
{
  long sz=nc_state_size(NR); memcpy(st,st_in,sz);
  int32_t*cur=(int32_t*)st; uint8_t*owned=st+4L*NR; long vo=(4L*NR+NR+7)&~7L; uint64_t*val=(uint64_t*)(st+vo);
  int cnt=0; for(int r=0;r<NR;r++) cnt+=owned[r]!=0;
  int64_t paid[16]; memset(paid,0,sizeof paid); int64_t scalar=0,life=0,peak=0; int nv=0;
#define VIOL(I,C,X) do{ if(nv>=vcap) return -2; viol[4*nv]=(I); viol[4*nv+1]=(C); viol[4*nv+2]=(X); viol[4*nv+3]=0; nv++; }while(0)
  for(int i=0;i<nev;i++){
    const Ev*e=&ev[i]; int r=e->r;
    if(!(0<=r&&r<NR)){ VIOL(i,V_ROLE,0); continue; }
    switch(e->op){
    case OP_MOVE:{
      int a=e->a,b=e->b,pv=e->pv!=0;
      if(cur[r]!=a || ((owned[r]!=0)!=pv)) VIOL(i,V_SRC,cur[r]);
      int ia=rsv(a,nf),ib=rsv(b,nf); if(ia<0||ib<0) return -1;
      int ok=pv? psub(span+8L*ib,span+8L*ia) : psub(span+8L*ia,span+8L*ib);
      if(!ok) VIOL(i,V_NEST,0);
      int k=dim[ib]-dim[ia]; if(k<0)k=-k; if(k>15) return -3; paid[k]++; cur[r]=b; break; }
    case OP_INIT:
      if(!(own[r] && !owned[r])) VIOL(i,V_OINIT,0);
      life++; if(!owned[r]){ owned[r]=1; cnt++; } if(cnt>peak) peak=cnt;
      for(int k=0;k<KV;k++) val[(long)k*NR+r]=0;
      cur[r]=e->f; scalar+=2; break;
    case OP_CLEAR:
      if(!(owned[r] && cur[r]==e->f)) VIOL(i,V_OERASE,0);
      for(int k=0;k<KV;k++) val[(long)k*NR+r]=0;
      cur[r]=NONE; if(owned[r]){ owned[r]=0; cnt--; } scalar+=2; break;
    default:{
      const Coef*c=&ct[e->ci]; int f=e->f;
      if(c->zero || cur[r]!=f){ VIOL(i,V_DEST,cur[r]); continue; }
      if(c->dy) VIOL(i,V_DYAD,0);
      if(c->grow) VIOL(i,V_GROW,0);
      if(e->op==OP_SCALE){
        if(c->unit) VIOL(i,V_UNIT,0);
        for(int k=0;k<KV;k++){ uint64_t*x=&val[(long)k*NR+r]; *x=red((u128)*x*c->qm); }
        scalar+=c->cs;
      } else {
        int s=e->s;
        if(!(s!=r && 0<=s && s<NR && cur[s]==f)){ VIOL(i,V_CHART,(0<=s&&s<NR)?cur[s]:NONE); continue; }
        if(e->op==OP_COPY){
          if(!(owned[r] && val[r]==0 && val[(long)NR+r]==0)) VIOL(i,V_COPY,0);
          for(int k=0;k<KV;k++) val[(long)k*NR+r]=red((u128)val[(long)k*NR+s]*c->qm);
        } else if(e->op==OP_ADD){
          for(int k=0;k<KV;k++) val[(long)k*NR+r]=red((u128)val[(long)k*NR+r]+(u128)c->qm*val[(long)k*NR+s]);
        } else { VIOL(i,V_OPC,0); continue; }
        scalar+=c->ca;
      } }
    }
  }
  *nviol=nv; for(int k=0;k<16;k++) out[k]=paid[k]; out[16]=scalar; out[17]=life; out[18]=peak;
  return 0;
}
