import os, unittest

from sgfanalysis import utils

class TestFixingHandicapGameStrings(unittest.TestCase):
    def get_sgf_str(self, filename):
        with open(os.path.join('tests', 'files', filename), encoding='utf-8') as f:
            game_str = f.read()
        return game_str

    def test_no_change_one_handicap(self):
        game_str = self.get_sgf_str('handicap1.sgf')
        fixed_game_str = utils.fix_handicap_game_str(game_str)
        self.assertEqual(game_str, fixed_game_str)

    def test_correct_two_handicap(self):
        self.maxDiff = None
        game_str = self.get_sgf_str('handicap2_error.sgf')
        correct_game_str = self.get_sgf_str('handicap2_corrected.sgf')
        fixed_game_str = utils.fix_handicap_game_str(game_str)
        self.assertEqual(correct_game_str, fixed_game_str)
