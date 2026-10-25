/*
 * Independent exhaustive replay of the corrected n=7, L=20 word exclusion.
 *
 * This implementation uses byte-frequency tables for pair differences and
 * reconstructs support multiplicities by reversible insertion. It does not
 * import or call either predecessor or corrected census implementation.
 * The proof of each prune and the exact finite scope are in PROOF.md.
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_N 7
#define MAX_L 20
#define MAX_STATES (1 << MAX_N)

static int n, length_, target_even, target_odd;
static int even_budget, odd_budget, max_label_count;
static int hp[MAX_STATES];
static int rem_even[MAX_L], rem_odd[MAX_L];
static int prefix_states[2][MAX_L + 1];
static int class_size[2];
static int label_count[MAX_N];
static unsigned char seen[MAX_STATES];
static unsigned char same_frequency[MAX_STATES];
static unsigned char cross_frequency[MAX_STATES];
static uint64_t nodes, closed_leaves, hits;
static uint64_t even_prunes, odd_prunes, class_prunes, room_prunes;
static uint64_t node_cap;
static int aborted;
static int even_excess, odd_excess;

static int choose2(int x) { return x * (x - 1) / 2; }

static int universal(void) {
    unsigned char covered[MAX_STATES] = {0};
    int points[MAX_L];
    int count = 0;
    for (int p = 0; p < 2; ++p)
        for (int i = 0; i < class_size[p]; ++i)
            points[count++] = prefix_states[p][i];
    for (int i = 0; i < count; ++i)
        for (int j = 0; j < count; ++j)
            covered[points[i] ^ points[j]] = 1;
    for (int x = 0; x < (1 << n); ++x)
        if (!covered[x]) return 0;
    return 1;
}

static void undo_pairs(int value, int parity, int same_size, int other_size,
                       int delta_even, int delta_odd) {
    const int *same = prefix_states[parity];
    const int *other = prefix_states[1 - parity];
    for (int i = 0; i < same_size; ++i)
        --same_frequency[value ^ same[i]];
    for (int i = 0; i < other_size; ++i)
        --cross_frequency[value ^ other[i]];
    even_excess -= delta_even;
    odd_excess -= delta_odd;
}

static void visit(int depth, int state, int used, int odd_labels) {
    if (aborted) return;
    if (node_cap && nodes >= node_cap) {
        aborted = 1;
        return;
    }
    ++nodes;

    if (depth == length_) {
        if (state != 0 || used != n || odd_labels != 0 ||
            class_size[0] != target_even || class_size[1] != target_odd)
            return;
        ++closed_leaves;
        if (universal()) ++hits;
        return;
    }

    const int remaining = length_ - depth;
    if (odd_labels + 2 * (n - used) > remaining) {
        ++room_prunes;
        return;
    }
    if (class_size[0] + rem_even[depth] < target_even ||
        class_size[1] + rem_odd[depth] < target_odd)
        return;

    const int choices = used < n ? used + 1 : n;
    for (int label = 0; label < choices && !aborted; ++label) {
        if (label_count[label] >= max_label_count) continue;
        const int next = state ^ (1 << label);
        const int last = depth == length_ - 1;
        if (last && next != 0) continue;

        int next_used = used + (label == used);
        int next_odd_labels = odd_labels + ((label_count[label] & 1) ? -1 : 1);
        int delta_even = 0, delta_odd = 0;
        int old_same_size = 0, old_other_size = 0;
        int parity = hp[next];
        int fresh = !last && !seen[next];

        if (fresh) {
            old_same_size = class_size[parity];
            old_other_size = class_size[1 - parity];

            /* New same-parity pairs have distinct differences. A difference
               already represented by either same-parity class increments the
               exact even collision excess. */
            for (int k = 0; k < old_same_size; ++k) {
                int d = next ^ prefix_states[parity][k];
                if (same_frequency[d]++) ++delta_even;
            }
            for (int k = 0; k < old_other_size; ++k) {
                int d = next ^ prefix_states[1 - parity][k];
                if (cross_frequency[d]++) ++delta_odd;
            }

            even_excess += delta_even;
            odd_excess += delta_odd;

            if (even_excess > even_budget) {
                undo_pairs(next, parity, old_same_size, old_other_size,
                           delta_even, delta_odd);
                ++even_prunes;
                continue;
            }
            if (odd_excess > odd_budget) {
                undo_pairs(next, parity, old_same_size, old_other_size,
                           delta_even, delta_odd);
                ++odd_prunes;
                continue;
            }
            if ((parity == 0 && class_size[0] >= target_even) ||
                (parity == 1 && class_size[1] >= target_odd)) {
                undo_pairs(next, parity, old_same_size, old_other_size,
                           delta_even, delta_odd);
                ++class_prunes;
                continue;
            }
            prefix_states[parity][class_size[parity]++] = next;
            seen[next] = 1;
        }

        const int old_count = label_count[label];
        ++label_count[label];
        if (fresh && ((parity == 0 && class_size[0] > target_even) ||
                      (parity == 1 && class_size[1] > target_odd))) {
            /* Kept as a separate fail-closed guard even though the earlier
               test makes this unreachable for a valid task split. */
            --label_count[label];
            --class_size[parity];
            seen[next] = 0;
            undo_pairs(next, parity, old_same_size, old_other_size,
                       delta_even, delta_odd);
            ++class_prunes;
            continue;
        }

        visit(depth + 1, next, next_used, next_odd_labels);

        label_count[label] = old_count;
        if (fresh) {
            --class_size[parity];
            seen[next] = 0;
            undo_pairs(next, parity, old_same_size, old_other_size,
                       delta_even, delta_odd);
        }
    }
}

