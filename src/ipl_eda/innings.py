"""Build the innings table: one row per (match_id, innings), from the ball-by-ball deliveries."""
import pandas as pd

EXTRAS_TYPES = ["wides", "noballs", "byes", "legbyes", "penalty"]

# A dismissal (a non-blank wicket_type) is a wicket lost by the batting side unless its type is listed here.
# Evidence: notebook 03, section C1 - the recorded wicket margins ("won by N wickets") are matched in all 650
# plain chases only when `retired hurt` is NOT counted (counting it breaks 7 margins) and `obstructing the field`
# IS counted (dropping it breaks 2). `retired out` is counted because the Laws treat it as a dismissal, but the data
# do not settle it: all six occur in innings that carry no wicket margin.
NOT_WICKETS = ["retired hurt"]


def build_innings(deliveries):
    """One row per (match_id, innings). Totals are over every delivery of that innings, super overs included as innings 3+.

    `deliveries` needs: match_id, innings, batting_team, bowling_team, runs_off_bat, extras, wides, noballs,
    byes, legbyes, penalty, wicket_type.
    """
    d = deliveries.copy()
    d[EXTRAS_TYPES] = d[EXTRAS_TYPES].fillna(0)
    d["legal"] = (d["wides"] == 0) & (d["noballs"] == 0)             # a wide or a no-ball is not a legal delivery
    d["wicket"] = d["wicket_type"].notna() & ~d["wicket_type"].isin(NOT_WICKETS)

    groups = d.groupby(["match_id", "innings"])
    for column in ("batting_team", "bowling_team"):         # the table takes one value per innings, so check there is only one
        if (groups[column].nunique() != 1).any():
            raise ValueError(f"an innings has more than one {column}")

    table = groups.agg(
        batting_team=("batting_team", "first"), bowling_team=("bowling_team", "first"),
        runs_off_bat=("runs_off_bat", "sum"), extras=("extras", "sum"),
        wides=("wides", "sum"), noballs=("noballs", "sum"), byes=("byes", "sum"),
        legbyes=("legbyes", "sum"), penalty=("penalty", "sum"),
        deliveries=("legal", "size"), legal_balls=("legal", "sum"), wickets=("wicket", "sum"),
    ).reset_index()

    counts = ["runs_off_bat", "extras", *EXTRAS_TYPES, "deliveries", "legal_balls", "wickets"]
    table[counts] = table[counts].astype("int64")
    table["runs"] = table["runs_off_bat"] + table["extras"]
    table["is_super_over"] = table["innings"] > 2    # Cricsheet README: in a match that normally has 2 innings, any later innings is a super over

    order = ["match_id", "innings", "batting_team", "bowling_team", "is_super_over", "runs", "runs_off_bat", "extras",
             *EXTRAS_TYPES, "deliveries", "legal_balls", "wickets"]
    return table[order]
