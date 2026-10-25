/* join_a.c - primary exact 3+1+3 join (left side of length 4) for the A4 four-role target.
 *
 * State: 4x4 matrix over F2[A4]; entry (i,j) is a 12-bit mask over the 12 group elements.
 * Paid factor f = 120*gi + n: D_N(g) = I + ([g]+[1]) x y^T, g = a (gi=0) or b (gi=1),
 * n enumerates (x,y) in F2^4 x F2^4, x,y != 0, popcount(x&y) odd, x-major then y ascending.
 * S3 = distinct products of length <= 3 (built by right multiplication, BFS).
 * Search: for every X in S3, Q = X^-1 T; Q in S3 => word of length <= 6.  For every X whose
 * minimal length is 3 and every f, Q' = D_f^-1 Q; Q' in S3 => word X f Y of length <= 7.
 * A word of length 7 whose prefix of length 3 has a shorter equivalent has a word of length <= 6,
 * which the first check covers.  The hash is GF(2)-linear so the 240 children hashes are XOR updates;
 * every accepted hit is confirmed by full-state comparison and by multiplying out the word.
 * usage: join_a MODE [threads] [sample] [seed]
 *   MODE = target | three | planted.  sample K>1 processes only X with idx%K==0 plus forced X.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

typedef struct { uint16_t m[16]; } St;

static int perm_[12][4], mul_[12][12], inv_[12];
static uint16_t LT[12][4096], RT[12][4096];
static int fx[240], fy[240], fg[240], flabel[2];
static uint64_t H6[16][2][64];

#define TBITS 24
#define TSIZE (1u << TBITS)
#define TMASK (TSIZE - 1)
#define MAXS 7000000u
static uint64_t *table_;
static St *states;
static uint8_t *level_;
static uint8_t (*word_)[3];
static uint32_t nstates;
static St T;

static uint64_t rng_state;
static uint64_t splitmix(void) {
  uint64_t z = (rng_state += 0x9E3779B97F4A7C15ull);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
  return z ^ (z >> 31);
}

static int find_perm(const int *p) {
  for (int k = 0; k < 12; k++)
    if (!memcmp(perm_[k], p, sizeof(int) * 4)) return k;
  return -1;
}

static void build_group(void) {
  int n = 0, p[4];
  for (p[0] = 0; p[0] < 4; p[0]++)
    for (p[1] = 0; p[1] < 4; p[1]++)
      for (p[2] = 0; p[2] < 4; p[2]++)
        for (p[3] = 0; p[3] < 4; p[3]++) {
          int seen = 0, inv = 0;
          for (int i = 0; i < 4; i++) seen |= 1 << p[i];
          if (seen != 15) continue;
          for (int i = 0; i < 4; i++)
            for (int j = i + 1; j < 4; j++) inv += p[i] > p[j];
          if (inv & 1) continue;
          memcpy(perm_[n++], p, sizeof p);
        }
  if (n != 12) { fprintf(stderr, "group size %d\n", n); exit(2); }
  for (int i = 0; i < 12; i++)
    for (int j = 0; j < 12; j++) {
      int q[4];
      for (int t = 0; t < 4; t++) q[t] = perm_[i][perm_[j][t]]; /* (p o q)(t) = p(q(t)) */
      mul_[i][j] = find_perm(q);
    }
  for (int i = 0; i < 12; i++)
    for (int j = 0; j < 12; j++)
      if (mul_[i][j] == 0) inv_[i] = j;
  for (int g = 0; g < 12; g++)
    for (int m = 0; m < 4096; m++) {
      uint16_t l = 0, r = 0;
      for (int k = 0; k < 12; k++)
        if (m >> k & 1) { l |= 1u << mul_[g][k]; r |= 1u << mul_[k][g]; }
      LT[g][m] = l; RT[g][m] = r;
    }
}

