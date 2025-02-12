# Create and populate a sqlite3 database using a pgn file
# Drawing on https://github.com/EndlessTrax/pgn-to-sqlite/
# By Emma Bingham
# Feb 2025

import sqlite3
import re


def create_db(cursor):
    """
    Create the main table if it doesn't exist.
    """

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Event TEXT,
            Site TEXT,
            Round TEXT,
            White TEXT,
            Black TEXT,
            Result TEXT,
            UTCDate TEXT,
            UTCTime TEXT,
            UTCDateTime TEXT,
            WhiteElo INTEGER,
            BlackElo INTEGER,
            WhiteRatingDiff TEXT,
            BlackRatingDiff TEXT,
            WhiteTitle TEXT,
            BlackTitle TEXT,
            ECO TEXT,
            Variant TEXT,
            Opening TEXT,
            TimeControl TEXT,
            Termination TEXT,
            Moves TEXT
        );
        """,
    )


def build_pgn_dict(pgn: str) -> dict:
    """Takes any pgn text of a SINGLE GAME and coverts to a dictionary object

    The dictionary is checked against a tuple of expected keys, and if missing, 
    adds them with an empty string value. This ensures that each dictionary is 
    uniform to match the database table.

    Args:
        pgn: A PGN string

    Returns:
        A Python Dictionary
    """
    game_dict = dict()
    pgn_lines = pgn.split("\n")

    for line in pgn_lines:
        if line.startswith("["):
            key_pattern = re.compile(r"([^\s]+)")
            value_pattern = re.compile(r"\"(.+?)\"")

            key = re.search(key_pattern, line).group().lstrip("[")

            value = re.search(value_pattern, line)

            if value is not None:
                game_dict[key] = value.group().strip('"')
            else:
                game_dict[key] = ""

        # The move notation is a single line in the pgn.
        # The whole move notation is added to a single key:value
        elif line.startswith("1."):
            game_dict["Moves"] = line

    # If an expected key isn't present in the dictionary representation of the
    # pgn, then it is added with an empty string as its value.
    expected_keys = (
        "Event",
        "Site",
        "Round",
        "White",
        "Black",
        "Result",
        "UTCDate",
        "UTCTime",
        "UTCDateTime",
        "WhiteElo",
        "BlackElo",
        "WhiteRatingDiff",
        "BlackRatingDiff",
        "WhiteTitle",
        "BlackTitle",
        "ECO",
        "Variant",
        "Opening",
        "TimeControl",
        "Termination",
        "Moves",
    )

    # Make combined DateTime
    game_dict["UTCDateTime"] = game_dict["UTCDate"].replace(".","-") + " " + game_dict["UTCTime"]

    for key in expected_keys:
        if key not in game_dict:
            game_dict[key] = ""

    return game_dict


def save_game_to_db(cursor, pgn: dict) -> None:
    """Saves a Game to the Sqlite3 database

    Args:
        connection: A database connection object
        pgn: A PGN dictionary representation

    Returns:
        Nothing.
    """

    cursor.execute(
        """INSERT INTO
        games(Event, Site, Round, White, Black, Result, UTCDate, 
        UTCTime, UTCDateTime, WhiteElo, BlackElo, WhiteRatingDiff, BlackRatingDiff, 
        WhiteTitle, BlackTitle, ECO, Variant, Opening, 
        TimeControl, Termination, Moves) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        (
            pgn["Event"],
            pgn["Site"],
            pgn["Round"],
            pgn["White"],
            pgn["Black"],
            pgn["Result"],
            pgn["UTCDate"],
            pgn["UTCTime"],
            pgn["UTCDateTime"],
            pgn["WhiteElo"],
            pgn["BlackElo"],
            pgn["WhiteRatingDiff"],
            pgn["BlackRatingDiff"],
            pgn["WhiteTitle"],
            pgn["BlackTitle"],
            pgn["ECO"],
            pgn["Variant"],
            pgn["Opening"],
            pgn["TimeControl"],
            pgn["Termination"],
            pgn["Moves"],
        ),
    )


def save_games_to_db(cursor, pgn_file):
    """
    Opens a pgn file, fetches lines from it one by one until it reaches the end of
    a game, then inserts that game into db, and continues

    Trying to save on RAM here by not opening the whole file at once. I think.
    It's kind of slow though.
    """

    with open(pgn_file, "r") as f:
        previous_line = ""
        game_text = ""
        for line in f:
            game_text += line
            # fetch lines until the end of the game is reached
            # then save that game to the db
            # then 'clear' the game so we can fetch the next game
            if previous_line.startswith("1. "):
                pgn_dict = build_pgn_dict(game_text)
                save_game_to_db(cursor, pgn_dict)
                game_text = ""
            previous_line = line


if __name__ == "__main__":
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    create_db(cursor)
    save_games_to_db(cursor, "../data/lichess_db_standard_rated_2013-01.pgn")
    conn.commit()
    conn.close()
