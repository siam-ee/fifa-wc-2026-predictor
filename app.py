import streamlit as st
import pandas as pd
import plotly.express as px

# --- SETUP & HELPERS ---
st.set_page_config(layout="wide")

def load_data():
    df = pd.read_csv("simulation_results.csv")
    # Add Quarter Odds estimation
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    # Clean up column names and index
    df = df.rename(columns={
        'win_odds': 'Win Odds', 'final_odds': 'Final Odds', 
        'semi_odds': 'Semi Odds', 'round16_odds': 'RO16 Odds',
        'elo_rating': 'ELO Rating'
    })
    df.index = df.index + 1
    return df

# --- UI & NAVIGATION ---
st.title("The Greatest Sporting Event is here")

if 'supported_team' not in st.session_state:
    st.session_state.supported_team = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Support a Team Popup
with st.expander("⚽ Support a Team"):
    teams_list = sorted(load_data()['team'].tolist())
    st.session_state.supported_team = st.selectbox("Select your nation to support:", teams_list)

# Navigation
col1, col2, col3 = st.columns(3)
if col1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if col2.button("📊 Tournament Table Odds"): st.session_state.page = "Table"
if col3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

# --- PAGE LOGIC ---
df = load_data()

if st.session_state.page == "Dashboard":
    st.header("FIFA World Cup Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    
    # Highlight logic
    top15['color'] = top15['team'].apply(lambda x: 'Gold' if x == st.session_state.supported_team else 'Blue')
    
    fig = px.bar(top15, x="Win Odds", y="team", orientation="h", color="color", 
                 color_discrete_map={"Gold": "gold", "Blue": "royalblue"},
                 title="Top 15 Teams")
    st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.supported_team not in top15['team'].values:
        st.warning("Oops, seems your team is not in top 15!!")

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    
    def highlight_row(row):
        color = 'background-color: gold' if row['team'] == st.session_state.supported_team else ''
        return [color] * len(row)
    
    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['team'].tolist())
    t2 = st.selectbox("Team 2", df['team'].tolist())
    if st.button("Simulate"):
        # Your match_prob logic here...
        st.write(f"Results for {t1} vs {t2}")
        st.metric("Win Probability", "45%") # Placeholder for your actual logic
