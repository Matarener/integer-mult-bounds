// SA search: closed cycle of K points in F2^N, consecutive (cyclic) Hamming distance 1 or 2,
// maximize |P+P| coverage; then report W = sum of distances.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#define N 7
#define M (1<<N)
static uint64_t s=88172645463325252ULL;
static inline uint64_t rnd(){ s^=s<<13; s^=s>>7; s^=s<<17; return s; }
static inline int wt(int x){ return __builtin_popcount(x); }
int K, WMAX; int P[64]; int cnt[M]; int cov;
static int ok(int d){ int w=wt(d); return w==1||w==2; }
static int W(){ int t=0; for(int i=0;i<K;i++) t+=wt(P[i]^P[(i+1)%K]); return t; }
static void add(int i,int sg){ for(int j=0;j<K;j++) if(j!=i){ int d=P[i]^P[j]; if(sg>0){ if(cnt[d]++==0) cov++; } else { if(--cnt[d]==0) cov--; } } }
int main(int argc,char**argv){
  K=atoi(argv[1]); WMAX=atoi(argv[2]); s^=strtoull(argv[3],0,10)*0x9E3779B97F4A7C15ULL; long iters=atol(argv[4]); int restarts=atoi(argv[5]);
  for(int r=0;r<restarts;r++){
    // init: random cycle by random walk then fix closure greedily: just random points with valid edges via repeated tries
    P[0]=0; for(int i=1;i<K;i++){ int q; do{ q=P[i-1]^(1<<(rnd()%N)); if(rnd()&1) q^=1<<(rnd()%N);}while(q==P[i-1]); P[i]=q; }
    // closure may be invalid: treat invalid edges as penalty
    for(int d=0;d<M;d++) cnt[d]=0; cov=1; cnt[0]=1; for(int i=0;i<K;i++) for(int j=i+1;j<K;j++){ int d=P[i]^P[j]; if(cnt[d]++==0) cov++; }
    double T=2.0;
    #define BAD() ({int b=0; for(int i=0;i<K;i++) if(!ok(P[i]^P[(i+1)%K])) b++; b;})
    double score; int bad=BAD(); int w=W();
    score = cov - 4.0*bad - 2.0*(w>WMAX? w-WMAX:0);
    for(long it=0;it<iters;it++){
      T = 2.0*pow(0.02/2.0,(double)it/iters);
      int i=1+rnd()%(K-1); int old=P[i]; int q;
      int mv=rnd()%3;
      if(mv==0) q=old^(1<<(rnd()%N)); else if(mv==1) q=old^(1<<(rnd()%N))^(1<<(rnd()%N)); else q=P[i-1]^(1<<(rnd()%N))^((rnd()&1)?(1<<(rnd()%N)):0);
      if(q==old) continue;
      int a=P[i-1], b=P[(i+1)%K];
      int dbad = (!ok(q^a))+(!ok(q^b)) - (!ok(old^a)) - (!ok(old^b));
      int dw = wt(q^a)+wt(q^b)-wt(old^a)-wt(old^b);
      int oc=cov; add(i,-1); P[i]=q; add(i,1);
      int nb=bad+dbad, nw=w+dw;
      double ns = cov - 4.0*nb - 2.0*(nw>WMAX? nw-WMAX:0);
      if(ns>=score || exp((ns-score)/T) > (rnd()%1000000)/1e6){ score=ns; bad=nb; w=nw; }
      else { add(i,-1); P[i]=old; add(i,1); }
      if(cov==M && bad==0 && w<=WMAX){
        printf("FOUND K=%d W=%d :",K,w); for(int j=0;j<K;j++) printf(" %d",P[j]); printf("\n"); fflush(stdout); return 0; }
      (void)oc;
    }
  }
  printf("NONE K=%d WMAX=%d\n",K,WMAX); return 1;
}
