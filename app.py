import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 1. ENHANCED GLASS CSS (Visible in Light/Dark Mode)
st.markdown("""
    <style>
    .stApp { background-image: url('https://i.imgur.com/GtqgyfN.jpeg'); background-size: cover; background-attachment: fixed; }
    div.block-container { 
        background: rgba(0, 0, 0, 0.4) !important; 
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2); 
        border-radius: 20px; padding: 3rem !important; 
    }
    h1, h2, h3, div, label, p, .stButton>button { color: white !important; font-weight: 600 !important; }
    /* Force dropdown visibility */
    .stSelectbox div[data-baseweb="select"] { background-color: rgba(255,255,255,0.2) !important; }
    .stSelectbox span { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 2. DATA
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    df = df.rename(columns={'team': 'Team Name', 'elo_rating': 'ELO Rating', 'round16_odds': 'RO16 Odds', 'quarter_odds': 'Quarter Odds', 'semi_odds': 'Semi Odds', 'final_odds': 'Final Odds', 'win_odds': 'Win Odds'})
    df.index = df.index + 1
    return df

df = load_data()

# 3. INITIALIZATION
if 'supported_team' not in st.session_state: st.session_state.supported_team = None
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 4. HEADER UI
st.title("The Greatest Sporting Event is here")
st.session_state.supported_team = st.selectbox("⚽ Support a Team", df['Team Name'].tolist())

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 5. NAVIGATION LOGIC
if st.session_state.page == "Dashboard":
    st.header("Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    top15['color'] = top15['Team Name'].apply(lambda x: 'Selected' if x == st.session_state.supported_team else 'Other')
    # Added text_auto=True for labels
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h", color="color", 
                 color_discrete_map={"Selected": "gold", "Other": "royalblue"}, text_auto='.1%')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    if st.session_state.supported_team not in top15['Team Name'].values:
        st.warning(f"Oops, {st.session_state.supported_team} is not in the top 15!!")

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    st.dataframe(df.style.apply(lambda row: ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == st.session_state.supported_team else '' for _ in row], axis=1), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    if st.button("Simulate Match Now"):
        if t1 == t2:
            p1, pd, p2 = 0.50, 0.00, 0.50
        else:
            # Your existing math logic here
            p1, pd, p2 = 0.45, 0.20, 0.35 
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{t1} Win", f"{p1:.1%}")
        col2.metric("Draw", f"{pd:.1%}")
        col3.metric(f"{t2} Win", f"{p2:.1%}")
