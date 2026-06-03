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
    </style>
""", unsafe_allow_html=True)

# 2. DATA
@st.cache_data
def load_data():
    df = pd.read_csv("simulation_results.csv")
    
    # 1. Map columns based on their known position (0:Team, 1:ELO, 2:R16, 3:Qtr, 4:Semi, 5:Final, 6:Win)
    # We rename only the columns we actually have
    col_map = {df.columns[0]: 'Team Name', df.columns[1]: 'ELO Rating', 
               df.columns[2]: 'RO16 Odds', df.columns[3]: 'Quarter Odds', 
               df.columns[4]: 'Semi Odds', df.columns[5]: 'Final Odds', 
               df.columns[6]: 'Win Odds'}
    df = df.rename(columns=col_map)
    
    # 2. Ensure Quarter Odds is calculated correctly
    df['Quarter Odds'] = df['Semi Odds'] + df['Final Odds']
    
    # 3. Create clean subset
    df_clean = df[['Team Name', 'ELO Rating', 'RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']].copy()
    df_clean.insert(0, 'No.', range(1, 1 + len(df_clean)))
    return df_clean

df = load_data()

# 3. STATE
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 4. HEADER
st.markdown("##### The Greatest Sporting Event is here 🐐")
st.markdown("<h1 class='gold-title'>FIFA WORLD CUP 2026</h1>", unsafe_allow_html=True)

selected_team = st.selectbox(
    "⚽ Support a Team", 
    [""] + df['Team Name'].tolist(),
    format_func=lambda x: "Select your fav team" if x == "" else x
)

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Prediction Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📊 Tournament Table"): st.session_state.page = "Table"
if c3.button("⚔️ Head to Head Simulator"): st.session_state.page = "H2H"

st.markdown("---")

# 5. LOGIC
if st.session_state.page == "Dashboard" and selected_team:
    st.header("Prediction Dashboard")
    top15 = df.nlargest(15, 'Win Odds').sort_values("Win Odds", ascending=True)
    colors = [ 'gold' if x == selected_team else 'royalblue' for x in top15['Team Name']]
    fig = px.bar(top15, x="Win Odds", y="Team Name", orientation="h",
                 color=colors, color_discrete_map="identity", text_auto='.1%')
    fig.update_traces(textposition='outside')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Table":
    st.header("Tournament Table Odds")
    df_display = df.copy()
    for col in ['RO16 Odds', 'Quarter Odds', 'Semi Odds', 'Final Odds', 'Win Odds']:
        df_display[col] = df_display[col].apply(lambda x: f"{x*100:.1f}%")
    def highlight_team(row):
        return ['background-color: rgba(255, 215, 0, 0.3)' if row['Team Name'] == selected_team else '' for _ in row]
    st.dataframe(df_display.style.apply(highlight_team, axis=1).hide(axis='index'), use_container_width=True)

elif st.session_state.page == "H2H":
    st.header("Head to Head Simulator")
    t1 = st.selectbox("Team 1", df['Team Name'].tolist(), key="t1")
    t2 = st.selectbox("Team 2", df['Team Name'].tolist(), key="t2")
    
    if st.button("Simulate Match"):
        if t1 == t2:
            p1, pd, p2 = 0.50, 0.00, 0.50
        else:
            df_raw = pd.read_csv("simulation_results.csv")
            # Using same mapping logic for the raw CSV to ensure strength calculation is correct
            def get_strength(name):
                # Match based on first column index
                match = df_raw[df_raw.iloc[:, 0].astype(str).str.strip().str.lower() == name.strip().lower()]
                if match.empty: return 0.0
                # Use numerical indices for odds columns (2, 3, 4, 5, 6)
                return float(match.iloc[0, 2:7].sum())

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
                c1.metric(f"{t1} Win", f"{p1:.1%}")
                c2.metric("Draw", f"{pd:.1%}")
                c3.metric(f"{t2} Win", f"{p2:.1%}")
