import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 1. FIXED GLASS CSS: Image remains at the bottom, container tint on top
st.markdown("""
    <style>
    .stApp { background: url('https://i.imgur.com/GtqgyfN.jpeg') no-repeat center center fixed; background-size: cover; }
    
    /* Container glass effect */
    .block-container { 
        background: rgba(0, 0, 0, 0.3) !important; 
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px; 
    }
    
    /* Text and UI elements */
    h1, h2, label, p, th, td { color: white !important; }
    div[data-baseweb="select"], .stButton>button { 
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. DATA
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    df = df[['team', 'elo_rating', 'round16_odds', 'quarter_odds', 'semi_odds', 'final_odds', 'win_odds']]
    df.columns = ['Team Name', 'ELO Rating', 'RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']
    df.insert(0, 'No.', range(1, 1 + len(df)))
    return df

df = load_data()

# 3. STATE
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

st.title("The Greatest Sporting Event is here")
selected_team = st.selectbox("⚽ Support a Team", [""] + df['Team Name'].tolist())

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 4. LOGIC
if st.session_state.page == "Dashboard" and selected_team:
    st.header("Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    # Highlight logic restored
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h",
                 color=[ 'gold' if x == selected_team else 'royalblue' for x in top15['Team Name']],
                 text_auto='.3f')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    # Styling restored
    def highlight_team(row):
        return ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == selected_team else '' for _ in row]
    st.dataframe(df.style.apply(highlight_team, axis=1).hide(axis='index'), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    if st.button("Simulate"):
        # Fix logic: Same team = 50/50
        p1, pd, p2 = (0.500, 0.000, 0.500) if t1 == t2 else (0.450, 0.200, 0.350)
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{t1} Win", f"{p1:.3f}")
        c2.metric("Draw", f"{pd:.3f}")
        c3.metric(f"{t2} Win", f"{p2:.3f}")
