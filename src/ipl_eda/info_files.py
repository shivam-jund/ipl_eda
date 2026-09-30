"""Parse Cricsheet "Ashwin" match-info files (<id>_info.csv) into pandas tables.

The steps, in the order notebooks/02_info_files.ipynb uses them:

    read_info_folder()  ->  long table: one row per info line, nothing interpreted
    check_schema()      ->  raises if the files hold anything the key survey did not expect
    build_matches()     ->  one row per match

Every line of an info file is either `version,<x>` or `info,<key>,<value>[,<value>[,<value>]]`.
"""
import csv
from pathlib import Path

import pandas as pd

# key -> (min rows per match, max rows per match, number of value fields).
# Encoded from the key survey in notebook 02, which also asserts that every entry agrees with the survey.
#   min 0         = optional key;  min 1 or more = the key must be present in every match
#   max None      = a list that may repeat freely (players, registry)
SCHEMA = {
    # exactly one row in every match
    "balls_per_over": (1, 1, 1), "event": (1, 1, 1), "gender": (1, 1, 1), "match_type": (1, 1, 1),
    "overs": (1, 1, 1), "team_type": (1, 1, 1), "match_id": (1, 1, 1), "season": (1, 1, 1),
    "venue": (1, 1, 1), "city": (1, 1, 1), "toss_winner": (1, 1, 1), "toss_decision": (1, 1, 1),
    "match_referee": (1, 1, 1),
    # optional: at most one row
    "match_number": (0, 1, 1), "player_of_match": (0, 1, 1), "tv_umpire": (0, 1, 1),
    "reserve_umpire": (0, 1, 1), "winner": (0, 1, 1), "winner_runs": (0, 1, 1),
    "winner_wickets": (0, 1, 1), "outcome": (0, 1, 1), "method": (0, 1, 1), "eliminator": (0, 1, 1),
    "target_overs": (0, 1, 2), "target_runs": (0, 1, 2),          # first field is the innings number
    # repeating
    "team": (2, 2, 1), "umpire": (2, 2, 1), "date": (1, 2, 1), "super_over": (0, 4, 1),
    "player": (22, None, 2), "registry": (26, None, 3),
}

# Same value in all 1,243 matches (notebook 02 asserts this), so they are listed, not turned into columns.
CONSTANT_KEYS = ["balls_per_over", "event", "gender", "match_type", "overs", "team_type"]

# One-to-many or not about the match itself. They stay in the long table but not in `matches`.
LEFT_OUT_KEYS = ["player", "registry", "umpire", "tv_umpire", "reserve_umpire", "match_referee",
                 "super_over", "match_id"]          # match_id repeats the file name; it is used for validation

# One column each, named after the key. The value is the first (only) field of the line.
SINGLE_COLUMNS = ["season", "venue", "city", "match_number", "toss_winner", "toss_decision",
                  "player_of_match", "winner", "winner_runs", "winner_wickets", "outcome", "method",
                  "eliminator"]
TWO_FIELD_COLUMNS = ["target_runs", "target_overs"]      # line is `key,innings,value`; the column keeps the value
INTEGER_COLUMNS = ["match_number", "winner_runs", "winner_wickets", "target_runs"]
DATE_FORMAT = "%Y/%m/%d"                                   # as written in the info files


def read_info_file(path):
    """Read one info file. Returns (version, rows); each row is (key, value1, value2, value3)."""
    version, rows = None, []
    with open(path, newline="", encoding="utf-8") as f:
        for line in csv.reader(f):
            if not line:
                continue
            if line[0] == "version":
                version = line[1]
            elif line[0] == "info":
                values = line[2:]
                if len(values) > 3:       # never drop a field silently
                    raise ValueError(f"{path}: {len(values)} value fields, the long table holds 3: {line}")
                rows.append((line[1], *values, *[None] * (3 - len(values))))
            else:
                raise ValueError(f"{path}: line starts with {line[0]!r}, expected 'version' or 'info'")
    return version, rows


