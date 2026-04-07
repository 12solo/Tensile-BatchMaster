import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import requests
import re
import os
import base64

# ==========================================
# PAGE CONFIG — must be first Streamlit call
# ==========================================
st.set_page_config(
    page_title="Tensile Extrapolator | Solomon Scientific",
    page_icon="LOGO.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# GLOBAL CUSTOM CSS — Midnight Navy & Gold Theme
# ==========================================
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── CSS Variables ────────────────────────────── */
:root {
    --bg-main:    #0b1120; 
    --bg-panel:   #111827; 
    --text-main:  #f8fafc; 
    --text-muted: #94a3b8; 
    --gold:       #c9a84c; 
    --gold-dim:   #9c7a32;
    --border-color: rgba(201, 168, 76, 0.25);
    
    --font-head:  'Playfair Display', Georgia, serif;
    --font-mono:  'IBM Plex Mono', 'Courier New', monospace;
    --font-body:  'IBM Plex Sans', 'Segoe UI', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--font-body);
    color: var(--text-main);
}
.stApp { background: var(--bg-main); }

[data-testid="block-container"] {
    padding-top: 2rem !important; 
    padding-bottom: 2rem !important;
}

/* ── Sidebar ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border-color);
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: var(--text-main) !important;
}
.material-symbols-rounded,
[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
    color: var(--gold) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-weight: 700;
    text-transform: uppercase;
}
[data-testid="stSidebar"] hr { border-color: var(--border-color); }

/* ── Inputs ── */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] textarea {
    background: var(--bg-main) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-main) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
    color: var(--bg-main) !important;
    font-weight: 700;
    text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--gold), #e2c97e) !important;
    box-shadow: 0 4px 15px rgba(201,168,76,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER COMPONENTS
# ==========================================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_header():
    logo_path = "LOGO.png"
    if os.path.exists(logo_path):
        img_b64 = get_base64_of_bin_file(logo_path)
        icon_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 54px; height: 54px; border-radius: 8px; background: white; object-fit: contain;">'
    else:
        icon_html = '<div style="width: 54px; height: 54px; background: #c9a84c; border-radius: 8px; display: flex; align-items: center; justify-content: center;">🔬</div>'

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #111827 0%, #1a2540 100%); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(201,168,76,0.3); display: flex; align-items: center; gap: 1.5rem;">
        {icon_html}
        <div>
            <div style="font-family: 'Playfair Display'; font-size: 1.75rem; font-weight: 700; color: #f0f4fb;">Tensile Extrapolation Suite</div>
            <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px;">Solomon Scientific · © 2026</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, unit=""):
    return f"""
    <div style="background: #111827; border: 1px solid rgba(201,168,76,0.25); border-radius: 6px; padding: 1rem; border-top: 3px solid #c9a84c;">
        <div style="font-size:0.68rem; color:#94a3b8; text-transform:uppercase; font-weight:700;">{label}</div>
        <div style="font-size:1.35rem; color:#f8fafc; font-weight:700;">{value}<span style="font-size:0.7rem; color:#94a3b8; margin-left:4px;">{unit}</span></div>
    </div>
    """

# ==========================================
# PROCESSING ENGINE
# ==========================================
def robust_load(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            raw_bytes = file.getvalue().decode("utf-8", errors="ignore")
            sep = '\t' if '\t' in raw_bytes else (',' if ',' in raw_bytes else r'\s+')
            df = pd.read_csv(io.StringIO(raw_bytes), sep=sep, engine='python', on_bad_lines='skip')
        df.columns = [str(c).strip() for c in df.columns]
        return df.apply(pd.to_numeric, errors='coerce').dropna(subset=df.columns[:2])
    except: return None

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    render_sidebar_brand()
    project_name = st.text_input("Project Name", "PBAT/PLA")
    batch_id = st.text_input("Batch ID", "Batch-001")
    st.markdown("---")
    target_def = st.number_input("Target Final Deformation (mm)", value=395.54)
    area = st.number_input("Cross-sectional Area (mm²)", value=16.0)
    gauge_length = st.number_input("Initial Gauge Length (mm)", value=25.0)
    st.markdown("---")
    ym_start = st.number_input("Modulus Start (%)", value=0.2)
    ym_end = st.number_input("Modulus End (%)", value=1.2)
    ref_points = st.number_input("Extrapolation Ref Points", value=50)
    st.markdown("---")
    inset_x = st.slider("Inset X", 0.0, 0.8, 0.55)
    inset_y = st.slider("Inset Y", 0.0, 0.8, 0.05)

# ==========================================
# MAIN DASHBOARD
# ==========================================
render_header()
uploaded_file = st.file_uploader("Upload Tensile Data", type=['csv', 'xlsx', 'txt'])

if uploaded_file:
    df = robust_load(uploaded_file)
    if df is not None:
        cols = df.columns.tolist()
        c1, c2 = st.columns(2)
        force_col = c1.selectbox("Force Column", cols, index=0)
        def_col = c2.selectbox("Extension Column", cols, index=1)

        if st.button("RUN ANALYSIS", use_container_width=True):
            # Peak detection
            idx_max = df[force_col].idxmax()
            df_trimmed = df.loc[:idx_max].copy()
            
            # Extrapolation
            last_n = df_trimmed.tail(int(ref_points))
            slope, intercept = np.polyfit(last_n[def_col].values, last_n[force_col].values, 1)
            D_stop = df_trimmed[def_col].iloc[-1]
            L_stop = df_trimmed[force_col].iloc[-1]
            avg_step = np.mean(np.diff(df_trimmed[def_col].tail(10).values))
            
            D_new = np.arange(D_stop + avg_step, target_def + avg_step, avg_step)
            L_new = L_stop + slope * (D_new - D_stop)
            
            df_orig = pd.DataFrame({'Force (N)': df_trimmed[force_col], 'Deformation (mm)': df_trimmed[def_col], 'Type': 'Original'})
            df_ext = pd.DataFrame({'Force (N)': L_new, 'Deformation (mm)': D_new, 'Type': 'Extrapolated'})
            df_combined = pd.concat([df_orig, df_ext], ignore_index=True)
            
            # Normalize
            df_combined['Stress (MPa)'] = df_combined['Force (N)'] / area
            df_combined['Strain (%)'] = (df_combined['Deformation (mm)'] / gauge_length) * 100

            # --- BREAK POINT TRUNCATION ---
            # Finds the first point after UTS where stress drops below 5% of peak
            uts_val = df_combined['Stress (MPa)'].max()
            break_mask = (df_combined.index > idx_max) & (df_combined['Stress (MPa)'] < (0.05 * uts_val))
            if break_mask.any():
                break_idx = break_mask.idxmax()
                df_combined = df_combined.loc[:break_idx].copy()

            # Modulus
            mask_ym = (df_combined['Strain (%)'] >= ym_start) & (df_combined['Strain (%)'] <= ym_end)
            E, inter_ym = np.polyfit(df_combined.loc[mask_ym, 'Deformation (mm)']/gauge_length, df_combined.loc[mask_ym, 'Stress (MPa)'], 1)
            
            # UI Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(metric_card("Modulus", f"{E:.1f}", "MPa"), unsafe_allow_html=True)
            m2.markdown(metric_card("Peak Stress", f"{uts_val:.2f}", "MPa"), unsafe_allow_html=True)
            m3.markdown(metric_card("Final Strain", f"{df_combined['Strain (%)'].iloc[-1]:.1f}", "%"), unsafe_allow_html=True)
            m4.markdown(metric_card("Toughness", f"{np.trapezoid(df_combined['Stress (MPa)'], df_combined['Strain (%)']/100):.2f}", "MJ/m³"), unsafe_allow_html=True)

            # Plotting
            plt.rcParams.update({'font.family': 'Arial', 'axes.linewidth': 2, 'xtick.direction': 'in', 'ytick.direction': 'in'})
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.plot(df_combined[df_combined['Type']=='Original']['Strain (%)'], 
                    df_combined[df_combined['Type']=='Original']['Stress (MPa)'], color='#0b1120', lw=3, label='Original')
            ax.plot(df_combined[df_combined['Type']=='Extrapolated']['Strain (%)'], 
                    df_combined[df_combined['Type']=='Extrapolated']['Stress (MPa)'], color='#c9a84c', ls='--', lw=2.5, label='Extrapolated')
            
            ax.set_xlabel('Strain (%)', fontweight='bold', fontsize=12)
            ax.set_ylabel('Stress (MPa)', fontweight='bold', fontsize=12)
            ax.legend(frameon=True, edgecolor='black')
            
            # Inset
            axins = ax.inset_axes([inset_x, inset_y, 0.4, 0.4])
            axins.plot(df_combined['Strain (%)'], df_combined['Stress (MPa)'], color='#0b1120')
            axins.set_xlim(0, ym_end * 3)
            axins.set_ylim(0, df_combined.loc[df_combined['Strain (%)'] < ym_end*3, 'Stress (MPa)'].max()*1.2)
            ax.indicate_inset_zoom(axins, edgecolor="black")
            
            st.pyplot(fig)
