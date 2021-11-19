import os, unittest

from sgfanalysis import utils

class TestFixingHandicapGameStrings(unittest.TestCase):
    def test_correct_string(self):
        with open(os.path.join('tests', 'files', 'handicap1.sgf'), encoding='utf-8') as f:
            game_str = f.read()
        fixed_game_str = utils.fix_handicap_game_str(game_str)
        self.assertEqual(game_str, fixed_game_str)