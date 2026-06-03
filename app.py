import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="2026 World Cup Predictor")

# 1. CSS
st.markdown("""
    <style>
    .stApp { background: url('https://i.imgur.com/GtqgyfN.jpeg') no-repeat center center fixed; background-size: cover; }
    .block-container { 
        background: rgba(0, 0, 0, 0.3) !important; 
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px; 
    }
    .gold-title { color: gold !important; text-shadow: 2px 2px 4px black; }
    h1, h2, h3, label, p { color: white !important; text-shadow: 2px 2px 4px black; }
    div[data-baseweb="select"], .stButton>button { 
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    @media (max-width: 768px) {
        .block-container { backdrop-filter: none !important; background: rgba(0,0,0,0.6) !important; }
    }
    </style>
""", unsafe_allow_html=True)

# 2. DATA
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("simulation_results.csv")
    except Exception:
        return pd.DataFrame() 
    
    # Rename original 'round16_odds' to 'RO32 Odds'
    df = df.rename(columns={
        'team': 'Team Name',
        'elo_rating': 'ELO Rating',
        'round16_odds': 'RO32 Odds',
        'semi_odds': 'Semi Odds',
        'final_odds': 'Final Odds',
        'win_odds': 'Win Odds'
    })
    
    # Calculations
    if 'Semi Odds' in df.columns and 'Final Odds' in df.columns:
        df['Quarter Odds'] = df['Semi Odds'] + df['Final Odds']
    
    # Calculate RO16 Odds as Quarter + Semi (per your request to add them)
    if 'Quarter Odds' in df.columns and 'Semi Odds' in df.columns:
        df['RO16 Odds'] = df['Quarter Odds'] + df['Semi Odds']
    
    # Set explicit column order
    cols_order = ['Team Name', 'ELO Rating', 'RO32 Odds', 'RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']
    for col in cols_order:
        if col not in df.columns: df[col] = 0.0
    
    df = df[cols_order]
    df['ELO Rating'] = df['ELO Rating'].astype(int)
    df.insert(0, 'No.', range(1, 1 + len(df)))
    return df

df = load_data()

# 3. STATE & UI
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

st.markdown("##### The Greatest Sporting Event is here")
st.markdown("<h1 class='gold-title'>FIFA WORLD CUP 2026</h1>", unsafe_allow_html=True)

selected_team = st.selectbox(
    "⚽ Support a Team", 
    [""] + (df['Team Name'].tolist() if not df.empty else []),
    format_func=lambda x: "Select your fav team" if x == "" else x
)

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 4. LOGIC
if st.session_state.page == "Dashboard" and selected_team:
    st.header("Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    colors = [ 'gold' if x == selected_team else 'royalblue' for x in top15['Team Name']]
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h",
                 color=colors, color_discrete_map="identity", text_auto='.2%')
    fig.update_traces(textposition='outside')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    df_display = df.copy()
    for col in ['RO32 Odds', 'RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']:
        df_display[col] = df_display[col].apply(lambda x: f"{x*100:.2f}%")
    
    df_display = df_display.set_index('No.')
    def highlight_team(row):
        return ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == selected_team else '' for _ in row]
    
    st.dataframe(df_display.style.apply(highlight_team, axis=1), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    
    if st.button("Simulate Match"):
        if t1 == t2:
            st.warning("⚠️ Are you sure they are not the same team?")
        else:
            df_raw = load_data()
            def get_strength(name):
                match = df_raw[df_raw['Team Name'].astype(str).str.strip().str.lower() == name.strip().lower()]
                if match.empty: return 0.0
                cols = ['RO32 Odds', 'RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']
                existing_cols = [c for c in cols if c in match.columns]
                return float(match[existing_cols].sum(axis=1).iloc[0])

            s1, s2 = get_strength(t1), get_strength(t2)
            if s1 == 0 or s2 == 0:
                st.error("Error: Team data not found.")
            else:
                total_s = s1 + s2
                diff_ratio = abs(s1 - s2) / total_s
                pd = max(0.02, 0.30 * (1 - diff_ratio**0.5))
                remaining = 1.0 - pd
                p1, p2 = (s1 / total_s) * remaining, (s2 / total_s) * remaining
                c1, c2, c3 = st.columns(3)
                c1.metric(f"{t1} Win", f"{p1:.2%}")
                c2.metric("Draw", f"{pd:.2%}")
                c3.metric(f"{t2} Win", f"{p2:.2%}")
