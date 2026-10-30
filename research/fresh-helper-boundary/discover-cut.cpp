// Optional floating-point discovery, never a proof checker. Apache-2.0.
// Prepared with substantial OpenAI Codex assistance.
#include <iostream>
#include <vector>
#include <array>
#include <queue>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <set>
using namespace std;
struct Arc{int v,rev;double cap;};
struct Flow{vector<vector<Arc>> a;vector<int> level,ptr;Flow(int n):a(n),level(n),ptr(n){};void edge(int u,int v,double c){Arc x{v,int(a[v].size()),c},y{u,int(a[u].size()),0};a[u].push_back(x);a[v].push_back(y);}double send(int u,int t,double f){if(u==t)return f;for(int&i=ptr[u];i<int(a[u].size());i++){auto&e=a[u][i];if(e.cap>1e-8&&level[e.v]==level[u]+1){double z=send(e.v,t,min(f,e.cap));if(z>1e-8){e.cap-=z;a[e.v][e.rev].cap+=z;return z;}}}return 0;}vector<bool>cut(int s,int t){while(true){fill(level.begin(),level.end(),-1);queue<int>q;level[s]=0;q.push(s);while(!q.empty()){int u=q.front();q.pop();for(auto e:a[u])if(e.cap>1e-8&&level[e.v]<0){level[e.v]=level[u]+1;q.push(e.v);}}if(level[t]<0){vector<bool>v(level.size());for(int i=0;i<int(v.size());i++)v[i]=level[i]>=0;return v;}fill(ptr.begin(),ptr.end(),0);while(send(s,t,1e15)>1e-8){}}}};
struct Node{bool mut;int oldf,newf;};
int main(int argc,char**argv){if(argc!=3){cerr<<"usage: discover-cut entry|exit output-file"<<endl;return 2;}bool entry=string(argv[1])=="entry";if(!entry && string(argv[1])!="exit")return 2;int F,N,E;cin>>F>>N>>E;vector<int>dim(F);vector<array<unsigned long long,8>>space(F);for(int f=0;f<F;f++){cin>>dim[f];for(auto&x:space[f])cin>>x;}vector<vector<bool>>sub(F,vector<bool>(F,true));for(int i=0;i<F;i++)for(int j=0;j<F;j++)for(int b=0;b<8;b++)if(space[i][b]&~space[j][b])sub[i][j]=false;
 vector<Node>nodes(N);vector<int>idx(N,-1),rev;for(int i=0;i<N;i++){int m;cin>>m>>nodes[i].oldf>>nodes[i].newf;nodes[i].mut=m;if(m){idx[i]=rev.size();rev.push_back(i);}}vector<pair<int,int>>edges(E);for(auto&[a,b]:edges)cin>>a>>b;
 int H;cin>>H;vector<pair<int,int>>helpers(H);for(auto&[i,f]:helpers)cin>>i>>f;
 vector<int>candidates;for(int f=0;f<F;f++){bool dup=false;for(int g:candidates)if(space[f]==space[g]){dup=true;break;}if(!dup)candidates.push_back(f);}double powers[10];for(int r=0;r<10;r++)powers[r]=pow(r,.997);const double INF=1e6;int V=rev.size();cerr<<"candidate frames "<<candidates.size()<<" variables "<<V<<endl;
 for(int round=0;round<10;round++){double best=0;int done=0;
 for(int g:candidates){Flow flow(V+2);vector<double>unary(V,0);int s=V,t=V+1;
 for(auto[a,b]:edges){int fa=nodes[a].newf,fb=nodes[b].oldf;double e0=powers[dim[fb]-dim[fa]];int i=idx[a],j=idx[b];
 double e10=sub[g][fb]?powers[dim[fb]-dim[g]]:INF;double e01=sub[fa][g]?powers[dim[g]-dim[fa]]:INF;
 if(i>=0&&j>=0){double w=e10+e01-e0;if(w<-1e-7){cerr<<"nonsubmodular"<<endl;return 2;}unary[i]-=e01;unary[j]+=e01-e0;flow.edge(i,j,max(0.,w));}else if(i>=0)unary[i]+=e10-e0;else if(j>=0)unary[j]+=e01-e0;
 }
 for(auto[i,f]:helpers){int old=nodes[i].newf;double delta=(entry?(sub[g][f] && dim[g]<dim[f]):(sub[f][g] && dim[g]>dim[f]))?(entry?powers[dim[f]-dim[old]]-powers[dim[f]-dim[g]]:powers[dim[old]-dim[f]]-powers[dim[g]-dim[f]]):INF;unary[idx[i]]+=delta;}
 for(int i=0;i<V;i++)if(unary[i]<0)flow.edge(s,i,-unary[i]);else flow.edge(i,t,unary[i]);auto reach=flow.cut(s,t);double delta=0;bool legal=true;
 for(auto[a,b]:edges){int fa=nodes[a].newf,fb=nodes[b].oldf;int ga=idx[a]>=0&&reach[idx[a]]?g:fa,gb=idx[b]>=0&&reach[idx[b]]?g:fb;if(!sub[ga][gb]){legal=false;break;}delta+=powers[dim[gb]-dim[ga]]-powers[dim[fb]-dim[fa]];}
 for(auto[i,f]:helpers)if(reach[idx[i]]){int old=nodes[i].newf;if(entry?(!sub[g][f]||dim[g]>=dim[f]):(!sub[f][g]||dim[g]<=dim[f])){legal=false;break;}delta+=entry?powers[dim[f]-dim[old]]-powers[dim[f]-dim[g]]:powers[dim[old]-dim[f]]-powers[dim[g]-dim[f]];}
 if(legal&&delta < -1e-8){int count=0;for(int i=0;i<V;i++)if(reach[i]){int k=rev[i];nodes[k].oldf=nodes[k].newf=g;count++;}best+=delta;cerr<<"ACCEPT round "<<round<<" frame "<<g<<" nodes "<<count<<" gain "<<setprecision(13)<<delta<<endl;ofstream out(argv[2]);for(int i=0;i<N;i++)out<<i<<" "<<nodes[i].oldf<<" "<<nodes[i].newf<<"\n";}
 done++;if(done%200==0)cerr<<"round "<<round<<" tested "<<done<<endl;
 }
 if(best>=-1e-8){cerr<<"NO_GAIN round "<<round<<endl;break;}
 
 }
}
