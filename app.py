# app.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

BASE_DIR = r"E:\ML_project_WC"
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
    
    fig = px.bar(
        chart_data,
        x="win_odds",
        y="team",
        orientation="h",
        title="Top 15 Teams by Win Odds",
        labels={"win_odds": "Win Probability", "team": "Team"},
        text=chart_data["win_odds"].map(lambda x: f"{x:.2%}")
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # --- SIDEBAR: HEAD-TO-HEAD MATCH SIMULATOR ---
    with st.sidebar:
        st.header("⚔️ Match Simulator")
        teams = sorted(df["team"].dropna().astype(str).unique().tolist())
        
        team_a = st.selectbox("Team A", teams, index=0)
        team_b = st.selectbox("Team B", [t for t in teams if t != team_a], index=0)
        
        if st.button("Simulate Match", use_container_width=True):
            probs = simulate_head_to_head(team_a, team_b, df)
            
            st.markdown(f"### 📊 {team_a} vs {team_b}")
            
            # Simple clean display metrics for the sidebar
            for idx, row in probs.iterrows():
                st.metric(label=row["Outcome"], value=f"{row['Probability']:.2%}")

    # --- MAIN PAGE: TOURNAMENT ODDS TABLE ---
    st.subheader("🏆 Full Tournament Odds Table")
    st.dataframe(df.head(48), use_container_width=True)


if __name__ == "__main__":
    main()
