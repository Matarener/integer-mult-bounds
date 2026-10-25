// Code-disjoint two-stage projection/lift replay. Apache-2.0.
// Only the frozen predecessor README/model/CENSUS were read, not its code.
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Word = std::vector<unsigned>;
using Count = std::uint64_t;

static void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

static unsigned popcount(Count x) {
    x -= (x >> 1U) & UINT64_C(0x5555555555555555);
    x = (x & UINT64_C(0x3333333333333333)) + ((x >> 2U) & UINT64_C(0x3333333333333333));
    x = (x + (x >> 4U)) & UINT64_C(0x0f0f0f0f0f0f0f0f);
    return static_cast<unsigned>((x * UINT64_C(0x0101010101010101)) >> 56U);
}

struct TargetBits {
    std::array<Count, 128> low{};
    std::array<Count, 128> high{};
    unsigned sources;
    unsigned target_count = 0;
    TargetBits(unsigned n, unsigned weight) : sources(n) {
        for (unsigned mask = 1; mask < (1U << n); ++mask) {
            if (popcount(mask) <= weight) {
                if (mask < 64) low[mask] = Count(1) << mask;
                else high[mask] = Count(1) << (mask - 64);
                ++target_count;
            }
        }
    }
};

static unsigned coverage(const Word& word, const TargetBits& targets) {
    require(word.size() <= 32, "bounded native word length");
    std::array<unsigned, 32> prefix{};
    unsigned parity = 0;
    for (std::size_t i = 0; i < word.size(); ++i) {
        require(word[i] < targets.sources, "source index range");
        prefix[i] = parity;                 // q_0,...,q_(L-1), not q_L.
        parity ^= 1U << word[i];
    }
    require(parity == 0, "unrestored source word");
    Count low = 0, high = 0;
    for (std::size_t b = 1; b < word.size(); ++b) {
        const unsigned right = prefix[b];
        for (std::size_t a = 0; a < b; ++a) {
            const unsigned mask = prefix[a] ^ right;
            low |= targets.low[mask];
            high |= targets.high[mask];
        }
    }
    return popcount(low) + popcount(high);
}

static Count canonical_pack(const Word& word) {
    std::array<int, 8> names{};
    names.fill(-1);
    unsigned next = 0;
    Count packed = 0;
    for (unsigned old : word) {
        require(old < names.size(), "canonical source label");
        if (names[old] < 0) names[old] = static_cast<int>(next++);
        packed = (packed << 3U) | static_cast<unsigned>(names[old]);
    }
    return packed;
}

static Word unpack(Count packed, unsigned length) {
    Word word(length);
    for (unsigned i = length; i > 0; --i) {
        word[i - 1] = static_cast<unsigned>(packed & 7U);
        packed >>= 3U;
    }
    require(packed == 0, "packed word width");
    return word;
}

template<class Visit>
static void insert_four(const Word& core, unsigned label, Visit visit) {
    const unsigned length = static_cast<unsigned>(core.size()) + 4;
    Word word(length);
    for (unsigned a = 0; a + 3 < length; ++a)
    for (unsigned b = a + 1; b + 2 < length; ++b)
    for (unsigned c = b + 1; c + 1 < length; ++c)
    for (unsigned d = c + 1; d < length; ++d) {
        unsigned old = 0;
        for (unsigned position = 0; position < length; ++position) {
            word[position] = (position == a || position == b || position == c || position == d)
                             ? label : core[old++];
        }
        require(old == core.size(), "lift retains every old source event");
        visit(word);
    }
}

struct StageFive {
    Count canonical_words = 0;
    std::map<unsigned, Count> histogram;
    std::vector<Word> full;
};

