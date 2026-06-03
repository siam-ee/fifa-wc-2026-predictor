import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 1. FIXED CSS: Targets the whole app area for glass
st.markdown("""
    <style>
    .stApp { background-image: url('https://i.imgur.com/GtqgyfN.jpeg'); background-size: cover; background-attachment: fixed; }
    
    /* Target the main container and all children to ensure glass covers everything */
    section.main { 
        background: rgba(0, 0, 0, 0.5) !important; 
        backdrop-filter: blur(10px) !important;
        border-radius: 20px; 
        padding: 2rem !important;
    }
    
    /* Glassify inputs/buttons */
    div[data-baseweb="select"], .stButton>button { 
        background-color: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: white !important;
    }
    
    /* Readable text */
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
    
    # FORCED FORMATTING: Convert to string with 3 decimal places
    cols_to_format = ['RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']
    for col in cols_to_format:
        df[col] = df[col].map('{:.3f}'.format)
    
    return df

df = load_data()

# 3. NAVIGATION UI
if 'page' not in st.session_state: st.session_state.page = "Dashboard"
selected_team = st.selectbox("⚽ Support a Team", [""] + df['Team Name'].tolist(), format_func=lambda x: x if x else "Select a team...")

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 4. PAGE LOGIC
if st.session_state.page == "Dashboard" and selected_team:
    st.header("Prediction Dashboard")
    # Convert back to float for plotting
    plot_df = df.copy()
    for col in ['Win Odds']: plot_df[col] = plot_df[col].astype(float)
    
    top15 = plot_df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    top15['color'] = top15['Team Name'].apply(lambda x: 'Selected' if x == selected_team else 'Other')
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h", color="color", 
                 color_discrete_map={"Selected": "gold", "Other": "royalblue"}, text_auto='.3f')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    st.dataframe(df.style.hide(axis='index'), use_container_width=True)
