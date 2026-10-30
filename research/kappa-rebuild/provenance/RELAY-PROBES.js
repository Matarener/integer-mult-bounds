#!/usr/bin/env node
"use strict";
/*
Recovery-only scalar relay probes, 2026-10-21.
The original repository and frozen research sources disappeared during an
execution-environment reset. This file is NEW recovery work. It is NOT a
byte-identical reconstruction of any missing scientific source.

Model: one constant chart per eight-dimensional channel, LK=13 I,
C=[L,I], B=[-K;11 I], CB=-2 I, H=I+BC.
The scalar coordinates are t=L U, a=A, with Cx=t+a.
No native frames, owner maps, child phases, dirty-helper hosting, or outer
admission are established here. Exact modular row ranks are screening
witnesses; the positive p=1 endpoint is additionally checked as an exact
integer matrix. Numerical H_r cost screens are ordinary double precision.

The core function probe below was retained in functions.store across the
filesystem reset. Explicit safe-integer and observation-rank guards were then
added. Its companion probeMatrix changes only the returned data.
*/
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
function safeMul(a,b){const v=a*b;assert(Number.isSafeInteger(v),"unsafe integer product");return v;}
function safeSub(a,b){const v=a-b;assert(Number.isSafeInteger(v),"unsafe integer difference");return v;}

function probe(p,lam=0,ids=[],premask=0,swapmask=-1){
const n=2*p,N=3*n+1,E=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>+(i===j))), M=E.map(r=>r.slice());
const plus=(a,b,k=1)=>a.map((v,j)=>v+k*b[j]), row=(i,j,k)=>{M[i]=plus(M[i],M[j],k)};
const ev=[];
let s=0;ev.push(['F',0,s++],['B',0,s++]);
for(let j=1;j<p;j++){ev.push(['bridge',j,j-1,1],['F',j-1,s++],['bridge',j,j-1,-1],['B',j,s++]);}
ev.push(['F',p-1,s++]);for(let j=p-2;j>=0;j--)ev.push(['bridge',j,j+1,1]);
for(const q of ev){
if(q[0]==='bridge'){let x=2*q[1],y=2*q[2],k=q[3];for(const off of [0,n]){row(off+y,off+x,k);row(off+x+1,off+y+1,-k);}continue;}
const [type,i,st]=q,x=2*i,y=x+1,di=2*n+(ids[st]??st);
if(type==='F'){
if((premask>>(st/2))&1){const oldq=plus(M[y],M[n+y]);M[n+y]=plus(M[di],M[y],-1);M[di]=oldq;}
let t=M[x].slice(),a=M[n+x].slice(),v=plus(t,a),d=M[di].slice();
M[y]=plus(plus(M[y],t),v,-13);M[n+y]=plus(plus(M[n+y],t,-1),v,12);
if((swapmask>>st)&1){M[x]=plus(plus(t,d,13),v,-13);M[n+x]=plus(d,M[x],-1);M[di]=v;}
if(lam!==0&&st<2*p){M[di+1]=plus(M[di+1],d,-(Array.isArray(lam)?lam[st/2]:lam));}
}else{
let t=M[y].slice(),v=plus(t,M[n+y]),d=M[di].slice();if((swapmask>>st)&1){M[n+y]=plus(d,t,-1);M[di]=v;}else{d=v;}
M[x]=plus(plus(M[x],t,-1),d,13);M[n+x]=plus(plus(M[n+x],t),d,-12);
}
}
for(let i=0;i<p;i++){let x=2*i,y=x+1;for(const off of [0,n]){const t=M[off+x];M[off+x]=M[off+y];M[off+y]=t.map(v=>-v);}}
assert(M.every(row=>row.every(Number.isSafeInteger)),"non-safe whole operator entry");
const obs=M.slice(n,2*n).concat(M.slice(2*n),Array.from({length:p},(_,i)=>M[2*i+1]));
const demanded=Array.from({length:p},(_,i)=>plus(M[2*i],E[2*i],-1));
const cacheDem=Array.from({length:n+1},(_,j)=>E[2*n+j]);
const mod=65521,norm=x=>{assert(Number.isSafeInteger(x),"non-safe modular input");return (x%mod+mod)%mod;};
function rank(A){A=A.map(r=>r.map(norm));let k=0;
for(let j=0;j<N&&k<A.length;j++){let i=k;while(i<A.length&&!A[i][j])i++;if(i===A.length)continue;[A[i],A[k]]=[A[k],A[i]];
let a=A[k][j],b=mod,u=1,v=0;while(b){const q=Math.floor(a/b);[a,b]=[b,safeSub(a,safeMul(q,b))];[u,v]=[v,safeSub(u,safeMul(q,v))];}
const inv=norm(u);for(let c=j;c<N;c++)A[k][c]=norm(safeMul(A[k][c],inv));
for(let i=k+1;i<A.length;i++){const q=A[i][j];if(q)for(let c=j;c<N;c++)A[i][c]=norm(safeSub(A[i][c],safeMul(q,A[k][c])));}k++;
}return k;}
const r=rank(obs);
assert.equal(r,obs.length,"full observation rank required for rational negative inference");
return{p,lam,obsRank:r,mainDemandGap:rank(obs.concat(demanded))-r,mainAndCacheGap:rank(obs.concat(demanded,cacheDem))-r,integralMax:Math.max(...M.flat().map(Math.abs))};
}