def read_info_folder(folder):
    """Read every <id>_info.csv in `folder`. Returns (long table, versions).

    The long table has one row per info line: match_id, key, value1, value2, value3
    (None where a line has fewer fields). The version line is not an info line, so it
    is returned separately as a Series indexed by match_id.
    """
    paths = sorted(Path(folder).glob("*_info.csv"))
    if not paths:
        raise FileNotFoundError(f"no *_info.csv files in {folder} - wrong folder?")
    records, versions = [], {}
    for path in paths:
        match_id = int(path.name.split("_")[0])
        versions[match_id], rows = read_info_file(path)
        records += [(match_id, *row) for row in rows]
    long = pd.DataFrame(records, columns=["match_id", "key", "value1", "value2", "value3"])
    return long, pd.Series(versions, name="version")


def check_schema(long):
    """Raise ValueError if the long table breaks SCHEMA.

    That means: an unknown key, a line with the wrong number of value fields, or a key with too few
    or too many rows in some match - a required key missing from a match counts as too few.
    """
    if long.empty:
        raise ValueError("the long table is empty: no info lines were read")

    unknown = sorted(set(long["key"]) - set(SCHEMA))
    if unknown:
        raise ValueError(f"unknown info key(s): {unknown}")

    n_fields = long[["value1", "value2", "value3"]].notna().sum(axis=1)
    wrong = long[n_fields != long["key"].map({k: v[2] for k, v in SCHEMA.items()})]
    if len(wrong):
        first = wrong.iloc[0]
        raise ValueError(f"{len(wrong)} line(s) with the wrong number of value fields, "
                         f"first: match {first['match_id']}, key {first['key']!r}")

    rows = long.groupby(["match_id", "key"]).size().unstack(fill_value=0)     # one row per match, one column per key
    for key, (min_rows, max_rows, _) in SCHEMA.items():
        count = rows[key] if key in rows.columns else pd.Series(0, index=rows.index)
        too_few = count[count < min_rows]
        if len(too_few):
            raise ValueError(f"key {key!r} has fewer than {min_rows} row(s) in {len(too_few)} match(es), "
                             f"first: match {too_few.index[0]} has {too_few.iloc[0]}")
        if max_rows is not None:
            too_many = count[count > max_rows]
            if len(too_many):
                raise ValueError(f"key {key!r} has more than {max_rows} row(s) in {len(too_many)} match(es), "
                                 f"first: match {too_many.index[0]} has {too_many.iloc[0]}")


def build_matches(long):
    """One row per match from the long table. Text stays raw; dates and integer fields are typed."""
    check_schema(long)
    matches = pd.DataFrame(index=pd.Index(sorted(long["match_id"].unique()), name="match_id"))

    for key in SINGLE_COLUMNS:
        matches[key] = long[long["key"] == key].set_index("match_id")["value1"]
    for key in TWO_FIELD_COLUMNS:
        matches[key] = long[long["key"] == key].set_index("match_id")["value2"]

    # A blank field (`info,city,`) is a missing value here. A CSV cannot tell "" from missing, and `long` still holds the raw ""
    for col in SINGLE_COLUMNS + TWO_FIELD_COLUMNS:
        matches[col] = matches[col].mask(matches[col] == "")

    # repeating keys: number the rows within each match, then spread them over columns
    teams = long[long["key"] == "team"].assign(n=lambda d: d.groupby("match_id").cumcount() + 1)
    teams = teams.pivot(index="match_id", columns="n", values="value1")
    dates = long[long["key"] == "date"].assign(n=lambda d: d.groupby("match_id").cumcount() + 1)
    dates = dates.pivot(index="match_id", columns="n", values="value1").reindex(columns=[1, 2])
    matches["team1"], matches["team2"] = teams[1], teams[2]
    matches["start_date"] = pd.to_datetime(dates[1], format=DATE_FORMAT)
    matches["end_date"] = pd.to_datetime(dates[2], format=DATE_FORMAT)      # only where a match has a second date

    for col in INTEGER_COLUMNS:
        matches[col] = pd.to_numeric(matches[col]).astype("Int64")

    order = ["season", "start_date", "end_date", "team1", "team2", "venue", "city", "match_number",
             "toss_winner", "toss_decision", "player_of_match", "winner", "winner_runs", "winner_wickets",
             "outcome", "method", "eliminator", "target_runs", "target_overs"]
    return matches[order].reset_index()
