"""One source-bound fixture correction for Nick Petalas's PR2947 replay.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
The archived traversal and all test assertions remain unchanged.
"""
from hashlib import sha256

ORIGINAL_SHA256 = 'b7ab473dfcd784786c4e1b68faaa80f9bb0b1cd9226a845ca2fd2658dfe39a45'
BEFORE = b'''    def test_complete_inventory_and_entry_budget(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
'''
AFTER = BEFORE.replace(b'root = Path(td)', b'root = Path(td).resolve()')


def repair_fixture(raw):
    """Normalize only the budget fixture's root, rejecting a changed predecessor."""
    if sha256(raw).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('archived fixture source differs')
    if raw.count(BEFORE) != 1:
        raise ValueError('expected exactly one entry-budget fixture anchor')
    return raw.replace(BEFORE, AFTER, 1)
