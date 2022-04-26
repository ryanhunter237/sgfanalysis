"""
Functions for processing sgf files
"""

from collections import Counter
import itertools, re, typing

from sgfmill import boards, sgf, sgf_moves

property2key = {'PC':'url', 'DT':'date', 'PB':'bname', 'PW':'wname', 'BR':'brank', 'WR':'wrank',
                'TM':'main_time', 'OT':'overtime', 'RE':'result', 'SZ':'size', 'HA':'handicap', 
                'KM':'komi', 'RU':'ruleset', 'GC':'game_type'}

def get_game_string(path: str) -> str:
    """
    Args:
        path (str): Full path of sgf file

    Returns:
        The sgf string with handicap encoding errors corrected

    Raises:
        RuntimeError: If the file contains [ZZ] as a move
        RuntimeError: If the file indicates a handicap, but has no handicap moves
    """
    with open(path, encoding="utf-8") as f:
        game_str = f.read()
    if re.search(r"\[ZZ\]", game_str):
        raise RuntimeError("Sgf file contains invalid [ZZ] move")
    if re.search(r"HA\[[0-9]{1,2}\]", game_str):     
        if not re.search(r"AB\[[a-z]{2}\]", game_str):
            raise RuntimeError("Sgf file has handicap, but no handicap stones")
        game_str = fix_handicap_game_string(game_str)
    return game_str

def fix_handicap_game_string(game_str: str) -> str:
    """
    Args:
        game_str (str): The sgf game string of a handicap game

    Returns:
        The sgf game string with the handicap encoding error corrected
    """
    i = re.search(r'AB\[[a-z]{2}\]', game_str).start()
    game_str_start = game_str[:i]
    game_str_end = game_str[i:]
    handicap = int(re.search(r'HA\[([0-9]+)\]', game_str_start).group(1))
    moves = re.findall(r"(?:\[[a-z]{2}\]|\[\])", game_str_end)
    placement_strings = 'AB' + ''.join(moves[:int(handicap)]) 
    move_strings = [''.join(x) for x in zip(itertools.cycle([';W',';B']), moves[int(handicap):])]
    return game_str_start + placement_strings + ''.join(move_strings) + ')'

def get_metadata(game: sgf.Sgf_game) -> typing.Dict:
    """
    Args:
        game (sgf.Sgf_game): The sgf game
    
    Returns:
        Dictionary of game metadata
    """
    metadata = {}
    root = game.get_root()
    for key, value in property2key.items():
        try:
            metadata[value] = root.get(key)
        except (KeyError, ValueError):
            metadata[value] = None
    metadata['url'] = metadata['url'][5:]
    metadata['game_id'] = metadata['url'].split("/")[-1]
    metadata['num_moves'] = len(game.get_main_sequence()) - 1
    game_type, ranked = metadata['game_type'].split(",")
    metadata['game_type'] = game_type
    metadata['ranked'] = (ranked == "ranked")
    metadata['winner'] = metadata['result'][0]
    if metadata['winner'] not in ['B', 'W']:
        metadata['winner'] = None
        
    return metadata

def get_empty_triangles(game: sgf.Sgf_game) -> typing.List[int]:
    """
    Args:
        game (sgf.Sgf_game): The sgf game

    Returns: 
        List of the move numbers for moves which create empty triangles
    """
    board, plays = sgf_moves.get_setup_and_moves(game)
    empty_triangles = []
    for move_num, (color, move) in enumerate(plays):
        if move is None:
            continue
        row, col = move
        board.play(row, col, color)
        if is_empty_triangle(board, row, col, color):
            empty_triangles.append(move_num+1)
    return empty_triangles
    
# should a move be considered an empty triangle if a stone is captured in the process?
def is_empty_triangle(board: boards.Board, row: int, col: int, color: str) -> bool:
    """
    Args:
        board (boards.Board): Board representing the game's current position
        row (int): The row of the last move played
        col (int): The column of the last move played
        color (str): The color ('b' or 'w') of the last move played

    Returns:
        Whether the last move created an empty triangle
    """
    for row_delta, col_delta in itertools.product([-1,1], [-1,1]):
        if (0 <= row+row_delta < board.side) and (0 <= col+col_delta < board.side):
            counts = Counter(
                board.get(row+row_delta*i, col+col_delta*j)
                for i,j in itertools.product([0,1], [0,1])
            )
            if counts[color] == 3 and counts[None] == 1:
                return True
    return False