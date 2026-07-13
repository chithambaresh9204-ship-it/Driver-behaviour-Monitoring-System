def calculate_driver_score(row):

    score = 100

    score -= row["harsh_acceleration_count"] * 1.5
    score -= row["harsh_braking_count"] * 1.5
    score -= row["sharp_turn_count"] * 1.2
    score -= row["distraction_events"] * 2
    score -= row["fatigue_score"] * 0.2

    if row["avg_speed"] < 50:
        score -= (50 - row["avg_speed"]) * 0.3

    if row["avg_speed"] > 70:
        score -= (row["avg_speed"] - 70) * 0.3

    score = max(0, min(100, score))

    return round(score, 2)


def classify_risk(score):
    """Classify risk level using 4-tier system"""
    if score >= 85:
        return "Very Low"
    elif score >= 70:
        return "Low"
    elif score >= 55:
        return "Medium"
    else:
        return "High"