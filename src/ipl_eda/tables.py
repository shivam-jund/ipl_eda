"""Typed loaders for the tables in data/processed/.

A CSV cannot carry types. Left to a default pd.read_csv, `target_overs` ("20", "9.2") becomes a float,
nullable integers become floats and dates become text. Each loader below says what the types are.
"""
import pandas as pd

MATCHES_TEXT = ["season", "team1", "team2", "venue", "city", "toss_winner", "toss_decision", "player_of_match",
                "winner", "outcome", "method", "eliminator", "target_overs"]
MATCHES_INTEGERS = ["match_number", "winner_runs", "winner_wickets", "target_runs"]    # may be missing -> Int64
MATCHES_DATES = ["start_date", "end_date"]

INNINGS_TEXT = ["batting_team", "bowling_team"]
INNINGS_BOOLEANS = ["is_super_over"]


def _read(path, text, integers=(), dates=(), booleans=()):
    dtypes = {c: str for c in text} | {c: "Int64" for c in integers} | {c: bool for c in booleans}
    # Only an empty field is missing; a text value such as "NA" or "None" stays text.
    return pd.read_csv(path, dtype=dtypes, parse_dates=list(dates), date_format="%Y-%m-%d",
                       keep_default_na=False, na_values=[""])


def read_matches(path):
    """Read matches.csv with explicit types: text stays text (target_overs included), margins are Int64, dates are dates."""
    return _read(path, MATCHES_TEXT, MATCHES_INTEGERS, MATCHES_DATES)


def read_innings(path):
    """Read innings.csv with explicit types."""
    return _read(path, INNINGS_TEXT, booleans=INNINGS_BOOLEANS)
