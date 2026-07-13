"""
DriveGuard — Intelligent Driver Behaviour Monitoring System
Modern UI/UX Edition
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from auth import AuthManager, init_auth_session, display_user_info
from database import db
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from fpdf import FPDF
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="DriveGuard — Driver Safety Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== MODERN CSS THEME ====================

st.markdown("""
<style>
    /* ---------- Import Google Font ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ---------- Global Fonts ---------- */
    .stApp, .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .st-emotion-cache-1gvkz7y, svg {
        font-family: inherit !important;
    }
    
    /* Force specific tags to dark independently of theme (fallback) */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1E293B;
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
    }

    /* ---------- Background ---------- */
    html, body, 
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main .block-container {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 50%, #F0F9FF 100%) !important;
    }

    /* ---------- Sidebar — Premium Dark ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 40%, #0F172A 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #CBD5E1 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 10px 16px !important;
        border-radius: 10px !important;
        margin: 3px 0 !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.12) !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] + label {
        background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }

    /* ---------- Headings ---------- */
    h1 { 
        color: #0F172A !important; 
        font-weight: 800 !important; 
        font-size: 2rem !important;
        letter-spacing: -0.02em !important;
    }
    h2 { 
        color: #1E293B !important; 
        font-weight: 700 !important; 
        font-size: 1.5rem !important;
    }
    h3 { 
        color: #334155 !important; 
        font-weight: 600 !important; 
        font-size: 1.2rem !important;
    }

    /* ---------- Metric Cards ---------- */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-2px);
    }
    [data-testid="stMetric"] label {
        color: #64748B !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }

    /* ---------- Custom HTML Metric Cards ---------- */
    .custom-dashboard-card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226,232,240,0.8);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        transition: all 0.25s ease;
    }
    .custom-dashboard-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    .custom-card-label {
        color: #475569 !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    .custom-card-val {
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-top: 4px !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338CA, #4F46E5) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669, #10B981) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25) !important;
    }

    /* ---------- Dropdowns ---------- */
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }
    /* Rest of the dropdown styling is handled by Streamlit's Light Theme */

    /* ---------- Dividers ---------- */
    hr { border-color: #E2E8F0 !important; opacity: 0.5 !important; }

    /* ---------- Alerts ---------- */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ---------- Expanders ---------- */
    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    .streamlit-expanderHeader p {
        color: inherit !important;
    }
    /* Main Content Expanders */
    .main [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
    }
    .main .streamlit-expanderHeader {
        color: #334155 !important;
    }
    /* Sidebar Expanders */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: transparent !important;
        border: none !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        color: #FFFFFF !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
init_auth_session()

# ==================== CONSTANTS ====================

MONTHS_LIST = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06',
               '2025-07', '2025-08', '2025-09', '2025-10', '2025-11']

MONTHS_DISPLAY = {
    '2025-01': 'January 2025', '2025-02': 'February 2025', '2025-03': 'March 2025',
    '2025-04': 'April 2025', '2025-05': 'May 2025', '2025-06': 'June 2025',
    '2025-07': 'July 2025', '2025-08': 'August 2025', '2025-09': 'September 2025',
    '2025-10': 'October 2025', '2025-11': 'November 2025'
}

RISK_COLORS = {
    'Very Low': '#10B981',
    'Low': '#3B82F6',
    'Medium': '#F59E0B',
    'High': '#EF4444',
}

RISK_ICONS = {
    'Very Low': '🟢',
    'Low': '🔵',
    'Medium': '🟡',
    'High': '🔴',
}

# ==================== UTILITY FUNCTIONS ====================

@st.cache_data
def get_driver_scores(driver_id: str) -> pd.DataFrame:
    """Get driver scores as DataFrame"""
    scores = db.get_monthly_scores(driver_id)
    if not scores:
        return pd.DataFrame()
    df = pd.DataFrame(scores, columns=[
        'score_id', 'driver_id', 'month_year', 'overall_score',
        'speed_control', 'focus', 'braking', 'turning',
        'risk_level', 'incidents_count', 'total_miles', 'avg_speed', 'created_at'
    ])
    return df

def calculate_risk_level(score: int) -> str:
    """Convert score to risk level"""
    if score >= 85: return 'Very Low'
    elif score >= 70: return 'Low'
    elif score >= 55: return 'Medium'
    else: return 'High'

def get_all_driver_ids():
    """Get all driver IDs"""
    drivers = db.get_all_drivers()
    return [driver[0] for driver in drivers] if drivers else []

# ==================== MODERN CHART BUILDERS ====================

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#334155', size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font=dict(family='Inter, sans-serif', color='#1E293B', size=18, weight='bold'),
    hoverlabel=dict(bgcolor='#1E293B', font_color='#FFFFFF', font_size=13, bordercolor='#334155'),
    xaxis=dict(tickfont=dict(color='#334155', size=11), title_font=dict(color='#1E293B', size=13), gridcolor='rgba(226,232,240,0.5)'),
    yaxis=dict(tickfont=dict(color='#334155', size=11), title_font=dict(color='#1E293B', size=13), gridcolor='rgba(226,232,240,0.5)'),
)

