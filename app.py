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


def get_flag_url(country_name):
    """
    Returns the URL of a high-quality flag PNG image.
    Uses standard 2-letter ISO codes mapped to a reliable online flag repository.
    """
    iso_codes = {
        # Hosts
        "Canada": "ca", "Mexico": "mx", "USA": "us",
        # AFC
        "Australia": "au", "IR Iran": "ir", "Iraq": "iq", "Japan": "jp", 
        "Jordan": "jo", "Qatar": "qa", "Saudi Arabia": "sa", "South Korea": "kr", "Uzbekistan": "uz",
        # CAF
        "Algeria": "dz", "Cape Verde": "cv", "Cabo Verde": "cv", "DR Congo": "cd", "Egypt": "eg", "Ghana": "gh", 
        "Côte d'Ivoire": "ci", "Morocco": "ma", "Senegal": "sn", "South Africa": "za", "Tunisia": "tn",
        # CONCACAF
        "Curaçao": "cw", "Haiti": "ht", "Panama": "pa",
        # CONMEBOL
        "Argentina": "ar", "Brazil": "br", "Colombia": "co", "Ecuador": "ec", "Paraguay": "py", "Uruguay": "uy",
        # OFC
        "New Zealand": "nz",
        # UEFA
        "Austria": "at", "Belgium": "be", "Bosnia": "ba", "Croatia": "hr", "Czechia": "cz", 
        "England": "gb-eng", "France": "fr", "Germany": "de", "Netherlands": "nl", "Norway": "no", 
        "Portugal": "pt", "Scotland": "gb-sct", "Spain": "es", "Sweden": "se", "Switzerland": "ch", "Turkey": "tr", "Turkiye": "tr"
    }
    
    code = iso_codes.get(country_name)
    if code:
        # Pulls clean, official vector/PNG flags from a reliable public CDN
        return f"https://flagcdn.com/w40/{code}.png"
    return None


def simulate_head_to_head(team_a, team_b, df):
    ra = float(df.loc[df["team"] == team_a, "elo_rating"].iloc[0]) if team_a in df["team"].values else 1500.0
    rb = float(df.loc[df["team"] == team_b, "elo_rating"].iloc[0]) if team_b in df["team"].values else 1500.0
    p_a, p_d, p_b = match_prob(ra, rb)

    return pd.DataFrame({
        "Outcome": [team_a, "Draw", team_b],
        "Probability": [p_a, p_d, p_b]
    })


def main():
    st.set_page_config(
        page_title="2026 FIFA World Cup Predictor", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
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
        filtered_teams = [t for t in teams if t != team_a]
        team_b = st.selectbox("Team B", filtered_teams, index=0)
        
        if st.button("Simulate Match", use_container_width=True):
            probs = simulate_head_to_head(team_a, team_b, df)
            
            st.markdown("---")
            st.markdown(f"### 📊 Matchup Prediction")
            
            # Display metrics alongside actual, high-quality flag image links
            for idx, row in probs.iterrows():
                outcome = row["Outcome"]
                
                if outcome == "Draw":
                    st.markdown("#### 🤝 Draw")
                else:
                    flag_url = get_flag_url(outcome)
                    if flag_url:
                        # Uses simple HTML formatting to position the flag image nicely inline next to the text
                        st.markdown(f'#### <img src="{flag_url}" width="25"> {outcome}', unsafe_allow_html=True)
                    else:
                        st.markdown(f"#### ⚽ {outcome}")
                        
                st.metric(label="Win Probability", value=f"{row['Probability']:.2%}")
                st.markdown("") # Tiny spacing block

    # --- MAIN PAGE: TOURNAMENT ODDS TABLE ---
    st.subheader("🏆 Full Tournament Odds Table")
    st.dataframe(df.head(48), use_container_width=True)


if __name__ == "__main__":
    main()
