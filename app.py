import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 2. FIXED GLASSMORPHISM CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('https://i.imgur.com/GtqgyfN.jpeg');
        background-size: cover;
        background-attachment: fixed;
    }}
    /* Target the container to create the frosted glass effect */
    .stApp > .main > div {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
    }}
    h1, h2, h3, div {{ color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# 3. HELPER FUNCTIONS
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    cols = ['team', 'elo_rating', 'round16_odds', 'quarter_odds', 'semi_odds', 'final_odds', 'win_odds']
    df = df[cols].rename(columns={
        'team': 'Team Name', 'elo_rating': 'ELO Rating', 'round16_odds': 'RO16 Odds',
        'quarter_odds': 'Quarter Odds', 'semi_odds': 'Semi Odds', 'final_odds': 'Final Odds', 'win_odds': 'Win Odds'
    })
    df.index = df.index + 1
    return df

# 4. INITIALIZE SESSION
if 'supported_team' not in st.session_state: st.session_state.supported_team = None
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 5. UI LAYOUT
st.title("The Greatest Sporting Event is here")
df = load_data()

# Team Selection
st.session_state.supported_team = st.selectbox("⚽ Support a Team", [None] + df['Team Name'].tolist(), 
                                               format_func=lambda x: x if x else "Select a team...")

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 6. PAGE NAVIGATION
if st.session_state.page == "Dashboard":
    st.header("Prediction Dashboard")
    if st.session_state.supported_team:
        top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
        top15['color'] = top15['Team Name'].apply(lambda x: 'Selected' if x == st.session_state.supported_team else 'Other')
        fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h", color="color",
                     color_discrete_map={"Selected": "gold", "Other": "royalblue"})
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select a team from the dropdown to see your highlighted stats.")

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    st.dataframe(df.style.apply(lambda row: ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == st.session_state.supported_team else '' for _ in row], axis=1), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    if st.button("Simulate"):
        ra = df.loc[df['Team Name'] == t1, 'ELO Rating'].values[0]
        rb = df.loc[df['Team Name'] == t2, 'ELO Rating'].values[0]
        # (Your match_prob logic here)
        p1, pd, p2 = 0.45, 0.20, 0.35 # Placeholder logic
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{t1} Win", f"{p1:.1%}")
        col2.metric("Draw", f"{pd:.1%}")
        col3.metric(f"{t2} Win", f"{p2:.1%}")
