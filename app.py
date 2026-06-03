import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 2. GLASSMORPHISM CSS
# Replace the URL below with your direct .jpg/.png link
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://i.imgur.com/GtqgyfN.jpeg');
        background-size: cover;
        background-attachment: fixed;
    }
    /* Apply Glassmorphism to the main content area */
    section.main > div {
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 40px;
        color: white;
    }
    h1, h2, h3, p, div { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 3. HELPER FUNCTIONS
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    df['quarter_odds'] = df['semi_odds'] + df['final_odds']
    # Specific column order
    cols = ['team', 'elo_rating', 'round16_odds', 'quarter_odds', 'semi_odds', 'final_odds', 'win_odds']
    df = df[cols]
    df = df.rename(columns={
        'team': 'Team Name', 'elo_rating': 'ELO Rating', 'round16_odds': 'RO16 Odds',
        'quarter_odds': 'Quarter Odds', 'semi_odds': 'Semi Odds', 'final_odds': 'Final Odds', 'win_odds': 'Win Odds'
    })
    df.index = df.index + 1
    return df

def match_prob(ra, rb, home_adv=65.0):
    diff = (ra + home_adv) - rb
    p_win = 1 / (1 + 10 ** (-diff / 400))
    p_draw = max(0.12, 0.28 - abs(diff) / 2000)
    p_draw = min(p_draw, 0.35)
    scale = 1 - p_draw
    return p_win * scale, p_draw, (1 - p_win) * scale

# 4. INITIALIZE SESSION
if 'supported_team' not in st.session_state: st.session_state.supported_team = None
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 5. UI LAYOUT
st.title("The Greatest Sporting Event is here 🐐")
df = load_data()

with st.expander("⚽ Support a Team"):
    st.session_state.supported_team = st.selectbox("Select your nation:", df['Team Name'].tolist())

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 6. PAGE NAVIGATION
if st.session_state.page == "Dashboard":
    st.header("Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    
    # Highlight
    top15['color'] = top15['Team Name'].apply(lambda x: 'Selected' if x == st.session_state.supported_team else 'Other')
    
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h", color="color",
                 color_discrete_map={"Selected": "gold", "Other": "royalblue"})
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.supported_team and st.session_state.supported_team not in top15['Team Name'].values:
        st.warning(f"Oops, {st.session_state.supported_team} is not in the top 15!!")

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    def style_row(row):
        return ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == st.session_state.supported_team else '' for _ in row]
    st.dataframe(df.style.apply(style_row, axis=1), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist())
    t2 = st.selectbox("Team 2", df['Team Name'].tolist())
    if st.button("Simulate"):
        ra = df.loc[df['Team Name'] == t1, 'ELO Rating'].values[0]
        rb = df.loc[df['Team Name'] == t2, 'ELO Rating'].values[0]
        p1, pd, p2 = match_prob(ra, rb)
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{t1} Win", f"{p1:.1%}")
        col2.metric("Draw", f"{pd:.1%}")
        col3.metric(f"{t2} Win", f"{p2:.1%}")
