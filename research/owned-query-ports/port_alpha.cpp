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
for(int pass=0;pass<3;++pass){int wins=0;for(int a:order){Dinic f(n+2);int s=n,t=n+1;vector<double>u(n,0.);for(auto[x,y]:edges){double A=p[D[L[x]][L[y]]],B=p[D[L[x]][a]],C=p[D[a][L[y]]];double cross=B+C-A;if(cross< -1e-8){cerr<<"nonmetric";return 3;}cross=max(0.,cross);I cap=llround(cross*1e8);f.add(x,y,cap);f.add(y,x,cap);u[x]+=C-A-B;u[y]+=B-A-C;}for(int i=0;i<n;++i){if(fixed[i]||L[i]==a)f.add(i,t,1LL<<55);if(u[i]>=0)f.add(i,t,llround(u[i]*1e8));else f.add(s,i,llround(-u[i]*1e8));}f.flow(s,t);auto old=L;double before=score();for(int i=0;i<n;++i)if(f.lv[i]>=0)L[i]=a;double after=score();if(after<before-1e-7){++wins;cout<<"WIN "<<a<<" "<<before-after<<" total "<<base-after<<endl;ofstream out(argv[2]);for(int v:L)out<<v<<"\n";}else L=old;}cout<<"pass "<<pass<<" wins "<<wins<<endl;if(!wins)break;}return 0;}
