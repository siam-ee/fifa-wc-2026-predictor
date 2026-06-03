import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 1. CSS: Full-height container and fixed glass for inputs/dropdowns
st.markdown("""
    <style>
    .stApp { background-image: url('https://i.imgur.com/GtqgyfN.jpeg'); background-size: cover; background-attachment: fixed; }
    
    /* Ensure glass container covers the whole page */
    div.block-container { 
        background: rgba(0, 0, 0, 0.4) !important; 
        backdrop-filter: blur(10px) !important;
        border-radius: 20px; 
        padding: 3rem !important;
        min-height: 90vh;
    }
    
    div[data-baseweb="select"], .stButton>button { 
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    h1, h2, label, p, th, td { color: white !important; text-shadow: 1px 1px 2px black; }
    </style>
""", unsafe_allow_html=True)

# 2. DATA
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    
    # Selecting and Ordering Columns
    df = df[['team', 'elo_rating', 'round16_odds', 'quarter_odds', 'semi_odds', 'final_odds', 'win_odds']]
    
    # Renaming
    df.columns = ['Team Name', 'ELO Rating', 'RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']
    
    # Reset index to start from 1
    df.insert(0, 'No.', range(1, 1 + len(df)))
    
    # Rounding to 3 decimals
    cols_to_round = ['RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']
    df[cols_to_round] = df[cols_to_round].round(3)
    
    return df

df = load_data()

# 3. UI
st.title("The Greatest Sporting Event is here")
selected_team = st.selectbox("⚽ Support a Team", [""] + df['Team Name'].tolist(), 
                             format_func=lambda x: x if x else "Select a team to highlight...")

if 'page' not in st.session_state: st.session_state.page = "Dashboard"
c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 4. NAVIGATION
if st.session_state.page == "Dashboard" and selected_team:
    st.header("Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    top15['color'] = top15['Team Name'].apply(lambda x: 'Selected' if x == selected_team else 'Other')
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h", color="color", 
                 color_discrete_map={"Selected": "gold", "Other": "royalblue"}, text_auto='.3f')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    # Styling row and hiding standard index (0,1,2...)
    styled_df = df.style.apply(lambda row: ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == selected_team else '' for _ in row], axis=1).hide(axis='index')
    st.write(styled_df.to_html(), unsafe_allow_html=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    if st.button("Simulate Match Now"):
        p1, pd, p2 = (0.5, 0, 0.5) if t1 == t2 else (0.45, 0.2, 0.35)
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{t1} Win", f"{p1:.3f}")
        c2.metric("Draw", f"{pd:.3f}")
        c3.metric(f"{t2} Win", f"{p2:.3f}")
