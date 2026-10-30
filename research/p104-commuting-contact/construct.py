"""Commuting-write contact cascade on the PR5580 P104 word.

Pierre-Loic Doulcet (hexapode). Apache-2.0.
The source word is by Ali Romman (PR5580), GamingPuzzled (PR5569),
DreamingOfClouds (PR5561), thu-nmrc (PR5551), and the retained P104 contributors.
"""

from copy import deepcopy


def need(ok, why):
    if not ok:
        raise ValueError(why)


def construct_fixed_endpoints(source):
    """Stage A: Commute four ADD writes into port 198 from helpers 648, 649, 650, 652
    before 198's move 3 -> 597 at event 13528, keeping all 735 initial/final frames fixed.
    """
    word = deepcopy(source)
    old = source['program']
    expected = {
        13528: ['MOVE', 198, 3, 597, False],
        13529: ['ADD', 198, 710, '2', 597],
        13624: ['MOVE', 648, 3, 597, False],
        13625: ['ADD', 198, 648, '1/2', 597],
        13627: ['MOVE', 649, 3, 597, False],
        13628: ['ADD', 198, 649, '-1/2', 597],
        13630: ['MOVE', 650, 3, 597, False],
        13631: ['ADD', 198, 650, '1/2', 597],
        13633: ['MOVE', 652, 3, 597, False],
        13634: ['ADD', 198, 652, '1/2', 597],
        13770: ['MOVE', 648, 597, 120, False],
        13772: ['MOVE', 649, 597, 120, False],
        13774: ['MOVE', 650, 597, 120, False],
        13778: ['MOVE', 652, 597, 120, False],
    }
    need(len(old) == 25140, 'Exact PR5580 source event count')
    need(all(old[i] == e for i, e in expected.items()), 'Exact Stage A source contacts')
    replacement = {
        13528: [
            ['ADD', 198, 648, '1/2', 3],
            ['ADD', 198, 649, '-1/2', 3],
            ['ADD', 198, 650, '1/2', 3],
            ['ADD', 198, 652, '1/2', 3],
            ['MOVE', 198, 3, 597, False],
        ],
        13624: [],
        13625: [],
        13627: [],
        13628: [],
        13630: [],
        13631: [],
        13633: [],
        13634: [],
        13770: [['MOVE', 648, 3, 120, False]],
        13772: [['MOVE', 649, 3, 120, False]],
        13774: [['MOVE', 650, 3, 120, False]],
        13778: [['MOVE', 652, 3, 120, False]],
    }
    word['program'] = [
        e for i, old_event in enumerate(old)
        for e in replacement.get(i, [deepcopy(old_event)])
    ]
    need(len(word['program']) == 25136, 'Exact Stage A event count (25136)')
    return word


def construct(source):
    """Full two-group commuting cascade (Stage A + Stage B):
    - Stage A: Commute 13625, 13628, 13631, 13634 (on 198 and 648, 649, 650, 652)
      before 13528 to frame 3 (0D), vacating 597 (1D) on 648, 649, 650, 652.
    - Stage B: Commute 13806 (ADD 113 += 531) before 13524 (MOVE 113: 3 -> 597) to
      frame 3 (0D), retime 13843 (ADD 197 += -531) and 14404 (ADD 507 += -531) from
      597 (1D) to 3 (0D) with initial[531] = 3, and demote 13846 (ADD 197 += 319)
      from 617 (3D) to 355 (2D), vacating 597 on 531, 197, 507 and vacating 617 on 197, 319.
    """
    word = deepcopy(source)
    old = source['program']
    expected = {
        13524: ['MOVE', 113, 3, 597, False],
        13525: ['ADD', 113, 710, '2', 597],
        13528: ['MOVE', 198, 3, 597, False],
        13529: ['ADD', 198, 710, '2', 597],
        13624: ['MOVE', 648, 3, 597, False],
        13625: ['ADD', 198, 648, '1/2', 597],
        13627: ['MOVE', 649, 3, 597, False],
        13628: ['ADD', 198, 649, '-1/2', 597],
        13630: ['MOVE', 650, 3, 597, False],
        13631: ['ADD', 198, 650, '1/2', 597],
        13633: ['MOVE', 652, 3, 597, False],
        13634: ['ADD', 198, 652, '1/2', 597],
        13770: ['MOVE', 648, 597, 120, False],
        13772: ['MOVE', 649, 597, 120, False],
        13774: ['MOVE', 650, 597, 120, False],
        13778: ['MOVE', 652, 597, 120, False],
        13806: ['ADD', 113, 531, '1', 597],
        13842: ['MOVE', 197, 3, 597, False],
        13843: ['ADD', 197, 531, '-1', 597],
        13844: ['MOVE', 197, 597, 617, False],
        13845: ['MOVE', 319, 355, 617, False],
        13846: ['ADD', 197, 319, '1', 617],
        14378: ['MOVE', 319, 617, 728, False],
        14403: ['MOVE', 507, 3, 597, False],
        14404: ['ADD', 507, 531, '-1', 597],
        14405: ['MOVE', 507, 597, 728, False],
        14477: ['MOVE', 531, 597, 741, False],
        14684: ['MOVE', 197, 617, 788, False],
    }
    need(len(old) == 25140, 'Exact PR5580 source event count')
    need(source['initial'][531] == 597 and source['final'][531] == 127, 'Exact helper 531 source endpoints')
    need(all(old[i] == e for i, e in expected.items()), 'Exact source contacts')
    word['initial'][531] = 3
    replacement = {
        13524: [
            ['ADD', 113, 531, '1', 3],
            ['MOVE', 113, 3, 597, False],
        ],
        13528: [
            ['ADD', 198, 648, '1/2', 3],
            ['ADD', 198, 649, '-1/2', 3],
            ['ADD', 198, 650, '1/2', 3],
            ['ADD', 198, 652, '1/2', 3],
            ['MOVE', 198, 3, 597, False],
        ],
        13624: [],
        13625: [],
        13627: [],
        13628: [],
        13630: [],
        13631: [],
        13633: [],
        13634: [],
        13770: [['MOVE', 648, 3, 120, False]],
        13772: [['MOVE', 649, 3, 120, False]],
        13774: [['MOVE', 650, 3, 120, False]],
        13778: [['MOVE', 652, 3, 120, False]],
        13806: [],
        13842: [],
        13843: [['ADD', 197, 531, '-1', 3]],
        13844: [['MOVE', 197, 3, 355, False]],
        13845: [],
        13846: [['ADD', 197, 319, '1', 355]],
        14378: [['MOVE', 319, 355, 728, False]],
        14403: [],
        14404: [['ADD', 507, 531, '-1', 3]],
        14405: [['MOVE', 507, 3, 728, False]],
        14477: [['MOVE', 531, 3, 741, False]],
        14684: [['MOVE', 197, 355, 788, False]],
    }
    word['program'] = [
        e for i, old_event in enumerate(old)
        for e in replacement.get(i, [deepcopy(old_event)])
    ]
    need(len(word['program']) == 25133, 'Exact cascade event count (25133)')
    return word
