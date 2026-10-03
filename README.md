# IPL EDA

Exploratory data analysis of Indian Premier League (IPL) cricket, built on [Cricsheet](https://cricsheet.org/)'s ball-by-ball data — every delivery of every IPL match from 2008 to 2026. The project is developed in small, committed sessions: understand the raw data, parse the match information, build match and innings tables, add reference keys, clean, then analyse with pandas and (later) SQL via DuckDB.

## Data

- **Source:** [cricsheet.org](https://cricsheet.org/) — the IPL download in Cricsheet's CSV format (`ipl_csv2.zip`: a combined `all_matches.csv`, plus one ball-by-ball file and one `_info` file per match). See Cricsheet's site for its terms of use.
- **The raw files are committed, as a dated snapshot:** 1,243 matches, 2008 to 2026-05-31, in `data/procured/cricsheet/`. Cricsheet's IPL archive gains matches every season, so a fresh download will not reproduce the numbers in the notebooks; the committed snapshot will.
- **Derived tables** are written to `data/processed/` by the notebooks: `matches.csv` (one row per match, notebook 02) and `innings.csv` (one row per match-innings, notebook 03). A CSV carries no types, so load them with `ipl_eda.tables.read_matches()` / `read_innings()`.
- **Reference tables** are in `data/reference/`: `teams.csv` (each raw team string and its franchise, the franchise's current name; written by hand and checked in notebook 04) and `seasons.csv` (each season label and its calendar year; derived from the matches in notebook 04). `ipl_eda.reference.add_keys()` adds the keys as new columns next to the raw ones; it never changes a raw column.

## Setup

Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # pinned libraries, plus this project (editable) so `import ipl_eda` works in notebooks
jupyter notebook                 # then open a notebook from notebooks/
```

## Notebooks

| Notebook | What it does |
|---|---|
| [`01_data_understanding.ipynb`](notebooks/01_data_understanding.ipynb) | Profiles `all_matches.csv`: shape, dtypes, missingness, season / team / venue values, `wicket_type`, deliveries per match, `ball` vs `actual_delivery`. Read-only — it catalogues problems and fixes none of them. |
| [`02_info_files.ipynb`](notebooks/02_info_files.ipynb) | Parses the 1,243 `_info.csv` files into a one-row-per-match `matches` table, validates it against the ball-by-ball file, and closes notebook 01's open items. |
| [`03_innings.ipynb`](notebooks/03_innings.ipynb) | Builds the innings table from the deliveries, proves the aggregation lost nothing, and reconciles it with the recorded results (wicket margins, D/L, super overs, seven-ball overs). |
| [`04_team_and_season_keys.ipynb`](notebooks/04_team_and_season_keys.ipynb) | Maps the 19 raw team strings to 15 franchises and each season label to a calendar year, proves both maps with structural checks, and adds them to `matches` and `innings` as key columns. |

## Code (`src/ipl_eda/`)

- `info_files.py` — reads the `_info.csv` files into a lossless long table, checks them against a schema, builds `matches`.
- `innings.py` — `build_innings()`: one row per match-innings from the deliveries; holds the definition of a wicket.
- `tables.py` — typed loaders for the CSVs in `data/processed/`.
- `reference.py` — typed loaders for `data/reference/` and `add_keys()`.

## Decisions

`DECISIONS.md` is the log of the choices made so far: what was decided, the evidence, what is outside knowledge, and what would change the decision.
