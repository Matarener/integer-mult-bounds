// Exhaust the three interior projectors of the four-field five-call word.
// Input matrices are prepared and checked by discovery.py.
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>
using Mat = std::array<int,16>;
int prime;
int mod(int a) { a %= prime; return a < 0 ? a+prime : a; }
Mat id() { Mat a{}; for(int i=0;i<4;++i)a[5*i]=1; return a; }
Mat add(Mat a,const Mat& b,int sign=1) {
    for(int i=0;i<16;++i)a[i]=mod(a[i]+sign*b[i]); return a;
}
Mat mul(const Mat& a,const Mat& b) {
    Mat c{};
    for(int i=0;i<4;++i)for(int j=0;j<4;++j) {
        int z=0; for(int k=0;k<4;++k)z+=a[4*i+k]*b[4*k+j];
        c[4*i+j]=z%prime;
    }
    return c;
}
using Poly = std::array<Mat,3>;
Poly two(const Mat& p,const Mat& q,const Mat& middle,const Mat& right) {
    const Mat a=add(id(),p,-1), b=add(id(),q,-1);
    return {mul(mul(mul(b,middle),a),right),
            add(mul(mul(mul(q,middle),a),right),mul(mul(mul(b,middle),p),right)),
            mul(mul(mul(q,middle),p),right)};
}
int main() {
    int count;
    if(!(std::cin>>prime>>count)||prime<3||count!=prime*prime*prime*prime)return 2;
    std::array<Mat,5> t;
    for(auto& a:t)for(int& x:a)if(!(std::cin>>x))return 2;
    std::array<std::vector<Mat>,3> family;
    for(auto& v:family){v.resize(count);for(auto& a:v)for(int& x:a)if(!(std::cin>>x))return 2;}
    const Mat ident=id(), right=mul(t[1],t[0]);
    uint64_t survivors=0, tested=0;
    std::vector<std::array<int,3>> first;
    for(int i=0;i<count;++i)for(int j=0;j<count;++j) {
        const Poly c=two(family[0][i],family[1][j],ident,ident);
        const Poly b=two(family[0][i],family[1][j],t[2],right);
        std::array<std::array<int,16>,48> equations{};
        std::array<int,48> targets{};
        Mat accumulated{};
        for(int degree=0;degree<3;++degree) {
            const Mat x=mul(t[3],b[degree]);
            accumulated=add(accumulated,add(mul(t[4],x),c[degree]));
            for(int row=0;row<4;++row)for(int col=0;col<4;++col) {
                const int e=16*degree+4*row+col;
                targets[e]=accumulated[4*row+col];
                for(int a=0;a<4;++a)for(int z=0;z<4;++z)
                    equations[e][4*a+z]=mod(t[4][4*row+a]*x[4*z+col]+(row==a?c[degree][4*z+col]:0));
            }
        }
        if(accumulated!=Mat{})return 3;
        for(int k=0;k<count;++k) {
            ++tested; bool pass=true;
            for(int e=0;e<48 && pass;++e) {
                int value=0;
                for(int a=0;a<16;++a)value+=equations[e][a]*family[2][k][a];
                pass=value%prime==targets[e];
            }
            if(pass){++survivors;if(first.size()<100)first.push_back({i,j,k});}
        }
    }
    std::cout<<"{\"prime\":"<<prime<<",\"tested\":"<<tested<<",\"query_survivors\":"<<survivors<<",\"first_triples\":[";
    for(size_t i=0;i<first.size();++i){if(i)std::cout<<",";std::cout<<"["<<first[i][0]<<","<<first[i][1]<<","<<first[i][2]<<"]";}
    std::cout<<"]}\n";
}
