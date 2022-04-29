import json, os, sqlite3, typing

from sgfmill import sgf

from . import utils

GAMES_TABLE_NAME = 'games'
GAMES_COL_NAMES = tuple(['id', 'date', 'filename',
                'size', 'handicap', 'komi',
                'wname', 'bname', 'wrank', 'brank',
                'num_moves', 'winner', 'wtris', 'btris'])
GAMES_COL_TYPES = tuple(['integer not null unique', 'text', 'text',
                'integer', 'integer', 'real',
                'text', 'text', 'text', 'text',
                'integer', 'text', 'text', 'text'])

def games_table_exists(con: sqlite3.Connection) -> bool:
    """
    Determine if the games table exists in a SQLite database

    Args:
        con: Connection to SQLite database

    Returns:
        Whether the games table already exists
    """
    cur = con.cursor()
    sql_str = f"select name from sqlite_master where type='table' and name='{GAMES_TABLE_NAME}'"
    cur.execute(sql_str)
    return bool(cur.fetchall())

def make_games_table(con: sqlite3.Connection):
    """
    Create a games table in a SQLite database

    Args:
        con: Connection to SQLite database

    Raises:
        RuntimeError: If the games table already exists
    """
    if games_table_exists(con):
        raise RuntimeError("games table already exists")
    cur = con.cursor()
    columns_and_types = [' '.join(x) for x in zip(GAMES_COL_NAMES, GAMES_COL_TYPES)]
    columns_and_types_str = ', '.join(columns_and_types)
    sql_str = f"create table {GAMES_TABLE_NAME} ({columns_and_types_str})"
    cur.execute(sql_str)
    con.commit()

def update_games_table(con: sqlite3.Connection, sgf_paths: typing.List[str], min_moves: int=20):
    """
    Add the games in the given paths to the games table in the SQLite database

    Args:
        con: Connection to SQLite database
        sgf_paths: List of sgf file paths for the games to add
        min_moves: Do not add any games with fewer than this many movess
    """
    values = []
    for path in sgf_paths:
        try:
            game_str = utils.get_game_string(path)
        except RuntimeError:
            continue
        try:
            game = sgf.Sgf_game.from_string(game_str)
        except ValueError:
            continue
        try:
            metadata = utils.get_metadata(game)
        except TypeError:
            continue
        if metadata['num_moves'] < min_moves:
            continue
        metadata['filename'] = os.path.split(path)[-1]
        try:
            empty_triangles = utils.get_empty_triangles_by_color(game)
        except ValueError:
            print(f"Error in {path}")
            continue
        metadata['wtris'] = json.dumps(empty_triangles['w'], separators=(',',':'))
        metadata['btris'] = json.dumps(empty_triangles['b'], separators=(',',':'))
        values.append(tuple(metadata.get(col) for col in GAMES_COL_NAMES))
    cur = con.cursor()
    place_holder = ", ".join(['?'] * len(GAMES_COL_NAMES))
    # insert data, ignoring any duplicate ids
    sql_string = f"insert or ignore into games values ({place_holder})"
    cur.executemany(sql_string, values)
    #con.commit()

def get_sgf_paths(dir: str) -> typing.List[str]:
    paths = []
    for root, _, files in os.walk(dir):
        for filename in files:
            if filename.endswith('.sgf'):
                paths.append(os.path.join(root, filename))
    return paths

def add_game_to_table(con, game_metadata):
    columns = list(game_metadata)
    values = [game_metadata[col] for col in columns]

    column_str = ', '.join(columns)
    placeholder_str = ', '.join('?' * len(columns))
    sql_str = f"insert into {GAMES_TABLE_NAME} ({column_str}) values ({placeholder_str})"

    cur = con.cursor()
    cur.execute(sql_str, values)
