"""Reference tables (data/reference/) and the function that adds their keys to the fact tables.

teams.csv    one row per raw team string -> its franchise (the franchise's current name)
seasons.csv  one row per raw season label -> the calendar year of its matches
"""
import pandas as pd

# Columns that hold a raw team string in the fact tables (matches, innings).
TEAM_COLUMNS = ["batting_team", "bowling_team", "team1", "team2", "toss_winner", "winner", "eliminator"]


def _no_blanks(table, path):
    """A reference table must be filled in everywhere: a blank key would silently turn into a missing value in every row that uses it."""
    blanks = table.isna().sum()
    if blanks.any():
        raise ValueError(f"{path}: blank value(s) in {blanks[blanks > 0].to_dict()}")
    return table


def read_teams(path):
    """teams.csv: text columns `team` (raw string) and `franchise`. A blank in either column raises."""
    return _no_blanks(pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""]), path)


def read_seasons(path):
    """seasons.csv: `season` (raw label, text) and `season_year` (integer). A blank in either column raises."""
    return _no_blanks(pd.read_csv(path, dtype={"season": str, "season_year": "int64"}, keep_default_na=False, na_values=[""]), path)


def _lookup(values, mapping, what):
    """Look `values` up in a one-row-per-key table. A value that is not in the table raises; a missing value stays missing."""
    unmapped = sorted(set(values.dropna()) - set(mapping.index))
    if unmapped:
        raise ValueError(f"{what}: not in the reference table: {unmapped}")
    keyed = values.to_frame("raw").merge(mapping.rename("key"), how="left", left_on="raw", right_index=True,
                                         validate="many_to_one")
    if len(keyed) != len(values):
        raise ValueError(f"{what}: the join changed the row count")
    return keyed["key"].set_axis(values.index)


def add_keys(table, teams, seasons, matches=None):
    """Return a copy of `table` with key columns added next to the raw ones. The raw columns are not changed.

    - `<column>_franchise` for each raw team column the table has (see TEAM_COLUMNS)
    - `season_year`, from the table's own `season` column - or, for a table without one (innings), from `matches` by match_id

    An unmapped value raises. A missing value stays missing. The row count must not change.
    """
    franchise = teams.set_index("team")["franchise"]
    year = seasons.set_index("season")["season_year"]
    out = table.copy()

    for column in [c for c in TEAM_COLUMNS if c in table.columns]:
        out.insert(out.columns.get_loc(column) + 1, f"{column}_franchise", _lookup(table[column], franchise, column))

    if "season" in table.columns:
        season, after = table["season"], "season"
    elif matches is not None:
        season = _lookup(table["match_id"], matches.set_index("match_id")["season"], "match_id")
        after = "match_id"
    else:
        return out
    out.insert(out.columns.get_loc(after) + 1, "season_year", _lookup(season, year, "season"))

    if len(out) != len(table):
        raise ValueError("adding keys changed the row count")
    return out
