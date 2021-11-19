import itertools, re
from sgfmill import sgf

def fix_handicap_game_str(game_str):
    i = re.search(r'AB\[[a-z]{2}\]', game_str).start()
    game_str_start = game_str[:i]
    game_str_end = game_str[i:]
    handicap = int(re.search(r'HA\[([0-9]+)\]', game_str_start).group(1))
    moves = re.findall(r"(?:\[[a-z]{2}\]|\[\])", game_str_end)
    placement_strings = 'AB' + ''.join(moves[:int(handicap)]) 
    move_strings = [''.join(x) for x in zip(itertools.cycle([';W',';B']), moves[int(handicap):])]
    return game_str_start + placement_strings + ''.join(move_strings) + ')'