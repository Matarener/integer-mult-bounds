// SPDX-License-Identifier: Apache-2.0
// Independent exact cover by active-row flags and reversible column counts.
// This implementation has no linked matrix and imports no DLX code.
#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace {
constexpr int row_limit = 4032;
constexpr int port_limit = 112;
constexpr std::uint64_t search_limit = 60000000;
void check(bool ok, const char* why) { if (!ok) throw std::runtime_error(why); }
struct Layer { int port = 0, cursor = 0, mark = 0, chosen = 0; };

class Exhaust {
    int ports[row_limit][8]{};
    int incidence[port_limit][row_limit]{};
    int length[port_limit]{}, count[port_limit]{};
    bool covered[port_limit]{};
    bool active[row_limit]{};
    int removed[row_limit]{};
    int answer[14]{};
    Layer stack[14]{};
    int width = 0, nrows = 0, fixed = 0, end = 0;
    std::uint64_t limit = 0, visited = 0;

    void choose(int id) {
        check(active[id], "inactive choice");
        for (int p : ports[id]) {
            check(!covered[p], "covered port chosen"); covered[p] = true;
        }
        for (int p : ports[id]) {
            for (int k = 0; k < length[p]; ++k) {
                const int other = incidence[p][k];
                if (!active[other]) continue;
                check(end < row_limit, "removal capacity");
                active[other] = false; removed[end++] = other;
                for (int q : ports[other]) --count[q];
            }
        }
    }

    void restore(const Layer& layer) {
        for (int k = 0; k < row_limit && end > layer.mark; ++k) {
            const int id = removed[--end];
            check(!active[id], "duplicate restoration"); active[id] = true;
            for (int p : ports[id]) ++count[p];
        }
        check(end == layer.mark, "restoration bound");
        for (int p : ports[layer.chosen]) covered[p] = false;
    }

    int minimum() const {
        int result = -1;
        for (int p = 0; p < width; ++p) {
            if (!covered[p] && (result < 0 || count[p] < count[result])) result = p;
        }
        return result;
    }

public:
    void input() {
        check(static_cast<bool>(std::cin >> width >> nrows >> fixed >> limit), "header");
        check(width > 0 && width <= port_limit && nrows > 0 && nrows <= row_limit &&
              fixed >= 0 && fixed <= 14 && limit <= search_limit, "input bounds");
        for (int k = 0; k < fixed; ++k) {
            check(static_cast<bool>(std::cin >> answer[k]), "fixed input");
            check(answer[k] >= 0 && answer[k] < nrows, "fixed bounds");
        }
        for (int id = 0; id < nrows; ++id) {
            bool present[port_limit]{};
            for (int& p : ports[id]) {
                check(static_cast<bool>(std::cin >> p), "row input");
                check(p >= 0 && p < width && !present[p], "invalid port");
                present[p] = true; incidence[p][length[p]++] = id; ++count[p];
            }
            active[id] = true;
        }
        std::cin >> std::ws; check(std::cin.eof(), "extra input");
        for (int k = 0; k < fixed; ++k) choose(answer[k]);
    }

    const char* run(int& total) {
        int depth = 0;
        bool entering = true;
        for (std::uint64_t turn = 0; turn < 4 * limit + 100; ++turn) {
            if (entering) {
                const int p = minimum();
                if (p < 0) { total = fixed + depth; return "SAT"; }
                if (++visited > limit) return "UNKNOWN";
                if (count[p] == 0) {
                    if (depth == 0) return "UNSAT";
                    --depth; restore(stack[depth]); entering = false; continue;
                }
                check(fixed + depth < 14, "depth capacity");
                stack[depth] = {p, 0, 0, 0}; entering = false;
            } else {
                Layer& layer = stack[depth];
                int id = -1;
                for (int k = 0; k < row_limit && layer.cursor < length[layer.port]; ++k) {
                    const int next = incidence[layer.port][layer.cursor++];
                    if (active[next]) { id = next; break; }
                }
                if (id < 0) {
                    if (depth == 0) return "UNSAT";
                    --depth; restore(stack[depth]); continue;
                }
                layer.mark = end; layer.chosen = id; answer[fixed + depth] = id;
                choose(id); ++depth; entering = true;
            }
        }
        throw std::runtime_error("transition capacity");
    }

    void output(const char* verdict, int total) const {
        std::cout << "{\"status\":\"" << verdict << "\",\"nodes\":" << visited
                  << ",\"rows\":[";
        for (int k = 0; k < total; ++k) {
            if (k > 0) std::cout << ',';
            std::cout << answer[k];
        }
        std::cout << "]}\n";
        check(static_cast<bool>(std::cout), "output");
    }
};
}

int main() {
    try {
        Exhaust proof;
        proof.input();
        int total = 0;
        const char* verdict = proof.run(total);
        proof.output(verdict, total);
        return 0;
    } catch (const std::exception& problem) {
        std::cerr << problem.what() << '\n';
        return 2;
    }
}
