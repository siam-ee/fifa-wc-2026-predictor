# 🏆 2026 FIFA World Cup Prediction Dashboard

An end-to-end machine learning pipeline and interactive simulation engine that predicts the winner of the upcoming 48-team 2026 FIFA World Cup. This project runs **10,000 Monte Carlo simulations** of the tournament structure to calculate realistic progression odds.

🔗 **[PASTE YOUR LIVE STREAMLIT WEB LINK HERE]**


## 🚀 Features
* **Predictive ML Model:** Uses an algorithm trained on historical international football data to evaluate team matchups.
* **10,000x Monte Carlo Engine:** Simulates the brand-new 48-team tournament layout, including group stage points and the new Round of 32 knockout bracket.
* **Interactive Head-to-Head Simulator:** Select any two tournament teams from a dropdown to instantly see their simulated win, loss, or draw probabilities.
* **Full Tournament Odds Table:** Displays advanced metrics for all 48 qualified countries showing their chances to reach the Round of 16, Semifinals, Finals, and lift the trophy.


## 📊 The Data Stack
This project integrates four comprehensive sports datasets to build its features:
1. Historical international football match results (1872 to 2025).
2. Historical team ELO ratings to calculate long-term strength and momentum (1872 to 2025)
3. Specific World Cup tournament match history (1930 to 2022) to scale tournament pressure.
4. The official 48-team 2026 FIFA World Cup group distributions, match schedule and host cities.


## 🔮 Top Model Prediction
According to the final model simulation, **Spain** has the highest probability of winning the 2026 World Cup with a **16.75%** overall chance, heavily weighted by their exceptional ELO and defensive metrics leading into the tournament year.


## 🛠️ Tech Stack & Requirements
* **Language:** Python
* **Web UI Framework:** Streamlit
* **Data Science:** Pandas, NumPy
* **Machine Learning:** XGBoost, Scikit-Learn
* **Visualization:** Plotly
