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
#include <map>
using namespace std;
struct Arc{int v,rev;double cap;};
struct Flow{vector<vector<Arc>> a;vector<int> level,ptr;Flow(int n):a(n),level(n),ptr(n){};void edge(int u,int v,double c){Arc x{v,int(a[v].size()),c},y{u,int(a[u].size()),0};a[u].push_back(x);a[v].push_back(y);}double send(int u,int t,double f){if(u==t)return f;for(int&i=ptr[u];i<int(a[u].size());i++){auto&e=a[u][i];if(e.cap>1e-8&&level[e.v]==level[u]+1){double z=send(e.v,t,min(f,e.cap));if(z>1e-8){e.cap-=z;a[e.v][e.rev].cap+=z;return z;}}}return 0;}vector<bool>cut(int s,int t){while(true){fill(level.begin(),level.end(),-1);queue<int>q;level[s]=0;q.push(s);while(!q.empty()){int u=q.front();q.pop();for(auto e:a[u])if(e.cap>1e-8&&level[e.v]<0){level[e.v]=level[u]+1;q.push(e.v);}}if(level[t]<0){vector<bool>v(level.size());for(int i=0;i<int(v.size());i++)v[i]=level[i]>=0;return v;}fill(ptr.begin(),ptr.end(),0);while(send(s,t,1e15)>1e-8){}}}};

struct Frame{int dim;array<unsigned long long,8> bits;};
bool sub(const Frame&a,const Frame&b){for(int k=0;k<8;k++)if(a.bits[k]&~b.bits[k])return false;return true;}
bool contains(const Frame&f,int v){return(f.bits[v/64]>>(v%64))&1;}
Frame mapped(const Frame&f,int v,bool join){Frame g=f;if(join){if(contains(f,v))return g;g.dim++;for(int x=0;x<512;x++)if(contains(f,x))g.bits[(x^v)/64]|=1ULL<<((x^v)%64);}else{bool changed=false;for(int x=0;x<512;x++)if(contains(f,x)&&(__builtin_popcount(unsigned(x&v))&1)){g.bits[x/64]&=~(1ULL<<(x%64));changed=true;}if(changed)g.dim--;}return g;}
struct Node{bool mut;int oldf,newf;};
int main(int argc,char**argv){
 if(argc!=2)return 2;
 int F,N,E;cin>>F>>N>>E;vector<Frame>frames(F);map<array<unsigned long long,8>,int>lookup;
 for(int f=0;f<F;f++){cin>>frames[f].dim;for(auto&x:frames[f].bits)cin>>x;lookup[frames[f].bits]=f;}
 vector<Node>nodes(N);vector<int>idx(N,-1),rev;
 for(int i=0;i<N;i++){int m;cin>>m>>nodes[i].oldf>>nodes[i].newf;nodes[i].mut=m;}
 vector<pair<int,int>>edges(E);for(auto&[a,b]:edges)cin>>a>>b;
 int H;cin>>H;vector<pair<int,int>>helpers(H);for(auto&[a,b]:helpers)cin>>a>>b;
 for(int i=0;i<N;i++)if(nodes[i].mut){idx[i]=rev.size();rev.push_back(i);}
 for(auto[a,b]:helpers)idx[b]=idx[a];
 double powers[10];for(int r=0;r<10;r++)powers[r]=pow(r,.99699894);const double INF=1e7;int V=rev.size();
 cerr<<"initial frames "<<F<<" variables "<<V<<endl;
 for(int round=0;round<5;round++){double gain=0;
 for(bool join:{true,false})for(int v=1;v<512;v++){
  set<int>used;for(auto n:nodes){used.insert(n.oldf);used.insert(n.newf);}vector<Frame>proposal(frames.size());
  for(int f:used)proposal[f]=mapped(frames[f],v,join);
  Flow flow(V+2);vector<double>unary(V,0);int s=V,t=V+1;
  for(auto[a,b]:edges){int fa=nodes[a].newf,fb=nodes[b].oldf;auto A=frames[fa],B=frames[fb],GA=proposal[fa],GB=proposal[fb];
   if(!sub(A,B)){cerr<<"bad baseline edge"<<endl;return 3;}
   double e00=powers[B.dim-A.dim];int i=idx[a],j=idx[b];
   double e10=sub(GA,B)?powers[B.dim-GA.dim]:INF;
   double e01=sub(A,GB)?powers[GB.dim-A.dim]:INF;
   double e11=powers[GB.dim-GA.dim];
   if(i>=0&&i==j){unary[i]+=e11-e00;continue;}
   if(i>=0&&j>=0){double w=e10+e01-e00-e11;if(w<-1e-7){cerr<<"nonsubmodular "<<w<<endl;return 2;}unary[i]+=e11-e01;unary[j]+=e01-e00;flow.edge(i,j,max(0.,w));}
   else if(i>=0)unary[i]+=e10-e00;else if(j>=0)unary[j]+=e01-e00;
  }
  for(auto[a,b]:helpers){auto A=frames[nodes[a].newf],B=frames[nodes[b].oldf],GA=proposal[nodes[a].newf],GB=proposal[nodes[b].oldf];
   unary[idx[a]]+=powers[B.dim-A.dim]-powers[GB.dim-GA.dim];
  }
  for(int i=0;i<V;i++)if(unary[i]<0)flow.edge(s,i,-unary[i]);else flow.edge(i,t,unary[i]);
  auto reach=flow.cut(s,t);double delta=0;bool legal=true;
  for(auto[a,b]:edges){int fa=nodes[a].newf,fb=nodes[b].oldf;auto A=frames[fa],B=frames[fb];
   auto GA=idx[a]>=0&&reach[idx[a]]?proposal[fa]:A,GB=idx[b]>=0&&reach[idx[b]]?proposal[fb]:B;
   if(!sub(GA,GB)){legal=false;break;}delta+=powers[GB.dim-GA.dim]-powers[B.dim-A.dim];
  }
  for(auto[a,b]:helpers)if(reach[idx[a]]){auto A=frames[nodes[a].newf],B=frames[nodes[b].oldf],GA=proposal[nodes[a].newf],GB=proposal[nodes[b].oldf];delta+=powers[B.dim-A.dim]-powers[GB.dim-GA.dim];}
  if(legal&&delta < -1e-8){int count=0,h=0;for(auto[a,b]:helpers)if(reach[idx[a]])h++;
   vector<int>translated(frames.size(),-1);
   for(int f:used){auto G=proposal[f];auto it=lookup.find(G.bits);if(it==lookup.end()){int k=frames.size();lookup[G.bits]=k;frames.push_back(G);translated[f]=k;}else translated[f]=it->second;}
   for(int k=0;k<N;k++)if(idx[k]>=0&&reach[idx[k]]){nodes[k].oldf=translated[nodes[k].oldf];nodes[k].newf=translated[nodes[k].newf];count++;}
   gain+=delta;cerr<<"ACCEPT round "<<round<<" "<<(join?"join":"meet")<<" vector "<<v<<" nodes "<<count<<" helpers "<<h<<" gain "<<setprecision(13)<<delta<<endl;
   ofstream out(argv[1]);out<<frames.size()<<" "<<N<<"\n";for(auto f:frames){out<<f.dim;for(auto x:f.bits)out<<" "<<x;out<<"\n";}for(int i=0;i<N;i++)out<<i<<" "<<nodes[i].oldf<<" "<<nodes[i].newf<<"\n";
  }
 }
 cerr<<"ROUND_GAIN "<<round<<" "<<setprecision(13)<<gain<<endl;if(gain>=-1e-8)break;
 }
}
