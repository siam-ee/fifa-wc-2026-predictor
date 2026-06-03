import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 1. ULTIMATE CSS - Forcefully glassifies every layer of the app
st.markdown("""
    <style>
    .stApp { background-image: url('https://i.imgur.com/GtqgyfN.jpeg'); background-size: cover; background-attachment: fixed; }
    
    /* Target everything within the main app */
    .stApp, .main, .block-container, div[data-testid="stVerticalBlock"] {
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
    }

    /* Force UI elements to look consistent */
    div[data-baseweb="select"], .stButton>button { 
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
    }
    
    h1, h2, label, p, th, td { color: white !important; text-shadow: 1px 1px 2px black; }
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
    
    # Format decimals to 3 places as strings
    for col in ['RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']:
        df[col] = df[col].apply(lambda x: f"{x:.3f}")
    return df

df = load_data()

# 3. UI & NAVIGATION
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

st.title("The Greatest Sporting Event is here")
selected_team = st.selectbox("⚽ Support a Team", [""] + df['Team Name'].tolist(), format_func=lambda x: x if x else "Select a team...")

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 4. RENDERING LOGIC
if st.session_state.page == "Dashboard":
    if selected_team:
        st.header(f"Dashboard for {selected_team}")
        # Convert back to float for plotting
        p_df = df.copy()
        for col in ['Win Odds']: p_df[col] = p_df[col].astype(float)
        top15 = p_df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
        fig = px.bar(top15, x="Win Odds", y="Team Name", color_discrete_sequence=['royalblue'], text_auto='.3f')
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select a team above to view the dashboard.")

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    st.dataframe(df.style.hide(axis='index'), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    if st.button("Simulate Match"):
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{t1} Win", "0.450")
        col2.metric("Draw", "0.200")
        col3.metric(f"{t2} Win", "0.350")