static void build_factors(void) {
  int pa[4] = {1, 2, 0, 3}, pb[4] = {1, 3, 2, 0}; /* a=(123), b=(124) on points 1..4 */
  flabel[0] = find_perm(pa); flabel[1] = find_perm(pb);
  int n = 0;
  for (int x = 1; x < 16; x++)
    for (int y = 1; y < 16; y++)
      if (__builtin_popcount(x & y) & 1) { fx[n] = x; fy[n] = y; n++; }
  if (n != 120) { fprintf(stderr, "idempotents %d\n", n); exit(2); }
  for (int gi = 0; gi < 2; gi++)
    for (int k = 0; k < 120; k++) {
      fx[120 * gi + k] = fx[k]; fy[120 * gi + k] = fy[k]; fg[120 * gi + k] = flabel[gi];
    }
}

static void build_hash(void) {
  uint64_t B[16][12];
  rng_state = 0x5EED0A4A4A4A4ull;
  for (int e = 0; e < 16; e++)
    for (int b = 0; b < 12; b++) B[e][b] = splitmix();
  for (int e = 0; e < 16; e++)
    for (int h = 0; h < 2; h++)
      for (int v = 0; v < 64; v++) {
        uint64_t s = 0;
        for (int b = 0; b < 6; b++)
          if (v >> b & 1) s ^= B[e][6 * h + b];
        H6[e][h][v] = s;
      }
}

static inline uint64_t hent(int e, uint16_t v) { return H6[e][0][v & 63] ^ H6[e][1][v >> 6]; }
static uint64_t hash_st(const St *s) {
  uint64_t h = 0;
  for (int e = 0; e < 16; e++) h ^= hent(e, s->m[e]);
  return h;
}

/* X <- X * D_f */
static void right_mul(St *X, int f) {
  int x = fx[f], y = fy[f], g = fg[f];
  for (int i = 0; i < 4; i++) {
    uint16_t v = 0;
    for (int k = 0; k < 4; k++)
      if (x >> k & 1) v ^= X->m[4 * i + k];
    uint16_t u = RT[g][v] ^ v;
    for (int j = 0; j < 4; j++)
      if (y >> j & 1) X->m[4 * i + j] ^= u;
  }
}

/* Q <- D_f^-1 * Q, with D_f^-1 = D_N(g^-1) */
static void left_inv(St *Q, int f) {
  int x = fx[f], y = fy[f], h = inv_[fg[f]];
  for (int j = 0; j < 4; j++) {
    uint16_t w = 0;
    for (int k = 0; k < 4; k++)
      if (y >> k & 1) w ^= Q->m[4 * k + j];
    uint16_t u = LT[h][w] ^ w;
    for (int i = 0; i < 4; i++)
      if (x >> i & 1) Q->m[4 * i + j] ^= u;
  }
}

static int64_t lookup(const St *s, uint64_t h) {
  uint32_t pos = (uint32_t)h & TMASK, tag = (uint32_t)(h >> 32);
  for (;;) {
    uint64_t e = table_[pos];
    if (!e) return -1;
    if ((uint32_t)(e >> 32) == tag) {
      uint32_t idx = (uint32_t)e - 1;
      if (!memcmp(&states[idx], s, sizeof(St))) return idx;
    }
    pos = (pos + 1) & TMASK;
  }
}

static void insert(uint32_t idx, uint64_t h) {
  uint32_t pos = (uint32_t)h & TMASK;
  while (table_[pos]) pos = (pos + 1) & TMASK;
  table_[pos] = ((h >> 32) << 32) | (uint64_t)(idx + 1);
}

static St identity(void) {
  St s; memset(&s, 0, sizeof s);
  for (int i = 0; i < 4; i++) s.m[5 * i] = 1u << 0; /* group element 0 is the identity */
  return s;
}

static uint32_t level_count[4];
static void build_S3(void) {
  states = malloc(sizeof(St) * MAXS); level_ = malloc(MAXS); word_ = malloc(3 * (size_t)MAXS);
  table_ = calloc(TSIZE, sizeof(uint64_t));
  if (!states || !level_ || !word_ || !table_) { fprintf(stderr, "oom\n"); exit(2); }
  nstates = 0;
  St id = identity();
  states[0] = id; level_[0] = 0; insert(0, hash_st(&id)); nstates = 1; level_count[0] = 1;
  uint32_t lo = 0, hi = 1;
  for (int L = 1; L <= 3; L++) {
    for (uint32_t s = lo; s < hi; s++)
      for (int f = 0; f < 240; f++) {
        St c = states[s]; right_mul(&c, f);
        uint64_t h = hash_st(&c);
        if (lookup(&c, h) >= 0) continue;
        if (nstates >= MAXS) { fprintf(stderr, "MAXS\n"); exit(2); }
        states[nstates] = c; level_[nstates] = (uint8_t)L;
        memcpy(word_[nstates], word_[s], 3); word_[nstates][L - 1] = (uint8_t)f;
        insert(nstates, h); nstates++;
      }
    lo = hi; hi = nstates; level_count[L] = hi - lo;
  }
}

