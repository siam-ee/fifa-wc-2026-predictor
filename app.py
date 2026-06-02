# app.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

SIM_PATH = "simulation_results.csv"


@st.cache_data
def load_results():
    return pd.read_csv(SIM_PATH)


def match_prob(home_rating, away_rating, home_adv=65.0):
    diff = (home_rating + home_adv) - away_rating
    p_win = 1 / (1 + 10 ** (-diff / 400))
    p_draw = max(0.12, 0.28 - abs(diff) / 2000)
    p_draw = min(p_draw, 0.35)
    scale = 1 - p_draw
    return p_win * scale, p_draw, (1 - p_win) * scale


def get_flag(country_name):
    flags = {
        # Hosts
        "Canada": "🇨🇦", "Mexico": "🇲🇽", "USA": "🇺🇸",
        # AFC
        "Australia": "🇦🇺", "IR Iran": "🇮🇷", "Iraq": "🇮🇶", "Japan": "🇯🇵", 
        "Jordan": "🇯🇴", "Qatar": "🇶🇦", "Saudi Arabia": "🇸🇦", "South Korea": "🇰🇷", "Uzbekistan": "🇺🇿",
        # CAF
        "Algeria": "🇩🇿", "Cape Verde": "🇨🇻", "DR Congo": "🇨🇩", "Egypt": "🇪🇬", "Ghana": "🇬🇭", 
        "Côte d'Ivoire": "🇨🇮", "Morocco": "🇲🇦", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "Tunisia": "🇹🇳",
        # CONCACAF
        "Curaçao": "🇨🇼", "Haiti": "🇭🇹", "Panama": "🇵🇦",
        # CONMEBOL
        "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Colombia": "🇨🇴", "Ecuador": "🇪🇨", "Paraguay": "🇵🇾", "Uruguay": "🇺🇾",
        # OFC
        "New Zealand": "🇳🇿",
        # UEFA
        "Austria": "🇦🇹", "Belgium": "🇧🇪", "Bosnia": "🇧🇦", "Croatia": "🇭🇷", "Czechia": "🇨🇿", 
        "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "France": "🇫🇷", "Germany": "🇩🇪", "Netherlands": "🇳🇱", "Norway": "🇳🇴", 
        "Portugal": "🇵🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Spain": "🇪🇸", "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Turkey": "🇹🇷"
    }
    return flags.get(country_name, "⚽")


def simulate_head_to_head(team_a, team_b, df):
    ra = float(df.loc[df["team"] == team_a, "elo_rating"].iloc[0]) if team_a in df["team"].values else 1500.0
    rb = float(df.loc[df["team"] == team_b, "elo_rating"].iloc[0]) if team_b in df["team"].values else 1500.0
    p_a, p_d, p_b = match_prob(ra, rb)

    return pd.DataFrame({
        "Outcome": [team_a, "Draw", team_b],
        "Probability": [p_a, p_d, p_b]
    })


def main():
    st.set_page_config(page_title="2026 FIFA World Cup Predictor", layout="wide")
    st.title("2026 FIFA World Cup Prediction Dashboard")

    df = load_results()
    if df.empty:
        st.error("simulation_results.csv is empty or missing.")
        return

    # --- MAIN PAGE: TOP 15 CHART ---
    top15 = df.nlargest(15, 'win_odds').copy()
    chart_data = top15.sort_values("win_odds", ascending=True)
    
    # Add flags to chart labels safely
    chart_data["display_name"] = chart_data["team"].map(lambda x: f"{get_flag(x)} {x}")
    
    fig = px.bar(
        chart_data,
        x="win_odds",
        y="display_name",
        orientation="h",
        title="Top 15 Teams by Win Odds",
        labels={"win_odds": "Win Probability", "display_name": "Team"},
        text=chart_data["win_odds"].map(lambda x: f"{x:.2%}")
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # --- SIDEBAR: HEAD-TO-HEAD MATCH SIMULATOR ---
    with st.sidebar:
        st.header("⚔️ Match Simulator")
        teams = sorted(df["team"].dropna().astype(str).unique().tolist())
        
        # format_func adds flags to dropdown lists dynamically
        team_a = st.selectbox("Team A", teams, index=0, format_func=lambda x: f"{get_flag(x)} {x}")
        
        filtered_teams = [t for t in teams if t != team_a]
        team_b = st.selectbox("Team B", filtered_teams, index=0, format_func=lambda x: f"{get_flag(x)} {x}")
        
        if st.button("Simulate Match", use_container_width=True):
            probs = simulate_head_to_head(team_a, team_b, df)
            
            st.markdown(f"### 📊 {get_flag(team_a)} vs {get_flag(team_b)}")
            
            for idx, row in probs.iterrows():
                outcome = row["Outcome"]
                if outcome == "Draw":
                    display_label = "🤝 Draw"
                else:
                    display_label = f"{get_flag(outcome)} {outcome}"
                    
                st.metric(label=display_label, value=f"{row['Probability']:.2%}")

    # --- MAIN PAGE: TOURNAMENT ODDS TABLE ---
    st.subheader("🏆 Full Tournament Odds Table")
    
    display_df = df.head(48).copy()
    display_df["team"] = display_df["team"].map(lambda x: f"{get_flag(x)} {x}")
    
    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
