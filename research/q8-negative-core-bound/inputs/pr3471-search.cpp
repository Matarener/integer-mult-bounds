// SPDX-License-Identifier: Apache-2.0
// Exact finite Q8 word search. Nick Petalas.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using State = std::array<std::uint32_t, 4>;
struct Factor { unsigned u, v, g; };
struct Hash {
    std::size_t operator()(const State& a) const {
        std::size_t h = 0;
        for (auto x : a) h ^= std::hash<std::uint32_t>{}(x) + 0x9e3779b9U + (h << 6) + (h >> 2);
        return h;
    }
};
using Set = std::unordered_set<State, Hash>;
using Table = std::array<std::array<unsigned, 256>, 8>;

void require(bool ok, const std::string& message) {
    if (!ok) throw std::runtime_error(message);
}
unsigned group(unsigned a, unsigned b) {
    // Encoding: 1,z,i,zi,j,zj,k,zk; i*j=k and j*i=zk.
    const unsigned x = a >> 1, y = b >> 1;
    const unsigned neg = (a & 1U) ^ (b & 1U) ^
        static_cast<unsigned>((x != 0 && x == y) || (x == 2 && y == 1) ||
                              (x == 3 && y == 2) || (x == 1 && y == 3));
    return ((x ^ y) << 1) | neg;
}
Table table() {
    Table t{};
    for (unsigned g = 0; g < 8; ++g)
        for (unsigned a = 0; a < 256; ++a)
            for (unsigned h = 0; h < 8; ++h)
                if ((a >> h) & 1U) t[g][a] ^= 1U << group(h, g);
    return t;
}
State identity(unsigned r) {
    State a{};
    for (unsigned k = 0; k < r; ++k) a[k] = 1U << (8 * k);
    return a;
}
std::vector<Factor> alphabet(unsigned r, bool inverse) {
    require(r >= 1 && r <= 4, "role limit");
    std::vector<Factor> out;
    for (unsigned u = 1; u < (1U << r); ++u)
        for (unsigned v = 1; v < (1U << r); ++v)
            if ((__builtin_popcount(u & v) & 1) != 0)
                for (unsigned g : {2U, 4U}) out.push_back({u, v, g + unsigned(inverse)});
    return out;
}
State step(State a, Factor f, unsigned r, const Table& t) {
    for (unsigned row = 0; row < r; ++row) {
        unsigned s = 0;
        for (unsigned k = 0; k < r; ++k)
            if ((f.u >> k) & 1U) s ^= (a[row] >> (8 * k)) & 255U;
        const unsigned delta = s ^ t[f.g][s];
        for (unsigned col = 0; col < r; ++col)
            if ((f.v >> col) & 1U) a[row] ^= delta << (8 * col);
    }
    return a;
}
State target_right(State a, const std::string& target, unsigned r, const Table& t) {
    require(target.size() == r, "target width");
    for (unsigned row = 0; row < r; ++row) {
        std::uint32_t b = 0;
        for (unsigned col = 0; col < r; ++col) {
            const unsigned g = unsigned(target[col] - '0');
            require(g < 8, "target group element");
            b |= t[g][(a[row] >> (8 * col)) & 255U] << (8 * col);
        }
        a[row] = b;
    }
    return a;
}
std::vector<State> ball(unsigned r, unsigned depth, bool inverse, const Table& t) {
    require(depth <= (r == 4 ? 2U : 3U), "stored depth limit");
    const auto factors = alphabet(r, inverse);
    std::vector<State> frontier{identity(r)};
    Set seen{identity(r)};
    for (unsigned d = 0; d < depth; ++d) {
        std::vector<State> next;
        for (const auto& a : frontier)
            for (auto f : factors) {
                const auto b = step(a, f, r, t);
                if (seen.insert(b).second) next.push_back(b);
            }
        frontier = std::move(next);
    }
    return {seen.begin(), seen.end()};
}
void emit_state(std::ostream& out, State a) {
    for (auto x : a)
        for (unsigned k = 0; k < 4; ++k) out.put(static_cast<char>((x >> (8 * k)) & 255U));
    require(bool(out), "state output failure");
}
void dump_ball(std::vector<State> states, const std::string& path) {
    std::sort(states.begin(), states.end());
    std::ofstream out(path, std::ios::binary);
    require(bool(out), "cannot open ball dump");
    for (auto a : states) emit_state(out, a);
    out.close();
    require(bool(out), "cannot close ball dump");
}
void search(unsigned r, unsigned left, unsigned right, const std::vector<std::string>& targets,
            const std::string& tag, const std::string& dir, const Table& t) {
    require(left <= 3 && right >= 1 && right <= 4, "search depth limit");
    const auto inverse_ball = ball(r, left, true, t);
    const auto factors = alphabet(r, false);
    const auto prefixes = ball(r, right - 1, false, t);
    std::vector<Set> wanted;
    for (const auto& target : targets) {
        Set s;
        for (auto a : inverse_ball) s.insert(target_right(a, target, r, t));
        wanted.push_back(std::move(s));
    }
    std::vector<std::uint64_t> hits(targets.size(), 0);
    std::uint64_t candidates = 0;
    for (auto a : prefixes) {
        // Includes the empty suffix; every <=right word is either in the
        // prefix ball or one legal extension of that ball.
        for (std::size_t k = 0; k < targets.size(); ++k) hits[k] += wanted[k].count(a);
        ++candidates;
        for (auto f : factors) {
            const auto b = step(a, f, r, t);
            for (std::size_t k = 0; k < targets.size(); ++k) hits[k] += wanted[k].count(b);
            ++candidates;
        }
    }
    dump_ball(inverse_ball, dir + "/" + tag + "-inverse.bin");
    dump_ball(prefixes, dir + "/" + tag + "-prefix.bin");
    std::cout << "{\"tag\":\"" << tag << "\",\"r\":" << r << ",\"left\":" << left
              << ",\"right\":" << right << ",\"factors\":" << factors.size()
              << ",\"inverse_ball\":" << inverse_ball.size() << ",\"prefix_ball\":" << prefixes.size()
              << ",\"candidates\":" << candidates << ",\"hits\":[";
    for (std::size_t k = 0; k < hits.size(); ++k) std::cout << (k == 0 ? "" : ",") << hits[k];
    std::cout << "]}" << std::endl;
}
void probes(const std::string& path, const Table& t) {
    std::ofstream out(path, std::ios::binary);
    require(bool(out), "cannot open probe dump");
    for (unsigned a = 0; a < 8; ++a)
        for (unsigned b = 0; b < 8; ++b) out.put(static_cast<char>(group(a, b)));
    for (unsigned r = 1; r <= 4; ++r) {
        const auto factors = alphabet(r, false);
        for (auto f : factors) {
            auto a = step(identity(r), f, r, t);
            emit_state(out, a);
            a = step(a, {f.u, f.v, f.g + 1}, r, t);
            require(a == identity(r), "factor inverse law");
        }
        std::uint32_t seed = 117;
        for (unsigned n = 0; n < 1024; ++n) {
            auto a = identity(r);
            for (unsigned depth = 0; depth < 5; ++depth) {
                seed = seed * 1664525U + 1013904223U;
                a = step(a, factors[seed % factors.size()], r, t);
            }
            emit_state(out, a);
            emit_state(out, target_right(a, std::string(r, '3'), r, t));
        }
    }
    out.close();
    require(bool(out), "cannot close probe dump");
}
int main(int argc, char** argv) {
    try {
        require(argc == 3, "usage: search MODE OUTPUT_DIRECTORY");
        const std::string mode = argv[1], dir = argv[2];
        const auto t = table();
        if (mode == "probes") probes(dir + "/probes.bin", t);
        else if (mode == "search") {
            search(3, 2, 3, {"332", "334", "352"}, "r3-two", dir, t);
            search(3, 3, 4, {"333", "335"}, "r3-three", dir, t);
            search(4, 2, 3, {"3320", "3340", "3520"}, "r4-two", dir, t);
            search(4, 2, 2, {"3300", "3500"}, "r4-pair", dir, t);
            search(3, 1, 2, {"222", "224", "242"}, "positive-control", dir, t);
        } else throw std::runtime_error("unknown mode");
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
