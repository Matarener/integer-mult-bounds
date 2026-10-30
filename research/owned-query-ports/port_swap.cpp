// SPDX-License-Identifier: Apache-2.0
// Dugongue; substantial OpenAI assistance. Discovery only, no new kappa.
#include <string>
#include <utility>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <queue>
#include <vector>
using namespace std;
using I=long long;
struct Dinic{struct E{int v,rev;I c;};vector<vector<E>>g;vector<int>lv,it;Dinic(int n):g(n),lv(n),it(n){} void add(int a,int b,I c){E x{b,(int)g[b].size(),c},y{a,(int)g[a].size(),0};g[a].push_back(x);g[b].push_back(y);} bool bfs(int s,int t){fill(lv.begin(),lv.end(),-1);queue<int>q;lv[s]=0;q.push(s);while(q.size()){int a=q.front();q.pop();for(auto&e:g[a])if(e.c&&lv[e.v]<0)lv[e.v]=lv[a]+1,q.push(e.v);}return lv[t]>=0;} I dfs(int a,int t,I f){if(a==t)return f;for(int&j=it[a];j<(int)g[a].size();++j){auto&e=g[a][j];if(e.c&&lv[e.v]==lv[a]+1){I z=dfs(e.v,t,min(f,e.c));if(z){e.c-=z;g[e.v][e.rev].c+=z;return z;}}}return 0;}void flow(int s,int t){while(bfs(s,t)){fill(it.begin(),it.end(),0);while(dfs(s,t,1LL<<55));}bfs(s,t);}};
int main(int argc,char**argv){if(argc!=3)return 2;ifstream in(argv[1]);int n,m,k;in>>n>>m>>k;vector<int>L(n),fixed(n);for(int i=0;i<n;++i)in>>L[i]>>fixed[i];vector<pair<int,int>>edges(m);for(auto&e:edges)in>>e.first>>e.second;vector<vector<int>>D(k,vector<int>(k));for(auto&r:D)for(auto&z:r)in>>z;vector<int>order;int z;while(in>>z)order.push_back(z);double p[10];for(int i=0;i<10;++i)p[i]=i?pow((double)i,.996979834):0.;auto score=[&](){double s=0;for(auto[a,b]:edges)s+=p[D[L[a]][L[b]]];return s;};double base=score();cout<<"baseline "<<base<<" nodes "<<n<<" edges "<<m<<endl;

vector<int>freq(k,0);for(int a:L)freq[a]++;vector<int>ls;for(int i=0;i<k;++i)if(freq[i])ls.push_back(i);sort(ls.begin(),ls.end(),[&](int a,int b){return freq[a]>freq[b];});if(ls.size()>70)ls.resize(70);
int tests=0,wins=0;
for(int ia=0;ia<(int)ls.size();++ia)for(int ib=ia+1;ib<(int)ls.size();++ib){int a=ls[ia],b=ls[ib];vector<int>mp(n,-1),vs;for(int i=0;i<n;++i)if(!fixed[i]&&(L[i]==a||L[i]==b)){mp[i]=vs.size();vs.push_back(i);}if(vs.empty())continue;int z=vs.size(),src=z,sink=z+1;Dinic f(z+2);vector<double>u(z,0.);double d=p[D[a][b]];for(auto[x,y]:edges){int xx=mp[x],yy=mp[y];if(xx>=0&&yy>=0){I cap=llround(d*1e8);f.add(xx,yy,cap);f.add(yy,xx,cap);}else if(xx>=0)u[xx]+=p[D[b][L[y]]]-p[D[a][L[y]]];else if(yy>=0)u[yy]+=p[D[b][L[x]]]-p[D[a][L[x]]];}for(int i=0;i<z;++i){if(u[i]>=0)f.add(i,sink,llround(u[i]*1e8));else f.add(src,i,llround(-u[i]*1e8));}f.flow(src,sink);auto old=L;double before=score();for(int i=0;i<z;++i)L[vs[i]]=f.lv[i]>=0?b:a;double after=score();if(after<before-1e-7){wins++;cout<<"WIN swap "<<a<<" "<<b<<" "<<before-after<<" total "<<base-after<<endl;ofstream out(argv[2]);for(int v:L)out<<v<<"\n";}else L=old;if(++tests%200==0)cout<<"tests "<<tests<<" wins "<<wins<<endl;}
cout<<"done "<<tests<<" wins "<<wins<<endl;return 0;}
