from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

FILE_NAME = "final_dataset.csv"

# Create CSV file if not exists
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=[
        "driver_id",
        "driver_name",
        "month",
        "trip_id",
        "avg_speed",
        "harsh_acceleration_count",
        "harsh_braking_count",
        "sharp_turn_count",
        "fatigue_score",
        "distraction_events",  
        "trip_duration_minutes",
        "timestamp"
    ])
    df.to_csv(FILE_NAME, index=False)

# =============================
# UPLOAD ROUTE
# =============================
@app.route("/upload", methods=["POST"])
def upload_data():
    try:
        data = request.get_json()
        print("Received data:", data)

        # Add timestamp
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to CSV
        new_row = pd.DataFrame([data])
        new_row.to_csv(FILE_NAME, mode='a', header=False, index=False)

        return jsonify({
            "status": "success",
            "message": "Data stored successfully"
        }), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =============================
# VIEW DATA ROUTE
# =============================
@app.route("/data", methods=["GET"])
def get_data():
    try:
        df = pd.read_csv(FILE_NAME)
        return jsonify(df.to_dict(orient="records")), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =============================
# RUN SERVER
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)