def create_score_chart(scores_df: pd.DataFrame, title: str = "Score Trend") -> go.Figure:
    """Modern line chart with gradient fill"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=scores_df['month_year'], y=scores_df['overall_score'],
        mode='lines+markers', name='Score',
        line=dict(color='#6366F1', width=3, shape='spline'),
        marker=dict(size=8, color='#6366F1', line=dict(width=2, color='#FFFFFF')),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.08)',
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(title=dict(text=title, font=dict(size=16, color='#1E293B', family='Inter')),
        height=380,
        yaxis=dict(range=[0, 105], gridcolor='rgba(226, 232, 240, 0.5)'),
        xaxis=dict(gridcolor='rgba(226, 232, 240, 0.5)'),
    )
    return fig

def create_pie_chart(score_data, title: str = "Score Components") -> go.Figure:
    """Modern donut chart"""
    components = {
        'Speed': int(score_data['speed_control']),
        'Focus': int(score_data['focus']),
        'Braking': int(score_data['braking']),
        'Turning': int(score_data['turning'])
    }
    fig = go.Figure(data=[go.Pie(
        labels=list(components.keys()), values=list(components.values()),
        hole=0.55,
        marker=dict(colors=['#6366F1', '#10B981', '#F59E0B', '#EF4444'],
                    line=dict(color='#FFFFFF', width=3)),
        textinfo='label+percent', textfont=dict(size=13, color='#334155'),
    )])
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(title=dict(text=title, font=dict(size=16, color='#1E293B')),
        height=400,
        showlegend=False,
    )
    return fig

# ==================== PREDICTION ENGINE ====================

def predict_next_month(driver_id: str) -> dict:
    """ML prediction for next month's score"""
    scores_df = get_driver_scores(driver_id)
    if len(scores_df) < 2:
        return None

    scores_df = scores_df.sort_values('month_year')
    X = np.arange(len(scores_df)).reshape(-1, 1)
    y = scores_df['overall_score'].values

    model = LinearRegression()
    model.fit(X, y)

    predicted_score = int(model.predict([[len(scores_df)]])[0])
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)
    accuracy = max(0, min(100, 100 - mae))
    current_score = y[-1]
    change = predicted_score - current_score

    if change > 2: trend = "Improving"
    elif change < -2: trend = "Declining"
    else: trend = "Stable"

    return {"predicted_score": predicted_score, "accuracy": accuracy, "trend": trend}

# ==================== PDF GENERATOR HELPERS ====================

