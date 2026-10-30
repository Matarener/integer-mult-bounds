/* join_b.c - independent exact join for the A4 four-role target (right side of length 4).
 *
 * Different representation from join_a: a state is sum_k [k] (x) M_k with one 4x4 F2 matrix
 * M_k per group element k, packed as 16 bits (entry (i,j) at bit 4i+j).  The group is generated
 * by closure from a and b on packed permutation codes.  S3 (distinct products of length <= 3) is
 * built by LEFT multiplication; the search runs over the RIGHT end: for every Y in S3,
 * R = T Y^-1 in S3 gives a word of length <= 6, and for every Y of minimal length 3 and every
 * paid factor f, R D_f^-1 in S3 gives a word X f Y of length <= 7.  Nonlinear hash, full compare.
 * usage: join_b MODE [threads] [sample] [seed]   MODE = target | three | planted
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

typedef struct { uint16_t g[12]; } St; /* g[k] = 4x4 F2 matrix coefficient of group element k */

static uint8_t code_[12];           /* packed permutation: image of t in bits 2t..2t+1 */
static int mulk[12][12], invk[12];  /* mulk[p][q] = index of p o q */
static int nfac = 0, fxs[240], fyx[240], fyb[240], flab[240], la, lb;
static uint16_t fxrep[240], fxspread[240];

static int img(uint8_t c, int t) { return c >> (2 * t) & 3; }
static uint8_t comp(uint8_t p, uint8_t q) { /* (p o q)(t) = p(q(t)) */
  uint8_t r = 0;
  for (int t = 0; t < 4; t++) r |= (uint8_t)(img(p, img(q, t)) << (2 * t));
  return r;
}
static int gidx(uint8_t c) {
  for (int k = 0; k < 12; k++) if (code_[k] == c) return k;
  return -1;
}

static void build(void) {
  uint8_t id = 0 | 1 << 2 | 2 << 4 | 3 << 6;
  uint8_t a = 1 | 2 << 2 | 0 << 4 | 3 << 6; /* (123): 0->1,1->2,2->0 */
  uint8_t b = 1 | 3 << 2 | 2 << 4 | 0 << 6; /* (124): 0->1,1->3,3->0 */
  int n = 0; code_[n++] = id;
  for (int i = 0; i < n; i++) {
    uint8_t c1 = comp(code_[i], a), c2 = comp(code_[i], b);
    int f1 = 0, f2 = 0;
    for (int k = 0; k < n; k++) { f1 |= code_[k] == c1; f2 |= code_[k] == c2; }
    if (!f1) code_[n++] = c1;
    if (!f2 && c2 != c1) code_[n++] = c2;
    if (n > 12) break;
  }
  if (n != 12) { fprintf(stderr, "closure size %d\n", n); exit(2); }
  for (int p = 0; p < 12; p++)
    for (int q = 0; q < 12; q++) mulk[p][q] = gidx(comp(code_[p], code_[q]));
  for (int p = 0; p < 12; p++)
    for (int q = 0; q < 12; q++) if (mulk[p][q] == 0) invk[p] = q;
  la = gidx(a); lb = gidx(b);
  for (int lab = 0; lab < 2; lab++)
    for (int x = 1; x <= 15; x++)
      for (int y = 1; y <= 15; y++) {
        int par = 0;
        for (int t = 0; t < 4; t++) par ^= (x >> t & 1) & (y >> t & 1);
        if (!par) continue;
        fxs[nfac] = x; fyx[nfac] = y; flab[nfac] = lab ? lb : la;
        fxrep[nfac] = (uint16_t)(x * 0x1111);
        uint16_t sp = 0;
        for (int t = 0; t < 4; t++) if (x >> t & 1) sp |= (uint16_t)(1u << (4 * t));
        fxspread[nfac] = sp; fyb[nfac] = y; nfac++;
      }
  if (nfac != 240) { fprintf(stderr, "factors %d\n", nfac); exit(2); }
}

/* row parities of z (bit 4i set iff row i of z has odd weight) */
static inline uint16_t rowpar(uint16_t z) { z ^= z >> 1; z ^= z >> 2; return z & 0x1111; }