static int nthreads = 2, sample = 1;
static int64_t forced = -1;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static uint64_t short_hits, long_hits, tag_matches, children, processed3;
static int best_len = 99, best_word[8];

static void record(const int *w, int len) {
  pthread_mutex_lock(&mu);
  if (len < best_len) { best_len = len; memcpy(best_word, w, sizeof(int) * len); }
  pthread_mutex_unlock(&mu);
}

static int product_is(const int *w, int len, const St *target) {
  St s = identity();
  for (int k = 0; k < len; k++) right_mul(&s, w[k]);
  return !memcmp(&s, target, sizeof(St));
}

static void *worker(void *arg) {
  int tid = (int)(intptr_t)arg;
  uint64_t sh = 0, lh = 0, tm = 0, ch = 0, p3 = 0;
  static __thread uint64_t sub[2][16][16];
  static __thread uint16_t uu[2][16][4];
  uint64_t hc[240];
  for (uint32_t idx = (uint32_t)tid; idx < nstates; idx += (uint32_t)nthreads) {
    if (sample > 1 && idx % (uint32_t)sample && (int64_t)idx != forced) continue;
    St Q = T;
    int L = level_[idx];
    for (int k = 0; k < L; k++) left_inv(&Q, word_[idx][k]);
    uint64_t hq = hash_st(&Q);
    int64_t y = lookup(&Q, hq);
    if (y >= 0) {
      int w[8], n = 0;
      for (int k = 0; k < L; k++) w[n++] = word_[idx][k];
      for (int k = 0; k < level_[y]; k++) w[n++] = word_[y][k];
      if (!product_is(w, n, &T)) { fprintf(stderr, "short hit failed replay\n"); exit(3); }
      sh++; record(w, n);
    }
    if (L != 3) continue;
    p3++;
    /* w_y for all y, then u_{gi,y} and subset hash deltas */
    uint16_t wy[16][4];
    memset(wy[0], 0, sizeof wy[0]);
    for (int yy = 1; yy < 16; yy++) {
      int k = __builtin_ctz(yy), prev = yy & (yy - 1);
      for (int j = 0; j < 4; j++) wy[yy][j] = wy[prev][j] ^ Q.m[4 * k + j];
    }
    for (int gi = 0; gi < 2; gi++) {
      int h = inv_[flabel[gi]];
      for (int yy = 1; yy < 16; yy++) {
        uint64_t r[4];
        for (int j = 0; j < 4; j++) uu[gi][yy][j] = LT[h][wy[yy][j]] ^ wy[yy][j];
        for (int i = 0; i < 4; i++) {
          r[i] = 0;
          for (int j = 0; j < 4; j++) r[i] ^= hent(4 * i + j, uu[gi][yy][j]);
        }
        sub[gi][yy][0] = 0;
        for (int xs = 1; xs < 16; xs++) sub[gi][yy][xs] = sub[gi][yy][xs & (xs - 1)] ^ r[__builtin_ctz(xs)];
      }
    }
    for (int f = 0; f < 240; f++) {
      hc[f] = hq ^ sub[f / 120][fy[f]][fx[f]];
      __builtin_prefetch(&table_[(uint32_t)hc[f] & TMASK]);
    }
    for (int f = 0; f < 240; f++) {
      uint32_t pos = (uint32_t)hc[f] & TMASK, tag = (uint32_t)(hc[f] >> 32);
      ch++;
      for (;;) {
        uint64_t e = table_[pos];
        if (!e) break;
        if ((uint32_t)(e >> 32) == tag) {
          tm++;
          St c = Q;
          const uint16_t *u = uu[f / 120][fy[f]];
          for (int i = 0; i < 4; i++)
            if (fx[f] >> i & 1)
              for (int j = 0; j < 4; j++) c.m[4 * i + j] ^= u[j];
          St chk = Q; left_inv(&chk, f);
          if (memcmp(&chk, &c, sizeof(St))) { fprintf(stderr, "incremental child mismatch\n"); exit(3); }
          uint32_t yi = (uint32_t)e - 1;
          if (!memcmp(&states[yi], &c, sizeof(St))) {
            int w[8], n = 0;
            for (int k = 0; k < 3; k++) w[n++] = word_[idx][k];
            w[n++] = f;
            for (int k = 0; k < level_[yi]; k++) w[n++] = word_[yi][k];
            if (!product_is(w, n, &T)) { fprintf(stderr, "long hit failed replay\n"); exit(3); }
            lh++; record(w, n);
          }
        }
        pos = (pos + 1) & TMASK;
      }
    }
  }
  pthread_mutex_lock(&mu);
  short_hits += sh; long_hits += lh; tag_matches += tm; children += ch; processed3 += p3;
  pthread_mutex_unlock(&mu);
  return NULL;
}

