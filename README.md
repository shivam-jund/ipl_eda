# IPL EDA

Exploratory data analysis of Indian Premier League (IPL) cricket, built on [Cricsheet](https://cricsheet.org/)'s ball-by-ball data — every delivery of every IPL match from 2008 to 2026. The project is developed in small, committed sessions: understand the raw data, parse the match information, clean it, then analyse it with pandas and (later) SQL via DuckDB.

## Data

- **Source:** [cricsheet.org](https://cricsheet.org/) — the IPL download in Cricsheet's CSV format (`ipl_csv2.zip`: a combined `all_matches.csv`, plus one ball-by-ball file and one `_info` file per match). See Cricsheet's site for its terms of use.
- **The raw files are committed, as a dated snapshot:** 1,243 matches, 2008 to 2026-05-31, in `data/procured/cricsheet/`. Cricsheet's IPL archive gains matches every season, so a fresh download will not reproduce the numbers in the notebooks; the committed snapshot will.
- **Derived tables** are written to `data/processed/` by the notebooks (for example `matches.csv`, built in notebook 02).

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
| [`02_info_files.ipynb`](notebooks/02_info_files.ipynb) | Parses the 1,243 `_info.csv` files into a one-row-per-match `matches` table (code in `src/ipl_eda/info_files.py`), validates it against the ball-by-ball file, and closes notebook 01's open items. |