/* S <- S * D_N(h): (S D)_k = S_k + (S_k + S_{k h^-1}) N, N = x y^T, Z N = rowpar(Z & xrep) * y */
static void rmul(St *s, int f, int h) {
  St o = *s;
  int hi = invk[h];
  for (int k = 0; k < 12; k++) {
    uint16_t z = o.g[k] ^ o.g[mulk[k][hi]];
    s->g[k] = o.g[k] ^ (uint16_t)(rowpar(z & fxrep[f]) * fyb[f]);
  }
}
/* S <- D_N(h) * S: (D S)_k = S_k + N (S_k + S_{h^-1 k}), N Z = (y^T Z) placed in rows of x */
static void lmul(St *s, int f, int h) {
  St o = *s;
  int hi = invk[h];
  for (int k = 0; k < 12; k++) {
    uint16_t z = o.g[k] ^ o.g[mulk[hi][k]];
    uint16_t r = 0;
    for (int t = 0; t < 4; t++) if (fyx[f] >> t & 1) r ^= (uint16_t)(z >> (4 * t) & 15);
    s->g[k] = o.g[k] ^ (uint16_t)(r * fxspread[f]);
  }
}

static uint64_t hst(const St *s) {
  uint64_t w[3];
  memcpy(w, s->g, 24);
  uint64_t h = w[0] * 0xD6E8FEB86659FD93ull;
  h ^= h >> 32; h += w[1] * 0xA0761D6478BD642Full;
  h ^= h >> 29; h += w[2] * 0xE7037ED1A0B428DBull;
  h ^= h >> 32; h *= 0x8EBC6AF09C88C6E3ull; h ^= h >> 31;
  return h;
}

#define TB 24
#define TS (1u << TB)
#define TM (TS - 1)
#define MAXS 7000000u
static uint64_t *tab; static St *st; static uint8_t *lev; static uint8_t (*wd)[3]; static uint32_t ns;
static uint32_t lcount[4];
static St T;

static int64_t find(const St *s, uint64_t h) {
  uint32_t p = (uint32_t)(h >> 40) & TM; /* index from high bits, tag from low 32 */
  uint32_t tag = (uint32_t)h;
  for (;;) {
    uint64_t e = tab[p];
    if (!e) return -1;
    if ((uint32_t)(e >> 32) == tag && !memcmp(&st[(uint32_t)e - 1], s, sizeof(St))) return (uint32_t)e - 1;
    p = (p + 1) & TM;
  }
}
static void put(uint32_t i, uint64_t h) {
  uint32_t p = (uint32_t)(h >> 40) & TM;
  while (tab[p]) p = (p + 1) & TM;
  tab[p] = (uint64_t)(uint32_t)h << 32 | (uint64_t)(i + 1);
}

static St ident(void) {
  St s; memset(&s, 0, sizeof s); s.g[0] = 0x8421; return s;
}

static void build_S3(void) {
  st = malloc(sizeof(St) * MAXS); lev = malloc(MAXS); wd = malloc(3 * (size_t)MAXS);
  tab = calloc(TS, 8);
  if (!st || !lev || !wd || !tab) { fprintf(stderr, "oom\n"); exit(2); }
  St id = ident(); st[0] = id; lev[0] = 0; put(0, hst(&id)); ns = 1; lcount[0] = 1;
  uint32_t lo = 0, hi = 1;
  for (int L = 1; L <= 3; L++) {
    for (uint32_t s = lo; s < hi; s++)
      for (int f = 0; f < 240; f++) {
        St c = st[s]; lmul(&c, f, flab[f]); /* new = D_f * old: word = f, old word */
        uint64_t h = hst(&c);
        if (find(&c, h) >= 0) continue;
        if (ns >= MAXS) { fprintf(stderr, "MAXS\n"); exit(2); }
        st[ns] = c; lev[ns] = (uint8_t)L; wd[ns][0] = (uint8_t)f;
        for (int k = 0; k < L - 1; k++) wd[ns][k + 1] = wd[s][k];
        put(ns, h); ns++;
      }
    lo = hi; hi = ns; lcount[L] = hi - lo;
  }
}

static int prod_eq(const int *w, int n, const St *t) {
  St s = ident();
  for (int k = n - 1; k >= 0; k--) lmul(&s, w[k], flab[w[k]]);
  return !memcmp(&s, t, sizeof(St));
}

static int nth = 2, samp = 1; static int64_t forced = -1;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static uint64_t n_short, n_long, n_child, n_y3;
static int best = 99, bw[8];

static void rec(const int *w, int n) {
  pthread_mutex_lock(&mu);
  if (n < best) { best = n; memcpy(bw, w, sizeof(int) * n); }
  pthread_mutex_unlock(&mu);
}