function probeMatrix(p,lam=0,ids=[],premask=0,swapmask=-1){
const n=2*p,N=3*n+1,E=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>+(i===j))), M=E.map(r=>r.slice());
const plus=(a,b,k=1)=>a.map((v,j)=>v+k*b[j]), row=(i,j,k)=>{M[i]=plus(M[i],M[j],k)};
const ev=[];
let s=0;ev.push(['F',0,s++],['B',0,s++]);
for(let j=1;j<p;j++){ev.push(['bridge',j,j-1,1],['F',j-1,s++],['bridge',j,j-1,-1],['B',j,s++]);}
ev.push(['F',p-1,s++]);for(let j=p-2;j>=0;j--)ev.push(['bridge',j,j+1,1]);
for(const q of ev){
if(q[0]==='bridge'){let x=2*q[1],y=2*q[2],k=q[3];for(const off of [0,n]){row(off+y,off+x,k);row(off+x+1,off+y+1,-k);}continue;}
const [type,i,st]=q,x=2*i,y=x+1,di=2*n+(ids[st]??st);
if(type==='F'){
if((premask>>(st/2))&1){const oldq=plus(M[y],M[n+y]);M[n+y]=plus(M[di],M[y],-1);M[di]=oldq;}
let t=M[x].slice(),a=M[n+x].slice(),v=plus(t,a),d=M[di].slice();
M[y]=plus(plus(M[y],t),v,-13);M[n+y]=plus(plus(M[n+y],t,-1),v,12);
if((swapmask>>st)&1){M[x]=plus(plus(t,d,13),v,-13);M[n+x]=plus(d,M[x],-1);M[di]=v;}
if(lam!==0&&st<2*p){M[di+1]=plus(M[di+1],d,-(Array.isArray(lam)?lam[st/2]:lam));}
}else{
let t=M[y].slice(),v=plus(t,M[n+y]),d=M[di].slice();if((swapmask>>st)&1){M[n+y]=plus(d,t,-1);M[di]=v;}else{d=v;}
M[x]=plus(plus(M[x],t,-1),d,13);M[n+x]=plus(plus(M[n+x],t),d,-12);
}
}
for(let i=0;i<p;i++){let x=2*i,y=x+1;for(const off of [0,n]){const t=M[off+x];M[off+x]=M[off+y];M[off+y]=t.map(v=>-v);}}
assert(M.every(row=>row.every(Number.isSafeInteger)),"non-safe whole operator entry");
const obs=M.slice(n,2*n).concat(M.slice(2*n),Array.from({length:p},(_,i)=>M[2*i+1]));
const demanded=Array.from({length:p},(_,i)=>plus(M[2*i],E[2*i],-1));
const cacheDem=Array.from({length:n+1},(_,j)=>E[2*n+j]);
const mod=65521,norm=x=>{assert(Number.isSafeInteger(x),"non-safe modular input");return (x%mod+mod)%mod;};
function rank(A){A=A.map(r=>r.map(norm));let k=0;
for(let j=0;j<N&&k<A.length;j++){let i=k;while(i<A.length&&!A[i][j])i++;if(i===A.length)continue;[A[i],A[k]]=[A[k],A[i]];
let a=A[k][j],b=mod,u=1,v=0;while(b){const q=Math.floor(a/b);[a,b]=[b,safeSub(a,safeMul(q,b))];[u,v]=[v,safeSub(u,safeMul(q,v))];}
const inv=norm(u);for(let c=j;c<N;c++)A[k][c]=norm(safeMul(A[k][c],inv));
for(let i=k+1;i<A.length;i++){const q=A[i][j];if(q)for(let c=j;c<N;c++)A[i][c]=norm(safeSub(A[i][c],safeMul(q,A[k][c])));}k++;
}return k;}
const r=rank(obs);
assert.equal(r,obs.length,"full observation rank required for rational negative inference");
return {M,obs,demanded};
}

