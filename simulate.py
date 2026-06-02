import os
import itertools
import numpy as np
import pandas as pd

# --- ADD THIS START ---
def get_team_name_map(teams_csv_path):
    teams_df = pd.read_csv(teams_csv_path)
    return dict(zip(teams_df['id'], teams_df['team_name']))
# --- ADD THIS END ---

BASE_DIR = r"E:\ML_project_WC"
MATCHES_PATH = os.path.join(BASE_DIR, "matches.csv")
STAGES_PATH = os.path.join(BASE_DIR, "tournament_stages.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "simulation_results.csv")

N_SIM = 10000
RNG = np.random.default_rng(42)


def team_pool(matches, team_map):
    # Use the ID columns to get the names
    home_teams = matches['home_team_id'].map(team_map)
    away_teams = matches['away_team_id'].map(team_map)
    return pd.concat([home_teams, away_teams]).dropna().unique().tolist()

def load_inputs():
    matches = pd.read_csv(MATCHES_PATH)
    stages = pd.read_csv(STAGES_PATH)
    return matches, stages

def pick_col(df, candidates, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        # Instead of crashing, let's print what we have so we can see
        print(f"DEBUG: Could not find any of {candidates} in columns: {df.columns.tolist()}")
        raise KeyError(f"Missing required column from: {candidates}")
    return None

def standardize_matches(matches):
    # Load your teams mapping file to translate IDs to Names
    teams_df = pd.read_csv(os.path.join(BASE_DIR, "teams.csv"))
    # Create a lookup dictionary: {1: 'Mexico', 2: 'South Africa', ...}
    # Adjust 'id' and 'team_name' to match your teams.csv column headers exactly
    team_map = dict(zip(teams_df['id'], teams_df['team_name']))

    matches = matches.copy()
    
    # Map the IDs to Names
    matches["home_team"] = matches["home_team_id"].map(team_map)
    matches["away_team"] = matches["away_team_id"].map(team_map)
    
    # Fill in any missing names with a placeholder to prevent crashes
    matches["home_team"] = matches["home_team"].fillna("Unknown")
    matches["away_team"] = matches["away_team"].fillna("Unknown")
    
    return matches
def standardize_stages(stages):
    stages = stages.copy()
    # Added more candidates for stage information
    stage_names = ["stage", "round", "phase", "tournament_stage", "tournament_stage_name", "stage_name"]
    c = pick_col(stages, stage_names, required=False)
    
    if c:
        stages["stage"] = stages[c]
    else:
        # Fallback if no stage column is found
        stages["stage"] = "Group"
    return stages

def team_pool(matches):
    # Ensure columns are treated as strings and drop any empty/missing values
    home_teams = matches["home_team"].dropna().astype(str)
    away_teams = matches["away_team"].dropna().astype(str)
    return sorted(set(home_teams).union(set(away_teams)))

def strength_table(elo_csv_path):
    elo_df = pd.read_csv(elo_csv_path)
    
    # This removes hidden spaces and special characters like \xa0
    elo_df['team'] = elo_df['team'].astype(str).str.replace(u'\xa0', u' ', regex=True).str.strip()
    
    # Sort by date
    elo_df['date'] = pd.to_datetime(elo_df['date'], errors='coerce')
    elo_df = elo_df.dropna(subset=['date'])
    elo_df = elo_df.sort_values('date')
    
    latest_ratings = {}
    for team in elo_df['team'].unique():
        team_data = elo_df[elo_df['team'] == team]
        latest_ratings[team] = team_data.iloc[-1]['rating']
        
    return latest_ratings

def match_prob(home_rating, away_rating, neutral=True):
    home_adv = 30.0 if not neutral else 0.0
    diff = (home_rating + home_adv) - away_rating
    p_win = 1 / (1 + 10 ** (-diff / 400))
    p_draw = max(0.12, 0.28 - abs(diff) / 2000)
    p_draw = min(p_draw, 0.35)
    scale = 1 - p_draw
    return p_win * scale, p_draw, (1 - p_win) * scale


def simulate_match(home, away, ratings, knockouts=False):
    p_home, p_draw, p_away = match_prob(ratings.get(home, 1500), ratings.get(away, 1500))
    probs = np.array([p_home, p_draw, p_away], dtype=float)
    probs = probs / probs.sum()
    outcome = RNG.choice(["home", "draw", "away"], p=probs)

    if outcome == "home":
        return home
    if outcome == "away":
        return away
    if knockouts:
        return RNG.choice([home, away])
    return "Draw"


def simulate_group_stage(teams, ratings):
    shuffled = teams[:]
    RNG.shuffle(shuffled)
    standings = {t: {"pts": 0, "gd": 0, "gf": 0} for t in shuffled}

    for home, away in itertools.combinations(shuffled, 2):
        winner = simulate_match(home, away, ratings, knockouts=False)
        if winner == "Draw":
            standings[home]["pts"] += 1
            standings[away]["pts"] += 1
        elif winner == home:
            standings[home]["pts"] += 3
            standings[home]["gd"] += 1
            standings[home]["gf"] += 1
            standings[away]["gd"] -= 1
        else:
            standings[away]["pts"] += 3
            standings[away]["gd"] += 1
            standings[away]["gf"] += 1
            standings[home]["gd"] -= 1

    ranked = sorted(standings.items(), key=lambda kv: (kv[1]["pts"], kv[1]["gd"], kv[1]["gf"], ratings.get(kv[0], 1500)), reverse=True)
    return [t for t, _ in ranked]


def simulate_knockout(qualified, ratings):
    q = qualified[:]
    while len(q) > 1:
        next_round = []
        # Loop starts here (8 spaces)
        for i in range(0, len(q), 2):
            # These 3 lines MUST have 12 spaces of indentation
            a, b = q[i], q[i + 1]
            winner = simulate_match(a, b, ratings, knockouts=True)
            next_round.append(winner)
        q = next_round
    return q[0]


def main():
    # 1. Define paths (hard-coded to be safe)
    TEAMS_PATH = r"E:\ML_project_WC\teams.csv"
    MATCHES_PATH = r"E:\ML_project_WC\matches.csv"
    ELO_PATH = r"E:\ML_project_WC\elo_ratings.csv"
    
    # 2. Create the mapping for your IDs
    teams_df = pd.read_csv(TEAMS_PATH)
    team_map = dict(zip(teams_df['id'], teams_df['team_name']))
    
    # 3. Load matches and translate IDs to Names
    matches = pd.read_csv(MATCHES_PATH)
    matches['home_team'] = matches['home_team_id'].map(team_map)
    matches['away_team'] = matches['away_team_id'].map(team_map)
    

    # 4. Now call your ratings function with the path
    ratings = strength_table(ELO_PATH)
        
    # --- ADD THIS BLOCK HERE ---
    print("DEBUG: Verifying Elo ratings for top teams:")
    test_teams = ["Spain", "Argentina", "France", "Brazil", "Australia"]
    for t in test_teams:
        rating = ratings.get(t, "NOT FOUND (Defaulting to 1500)")
        print(f"DEBUG: {t} -> {rating}")
    # ---------------------------

    # ... (rest of your code continues here) ...

    teams = team_pool(matches)


    # --- INITIALIZE THESE BEFORE THE LOOP ---
    win_counts = {t: 0 for t in teams}
    finalist_counts = {t: 0 for t in teams}
    semi_counts = {t: 0 for t in teams}
    round16_counts = {t: 0 for t in teams}
    group_win_counts = {t: 0 for t in teams}
    # ----------------------------------------
    for t in ["Spain", "Argentina", "France", "Australia"]:
      print(f"DEBUG: {t} rating: {ratings.get(t, 'NOT FOUND - Defaulting to 1500')}")

# Ensure teams list exists before this block
    if len(teams) >= 48:
        win_counts = {t: 0 for t in teams}
        finalist_counts = {t: 0 for t in teams}
        semi_counts = {t: 0 for t in teams}
        round16_counts = {t: 0 for t in teams}
        group_win_counts = {t: 0 for t in teams}

        for _ in range(N_SIM):
            sim_teams = teams[:]
            RNG.shuffle(sim_teams)
            
            # 1. Group Stage
            group_order = simulate_group_stage(sim_teams, ratings)
            group_win_counts[group_order[0]] += 1
            
            # 2. Round of 32
            qualified = group_order[:32]
            for t in qualified:
                round16_counts[t] += 1
            
            # 3. Simulate Knockout
            q = qualified[:]
            next_round = [simulate_match(q[i], q[i+1], ratings, knockouts=True) for i in range(0, 32, 2)]
            quarters = [simulate_match(next_round[i], next_round[i+1], ratings, knockouts=True) for i in range(0, 16, 2)]
            semis = [simulate_match(quarters[i], quarters[i+1], ratings, knockouts=True) for i in range(0, 8, 2)]
            for t in semis:
                semi_counts[t] += 1
            finalists = [simulate_match(semis[i], semis[i+1], ratings, knockouts=True) for i in range(0, 4, 2)]
            for t in finalists:
                finalist_counts[t] += 1
            champion = simulate_match(finalists[0], finalists[1], ratings, knockouts=True)
            win_counts[champion] += 1

        # 4. Results Processing
        results = pd.DataFrame({
            "team": teams, 
            "win_odds": [win_counts[t] / N_SIM for t in teams],
            "final_odds": [finalist_counts[t] / N_SIM for t in teams],
            "semi_odds": [semi_counts[t] / N_SIM for t in teams],
            "round16_odds": [round16_counts[t] / N_SIM for t in teams],
            "elo_rating": [ratings.get(t, 1500) for t in teams],
        }).sort_values("win_odds", ascending=False)

        with pd.option_context('display.max_rows', None):
            print(results)

        results.to_csv(OUTPUT_PATH, index=False)
        print(f"Success! Saved results to {OUTPUT_PATH}")
    else:
        print(f"Error: Not enough teams. Found {len(teams)}, need 48.")
if __name__ == "__main__":
    main()