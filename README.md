# IPL EDA

Exploratory data analysis of Indian Premier League (IPL) cricket, built on [Cricsheet](https://cricsheet.org/)'s ball-by-ball data — every delivery of every IPL match from 2008 to 2026. The project is developed in small, committed sessions: understand the raw data first, then clean it, then analyse it with pandas and (later) SQL via DuckDB. Session 1 sets up the repository and profiles the combined ball-by-ball file.

## Data

- **Source:** [cricsheet.org](https://cricsheet.org/) — the IPL download in Cricsheet's CSV format (`ipl_csv2.zip`: a combined `all_matches.csv`, plus one ball-by-ball file and one `_info` file per match). See Cricsheet's site for its terms of use.
- **Where to put it:** the raw files are **not** stored in git. Unzip the download into `data/procured/cricsheet/` so that `data/procured/cricsheet/all_matches.csv` exists. That folder is git-ignored.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook                 # then open notebooks/01_data_understanding.ipynb
```

## Notebooks

| Notebook | What it does |
|---|---|
| [`01_data_understanding.ipynb`](notebooks/01_data_understanding.ipynb) | Profiles `all_matches.csv`: shape, dtypes, missingness, season / team / venue values, `wicket_type`, deliveries per match, `ball` vs `actual_delivery`. Read-only — it catalogues problems and fixes none of them. |