static StageFive five_source(const TargetBits& targets) {
    StageFive result;
    Word word(12);
    std::array<unsigned, 5> remaining{};
    // A restricted-growth recursion: new labels are introduced in first-
    // appearance order. Exactly one new label gets multiplicity four and
    // four labels get multiplicity two; the heavy label is not fixed to0.
    std::function<void(unsigned, unsigned, unsigned, unsigned)> visit;
    visit = [&](unsigned position, unsigned used, unsigned heavy, unsigned light) {
        if (position == word.size()) {
            require(used == 5 && heavy == 0 && light == 0, "five-source profile exhausted");
            for (unsigned value : remaining) require(value == 0, "complete multiplicity budget");
            ++result.canonical_words;
            const unsigned count = coverage(word, targets);
            ++result.histogram[count];
            if (count == targets.target_count) result.full.push_back(word);
            return;
        }
        for (unsigned label = 0; label < used; ++label) {
            if (remaining[label]) {
                word[position] = label;
                --remaining[label];
                visit(position + 1, used, heavy, light);
                ++remaining[label];
            }
        }
        if (used < 5 && heavy) {
            word[position] = used;
            remaining[used] = 3;
            visit(position + 1, used + 1, heavy - 1, light);
            remaining[used] = 0;
        }
        if (used < 5 && light) {
            word[position] = used;
            remaining[used] = 1;
            visit(position + 1, used + 1, heavy, light - 1);
            remaining[used] = 0;
        }
    };
    visit(0, 0, 1, 4);
    require(result.canonical_words == 51975, "five-source complete canonical count");
    return result;
}

static void write_word(std::ostream& out, const Word& word) {
    out << '[';
    for (std::size_t i = 0; i < word.size(); ++i) {
        if (i) out << ',';
        out << word[i];
    }
    out << ']';
}

template<class Key>
static void write_histogram(std::ostream& out, const std::map<Key, Count>& histogram) {
    out << '{';
    bool first = true;
    for (const auto& entry : histogram) {
        if (!first) out << ',';
        first = false;
        out << '"' << entry.first << "\":" << entry.second;
    }
    out << '}';
}

struct Controls {
    unsigned full22, old_weight3, old_weight4, changed_order;
    unsigned swap_position;
};

static Controls controls() {
    const TargetBits seven4(7, 4), seven3(7, 3), six4(6, 4);
    const Word full22{0,6,1,6,2,3,0,6,3,4,6,2,3,5,6,3,4,6,1,3,5,3};
    const Word old18{0,1,2,3,0,2,4,5,3,4,2,6,5,2,1,4,6,4};
    const Word six16{0,1,2,0,3,2,4,5,4,3,4,5,1,5,4,5};
    require(coverage(six16, six4) == 56, "retained six-source full witness");
    Controls result{coverage(full22, seven4), coverage(old18, seven3), coverage(old18, seven4), 0, 0};
    require(result.full22 == 98 && result.old_weight3 == 63 && result.old_weight4 == 91,
            "retained restored coverage controls");
    bool changed = false;
    for (std::size_t i = 0; i + 1 < full22.size(); ++i) {
        Word mutant = full22;
        std::swap(mutant[i], mutant[i + 1]);
        const unsigned count = coverage(mutant, seven4);
        if (count != result.full22) {
            result.changed_order = count;
            result.swap_position = static_cast<unsigned>(i);
            changed = true;
            break;
        }
    }
    require(changed, "order mutation must change coverage");
    Word unrestored = full22;
    unrestored.pop_back();
    bool rejected = false;
    try { (void)coverage(unrestored, seven4); }
    catch (const std::runtime_error& error) { rejected = std::string(error.what()) == "unrestored source word"; }
    require(rejected, "unrestored word must reject");
    return result;
}