function histAdd(hist,r){const key=r.mainDemandGap+","+r.mainAndCacheGap;hist[key]=(hist[key]||0)+1;}
function assertExpected(r,main,all){assert.equal(r.mainDemandGap,main);assert.equal(r.mainAndCacheGap,all);}
function signedAdditiveMenu(){
 const rows=[];
 for(const p of [1,2,3,4,5])for(const lam of [0,1,-1]){
  const r=probe(p,lam); assertExpected(r,p-1,p);rows.push(r);
 }
 const hist={};
 for(const a of [-2,-1,0,1,2])for(const b of [-2,-1,0,1,2])for(const c of [-2,-1,0,1,2]){
  const r=probe(3,[a,b,c]);assertExpected(r,2,3);histAdd(hist,r);
 }
 return {uniform_count:rows.length,rows,independent_p3_count:125,independent_p3_histogram:hist};
}
function optionalSwapMenu(){
 const rows=[];
 for(const p of [1,2,3,4]){
  const hist={},count=1<<(2*p+1);
  for(let mask=0;mask<count;mask++){
   const r=probe(p,0,[],0,mask);assert.equal(r.mainAndCacheGap,p);histAdd(hist,r);
  }
  rows.push({p,count,histogram:hist});
 }
 return {count:680,rows};
}
function reuseMenu(){
 const rows=[];
 for(const p of [1,2]){
  const k=2*p+1,count=Math.pow(k,k),hist={};
  for(let code=0;code<count;code++){
   let q=code;const ids=[];
   for(let j=0;j<k;j++){ids.push(q%k);q=Math.floor(q/k);}
   const r=probe(p,0,ids);assert.equal(r.mainAndCacheGap,p);histAdd(hist,r);
  }
  rows.push({p,count,histogram:hist});
 }
 return {count:3152,rows};
}
function earlyTargetMenu(){
 const rows=[];
 for(const p of [1,2]){
  const k=2*p+1,assignmentCount=p===1?27:1,hist={},successes=[];
  let count=0;
  for(let code=0;code<assignmentCount;code++){
   let q=code;const ids=[];
   for(let j=0;j<k;j++){ids.push(p===1?q%k:j);q=Math.floor(q/k);}
   for(let preMask=0;preMask<(1<<(p+1));preMask++)
   for(let swapMask=0;swapMask<(1<<k);swapMask++){
    const r=probe(p,0,ids,preMask,swapMask);histAdd(hist,r);count++;
    if(r.mainAndCacheGap===0)successes.push({ids,preMask,swapMask});
   }
  }
  if(p===1){assert.equal(count,864);assert.equal(successes.length,66);}
  else {assert.equal(count,256);assert.equal(successes.length,0);}
  rows.push({p,count,histogram:hist,successes});
 }
 return rows;
}
function matrixProduct(a,b){
 const z=Array.from({length:a.length},()=>Array(b[0].length).fill(0));
 for(let i=0;i<a.length;i++)for(let k=0;k<b.length;k++)for(let j=0;j<b[0].length;j++)z[i][j]+=a[i][k]*b[k][j];
 return z;
}
function quarterTurn(){
 // Exact dyadic arithmetic: every coefficient is a small dyadic rational.
 // A 2-main-coordinate instance realizes CB=-2; the general identity follows
 // from multiplication with CB=-2, as explained in README.
 const U=[[1,0,-0.5],[0,1,0.5],[0,0,1]];
 const L=[[1,0,0],[0,1,0],[1,-1,1]];
 const R=matrixProduct(matrixProduct(U,L),U);
 const R2=matrixProduct(R,R),cacheNegation=[[1,0,0],[0,1,0],[0,0,-1]];
 const closed=matrixProduct(cacheNegation,R2),expected=[[0,1,0],[1,0,0],[0,0,1]];
 assert.deepEqual(closed,expected);
 assert.notDeepEqual(R2,expected); // Without cache negation dirty d is not restored.
 const wrongL=[[1,0,0],[0,1,0],[1,0,1]];
 const wrongR=matrixProduct(matrixProduct(U,wrongL),U);
 assert.notDeepEqual(matrixProduct(cacheNegation,matrixProduct(wrongR,wrongR)),expected);
 return {B:[[-1],[1]],C:[[1,-1]],CB:-2,R,R_squared:R2,closed,expected,
  query_map:"(Cx,d) -> (-d,Cx)",
  general_closed_contract:"(x,d) -> ((I+BC)x,d), provided CB=-2I",
  primitive_counts_after_adjacent_U_merge:{C_queries:2,B_scatters:3,cache_sign_changes:1},
  negative_controls:["omit final cache negation","replace CB=-2 by CB=-1"],
  native_contact_cost_established:false};
}
function positiveEndpoint(){
 const r=probeMatrix(1,0,[0,0,0],2,2),indices=[0,1,2,3,4];
 const actual=indices.map(i=>indices.map(j=>r.M[i][j]||0));
 const expected=[
  [-12,0,-13,0,0],
  [-13,1,-13,0,-13],
  [10,1,11,1,-1],
  [12,-1,12,0,12],
  [0,0,0,0,1]
 ];
 assert.deepEqual(actual,expected);
 assertExpected(probe(1,0,[0,0,0],2,2),0,0);
 assert.equal(probe(1,0,[0,0,0],0,2).mainAndCacheGap,1);
 return {
  p:1,used_banks:1,coordinate_order:["L X_U","L Y_U","X_A","Y_A","d"],
  itinerary:[
   "F0: add H X to Y",
   "B0-pre: exchange C Y and P using Y_A only",
   "B0: subtract H Y from X",
   "F0-last-pre: exchange C Y and the same P using Y_A only",
   "F0-last: add H X to Y",
   "terminal signed swap: X<-Y, Y<-(-old X)"
  ],
  exact_integer_matrix:actual,
  endpoint:{
   P_out:"d",
   X_U_out:"X_U - K v",
   Y_U_out:"Y_U - K(v+d)",
   C_Y_out:"-v-d",
   v:"C X_initial",
   recover_v:"-(C Y_out)-P_out"
  },
  proof_status:"exact integer scalar-chart operator; no native proof",
  unpaid:["bank movement between the two entry frames","native owner-map equivalence for C",
   "scatter K v into final X holes","all main/selected-output endpoint corrections",
   "full productive-bank frame journey and recursive invoice"],
  negative_control:"omit second target-entry exchange: productive observation deficit returns to1"
 };
}
function invoiceScreens(){
 const pruned={1:2453,2:716,3:224,4:74,5:48},old={1:2487,2:713,3:224,4:102,5:20};
 const rows=[];
 for(const kappa of [0.001745,0.004]){
  const H=r=>r?Math.pow(r,1-kappa):0;
  const sum=h=>Object.entries(h).reduce((s,[r,n])=>s+n*H(+r),0);
  const local=sum(pruned),delta=sum(old)-local,residual=129*H(1)+84*H(2);
  const raw=632*H(25)-3*local-residual;
  rows.push({kappa,H_definition:"r^(1-kappa)",p:1,productive_extra_fields:408,width:632,
   outer_rank:25,residual_profile:{1:129,2:84},raw_allowance:raw,
   local_unpruned_minus_pruned:delta,
   complete_identity_surcharge:3*(8*H(8)+delta),
   after_complete_identity:raw-3*(8*H(8)+delta)});
 }
 return {status:"double-precision screen, not interval-certified admission",provider:"THREE",
  pruned_histogram:pruned,unpruned_histogram:old,rows,
  provenance:"histograms supplied by C from frozen receipt before reset; old receipt bytes currently unavailable"};
}
function singularRelay(){
 const bad=[[0,1,0],[0,-1,0],[0,0,1]];
 assert.deepEqual(bad[0].map((v,j)=>v+bad[1][j]),[0,0,0]);
 return {input:["v","d","b"],bad_output:["d","-d","b"],matrix:bad,
  dependent_output_relation:"output0+output1=0",
  conclusion:"Pure next dirt=-d while retaining source query=d is singular; extra independent untouched registers do not remove this output relation.",
  scope:"Does not rule out changing the source query, retaining extra dirt, or another chronological controller."};
}
function ownerGate(){
 const C1=[[1,1]],C2=[[2,1]],E=[[0],[1]],I=[[1,0],[0,1]];
 const EC=matrixProduct(E,C1),T=I.map((row,i)=>row.map((v,j)=>v-EC[i][j]));
 const remaining=matrixProduct(C2,T),dCoefficient=matrixProduct(C2,E);
 assert.deepEqual(remaining,[[1,0]]);assert.deepEqual(dCoefficient,[[1]]);
 return {C1,C2,E,remaining_old_Y_coefficient:remaining,d_coefficient:dCoefficient,
  mismatch_control:"P_out=Y0_U+d, so the dirty bank is not restored",
  exact_condition:"C2(I-E1 C1)=0 and C2 E1=I, with C1 E1=I, force C2=C1",
  native_condition:"Use actual common-chart conjugations and cache/target transports before comparing C1 and C2",
  native_owner_gate_evaluated:false};
}
function commonFutureQuery(){
 // This checks a noncommuting matrix instance of the operator identity in
 // README. It does not certify availability of these queries in native frames.
 const H0=[[-1,0],[0,1]],H1=[[0,-1],[-1,0]],H2=[[1,0],[-4,-1]];
 const Q=[2,1],E=[0,1],N=5;
 const id=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>+(i===j)));
 const M=id.map(row=>row.slice());
 const plus=(a,b,k=1)=>a.map((v,j)=>v+k*b[j]);
 function addBlock(dst,src,H,sign){
  const old=M.map(row=>row.slice());
  for(let i=0;i<2;i++)for(let j=0;j<2;j++)M[dst+i]=plus(M[dst+i],old[src+j],sign*H[i][j]);
 }
 function swapQuery(){
  const oldP=M[4].slice(),value=plus(M[2].map(v=>Q[0]*v),M[3],Q[1]);
  for(let i=0;i<2;i++)M[2+i]=plus(M[2+i],plus(oldP,value,-1),E[i]);
  M[4]=value;
 }
 addBlock(2,0,H0,1);const Y0=[M[2].slice(),M[3].slice()];
 swapQuery();addBlock(0,2,H1,-1);const X1=[M[0].slice(),M[1].slice()];
 swapQuery();assert.deepEqual([M[2],M[3]],Y0);assert.deepEqual(M[4],id[4]);
 addBlock(2,0,H2,1);
 for(let i=0;i<2;i++){const old=M[i];M[i]=M[2+i];M[2+i]=old.map(v=>-v||0);}
 const expectedX=Y0.map(row=>row.slice());
 for(let i=0;i<2;i++)for(let j=0;j<2;j++)expectedX[i]=plus(expectedX[i],X1[j],H2[i][j]);
 assert.deepEqual(M.slice(0,2),expectedX);assert.deepEqual(M.slice(2,4),X1.map(row=>row.map(v=>-v||0)));
 assert.notDeepEqual(matrixProduct(H1,H2),matrixProduct(H2,H1));
 return {H0,H1,H2,Q,E,noncommuting:true,exact_final_matrix:M,
  scalar_identity_assumed:false,bank_restored:true,
  general_equations:{T:"I-EQ",Y0:"Y+H0 X",Y1:"T Y0+E d",X1:"X-H1 Y1",
   second_swap:"Y2=Y0 and P=d",terminal:"X_out=Y0+H2 X1; Y_out=-X1"},
  native_gate:"The same future query Q and its right inverse E must be legal at both pre-Y contacts after actual owner transports",
  still_unpaid:["native bank path","main-output correction","complete recursive invoice"]};
}
function main(){
 const report={
  schema:"kappa-recovery-relay-probes-v1",
  status:"PASS scalar recovery probes; native supplier and new kappa NOT established",
  recovery_date:"2026-10-21",
  provenance:{
   original_scientific_sources_available:false,
   reconstruction_of_missing_files:false,
   model_source:"function source retained in functions.store across workspace reset",
   modular_prime:65521,
   integer_arithmetic:"Small exact integer matrices; elimination products below 2^53",
   rank_interpretation:"Ranks over F_65521. A full-row-rank observation matrix and a larger stacked rank give a rational obstruction. A modular zero gap alone is not a rational certificate; selected positive endpoint is separately checked exactly."
  },
  signed_additive_relays:signedAdditiveMenu(),
  optional_swaps:optionalSwapMenu(),
  reused_bank_assignments:reuseMenu(),
  early_target_exchange:earlyTargetMenu(),
  selected_positive:positiveEndpoint(),
  quarter_turn:quarterTurn(),
  singular_pure_relay:singularRelay(),
  owner_mismatch_gate:ownerGate(),
  same_future_query_identity:commonFutureQuery(),
  invoice_screens:invoiceScreens(),
  source_sha256:crypto.createHash("sha256").update(fs.readFileSync(__filename)).digest("hex")
 };
 const output=process.argv[2]||path.join(__dirname,"RELAY-PROBES.json");
 fs.writeFileSync(output,JSON.stringify(report,null,2)+"\n");
 process.stdout.write(JSON.stringify({status:report.status,output,
  source_sha256:report.source_sha256,
  complete_native_supplier:false,
  recovery_positive_p1_count:report.early_target_exchange[0].successes.length})+"\n");
}
if(require.main===module)main();
module.exports={probe,probeMatrix,matrixProduct};

