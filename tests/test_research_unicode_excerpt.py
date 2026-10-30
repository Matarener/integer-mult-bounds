"""Search excerpts must retain matches when Unicode lowercase expands text."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


def row(body, title='scope'):
    return {'kind': 'discussion', 'title': title, 'body': body, 'url': 'https://example.invalid'}


class UnicodeExcerptTests(unittest.TestCase):
    def test_expanding_prefix_does_not_move_excerpt_past_the_match(self):
        body = 'İ' * 600 + 'NEEDLE' + ' tail' * 150
        result = overlap.search([row(body)], ['needle'])[0]
        self.assertEqual(result['excerpt'], body[500:1000])
        self.assertIn('NEEDLE', result['excerpt'])
        self.assertEqual(result['matched_terms'], ['needle'])

    def test_ascii_excerpt_and_score_are_unchanged(self):
        body = 'x' * 600 + 'needle' + 'y' * 500
        result = overlap.search([row(body)], ['needle'])[0]
        self.assertEqual(result['excerpt'], body[500:1000]); self.assertEqual(result['score'], 1)

    def test_card_reference_matches_keep_original_positions(self):
        body = 'İ' * 550 + ' PR #42 has the relevant claim. ' + 'x' * 600
        result = overlap.search([row(body)], ['42'], reference_terms=['42'])[0]
        self.assertIn('PR #42 has the relevant claim.', result['excerpt'])
        self.assertNotIn('body', result)

    def test_first_body_hit_and_title_only_fallback_remain_distinct(self):
        body = 'İ' * 550 + 'first' + 'x' * 600 + 'second'
        result = overlap.search([row(body)], ['second', 'first'], all_terms=True)[0]
        self.assertEqual(result['excerpt'], body[450:950])
        self.assertEqual(overlap.search([row(body, 'title needle')], ['needle'])[0]['excerpt'], body[:500])

    def test_match_inside_an_expanded_character_maps_to_that_character(self):
        body = 'x' * 600 + 'İ' + 'y' * 500
        result = overlap.search([row(body)], ['\u0307'])[0]
        self.assertEqual(result['excerpt'], body[500:1000])


if __name__ == '__main__':
    unittest.main()