int main(int argc, char** argv) {
    try {
        bool quick = false;
        std::string output;
        for (int i = 1; i < argc; ++i) {
            const std::string arg(argv[i]);
            if (arg == "--quick") quick = true;
            else if (arg == "--output" && i + 1 < argc) output = argv[++i];
            else throw std::runtime_error("usage: census [--quick] [--output PATH]");
        }
        const Controls control = controls();
        std::ostringstream json;
        json << "{\"status\":\"PASS_CONTROLS" << (quick ? "_ONLY" : "_AND_FULL_FILTERED_L20_REPLAY")
             << "\",\"quick_only\":" << (quick ? "true" : "false")
             << ",\"controls\":{\"length22_weight4\":" << control.full22
             << ",\"retained_length18_weight3\":" << control.old_weight3
             << ",\"retained_length18_weight4\":" << control.old_weight4
             << ",\"adjacent_swap_position\":" << control.swap_position
             << ",\"adjacent_swap_weight4\":" << control.changed_order
             << ",\"unrestored_rejected\":true,\"six_source_witness_full56\":true"
             << ",\"F2_sign_reversal_is_same_operation\":true}";
        if (!quick) {
            const TargetBits five4(5, 4), six4(6, 4), seven4(7, 4);
            require(five4.target_count == 30 && six4.target_count == 56 && seven4.target_count == 98,
                    "target family sizes");
            const StageFive five = five_source(five4);
            Count six_candidates = 0, six_full_raw = 0;
            std::map<Count, Count> full_six;
            std::map<unsigned, Count> six_histogram;
            for (const Word& core : five.full) {
                insert_four(core, 5, [&](const Word& word) {
                    ++six_candidates;
                    const unsigned count = coverage(word, six4);
                    ++six_histogram[count];
                    if (count == six4.target_count) {
                        ++six_full_raw;
                        ++full_six[canonical_pack(word)];
                    }
                });
            }
            std::map<Count, Count> multiplicities;
            for (const auto& entry : full_six) ++multiplicities[entry.second];
            require(full_six.size() == 8576 && six_full_raw == 17152,
                    "complete full-six count and raw heavy-choice multiplicity");
            require(multiplicities.size() == 1 && multiplicities.begin()->first == 2,
                    "each full-six class has exactly two heavy deletions");
            Count lifts = 0, maximum_count = 0, full98 = 0;
            unsigned maximum = 0;
            Word witness;
            std::map<unsigned, Count> seven_histogram;
            for (const auto& entry : full_six) {
                const Word core = unpack(entry.first, 16);
                insert_four(core, 6, [&](const Word& word) {
                    ++lifts;
                    const unsigned count = coverage(word, seven4);
                    ++seven_histogram[count];
                    if (count == 98) ++full98;
                    if (count > maximum) {
                        maximum = count;
                        maximum_count = 1;
                        witness = word;
                    } else if (count == maximum) ++maximum_count;
                });
            }
            require(lifts == UINT64_C(41550720) && full98 == 0 && maximum == 95 && maximum_count == 940,
                    "full filtered candidate-lift replay result");
            json << ",\"five_source\":{\"canonical_words\":" << five.canonical_words
                 << ",\"full30_words\":" << five.full.size() << ",\"histogram\":";
            write_histogram(json, five.histogram);
            json << "},\"six_source_candidates\":{\"insertions\":" << six_candidates
                 << ",\"full56_raw\":" << six_full_raw << ",\"full56_canonical_unique\":" << full_six.size()
                 << ",\"multiplicity_histogram\":";
            write_histogram(json, multiplicities);
            json << ",\"filtered_candidate_histogram\":";
            write_histogram(json, six_histogram);
            json << ",\"full56_packed_canonical_words\":[";
            bool first = true;
            for (const auto& entry : full_six) {
                if (!first) json << ',';
                first = false;
                json << entry.first;
            }
            json << "]},\"seven_source_candidates\":{\"raw_lifts\":" << lifts
                 << ",\"full98_lifts\":" << full98 << ",\"candidate_lift_max_coverage\":" << maximum
                 << ",\"raw_candidate_lifts_at_max\":" << maximum_count << ",\"first_max_witness\":";
            write_word(json, witness);
            json << ",\"histogram\":";
            write_histogram(json, seven_histogram);
            json << "},\"scope\":\"Full L20 profile exclusion via necessary full-five/full-six projections; max95 and940 count only filtered raw candidate lifts, not all seven-source canonical words. No L16/L18 native replay, complete218-call theorem or new kappa is claimed.\"";
        }
        json << "}\n";
        if (output.empty()) std::cout << json.str();
        else {
            std::ofstream file(output);
            require(bool(file), "output file open");
            file << json.str();
            require(bool(file), "output file write");
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 2;
    }
}