def _create_trend_chart_img(df):
    """Creates a 12-month trend chart for the PDF"""
    import matplotlib.pyplot as plt
    import io
    
    plt.figure(figsize=(10, 4))
    # Standardize data
    data = df.sort_values('month_year').tail(12)
    
    plt.plot(data['month_year'], data['overall_score'], marker='o', color='#6366F1', linewidth=3, markersize=8)
    plt.fill_between(data['month_year'], data['overall_score'], color='#6366F1', alpha=0.1)
    
    plt.title("12-Month Score Trend", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Safety Score", fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, 105)
    
    # Hide top/right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    plt.close()
    img_buf.seek(0)
    return img_buf

def _create_component_chart_img(row):
    """Creates a bar chart for score components for the PDF"""
    import matplotlib.pyplot as plt
    import io
    
    plt.figure(figsize=(6, 4))
    labels = ['Speed', 'Focus', 'Braking', 'Turning']
    values = [row['speed_control'], row['focus'], row['braking'], row['turning']]
    colors = ['#6366F1', '#3B82F6', '#8B5CF6', '#EC4899']
    
    plt.bar(labels, values, color=colors, alpha=0.8, width=0.6)
    plt.title("Behavioral Breakdown", fontsize=14, fontweight='bold', pad=20)
    plt.ylim(0, 105)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Hide spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    for i, v in enumerate(values):
        plt.text(i, v + 2, f"{int(v)}", ha='center', fontweight='bold')
        
    plt.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    plt.close()
    img_buf.seek(0)
    return img_buf

# ==================== PDF GENERATOR ====================

def generate_professional_pdf(driver_id, driver_name, current_score, risk_level,
                               scores_df, prediction) -> bytes:
    """Generate 3-page professional PDF report"""
    driver_name = str(driver_name) if driver_name else f"Driver {driver_id}"
    current_score = int(current_score) if current_score else 0
    risk_level = str(risk_level) if risk_level else "Unknown"

    class HeaderFooterPDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 10)
            self.cell(0, 5, "DriveGuard - Intelligent Driver Behaviour Monitoring", ln=True)
            self.ln(2)
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "", 8)
            self.cell(0, 5, "DriveGuard Inc. | Driver Safety Solutions", align="L")
            self.cell(0, 5, f"Page {self.page_no()}", align="R", ln=True)

    pdf = HeaderFooterPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # PAGE 1 — Overview
    pdf.add_page()
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 12, "DRIVEGUARD", ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, "Driver Behaviour Monitoring System", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "DRIVER PERFORMANCE REPORT", ln=True, align="C")
    pdf.ln(8)

    for label, value in [
        ("Driver ID:", str(driver_id)),
        ("Driver Name:", driver_name),
        ("Report Date:", datetime.now().strftime('%Y-%m-%d %H:%M')),
        ("Current Score:", f"{current_score}/100"),
        ("Risk Level:", risk_level),
    ]:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(50, 8, label)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, value, ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "EXECUTIVE SUMMARY", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7,
        f"This report evaluates the driving behaviour of {driver_name} (ID: {driver_id}). "
        f"The driver holds a current safety score of {current_score}/100, categorized under "
        f"the '{risk_level}' risk level. This assessment is based on speed control, "
        f"braking patterns, turning stability, focus, and fatigue indicators."
    )

    # PAGE 1 - Component Chart
    try:
        current_data = scores_df.sort_values('month_year', ascending=False).iloc[0]
        comp_img = _create_component_chart_img(current_data)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(comp_img.getvalue())
            tmp_path = tmp.name
        pdf.image(tmp_path, x=50, w=110)
        os.unlink(tmp_path)
    except: pass

    # PAGE 2 — Performance Data
    pdf.add_page()
    
    # 12-Month Trend Chart
    try:
        trend_img = _create_trend_chart_img(scores_df)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(trend_img.getvalue())
            tmp_path = tmp.name
        pdf.image(tmp_path, x=20, w=170)
        os.unlink(tmp_path)
    except: pass
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "MONTHLY PERFORMANCE DATA", ln=True)
    pdf.ln(4)

    pdf.set_fill_color(79, 70, 229)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    headers = ["Month", "Score", "Speed", "Focus", "Braking", "Turning", "Risk"]
    widths = [30, 20, 22, 22, 22, 22, 22]
    for i, h in enumerate(headers):
        pdf.cell(widths[i], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    for _, row in scores_df.sort_values('month_year').head(12).iterrows():
        vals = [str(row['month_year']), str(int(row['overall_score'])),
                str(int(row['speed_control'])), str(int(row['focus'])),
                str(int(row['braking'])), str(int(row['turning'])),
                str(row['risk_level'])]
        for i, v in enumerate(vals):
            pdf.cell(widths[i], 7, v, border=1, align="C")
        pdf.ln()

    pdf.ln(8)
    avg_score = scores_df['overall_score'].mean()
    best = scores_df['overall_score'].max()
    worst = scores_df['overall_score'].min()
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f"Average Score: {avg_score:.1f}  |  Best: {int(best)}  |  Worst: {int(worst)}", ln=True)

    # PAGE 3 — Prediction
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "PREDICTION & RECOMMENDATIONS", ln=True)
    pdf.ln(4)

    if prediction and isinstance(prediction, dict) and prediction.get('predicted_score'):
        predicted_score = prediction.get('predicted_score', 0)
        trend = prediction.get('trend', 'Stable')
        accuracy = prediction.get('accuracy', 0)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, f"Predicted next month score: {predicted_score}/100")
        pdf.multi_cell(0, 7, f"Trend: {trend}  |  Model accuracy: {accuracy:.1f}%")
        pdf.ln(4)
    else:
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, "Insufficient data for prediction (need 2+ months).")
        pdf.ln(4)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "RECOMMENDATIONS", ln=True)
    pdf.set_font("Arial", "", 11)
    recommendations = [
        "Maintain consistent speeds within 50-70 km/h range.",
        "Avoid harsh braking - anticipate stops early.",
        "Minimize distractions while driving.",
        "Take regular breaks to combat fatigue on long routes.",
        "Practice smooth turning and lane changes.",
    ]
    for rec in recommendations:
        pdf.multi_cell(0, 7, f"  - {rec}")
        pdf.ln(1)

    pdf.ln(6)
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "This report is confidential and for authorized use only.", ln=True, align="C")

    pdf_str = pdf.output(dest='S')
    if isinstance(pdf_str, str):
        return pdf_str.encode('latin-1')
    return bytes(pdf_str)

# ==================== DATA IMPORT ====================

