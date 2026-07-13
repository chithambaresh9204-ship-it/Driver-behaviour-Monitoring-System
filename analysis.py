import pandas as pd
from scoring import calculate_driver_score, classify_risk


def analyze_driver():

    df = pd.read_csv("final_dataset.csv")

    df["month"] = pd.to_datetime(df["month"])

    monthly = df.groupby(
        ["driver_id","driver_name","month"]
    ).agg({
        "avg_speed":"mean",
        "harsh_acceleration_count":"sum",
        "harsh_braking_count":"sum",
        "sharp_turn_count":"sum",
        "fatigue_score":"mean",
        "distraction_events":"sum"
    }).reset_index()

    monthly["driver_score"] = monthly.apply(calculate_driver_score,axis=1)

    monthly["risk_level"] = monthly["driver_score"].apply(classify_risk)

    return monthly