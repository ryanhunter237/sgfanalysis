import itertools, re

from sgfmill import sgf

property2key = {'PC':'url', 'DT':'date', 'PB':'bname', 'PW':'wname', 'BR':'brank', 'WR':'wrank',
                'TM':'main_time', 'OT':'overtime', 'RE':'result', 'SZ':'size', 'HA':'handicap', 
                'KM':'komi', 'RU':'ruleset', 'GC':'game_type'}

def fix_handicap_game_string(game_str):
    i = re.search(r'AB\[[a-z]{2}\]', game_str).start()
    game_str_start = game_str[:i]
    game_str_end = game_str[i:]
    handicap = int(re.search(r'HA\[([0-9]+)\]', game_str_start).group(1))
    moves = re.findall(r"(?:\[[a-z]{2}\]|\[\])", game_str_end)
    placement_strings = 'AB' + ''.join(moves[:int(handicap)]) 
    move_strings = [''.join(x) for x in zip(itertools.cycle([';W',';B']), moves[int(handicap):])]
    return game_str_start + placement_strings + ''.join(move_strings) + ')'

def get_game_string(path):
    with open(path, encoding="utf-8") as f:
        game_str = f.read()
    if re.search(r"\[ZZ\]", game_str):
        raise RuntimeError("Sgf file contains invalid [ZZ] move")
    if re.search(r"HA\[[0-9]{1,2}\]", game_str):     
        if not re.search(r"AB\[[a-z]{2}\]", game_str):
            raise RuntimeError("Sgf file has handicap, but no handicap stones")
        game_str = fix_handicap_game_string(game_str)
    return game_str

def get_metadata(game):
    metadata = {}
    root = game.get_root()
    for key, value in property2key.items():
        try:
            metadata[value] = root.get(key)
        except (KeyError, ValueError):
            metadata[value] = None
    metadata['url'] = metadata['url'][5:]
    metadata['num_moves'] = len(game.get_main_sequence()) - 1
    game_type, ranked = metadata['game_type'].split(",")
    metadata['game_type'] = game_type
    metadata['ranked'] = (ranked == "ranked")
    return metadata