def import_real_dataset():
    """Import dataset with all drivers from CSV"""
    try:
        df = pd.read_csv('final_dataset.csv')
        import bcrypt

        unique_drivers = df[['driver_id', 'driver_name']].drop_duplicates()
        driver_mapping = {}
        drivers_created = 0

        for idx, (_, driver_row) in enumerate(unique_drivers.iterrows(), 1):
            csv_driver_id = str(driver_row['driver_id']).strip()
            driver_name = str(driver_row['driver_name']).strip()
            email = f"driver{idx}@gmail.com"
            password = "Password123!"

            existing = db.get_user_by_email(email)
            if not existing:
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                user_id = db.add_user(email, password_hash, driver_name, 'driver')
                if user_id:
                    drv_id = f"DRV{user_id:06d}"
                    db.add_driver(
                        driver_id=drv_id, user_id=user_id,
                        phone="9876543210", license_no=f"DL{idx:03d}",
                        license_exp=None, dob=None, address="India",
                        join_date=datetime.now().strftime('%Y-%m-%d')
                    )
                    driver_mapping[driver_name] = drv_id
                    drivers_created += 1
            else:
                drv_id = f"DRV{existing[0]:06d}"
                driver_mapping[driver_name] = drv_id
                drivers_created += 1

        records_imported = 0
        for _, row in df.iterrows():
            driver_name = str(row['driver_name']).strip()
            month_year = str(row['month']).strip()
            drv_id = None
            for name, mapped_id in driver_mapping.items():
                if name.lower() == driver_name.lower():
                    drv_id = mapped_id
                    break
            if not drv_id:
                continue

            overall_score = int((
                min(100, int(row['avg_speed'])) +
                min(100, max(0, 100 - (row['harsh_acceleration_count'] * 10))) +
                min(100, max(0, 100 - (row['harsh_braking_count'] * 10))) +
                min(100, max(0, 100 - (row['sharp_turn_count'] * 10))) +
                min(100, max(0, 100 - (row['fatigue_score']))) +
                min(100, max(0, 100 - (row['distraction_events'] * 15)))
            ) / 6)
            risk_level = calculate_risk_level(overall_score)

            try:
                db.add_monthly_score(
                    driver_id=drv_id, month_year=month_year,
                    overall_score=overall_score,
                    speed=min(100, int(row['avg_speed'])),
                    focus=min(100, max(0, 100 - (row['distraction_events'] * 15))),
                    braking=min(100, max(0, 100 - (row['harsh_braking_count'] * 10))),
                    turning=min(100, max(0, 100 - (row['sharp_turn_count'] * 10))),
                    risk_level=risk_level,
                    incidents=int(row['harsh_acceleration_count'] + row['harsh_braking_count']),
                    miles=int(row['trip_duration_minutes']),
                    avg_speed=int(row['avg_speed'])
                )
                records_imported += 1
            except Exception:
                pass

        return True, f"✓ Imported {records_imported} records for {drivers_created} drivers!"
    except FileNotFoundError:
        return False, "Error: final_dataset.csv not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== HELPER: METRIC CARD HTML ====================

def metric_card(icon, label, value, color="#6366F1"):
    """Render a premium glassmorphism metric card"""
    return f"""
    <div class='custom-dashboard-card'>
        <div style='font-size: 1.8rem; margin-bottom: 8px;'>{icon}</div>
        <div class='custom-card-label'>{label}</div>
        <div class='custom-card-val' style='color: {color};'>{value}</div>
    </div>
    """

# ========================================================================
# ==================== MAIN APPLICATION ====================
# ========================================================================

if st.session_state.user is None:
    AuthManager.show_login_page()
