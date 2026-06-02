# train.py
import os
import warnings

import numpy as np
import pandas as pd

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

BASE_DIR = r"E:\ML_project_WC"
PROCESSED_PATH = os.path.join(BASE_DIR, "processed_data.csv")


def prepare_data(df):
    df = df.copy()
    df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    df = df[df["match_date"] >= pd.Timestamp("2014-01-01")].copy()

    if "result" not in df.columns:
        gd = df["home_goals"] - df["away_goals"]
        df["result"] = np.where(gd > 0, "Win", np.where(gd < 0, "Loss", "Draw"))

    feature_cols = [c for c in [
        "home_elo", "away_elo", "elo_diff", "home_current_form",
        "away_current_form", "form_diff", "neutral"
    ] if c in df.columns]

    X = df[feature_cols].copy()
    X = X.fillna(X.median(numeric_only=True))

    y = df["result"].astype(str)

    label_map = {"Loss": 0, "Draw": 1, "Win": 2}
    y_enc = y.map(label_map).astype(int)

    return df, X, y_enc, label_map, feature_cols


def backtest_2022(model, df, feature_cols, label_map):
    test = df[
        (df["match_date"] >= pd.Timestamp("2022-01-01")) &
        (df["match_date"] <= pd.Timestamp("2022-12-31"))
    ].copy()

    if len(test) == 0:
        print("No 2022 matches found for backtest.")
        return

    X_test = test[feature_cols].copy().fillna(test[feature_cols].median(numeric_only=True))
    y_test = test["result"].map(label_map).astype(int)

    preds = model.predict(X_test)
    print("\n=== 2022 World Cup / 2022 Match Backtest ===")
    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds))
    print("Classification Report:")
    print(classification_report(y_test, preds, target_names=["Loss", "Draw", "Win"]))


def main():
    df = pd.read_csv(PROCESSED_PATH)
    df, X, y, label_map, feature_cols = prepare_data(df)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=400,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42,
    )

    model.fit(X_train, y_train)

    val_preds = model.predict(X_val)
    print("=== Validation Metrics ===")
    print(f"Accuracy: {accuracy_score(y_val, val_preds):.4f}")
    print(classification_report(y_val, val_preds, target_names=["Loss", "Draw", "Win"]))

    backtest_2022(model, df, feature_cols, label_map)


if __name__ == "__main__":
    main()
