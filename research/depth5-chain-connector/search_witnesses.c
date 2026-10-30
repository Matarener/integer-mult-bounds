/* Simulated annealing for a depth-K chain word with the given letter counts
   (default: M copies of each call) whose interval counts N[i..j] are 0 mod M
   except N[1..K] = C. Not part of the replay: verify.py checks the words.
   Build: cc -O2 -o anneal search_witnesses.c -lm
   Usage: ./anneal K M C SEED TRIES SWEEPS [count_1 ... count_K] */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
static unsigned long long s;
static unsigned long long rnd(void){ s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static int K, M, C, L, w[1024];
static int cost(void){
  long N[8][8] = {{0}};
  for (int t = 0; t < L; t++){ int l = w[t]; for (int i = l - 1; i >= 1; i--) N[i][l] = (N[i][l] + N[i][l-1]) % M; N[l][l]++; }
  int tot = 0;
  for (int i = 1; i <= K; i++) for (int j = i + 1; j <= K; j++){
    int want = (i == 1 && j == K) ? C : 0; int a = (int)((N[i][j] - want) % M + M) % M; tot += a < M - a ? a : M - a; }
  return tot;
}
int main(int argc, char **argv){
  K = atoi(argv[1]); M = atoi(argv[2]); C = atoi(argv[3]); s = 88172645463325252ULL ^ (unsigned long long)atoll(argv[4]) * 2654435761ULL;
  int tries = atoi(argv[5]); long sweeps = atol(argv[6]);
  int cnt[8]; for (int l = 1; l <= K; l++) cnt[l] = argc > 6 + l ? atoi(argv[6 + l]) : M;
  for (int a = 0; a < tries; a++){
    L = 0; for (int l = 1; l <= K; l++) for (int k = 0; k < cnt[l]; k++) w[L++] = l;
    for (int t = L - 1; t > 0; t--){ int u = rnd() % (t + 1); int x = w[t]; w[t] = w[u]; w[u] = x; }
    int cur = cost(); double T = 2.0;
    for (long it = 0; it < sweeps && cur; it++){
      int i = rnd() % L, j = rnd() % L; if (w[i] == w[j]) continue;
      int x = w[i]; w[i] = w[j]; w[j] = x; int nw = cost();
      if (nw <= cur || (rnd() % 1000000) / 1e6 < exp((cur - nw) / T)) cur = nw; else { w[j] = w[i]; w[i] = x; }
      T = T * 0.99999; if (T < 0.3) T = 0.3;
    }
    if (!cur){ printf("%d %d %d ", M, C, a); for (int t = 0; t < L; t++) printf("%d", w[t]); printf("\n"); return 0; }
  }
  printf("%d %d NONE\n", M, C); return 1;
}
