# data_pipeline.py
import os
from collections import deque, defaultdict

import numpy as np
import pandas as pd

BASE_DIR = r"E:\ML_project_WC"
ELO_PATH = os.path.join(BASE_DIR, "elo_ratings.csv")
MATCHES_PATH = os.path.join(BASE_DIR, "international_matches.csv")
TEAMS_PATH = os.path.join(BASE_DIR, "teams.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "processed_data.csv")


def _safe_col(df, candidates, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise KeyError(f"None of these columns were found: {candidates}")
    return None


def _normalize_team_name(x):
    if pd.isna(x):
        return np.nan
    return str(x).strip()


def _to_datetime_series(s):
    return pd.to_datetime(s, errors="coerce", dayfirst=False)


def load_data():
    elo = pd.read_csv(ELO_PATH)
    matches = pd.read_csv(MATCHES_PATH)
    teams = pd.read_csv(TEAMS_PATH)
    return elo, matches, teams


def standardize_matches(matches):
    matches = matches.copy()

    date_col = _safe_col(matches, ["date", "match_date", "Date", "matchday"])
    home_col = _safe_col(matches, ["home_team", "home", "Home Team", "team1", "home_country"])
    away_col = _safe_col(matches, ["away_team", "away", "Away Team", "team2", "away_country"])
    hg_col = _safe_col(matches, ["home_score", "home_goals", "Home Score", "home_goals_scored", "score_home"])
    ag_col = _safe_col(matches, ["away_score", "away_goals", "Away Score", "away_goals_scored", "score_away"])

    matches["match_date"] = _to_datetime_series(matches[date_col])
    matches["home_team"] = matches[home_col].map(_normalize_team_name)
    matches["away_team"] = matches[away_col].map(_normalize_team_name)
    matches["home_goals"] = pd.to_numeric(matches[hg_col], errors="coerce")
    matches["away_goals"] = pd.to_numeric(matches[ag_col], errors="coerce")

    if "tournament" not in matches.columns:
        tcol = _safe_col(matches, ["competition", "tournament_name", "league", "event"], required=False)
        if tcol:
            matches["tournament"] = matches[tcol]
        else:
            matches["tournament"] = "Unknown"

    if "neutral" not in matches.columns:
        ncol = _safe_col(matches, ["neutral_venue", "neutral", "is_neutral"], required=False)
        matches["neutral"] = matches[ncol] if ncol else 0

    matches = matches.dropna(subset=["match_date", "home_team", "away_team", "home_goals", "away_goals"]).copy()
    matches = matches.sort_values("match_date").reset_index(drop=True)
    return matches


def standardize_elo(elo):
    elo = elo.copy()

    date_col = _safe_col(elo, ["date", "match_date", "Date"], required=False)
    team_col = _safe_col(elo, ["team", "Team", "country", "Country"])
    rating_col = _safe_col(elo, ["elo", "Elo", "rating", "Rating", "elo_rating"])

    if date_col:
        elo["elo_date"] = _to_datetime_series(elo[date_col])
    else:
        elo["elo_date"] = pd.NaT

    elo["team"] = elo[team_col].map(_normalize_team_name)
    elo["elo_rating"] = pd.to_numeric(elo[rating_col], errors="coerce")
    elo = elo.dropna(subset=["team", "elo_rating"]).copy()
    elo = elo.sort_values(["team", "elo_date"]).reset_index(drop=True)
    return elo


def standardize_teams(teams):
    teams = teams.copy()
    if "team" in teams.columns:
        teams["team"] = teams["team"].map(_normalize_team_name)
    elif "Team" in teams.columns:
        teams["team"] = teams["Team"].map(_normalize_team_name)
    else:
        teams["team"] = teams.iloc[:, 0].map(_normalize_team_name)
    return teams


def build_elo_lookup(elo):
    lookup = {}
    if "elo_date" in elo.columns and elo["elo_date"].notna().any():
        for team, grp in elo.groupby("team"):
            grp = grp.sort_values("elo_date")
            lookup[team] = grp[["elo_date", "elo_rating"]].reset_index(drop=True)
    else:
        last_ratings = elo.groupby("team")["elo_rating"].last()
        for team, rating in last_ratings.items():
            lookup[team] = rating
    return lookup


def get_elo_before_date(elo_lookup, team, dt, fallback=None):
    if team not in elo_lookup:
        return fallback
    obj = elo_lookup[team]
    if isinstance(obj, pd.DataFrame):
        eligible = obj[obj["elo_date"] <= dt]
        if len(eligible) > 0:
            return float(eligible.iloc[-1]["elo_rating"])
        if len(obj) > 0:
            return float(obj.iloc[0]["elo_rating"])
    else:
        return float(obj)
    return fallback


def calculate_current_form(matches):
    form_values = []
    history = defaultdict(lambda: deque(maxlen=10))

    for _, row in matches.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        home_gd = float(row["home_goals"] - row["away_goals"])
        away_gd = -home_gd

        home_hist = list(history[home])
        away_hist = list(history[away])

        home_form = np.mean(home_hist) if home_hist else 0.0
        away_form = np.mean(away_hist) if away_hist else 0.0

        form_values.append((home_form, away_form))

        history[home].append(home_gd)
        history[away].append(away_gd)

    matches["home_current_form"] = [x[0] for x in form_values]
    matches["away_current_form"] = [x[1] for x in form_values]
    return matches


def merge_elo_and_form(matches, elo):
    elo_lookup = build_elo_lookup(elo)
    home_elos = []
    away_elos = []

    for _, row in matches.iterrows():
        dt = row["match_date"]
        home_elos.append(get_elo_before_date(elo_lookup, row["home_team"], dt, fallback=np.nan))
        away_elos.append(get_elo_before_date(elo_lookup, row["away_team"], dt, fallback=np.nan))

    matches["home_elo"] = home_elos
    matches["away_elo"] = away_elos
    matches["elo_diff"] = matches["home_elo"] - matches["away_elo"]
    matches["form_diff"] = matches["home_current_form"] - matches["away_current_form"]
    matches["goal_diff"] = matches["home_goals"] - matches["away_goals"]

    def outcome(gd):
        if gd > 0:
            return "Win"
        if gd < 0:
            return "Loss"
        return "Draw"

    matches["result"] = matches["goal_diff"].apply(outcome)
    return matches


def main():
    elo, matches, teams = load_data()
    matches = standardize_matches(matches)
    elo = standardize_elo(elo)
    teams = standardize_teams(teams)

   # team_set = set(teams["team"].dropna().astype(str))
   # matches = matches[matches["home_team"].isin(team_set) & matches["away_team"].isin(team_set)].copy()

    matches = calculate_current_form(matches)
    matches = merge_elo_and_form(matches, elo)

    cols = [
        "match_date", "tournament", "home_team", "away_team",
        "home_goals", "away_goals", "goal_diff", "result",
        "home_elo", "away_elo", "elo_diff",
        "home_current_form", "away_current_form", "form_diff",
        "neutral"
    ]
    cols = [c for c in cols if c in matches.columns]
    output = matches[cols].sort_values("match_date").reset_index(drop=True)
    output.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved processed data to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
