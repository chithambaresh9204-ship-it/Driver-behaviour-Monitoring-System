import os
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np


class DriverReportPDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "DriveGuard - Driver Behaviour Monitoring System", ln=True)
        if os.path.exists("logo.png"):
            self.image("logo.png", 170, 8, 25)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"DriveGuard | Page {self.page_no()}", align="C")


# ---------------- SCORE GAUGE ----------------

def create_gauge(score):
    os.makedirs("charts", exist_ok=True)
    path = "charts/gauge.png"
    fig, ax = plt.subplots()
    theta = np.linspace(0, np.pi, 100)
    r = np.ones(100)
    ax.plot(theta, r)
    angle = np.pi * (score / 100)
    ax.plot([angle, angle], [0, 1], linewidth=3)
    ax.set_title(f"Driver Score: {score}")
    ax.axis("off")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


# ---------------- PIE CHART ----------------

def create_pie_chart(row):
    os.makedirs("charts", exist_ok=True)
    path = "charts/pie_chart.png"
    labels = ["Speed", "Focus", "Braking", "Turning"]
    values = [
        row["speed_control"],
        row["focus"],
        row["braking"],
        row["turning"]
    ]
    plt.figure(figsize=(4, 4))
    plt.pie(values, labels=labels, autopct="%1.0f%%")
    plt.title("Score Component Distribution")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path


# ---------------- TREND GRAPH ----------------

def create_line_chart(df):
    os.makedirs("charts", exist_ok=True)
    path = "charts/line_chart.png"
    data = df.head(6)
    plt.figure(figsize=(6, 4))
    plt.plot(data["month_year"], data["overall_score"], marker="o")
    plt.title("6 Month Driver Score Trend")
    plt.xlabel("Month")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path


# ---------------- REPORT GENERATION ----------------

def generate_driver_pdf(driver_id, driver_name, current_score, risk_level,
                        scores_df, prediction, return_bytes=False):
    """Generate a 3-page driver performance PDF report.
    
    Args:
        return_bytes: If True, return PDF as bytes instead of saving to file.
    """
    pdf = DriverReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ================= PAGE 1 =================
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Driver Safety Performance Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(60, 8, "Driver Name:")
    pdf.cell(0, 8, driver_name, ln=True)
    pdf.cell(60, 8, "Driver ID:")
    pdf.cell(0, 8, driver_id, ln=True)
    pdf.cell(60, 8, "Generated Time:")
    pdf.cell(0, 8, datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True)
    pdf.cell(60, 8, "Current Score:")
    pdf.cell(0, 8, str(current_score), ln=True)

    # Risk indicator box
    pdf.ln(5)
    risk_colors = {
        "Very Low": (16, 185, 129),
        "Low": (0, 200, 0),
        "Medium": (255, 200, 0),
        "High": (255, 0, 0),
    }
    color = risk_colors.get(risk_level, (100, 100, 100))
    pdf.set_fill_color(*color)
    pdf.cell(0, 10, f"Risk Level: {risk_level}", ln=True, fill=True)
    pdf.ln(10)

    # Gauge chart
    gauge = create_gauge(current_score)
    pdf.image(gauge, x=55, w=100)
    pdf.ln(60)

    pdf.multi_cell(
        0, 8,
        f"This report evaluates the driving behaviour of {driver_name}. "
        f"The driver currently holds a safety score of {current_score}. "
        f"The driver falls under the {risk_level} risk category based on "
        f"speed control, braking behaviour, turning stability and focus."
    )

    # ================= PAGE 2 =================
    pdf.add_page()
    latest = scores_df.iloc[0]
    pie_chart = create_pie_chart(latest)
    line_chart = create_line_chart(scores_df)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Score Component Distribution", ln=True, align="C")
    pdf.image(pie_chart, x=55, w=100)
    pdf.ln(65)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "6 Month Driver Score Trend", ln=True, align="C")
    pdf.image(line_chart, x=30, w=150)
    pdf.ln(70)

    # KPI Dashboard
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Driver KPI Dashboard", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)

    avg_score = round(scores_df.head(6)["overall_score"].mean(), 2)
    incidents = scores_df.head(6)["incidents_count"].sum()
    avg_speed = round(scores_df.head(6)["avg_speed"].mean(), 2)

    pdf.cell(60, 10, f"Avg Score: {avg_score}", border=1)
    pdf.cell(60, 10, f"Incidents: {incidents}", border=1)
    pdf.cell(60, 10, f"Avg Speed: {avg_speed}", border=1, ln=True)

    # ================= PAGE 3 =================
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Future Driver Score Prediction", ln=True, align="C")
    pdf.ln(10)

    predicted_score = prediction["predicted_score"]
    if predicted_score > current_score + 2:
        status = "Improving"
    elif predicted_score < current_score - 2:
        status = "Declining"
    else:
        status = "Stable"

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(60, 10, "Predicted Status:")
    pdf.set_font("Helvetica", "", 13)
    pdf.cell(0, 10, status, ln=True)
    pdf.ln(5)

    pdf.multi_cell(
        0, 8,
        f"The predicted driver safety score for the next month is "
        f"approximately {predicted_score}. The machine learning model "
        f"analyzes historical driving trends to estimate future safety."
    )
    pdf.ln(5)
    pdf.multi_cell(
        0, 8,
        "Recommendation: Maintain disciplined driving behaviour. "
        "Avoid overspeeding and aggressive braking to improve "
        "driver safety score."
    )

    # ================= OUTPUT =================
    if return_bytes:
        pdf_str = pdf.output(dest='S')
        if isinstance(pdf_str, str):
            return pdf_str.encode('latin-1')
        return bytes(pdf_str)

    os.makedirs("reports", exist_ok=True)
    path = f"reports/DriveGuard_Report_{driver_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(path)
    return path