import os, sqlite3

from sgfmill import sgf

import utils

DB_DIR = r'C:\Users\ryanh\Databases'
GAMES_DB_NAME = 'ogs_sgf.db'
GAMES_TABLE_NAME = 'games'
GAMES_COL_NAMES = tuple(['wname', 'bname', 'wrank', 'brank',
               'main_time', 'overtime', 'result',
               'size', 'handicap', 'komi', 'ruleset',
               'game_type', 'ranked', 'num_moves', 'date',
               'url', 'filename'])
GAMES_COL_TYPES = tuple(['text', 'text', 'text', 'text',
                'integer', 'text', 'text',
                'integer', 'integer', 'real', 'text',
                'text', 'integer', 'integer', 'text',
                'text', 'text'])

def get_sgf_paths(dir):
    paths = []
    for root, _, files in os.walk(dir):
        for filename in files:
            if filename.endswith('.sgf'):
                paths.append(os.path.join(root, filename))
    return paths

def games_table_exists(con):
    cur = con.cursor()
    sql_str = f"select name from sqlite_master where type='table' and name='{GAMES_TABLE_NAME}'"
    cur.execute(sql_str)
    return bool(cur.fetchall())

def make_games_table(con):
    if games_table_exists(con):
        return
    cur = con.cursor()
    columns_and_types = [' '.join(x) for x in zip(GAMES_COL_NAMES, GAMES_COL_TYPES)]
    columns_and_types_str = ', '.join(columns_and_types)
    sql_Str = f"create table {GAMES_TABLE_NAME} ({columns_and_types_str})"
    cur.execute()
    con.commit()

def add_game_to_table(con, game_metadata):
    columns = list(game_metadata)
    values = [game_metadata[col] for col in columns]

    column_str = ', '.join(columns)
    placeholder_str = ', '.join('?' * len(columns))
    sql_str = f"insert into {GAMES_TABLE_NAME} ({column_str}) values ({placeholder_str})"

    cur = con.cursor()
    cur.execute(sql_str, values)

def update_games_table(con, sgf_dir, min_moves=0):
    paths = get_sgf_paths(sgf_dir)
    for path in paths:
        try:
            game_str = utils.get_game_string(path)
        except RuntimeError:
            continue
        try:
            game = sgf.Sgf_game.from_string(game_str)
        except ValueError:
            continue
        metadata = utils.get_metadata(game)
        if metadata['num_moves'] < min_moves:
            continue
        metadata['filename'] = os.path.split(path)[-1]
        add_game_to_table(con, metadata)
    con.commit()
