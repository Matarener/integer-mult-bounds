// independent count of label-spanned subspaces of F2^9 by dimension: enumerate ALL subspaces via RREF, test span(labels inside)==subspace
#include <stdio.h>
#include <stdlib.h>
int lab[112], islab[512];
long cnt[10];
int B[9];
static int rankv(int *v,int m){int b[9],r=0;for(int i=0;i<m;i++){int x=v[i];for(int j=0;j<r;j++){if((x^b[j])<x)x^=b[j];}if(x){b[r++]=x;// keep reduced
 for(int j=0;j<r-1;j++){} }}return r;}
void test(int d){ // B[0..d-1] rref basis
  int mem[512];int m=1;mem[0]=0;
  for(int i=0;i<d;i++){for(int j=0;j<m;j++)mem[m+j]=mem[j]^B[i];m*=2;}
  int L[512],k=0;for(int j=0;j<m;j++)if(islab[mem[j]])L[k++]=mem[j];
  // rank of labels inside (greedy basis with min-reduction)
  int b[9],r=0;for(int i=0;i<k;i++){int x=L[i];for(int j=0;j<r;j++){if((x^b[j])<x)x^=b[j];}
    if(x){ // insert keeping elements reduced w.r.t. top bits: simple approach: re-reduce all
      b[r++]=x; for(int a=0;a<r;a++)for(int c=0;c<r;c++)if(a!=c){int hb=31-__builtin_clz(b[c]); if((b[a]>>hb)&1) b[a]^=b[c];}
    }}
  if(r==d)cnt[d]++;
}
// enumerate RREF: choose pivot set P (increasing bit positions), free entries in non-pivot positions below each pivot
void rec(int d,int target,int minpiv){
  if(d==target){test(d);return;}
}
int main(){FILE*f=fopen("labels.txt","r");for(int i=0;i<112;i++){fscanf(f,"%d",&lab[i]);islab[lab[i]]=1;}
  for(int d=0;d<=9;d++){
    // iterate pivot subsets of size d of {0..8}
    for(int P=0;P<512;P++){ if(__builtin_popcount(P)!=d)continue;
      int piv[9],np=0;for(int i=0;i<9;i++)if(P>>i&1)piv[np++]=i;
      // row i has leading bit piv[i] (highest set bit), free bits: positions < piv[i] that are not pivots
      int fb[9][9],nf[9],tot=0;
      for(int i=0;i<d;i++){nf[i]=0;for(int j=0;j<piv[i];j++)if(!(P>>j&1))fb[i][nf[i]++]=j;tot+=nf[i];}
      for(long s=0;s<(1L<<tot);s++){long t=s;for(int i=0;i<d;i++){int v=1<<piv[i];for(int j=0;j<nf[i];j++){if(t&1)v|=1<<fb[i][j];t>>=1;}B[i]=v;}
        test(d);}
    }
    printf("dim %d label-spanned %ld\n",d,cnt[d]);fflush(stdout);
  }
}
