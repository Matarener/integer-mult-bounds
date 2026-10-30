// Enumerate all four-axis phase witnesses through width 12.
// Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
#include <array>
#include <cstdint>
#include <iostream>

namespace {
constexpr int limit = 12;
std::array<bool, 65536> full_span{};
std::array<int, 65536> minimum;
std::array<std::array<std::uint16_t, 65536>, 16> next_character;
std::array<std::uint64_t, 65536> witness{};
std::uint64_t visited = 0;

void scan(int address, int remaining, int width, int character,
          int support, std::uint64_t packed) {
    if (address == 16) {
        ++visited;
        if (full_span[support] && width < minimum[character]) {
            minimum[character] = width;
            witness[character] = packed;
        }
        return;
    }
    scan(address + 1, remaining, width, character, support, packed);
    for (int count = 1; count <= remaining; ++count) {
        character = next_character[address][character];
        scan(address + 1, remaining - count, width + count, character,
             support | (1 << address),
             packed | (std::uint64_t(count) << (4 * address)));
    }
}
}  // namespace

int main() {
    minimum.fill(100);
    for (int support = 1; support < 65536; ++support) {
        std::array<int, 5> basis{};
        int rank = 0;
        for (int x = 0; x < 16; ++x) {
            if (!(support & (1 << x))) continue;
            int vector = 16 | x;
            for (int i = 4; i >= 0; --i) {
                if (!(vector & (1 << i))) continue;
                if (basis[i]) vector ^= basis[i];
                else {
                    basis[i] = vector;
                    ++rank;
                    break;
                }
            }
        }
        full_span[support] = rank == 5;
    }
    for (int x = 0; x < 16; ++x) {
        int pairs = 0, bit = 0;
        for (int i = 0; i < 4; ++i) {
            for (int j = i + 1; j < 4; ++j, ++bit) {
                if ((x & (1 << i)) && (x & (1 << j))) pairs |= 1 << bit;
            }
        }
        for (int character = 0; character < 65536; ++character) {
            int r = character & 3;
            int low = (character >> 2) & 15;
            int high = (character >> 6) & 15;
            int cross = character >> 10;
            next_character[x][character] = ((r + 1) & 3) | ((low ^ x) << 2)
                | ((high ^ (low & x)) << 6) | ((cross ^ pairs) << 10);
        }
    }
    scan(0, limit, 0, 0, 0, 0);
    if (visited != 30421755) return 1;
    for (int character = 0; character < 65536; ++character) {
        if (minimum[character] > limit) return 2;
        std::cout << character << ' ' << minimum[character] << ' '
                  << witness[character] << '\n';
    }
    std::cerr << "PASS_FOUR_AXIS_WITNESS_GENERATION " << visited << '\n';
}
