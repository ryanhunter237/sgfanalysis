import json, os, unittest

from sgfanalysis import utils
from sgfmill import sgf

class TestFixingHandicapGameStrings(unittest.TestCase):
    def get_sgf_str(self, filename):
        with open(os.path.join('tests', 'files', filename), encoding='utf-8') as f:
            game_str = f.read()
        return game_str

    def test_no_change_one_handicap(self):
        game_str = self.get_sgf_str('handicap1.sgf')
        fixed_game_str = utils.fix_handicap_game_string(game_str)
        self.assertEqual(game_str, fixed_game_str)

    def test_correct_two_handicap(self):
        self.maxDiff = None
        game_str = self.get_sgf_str('handicap2_error.sgf')
        correct_game_str = self.get_sgf_str('handicap2_corrected.sgf')
        fixed_game_str = utils.fix_handicap_game_string(game_str)
        self.assertEqual(correct_game_str, fixed_game_str)

    def test_correct_nine_handicap(self):
        self.maxDiff = None
        game_str = self.get_sgf_str('handicap9_error.sgf')
        correct_game_str = self.get_sgf_str('handicap9_corrected.sgf')
        fixed_game_str = utils.fix_handicap_game_string(game_str)
        self.assertEqual(correct_game_str, fixed_game_str)

class TestGetMetadata(unittest.TestCase):
    def test_no_handicap_metadata(self):
        game_str = utils.get_game_string(os.path.join('tests', 'files', 'full_game_no_handicap.sgf'))
        game = sgf.Sgf_game.from_string(game_str)
        metadata = utils.get_metadata(game)

        metadata_file = "full_game_no_handicap_metadata.json"
        with open(os.path.join('tests', 'files', metadata_file), encoding='utf-8') as f:
            check_metadata = json.load(f)
        
        self.assertEqual(metadata, check_metadata)

    def test_one_handicap_metadata(self):
        game_str = utils.get_game_string(os.path.join('tests', 'files', 'full_game_one_handicap.sgf'))
        game = sgf.Sgf_game.from_string(game_str)
        metadata = utils.get_metadata(game)

        metadata_file = "full_game_one_handicap_metadata.json"
        with open(os.path.join('tests', 'files', metadata_file), encoding='utf-8') as f:
            check_metadata = json.load(f)

        self.assertEqual(metadata, check_metadata)

    def test_five_handicap_metadata(self):
        game_str = utils.get_game_string(os.path.join('tests', 'files', 'full_game_five_handicap.sgf'))
        game = sgf.Sgf_game.from_string(game_str)
        metadata = utils.get_metadata(game)

        metadata_file = "full_game_five_handicap_metadata.json"
        with open(os.path.join('tests', 'files', metadata_file), encoding='utf-8') as f:
            check_metadata = json.load(f)

        self.assertEqual(metadata, check_metadata)

class TestEmptyTriangles(unittest.TestCase):
    def test_no_handicap_empty_triangles(self):
        game_str = utils.get_game_string(os.path.join('tests', 'files', 'full_game_no_handicap.sgf'))
        game = sgf.Sgf_game.from_string(game_str)
        empty_triangles = utils.get_empty_triangles(game)

        empty_triangles_file = 'full_game_no_handicap_empty_triangles.json'
        with open(os.path.join('tests', 'files', empty_triangles_file), encoding='utf-8') as f:
            check_empty_triangles = json.load(f)

        self.assertEqual(empty_triangles, check_empty_triangles)

    def test__honeandicap_empty_triangles(self):
        game_str = utils.get_game_string(os.path.join('tests', 'files', 'full_game_one_handicap.sgf'))
        game = sgf.Sgf_game.from_string(game_str)
        empty_triangles = utils.get_empty_triangles(game)
        print(empty_triangles)
    