else:
    user = st.session_state.user

    # Auto-import on first run
    scores_count = db.execute_query("SELECT COUNT(*) as count FROM monthly_scores")
    if scores_count and scores_count[0][0] == 0:
        with st.spinner("🔄 Setting up your fleet data..."):
            success, message = import_real_dataset()
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    # ==================== SIDEBAR ====================
    with st.sidebar:
        # Logo / Brand
        st.markdown("""
        <div style='text-align: center; padding: 20px 0 10px 0;'>
            <div style='font-size: 2.2rem;'>🛡️</div>
            <div style='color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; letter-spacing: -0.02em; margin-top: 4px;'>DriveGuard</div>
            <div style='color: #64748B !important; font-size: 0.75rem; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px;'>Safety Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User info
        with st.expander("👤 User Information", expanded=False):
            display_user_info()

        st.markdown("---")

        # Navigation
        if user['role'] == 'driver':
            st.markdown("<p style='color: #64748B !important; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; padding-left: 16px;'>Navigation</p>", unsafe_allow_html=True)
            page = st.radio("Nav", [
                "🏠 Dashboard",
                "📊 Score Analysis",
                "📅 Time-Period Analysis"
            ], key="driver_nav", label_visibility="collapsed")
        else:
            st.markdown("<p style='color: #64748B !important; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; padding-left: 16px;'>Fleet Management</p>", unsafe_allow_html=True)
            page = st.radio("Nav", [
                "🏠 Fleet Dashboard",
                "👥 Drivers",
                "📊 Monthly Analysis",
                "📅 Time-Period Analysis",
                "🧠 Model Training",
                "📄 Reports"
            ], key="admin_nav", label_visibility="collapsed")

        st.markdown("---")
        AuthManager.show_logout_button()

        # Footer
        st.markdown("""
        <div style='position: fixed; bottom: 20px; left: 16px; right: 16px; text-align: center;'>
            <div style='color: #475569 !important; font-size: 0.68rem;'>DriveGuard v2.0</div>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================================
    # ==================== DRIVER PAGES ====================
    # ========================================================================

    if user['role'] == 'driver':
        driver_id = user.get('driver_id') or f"DRV{user['user_id']:06d}"
        driver = db.get_driver(driver_id)

        if not driver:
            st.error("❌ Driver profile not found. Contact admin.")
            st.stop()

        scores_df = get_driver_scores(driver_id)

        if scores_df.empty:
            st.warning("⚠️ No performance data yet.")
            st.info("💡 Use auto-created accounts (driver1@gmail.com / Password123!) to see demo data.")
            st.stop()

        # ---- DRIVER: Dashboard ----
        if page == "🏠 Dashboard":
            st.markdown("<h1>🏠 My Dashboard</h1>", unsafe_allow_html=True)

            current = scores_df.sort_values('month_year', ascending=False).iloc[0]
            risk_icon = RISK_ICONS.get(current['risk_level'], '⚪')

            # Hero metrics
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(metric_card("📈", "Current Score", f"{int(current['overall_score'])}", "#6366F1"), unsafe_allow_html=True)
            with c2:
                st.markdown(metric_card(risk_icon, "Risk Level", current['risk_level'], RISK_COLORS.get(current['risk_level'], '#666')), unsafe_allow_html=True)
            with c3:
                st.markdown(metric_card("⭐", "Avg Score", f"{scores_df['overall_score'].mean():.0f}", "#3B82F6"), unsafe_allow_html=True)
            with c4:
                st.markdown(metric_card("🏆", "Best Month", f"{int(scores_df['overall_score'].max())}", "#10B981"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Charts
            col1, col2 = st.columns([3, 2])
            with col1:
                st.plotly_chart(create_score_chart(scores_df.sort_values('month_year'), "Performance Trend"), use_container_width=True, theme=None)
            with col2:
                st.plotly_chart(create_pie_chart(current, "Score Breakdown"), use_container_width=True, theme=None)

            # Driver details (collapsed)
            with st.expander("👤 My Details", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Full Name", value=user['full_name'], disabled=True)
                    st.text_input("Driver ID", value=driver_id, disabled=True)
                with c2:
                    st.text_input("Email", value=user['email'], disabled=True)
                    st.text_input("Status", value=driver[8] or "Active", disabled=True)

        # ---- DRIVER: Score Analysis ----
        elif page == "📊 Score Analysis":
            st.markdown("<h1>📊 Score Analysis</h1>", unsafe_allow_html=True)

            st.plotly_chart(create_score_chart(scores_df.sort_values('month_year'), "Your Performance Trend"), use_container_width=True, theme=None)

            st.divider()
            st.markdown("<h3>Monthly Breakdown</h3>", unsafe_allow_html=True)

            selected_month = st.selectbox("Select Month", sorted(scores_df['month_year'].unique(), reverse=True), key="driver_month_sel")
            month_data = scores_df[scores_df['month_year'] == selected_month]

            if not month_data.empty:
                m = month_data.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Score", int(m['overall_score']))
                with c2: st.metric("Risk Level", m['risk_level'])
                with c3: st.metric("Incidents", int(m['incidents_count']))
                with c4: st.metric("Avg Speed", f"{int(m['avg_speed'])} km/h")

                st.divider()
                st.plotly_chart(create_pie_chart(m, f"Components — {selected_month}"), use_container_width=True, theme=None)

        # ---- DRIVER: Time-Period Analysis ----
        elif page == "📅 Time-Period Analysis":
            st.markdown("<h1>📅 Time-Period Analysis</h1>", unsafe_allow_html=True)

            available = sorted(scores_df['month_year'].unique(), reverse=True)
            if len(available) < 2:
                st.warning("⚠️ Need at least 2 months of data.")
            else:
                c1, c2 = st.columns(2)
                with c1: 
                    end_m = st.selectbox("Select 6-Month Period Ending", available, index=0, key="d6_end")

                try:
                    end_idx = MONTHS_LIST.index(end_m)
                    start_idx = max(0, end_idx - 5)
                    start_m = MONTHS_LIST[start_idx]
                    filtered = scores_df[(scores_df['month_year'] >= start_m) & (scores_df['month_year'] <= end_m)]
                except ValueError:
                    filtered = pd.DataFrame()

                if len(filtered) > 0:
                    vs = filtered['overall_score'].dropna()
                    if len(vs) > 0:
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Avg Score", f"{vs.mean():.0f}")
                        with c2: st.metric("Best", int(vs.max()))
                        with c3: st.metric("Worst", int(vs.min()))
                        with c4:
                            t = "📈 Improving" if vs.iloc[-1] > vs.iloc[0] else "📉 Declining" if vs.iloc[-1] < vs.iloc[0] else "→ Stable"
                            st.metric("Trend", t)

                        st.divider()
                        st.plotly_chart(create_score_chart(filtered.sort_values('month_year'), "Period Trend"), use_container_width=True, theme=None)

                        c1, c2 = st.columns(2)
                        with c1: st.metric("Total Incidents", int(filtered['incidents_count'].sum()))
                        with c2: st.metric("Avg Speed", f"{int(filtered['avg_speed'].mean())} km/h")

    # ========================================================================
    # ==================== ADMIN PAGES ====================
    # ========================================================================

    else:

        # ---- ADMIN: Fleet Dashboard ----
        if page == "🏠 Fleet Dashboard":
            st.markdown("<h1>🏠 Fleet Dashboard</h1>", unsafe_allow_html=True)

            selected_month = st.selectbox("Select Month", MONTHS_LIST, format_func=lambda x: MONTHS_DISPLAY.get(x, x), key="fleet_m")

            all_ids = get_all_driver_ids()
            month_data_list = []
            for did in all_ids:
                scores = db.get_monthly_scores(did)
                if scores:
                    tdf = pd.DataFrame(scores, columns=[
                        'score_id','driver_id','month_year','overall_score',
                        'speed_control','focus','braking','turning',
                        'risk_level','incidents_count','total_miles','avg_speed','created_at'
                    ])
                    ms = tdf[tdf['month_year'] == selected_month]
                    if not ms.empty:
                        r = ms.iloc[0]
                        month_data_list.append({
                            'driver_id': did, 'score': r['overall_score'],
                            'risk_level': r['risk_level'], 'speed': r['avg_speed'],
                            'incidents': r['incidents_count'],
                            'speed_ctrl': r['speed_control'], 'braking': r['braking']
                        })

            if month_data_list:
                mdf = pd.DataFrame(month_data_list)

                # Hero cards
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(metric_card("📊", "Fleet Avg", f"{mdf['score'].mean():.0f}", "#6366F1"), unsafe_allow_html=True)
                with c2:
                    hr = len(mdf[mdf['risk_level'] == 'High'])
                    st.markdown(metric_card("🔴", "High Risk", str(hr), "#EF4444"), unsafe_allow_html=True)
                with c3:
                    st.markdown(metric_card("👥", "Total Drivers", str(len(mdf)), "#3B82F6"), unsafe_allow_html=True)
                with c4:
                    vl = len(mdf[mdf['risk_level'] == 'Very Low'])
                    si = (vl / len(mdf)) * 100 if len(mdf) > 0 else 0
                    st.markdown(metric_card("🟢", "Safety Index", f"{si:.0f}%", "#10B981"), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Top & Bottom 3
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<h3>🏆 Top Performers</h3>", unsafe_allow_html=True)
                    for idx, (_, d) in enumerate(mdf.nlargest(3, 'score').iterrows(), 1):
                        badge = "🥇🥈🥉"[idx-1]
                        rc = RISK_COLORS.get(d['risk_level'], '#666')
                        st.markdown(f"""
                        <div style='color: #1E293B; background: rgba(255,255,255,0.8); border-radius: 12px; padding: 12px 16px; margin: 8px 0; border-left: 4px solid {rc};'>
                            <strong>{badge} {d['driver_id']}</strong> - Score: <strong>{d['score']:.0f}</strong> | 
                            <span style='color: {rc}; font-weight: 600;'>{d['risk_level']}</span>
                        </div>""", unsafe_allow_html=True)

                with c2:
                    st.markdown("<h3>⚠️ Needs Attention</h3>", unsafe_allow_html=True)
                    for idx, (_, d) in enumerate(mdf.nsmallest(3, 'score').iterrows(), 1):
                        rc = RISK_COLORS.get(d['risk_level'], '#666')
                        st.markdown(f"""
                        <div style='color: #1E293B; background: rgba(255,255,255,0.8); border-radius: 12px; padding: 12px 16px; margin: 8px 0; border-left: 4px solid {rc};'>
                            <strong>⬇️ {d['driver_id']}</strong> - Score: <strong>{d['score']:.0f}</strong> | 
                            <span style='color: {rc}; font-weight: 600;'>{d['risk_level']}</span>
                        </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Charts row
                c1, c2 = st.columns(2)
                with c1:
                    risk_counts = mdf['risk_level'].value_counts()
                    fig = go.Figure(data=[go.Pie(
                        labels=risk_counts.index, values=risk_counts.values,
                        hole=0.55,
                        marker=dict(colors=[RISK_COLORS.get(l, '#999') for l in risk_counts.index],
                                    line=dict(color='#FFFFFF', width=3)),
                    )])
                    fig.update_layout(**CHART_LAYOUT)
                    fig.update_layout(title=dict(text="Risk Distribution"), height=380)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

                with c2:
                    fig = go.Figure(data=[go.Bar(
                        x=['Avg Speed', 'Avg Incidents', 'Speed Ctrl', 'Braking'],
                        y=[mdf['speed'].mean(), mdf['incidents'].mean(),
                           mdf['speed_ctrl'].mean(), mdf['braking'].mean()],
                        marker_color=['#6366F1', '#EF4444', '#F59E0B', '#10B981'],
                        marker=dict(cornerradius=6),
                    )])
                    fig.update_layout(**CHART_LAYOUT)
                    fig.update_layout(title=dict(text="Fleet Metrics"), height=380, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, theme=None)
            else:
                st.info(f"No data for {MONTHS_DISPLAY.get(selected_month, selected_month)}")

        # ---- ADMIN: Drivers Management ----
        elif page == "👥 Drivers":
            st.markdown("<h1>👥 Driver Management</h1>", unsafe_allow_html=True)

            all_ids = get_all_driver_ids()
            if all_ids:
                sel = st.selectbox("Select Driver", all_ids, key="mgmt_d")
                sdf = get_driver_scores(sel)

                if not sdf.empty:
                    latest = sdf.sort_values('month_year', ascending=False).iloc[0]

                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("Avg Score (12M)", f"{sdf['overall_score'].mean():.0f}")
                    with c2: st.metric("Best Month", int(sdf['overall_score'].max()))
                    with c3: st.metric("Worst Month", int(sdf['overall_score'].min()))
                    with c4: st.metric("Current", int(latest['overall_score']))

                    st.divider()
                    st.plotly_chart(create_score_chart(sdf.sort_values('month_year'), f"Performance — {sel}"), use_container_width=True, theme=None)
                else:
                    st.info(f"No data for {sel}")

        # ---- ADMIN: Monthly Analysis ----
        elif page == "📊 Monthly Analysis":
            st.markdown("<h1>📊 Monthly Analysis</h1>", unsafe_allow_html=True)

            all_ids = get_all_driver_ids()
            if all_ids:
                c1, c2 = st.columns(2)
                with c1: sel_d = st.selectbox("Driver", all_ids, key="ma_d")
                sdf = get_driver_scores(sel_d)

                if not sdf.empty:
                    avail = sorted(sdf['month_year'].unique(), reverse=True)
                    with c2: sel_m = st.selectbox("Month", avail, key="ma_m")

                    md = sdf[sdf['month_year'] == sel_m]
                    if not md.empty:
                        r = md.iloc[0]
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Score", int(r['overall_score']))
                        with c2: st.metric("Risk", r['risk_level'])
                        with c3: st.metric("Incidents", int(r['incidents_count']))
                        with c4: st.metric("Avg Speed", f"{int(r['avg_speed'])} km/h")

                        st.divider()
                        st.plotly_chart(create_pie_chart(r, f"Components — {sel_d} ({sel_m})"), use_container_width=True, theme=None)

        # ---- ADMIN: 6-Month Analysis ----
        elif page == "📅 Time-Period Analysis":
            st.markdown("<h1>📅 Time-Period Analysis</h1>", unsafe_allow_html=True)

            all_ids = get_all_driver_ids()
            if all_ids:
                c1, c2, c3 = st.columns(3)
                with c1: sel_d = st.selectbox("Driver", all_ids, key="a6_d")
                sdf = get_driver_scores(sel_d)

                if not sdf.empty:
                    avail = sorted(sdf['month_year'].unique(), reverse=True)
                    with c2: 
                        lo = st.selectbox("From", avail[::-1], key="a6_l")
                    with c3:
                        hi = st.selectbox("To", avail, key="a6_h")

                    try:
                        fdf = sdf[(sdf['month_year'] >= lo) & (sdf['month_year'] <= hi)]
                    except ValueError:
                        fdf = pd.DataFrame()

                    if len(fdf) > 0:
                        vs = fdf['overall_score'].dropna()
                        if len(vs) > 0:
                            c1, c2, c3, c4 = st.columns(4)
                            with c1: st.metric("Avg", f"{vs.mean():.0f}")
                            with c2: st.metric("Best", int(vs.max()))
                            with c3: st.metric("Worst", int(vs.min()))
                            with c4:
                                td = vs.iloc[-1] - vs.iloc[0]
                                st.metric("Trend", "📈 Up" if td > 0 else "📉 Down" if td < 0 else "→ Stable")

                            st.divider()
                            st.plotly_chart(create_score_chart(fdf.sort_values('month_year'), f"Trend ({lo} to {hi})"), use_container_width=True, theme=None)

        # ---- ADMIN: Model Training ----
        elif page == "🧠 Model Training":
            st.markdown("<h1>🧠 Model Training & Predictions</h1>", unsafe_allow_html=True)

            all_ids = get_all_driver_ids()
            if all_ids:
                sel_d = st.selectbox("Select Driver", all_ids, key="mt_d")
                sdf = get_driver_scores(sel_d)

                if not sdf.empty:
                    # Section 1: Actual Performance
                    st.markdown("<h3>📊 Actual Performance (12 Months)</h3>", unsafe_allow_html=True)
                    st.plotly_chart(
                        create_score_chart(sdf.sort_values('month_year'), "12-Month Performance"),
                        use_container_width=True
                    )

                    st.divider()

                    # Section 2: Prediction & Forecast
                    prediction = predict_next_month(sel_d)
                    if prediction:
                        st.markdown("<h3>🔮 Prediction & Forecast</h3>", unsafe_allow_html=True)

                        current_sc = int(sdf.sort_values('month_year').iloc[-1]['overall_score'])
                        change = prediction['predicted_score'] - current_sc
                        trend_icon = "📈" if change > 2 else "📉" if change < -2 else "➡️"

                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.markdown(metric_card("🎯", "Predicted Score", str(prediction['predicted_score']), "#6366F1"), unsafe_allow_html=True)
                        with c2:
                            st.markdown(metric_card("📏", "Accuracy", f"{prediction['accuracy']:.1f}%", "#10B981"), unsafe_allow_html=True)
                        with c3:
                            st.markdown(metric_card(trend_icon, "Trend", prediction['trend'], "#3B82F6"), unsafe_allow_html=True)
                        with c4:
                            c_color = "#10B981" if change > 0 else "#EF4444" if change < 0 else "#64748B"
                            st.markdown(metric_card("📊", "Score Change", f"{change:+}", c_color), unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Actual vs Predicted chart
                        sorted_df = sdf.sort_values('month_year')
                        X_act = np.arange(len(sorted_df))
                        y_act = sorted_df['overall_score'].values

                        lr = LinearRegression()
                        lr.fit(X_act.reshape(-1, 1), y_act)
                        future_x = np.arange(len(sorted_df), len(sorted_df) + 3).reshape(-1, 1)
                        future_preds = lr.predict(future_x)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=sorted_df['month_year'].tolist(),
                            y=y_act.tolist(),
                            mode='lines+markers', name='Actual',
                            line=dict(color='#6366F1', width=3, shape='spline'),
                            marker=dict(size=8, color='#6366F1', line=dict(width=2, color='#FFF')),
                            fill='tozeroy', fillcolor='rgba(99,102,241,0.06)',
                        ))
                        fig.add_trace(go.Scatter(
                            x=[sorted_df['month_year'].iloc[-1]] + [f"+{i}m" for i in range(1, 4)],
                            y=[y_act[-1]] + list(future_preds),
                            mode='lines+markers', name='Forecast',
                            line=dict(color='#EF4444', width=3, dash='dash'),
                            marker=dict(size=8, color='#EF4444', symbol='diamond',
                                        line=dict(width=2, color='#FFF')),
                        ))
                        fig.update_layout(**CHART_LAYOUT)
                        fig.update_layout(title=dict(text="Actual vs Forecast", font=dict(size=16, color='#1E293B')),
                            height=400,
                            yaxis=dict(range=[0, 105], gridcolor='rgba(226,232,240,0.5)'),
                            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)', bordercolor='#E2E8F0'),
                        )
                        st.plotly_chart(fig, use_container_width=True, theme=None)

                        st.metric("🔒 Confidence", f"{min(100, prediction['accuracy'] + 20):.0f}%")
                    else:
                        st.warning("⚠️ Need at least 2 months of data for predictions.")
                else:
                    st.info(f"No data for {sel_d}")

        # ---- ADMIN: Report Generation ----
        elif page == "📄 Reports":
            st.markdown("<h1>📄 Report Generation</h1>", unsafe_allow_html=True)

            all_ids = get_all_driver_ids()
            if all_ids:
                sel_d = st.selectbox("Select Driver", all_ids, key="rpt_d")
                sdf = get_driver_scores(sel_d)

                if not sdf.empty:
                    driver = db.get_driver(sel_d)
                    csd = db.get_current_month_score(sel_d)
                    prediction = predict_next_month(sel_d)

                    if driver and csd:
                        d_name = driver[9] if driver[9] else f"Driver {sel_d}"
                        c_score = int(csd[3])
                        r_level = csd[8]
                        r_color = RISK_COLORS.get(r_level, '#666')
                        r_icon = RISK_ICONS.get(r_level, '⚪')

                        # Report Preview Card
                        st.markdown(f"""
                        <div style='
                            background: rgba(255,255,255,0.9);
                            backdrop-filter: blur(16px);
                            border: 1px solid rgba(226,232,240,0.8);
                            border-radius: 20px;
                            padding: 32px;
                            margin: 16px 0;
                            box-shadow: 0 4px 24px rgba(0,0,0,0.04);
                        '>
                            <div style='text-align: center; margin-bottom: 20px;'>
                                <div style='font-size: 2rem;'>🛡️</div>
                                <div style='color: #6366F1; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em;'>DRIVEGUARD</div>
                                <div style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;'>Driver Performance Report</div>
                            </div>
                            <hr style='border: none; border-top: 1px solid #E2E8F0; margin: 16px 0;'>
                            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px;'>
                                <div><span style='color: #94A3B8; font-size: 0.82rem;'>Driver</span><br><strong style='color: #1E293B; font-size: 1.1rem;'>{d_name}</strong></div>
                                <div><span style='color: #94A3B8; font-size: 0.82rem;'>ID</span><br><strong style='color: #1E293B; font-size: 1.1rem;'>{sel_d}</strong></div>
                                <div><span style='color: #94A3B8; font-size: 0.82rem;'>Score</span><br><strong style='color: #6366F1; font-size: 1.4rem;'>{c_score}/100</strong></div>
                                <div><span style='color: #94A3B8; font-size: 0.82rem;'>Risk</span><br><strong style='color: {r_color}; font-size: 1.1rem;'>{r_icon} {r_level}</strong></div>
                            </div>
                            <hr style='border: none; border-top: 1px solid #E2E8F0; margin: 16px 0;'>
                            <div style='color: #64748B; font-size: 0.88rem;'>
                                <strong style='color: #334155;'>Report includes:</strong>
                                <div style='margin-top: 8px; display: grid; grid-template-columns: 1fr 1fr; gap: 6px;'>
                                    <div>📋 Driver overview & metrics</div>
                                    <div>📊 Monthly performance data</div>
                                    <div>🔮 Score predictions</div>
                                    <div>💡 Improvement recommendations</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Quick stats
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Score", f"{c_score}/100")
                        with c2: st.metric("Risk", r_level)
                        with c3: st.metric("Avg Score", f"{sdf['overall_score'].mean():.0f}")
                        with c4: st.metric("Data Months", len(sdf))

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Download button
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c2:
                            if st.button("📥 Generate PDF Report", use_container_width=True):
                                try:
                                    pdf_bytes = generate_professional_pdf(
                                        sel_d, d_name, c_score, r_level, sdf, prediction or {}
                                    )
                                    st.success("✅ Report generated!")
                                    st.download_button(
                                        label="📥 Download PDF Report",
                                        data=pdf_bytes,
                                        file_name=f"DriveGuard_{sel_d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Driver details not found.")
                else:
                    st.info(f"No data for {sel_d}")

if __name__ == '__main__':
    pass 