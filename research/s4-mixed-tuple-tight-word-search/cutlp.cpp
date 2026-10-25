// Enumerate all 2^24 coordinate cuts H of the regular S4-set; output distinct
// charge/profile vectors (c_s1,c_s2,c_s3,c_2143,c_3142,c_4231) with c_g(H)=#{x in H: g x notin H}.
#include <bits/stdc++.h>
using namespace std;
typedef array<int,4> P;
int main(){
  vector<P> el; P p={0,1,2,3}; do el.push_back(p); while(next_permutation(p.begin(),p.end()));
  map<P,int> idx; for(int i=0;i<24;i++) idx[el[i]]=i;
  auto comp=[&](const P&a,const P&b){P c; for(int i=0;i<4;i++) c[i]=a[b[i]]; return c;}; // (ab)(x)=a(b(x))
  auto parse=[&](const char*s){P q; for(int i=0;i<4;i++) q[i]=s[i]-'1'; return q;};
  const char* names[6]={"2134","1324","1243","2143","3142","4231"};
  // left-mult permutation tables, byte lookup
  static unsigned T[6][3][256];
  for(int k=0;k<6;k++){ P g=parse(names[k]); int perm[24]; for(int x=0;x<24;x++) perm[x]=idx[comp(g,el[x])];
    for(int b=0;b<3;b++) for(int v=0;v<256;v++){ unsigned m=0; for(int j=0;j<8;j++) if(v>>j&1) m|=1u<<perm[8*b+j]; T[k][b][v]=m; } }
  map<array<int,6>,long long> cnt;
  for(unsigned H=0; H<(1u<<24); H++){ array<int,6> c; for(int k=0;k<6;k++){ unsigned gH=T[k][0][H&255]|T[k][1][(H>>8)&255]|T[k][2][H>>16]; c[k]=__builtin_popcount(gH&~H);} cnt[c]++; }
  for(auto&kv:cnt){ for(int k=0;k<6;k++) printf("%d ",kv.first[k]); printf("%lld\n",kv.second);} 
}