static void *work(void *arg) {
  int tid = (int)(intptr_t)arg;
  uint64_t cs = 0, cl = 0, cc = 0, c3 = 0;
  St *kid = malloc(sizeof(St) * 240); uint64_t hk[240];
  for (uint32_t yi = (uint32_t)tid; yi < ns; yi += (uint32_t)nth) {
    if (samp > 1 && yi % (uint32_t)samp && (int64_t)yi != forced) continue;
    St R = T;
    int L = lev[yi];
    for (int k = L - 1; k >= 0; k--) { int f = wd[yi][k]; rmul(&R, f, invk[flab[f]]); } /* R = T Y^-1 */
    int64_t xi = find(&R, hst(&R));
    if (xi >= 0) {
      int w[8], n = 0;
      for (int k = 0; k < lev[xi]; k++) w[n++] = wd[xi][k];
      for (int k = 0; k < L; k++) w[n++] = wd[yi][k];
      if (!prod_eq(w, n, &T)) { fprintf(stderr, "short replay failed\n"); exit(3); }
      cs++; rec(w, n);
    }
    if (L != 3) continue;
    c3++;
    for (int f = 0; f < 240; f++) {
      kid[f] = R; rmul(&kid[f], f, invk[flab[f]]); /* R D_f^-1 */
      hk[f] = hst(&kid[f]);
      __builtin_prefetch(&tab[(uint32_t)(hk[f] >> 40) & TM]);
    }
    for (int f = 0; f < 240; f++) {
      cc++;
      int64_t x = find(&kid[f], hk[f]);
      if (x < 0) continue;
      int w[8], n = 0;
      for (int k = 0; k < lev[x]; k++) w[n++] = wd[x][k];
      w[n++] = f;
      for (int k = 0; k < 3; k++) w[n++] = wd[yi][k];
      if (!prod_eq(w, n, &T)) { fprintf(stderr, "long replay failed\n"); exit(3); }
      cl++; rec(w, n);
    }
  }
  free(kid);
  pthread_mutex_lock(&mu);
  n_short += cs; n_long += cl; n_child += cc; n_y3 += c3;
  pthread_mutex_unlock(&mu);
  return NULL;
}

int main(int argc, char **argv) {
  const char *mode = argc > 1 ? argv[1] : "target";
  if (argc > 2) nth = atoi(argv[2]);
  if (argc > 3) samp = atoi(argv[3]);
  uint64_t seed = argc > 4 ? strtoull(argv[4], 0, 10) : 1;
  build();
  int c = mulk[mulk[la][lb]][mulk[invk[la]][invk[lb]]], d = mulk[la][lb];
  build_S3();
  printf("S3 distinct by minimal length: %u %u %u %u total %u\n", lcount[0], lcount[1], lcount[2], lcount[3], ns);
  memset(&T, 0, sizeof T);
  if (!strcmp(mode, "target") || !strcmp(mode, "three")) {
    int lab[4] = {la, lb, c, !strcmp(mode, "three") ? 0 : d};
    for (int i = 0; i < 4; i++) T.g[lab[i]] |= (uint16_t)(1u << (5 * i));
  } else if (!strcmp(mode, "planted")) {
    uint64_t z = seed * 0x9E3779B97F4A7C15ull + 0x1234567ull;
    int pw[7];
    for (;;) {
      for (int k = 0; k < 7; k++) { z ^= z << 13; z ^= z >> 7; z ^= z << 17; pw[k] = (int)(z % 240); }
      St p = ident(), s = ident(); /* p = product of pw[0..2], s = product of pw[4..6] */
      for (int k = 2; k >= 0; k--) lmul(&p, pw[k], flab[pw[k]]);
      for (int k = 6; k >= 4; k--) lmul(&s, pw[k], flab[pw[k]]);
      int64_t ip = find(&p, hst(&p)), is = find(&s, hst(&s));
      if (ip < 0 || is < 0) { fprintf(stderr, "planted lookup failed\n"); exit(3); }
      if (lev[ip] == 3 && lev[is] == 3) { forced = is; break; }
    }
    T = ident();
    for (int k = 6; k >= 0; k--) lmul(&T, pw[k], flab[pw[k]]);
    printf("planted word:");
    for (int k = 0; k < 7; k++) printf(" %d", pw[k]);
    printf("\n");
  } else { fprintf(stderr, "mode?\n"); return 2; }
  pthread_t th[16];
  for (int t = 0; t < nth; t++) pthread_create(&th[t], NULL, work, (void *)(intptr_t)t);
  for (int t = 0; t < nth; t++) pthread_join(th[t], NULL);
  printf("mode=%s sample=%d processed_len3=%llu children=%llu short_hits=%llu long_hits=%llu\n", mode, samp,
         (unsigned long long)n_y3, (unsigned long long)n_child, (unsigned long long)n_short, (unsigned long long)n_long);
  if (best < 99) {
    printf("best_word len=%d:", best);
    for (int k = 0; k < best; k++) printf(" %d", bw[k]);
    printf("\n");
  } else printf("best_word none\n");
  return 0;
}