int main(int argc, char **argv) {
  const char *mode = argc > 1 ? argv[1] : "target";
  if (argc > 2) nthreads = atoi(argv[2]);
  if (argc > 3) sample = atoi(argv[3]);
  uint64_t seed = argc > 4 ? strtoull(argv[4], 0, 10) : 1;
  build_group(); build_factors(); build_hash();
  int a = flabel[0], b = flabel[1];
  int d = mul_[a][b], c = mul_[mul_[a][b]][mul_[inv_[a]][inv_[b]]];
  printf("A4 c=[%d%d%d%d] d=[%d%d%d%d] (0-based images)\n", perm_[c][0], perm_[c][1], perm_[c][2],
         perm_[c][3], perm_[d][0], perm_[d][1], perm_[d][2], perm_[d][3]);
  build_S3();
  printf("S3 distinct by minimal length: %u %u %u %u total %u\n", level_count[0], level_count[1],
         level_count[2], level_count[3], nstates);
  memset(&T, 0, sizeof T);
  int planted[7];
  if (!strcmp(mode, "target") || !strcmp(mode, "three")) {
    int t[4] = {a, b, c, !strcmp(mode, "three") ? 0 : d};
    for (int i = 0; i < 4; i++) T.m[5 * i] = 1u << t[i];
  } else if (!strcmp(mode, "planted")) {
    rng_state = seed * 0x1000003ull + 17;
    for (;;) { /* random 7-word whose two length-3 ends are minimal-length-3 classes */
      for (int k = 0; k < 7; k++) planted[k] = (int)(splitmix() % 240);
      St p = identity(), s = identity();
      for (int k = 0; k < 3; k++) right_mul(&p, planted[k]);
      for (int k = 4; k < 7; k++) right_mul(&s, planted[k]);
      int64_t ip = lookup(&p, hash_st(&p)), is = lookup(&s, hash_st(&s));
      if (ip < 0 || is < 0) { fprintf(stderr, "planted lookup failed\n"); exit(3); }
      if (level_[ip] == 3 && level_[is] == 3) { forced = ip; break; }
    }
    T = identity();
    for (int k = 0; k < 7; k++) right_mul(&T, planted[k]);
    printf("planted word:");
    for (int k = 0; k < 7; k++) printf(" %d", planted[k]);
    printf("\n");
  } else { fprintf(stderr, "mode?\n"); return 2; }
  pthread_t th[16];
  for (int t = 0; t < nthreads; t++) pthread_create(&th[t], NULL, worker, (void *)(intptr_t)t);
  for (int t = 0; t < nthreads; t++) pthread_join(th[t], NULL);
  printf("mode=%s sample=%d processed_len3=%llu children=%llu tag_matches=%llu short_hits=%llu long_hits=%llu\n",
         mode, sample, (unsigned long long)processed3, (unsigned long long)children,
         (unsigned long long)tag_matches, (unsigned long long)short_hits, (unsigned long long)long_hits);
  if (best_len < 99) {
    printf("best_word len=%d:", best_len);
    for (int k = 0; k < best_len; k++) printf(" %d", best_word[k]);
    printf("\n");
  } else printf("best_word none\n");
  return 0;
}
