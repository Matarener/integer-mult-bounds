// Exact nonnegative integer covering check. Douglas Colkitt / Codex, Apache-2.0.
// No external libraries. A node/time cap is UNKNOWN, never UNSAT.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <vector>
using namespace std;
int R,C,budget,target;
vector<vector<int>> a,suffix;
vector<int> score,counts,answer;
uint64_t nodes=0,pruned=0,limit=100000000;
bool stopped=false;
auto begun=chrono::steady_clock::now();
bool search(int j,int remaining){
    ++nodes;
    if(nodes>limit || ((nodes&65535)==0 && chrono::duration<double>(chrono::steady_clock::now()-begun).count()>60)){
        stopped=true;return false;
    }
    bool covered=true;
    for(int r=0;r<R;r++){
        if(score[r]<target)covered=false;
        if(score[r]+remaining*suffix[j][r]<target){++pruned;return false;}
    }
    if(covered){answer=counts;return true;}
    if(j==C || remaining==0)return false;
    // Enumerate each multiset once, including every solution with <= budget.
    for(int n=0;n<=remaining;n++){
        counts[j]=n;
        if(search(j+1,remaining-n))return true;
        if(stopped)return false;
        if(n<remaining)for(int r=0;r<R;r++)score[r]+=a[j][r];
    }
    for(int r=0;r<R;r++)score[r]-=remaining*a[j][r];
    counts[j]=0;
    return false;
}
int main(){
    if(!(cin>>R>>C>>budget>>target) || R<1 || C<1 || budget<0 || target<0)return 2;
    a.assign(C,vector<int>(R));
    for(int r=0;r<R;r++)for(int j=0;j<C;j++){
        if(!(cin>>a[j][r]) || a[j][r]<0)return 2;
    }
    suffix.assign(C+1,vector<int>(R));
    for(int j=C-1;j>=0;j--)for(int r=0;r<R;r++)suffix[j][r]=max(suffix[j+1][r],a[j][r]);
    score.assign(R,0);counts.assign(C,0);
    bool found=search(0,budget);
    cout<<"{\"result\":\""<<(found?"sat":stopped?"unknown":"unsat")<<"\",\"nodes\":"<<nodes
        <<",\"pruned\":"<<pruned<<",\"counts\":[";
    if(found)for(int j=0;j<C;j++){if(j)cout<<',';cout<<answer[j];}
    cout<<"]}\n";
}