static int parse_int(const char *s, int *out) {
    char *end = NULL;
    long x = strtol(s, &end, 10);
    if (!s[0] || !end || *end || x < 0 || x > 1000000) return 0;
    *out = (int)x;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 5 || argc > 6 ||
        !parse_int(argv[1], &n) || !parse_int(argv[2], &length_) ||
        !parse_int(argv[3], &target_even) || !parse_int(argv[4], &target_odd)) {
        fprintf(stderr, "usage: %s n length even_size odd_size [node_cap]\n", argv[0]);
        return 1;
    }
    if (n < 1 || n > MAX_N || length_ < 2 * n || length_ > MAX_L ||
        (length_ & 1) || target_even < 1 || target_odd < 1 ||
        target_even + target_odd > length_ || target_even > length_ / 2 ||
        target_odd > length_ / 2 || target_even < target_odd) {
        fprintf(stderr, "unsupported finite census parameters\n");
        return 1;
    }
    if (argc == 6) {
        char *end = NULL;
        unsigned long long cap = strtoull(argv[5], &end, 10);
        if (!argv[5][0] || !end || *end || cap == 0) {
            fprintf(stderr, "node_cap must be a positive integer\n");
            return 1;
        }
        node_cap = (uint64_t)cap;
    }

    const int half = 1 << (n - 1);
    even_budget = choose2(target_even) + choose2(target_odd) - (half - 1);
    odd_budget = target_even * target_odd - half;
    if (even_budget < 0 || odd_budget < 0) {
        fprintf(stderr, "pair-capacity necessary condition fails\n");
        return 0;
    }
    max_label_count = length_ - 2 * (n - 1);

    for (int x = 1; x < (1 << n); ++x)
        hp[x] = hp[x >> 1] ^ (x & 1);
    for (int depth = 0; depth < length_; ++depth) {
        for (int future = depth + 1; future < length_; ++future) {
            if ((future & 1) == 0) ++rem_even[depth];
            else ++rem_odd[depth];
        }
    }

    seen[0] = 1;
    prefix_states[0][class_size[0]++] = 0;
    visit(0, 0, 0, 0);

    printf("{\"n\":%d,\"length\":%d,\"split\":[%d,%d],"
           "\"even_budget\":%d,\"odd_budget\":%d,\"nodes\":\"%" PRIu64 "\","
           "\"closed_leaves\":\"%" PRIu64 "\",\"hits\":\"%" PRIu64 "\","
           "\"even_prunes\":\"%" PRIu64 "\",\"odd_prunes\":\"%" PRIu64 "\","
           "\"class_prunes\":\"%" PRIu64 "\",\"room_prunes\":\"%" PRIu64 "\","
           "\"aborted\":%s,\"complete\":%s}\n",
           n, length_, target_even, target_odd, even_budget, odd_budget,
           nodes, closed_leaves, hits, even_prunes, odd_prunes,
           class_prunes, room_prunes, aborted ? "true" : "false",
           aborted ? "false" : "true");
    return aborted ? 2 : 0;
}
