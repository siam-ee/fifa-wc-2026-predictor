import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 2. FORCED GLASSMORPHISM CSS
st.markdown(f"""
    <style>
    /* Full page background */
    .stApp {{
        background-image: url('https://i.imgur.com/GtqgyfN.jpeg');
        background-size: cover;
        background-attachment: fixed;
    }}
    /* Force the glass effect on the Streamlit container */
    div.block-container {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 40px !important;
    }}
    /* Ensure text readability */
    h1, h2, h3, div, label, p {{ color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# 3. HELPER FUNCTIONS
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    df = df.rename(columns={
        'team': 'Team Name', 'elo_rating': 'ELO Rating', 'round16_odds': 'RO16 Odds',
        'quarter_odds': 'Quarter Odds', 'semi_odds': 'Semi Odds', 'final_odds': 'Final Odds', 'win_odds': 'Win Odds'
    })
    df.index = df.index + 1
    return df

# 4. INITIALIZE SESSION
if 'supported_team' not in st.session_state: st.session_state.supported_team = None
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 5. UI
st.title("The Greatest Sporting Event is here")
df = load_data()

st.session_state.supported_team = st.selectbox("⚽ Support a Team", [None] + df['Team Name'].tolist(), 
                                               format_func=lambda x: x if x else "Select a team...")

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 6. NAVIGATION LOGIC
if st.session_state.page == "Dashboard":
    st.header("Prediction Dashboard")
    
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    
    # Highlight logic
    top15['color'] = top15['Team Name'].apply(lambda x: 'Selected' if x == st.session_state.supported_team else 'Other')
    
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h", color="color",
                 color_discrete_map={"Selected": "gold", "Other": "royalblue"})
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    
    # CRITICAL: Fix "Sorry" logic
    if st.session_state.supported_team and st.session_state.supported_team not in top15['Team Name'].values:
        st.warning(f"Oops, {st.session_state.supported_team} is not in the top 15!!")

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    st.dataframe(df.style.apply(lambda row: ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == st.session_state.supported_team else '' for _ in row], axis=1), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    # ... (H2H logic here)
