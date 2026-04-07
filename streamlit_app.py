import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import re
import os
import base64

# ==========================================
# PAGE CONFIG — must be first Streamlit call
# ==========================================
st.set_page_config(
    page_title="Tensile Pro Suite | Solomon Scientific",
    page_icon="LOGO.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# GLOBAL CUSTOM CSS — Full Light Theme
# ==========================================
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── CSS Variables ────────────────────────────── */
:root {
    /* Brand Colors */
    --navy:       #0b1120;
    --navy-mid:   #111827;
    --navy-light: #1a2540;
    --gold:       #c9a84c;
    --gold-light: #e2c97e;
    --gold-dim:   #9c7a32;
    
    /* Light Mode Colors */
    --bg-white:   #ffffff;
    --bg-offwhite:#f8fafc;
    --text-dark:  #000000; /* Pure Dark Black for normal text */
    --text-muted: #111111; /* Almost black for secondary text */
    --border-light:#e2e8f0;
    
    --accent:     #3a7bd5;
    --red:        #e05252;
    --green:      #3db87a;
    
    --font-head:  'Playfair Display', Georgia, serif;
    --font-mono:  'IBM Plex Mono', 'Courier New', monospace;
    --font-body:  'IBM Plex Sans', 'Segoe UI', sans-serif;
}

/* ── Base & Body ──────────────────────────────── */
html, body, [class*="css"] {
    font-family: var(--font-body);
    color: var(--text-dark);
}
.stApp {
    background: var(--bg-white);
}
.stApp::before { display: none; }

/* ── Sidebar (Pure White & User Friendly) ─────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border-light);
}

/* Fixed material icon bug and force pure black text */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #000000 !important;
    font-family: var(--font-body);
}
.material-symbols-rounded,
[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold-dim) !important;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] hr { border-color: var(--border-light); margin: 1rem 0; }

/* Sidebar Inputs */
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    background: var(--bg-white) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 4px !important;
    color: #000000 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}

/* File Uploader Dropzone */
[data-testid="stFileUploadDropzone"] {
    background-color: var(--bg-white) !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 6px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--gold) !important;
    background-color: var(--bg-offwhite) !important;
}

/* ── Main Area Inputs ─────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--bg-white) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 4px !important;
    color: #000000 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}
.stSelectbox > div > div:hover,
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold-dim) !important;
}

/* ── Buttons ──────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
    color: var(--navy) !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--gold), var(--gold-light)) !important;
    box-shadow: 0 4px 15px rgba(201,168,76,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8b1a1a, var(--red)) !important;
    color: white !important;
}

/* Download buttons */
[data-testid="stDownloadButton"] > button {
    background: var(--bg-offwhite) !important;
    color: var(--navy) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 3px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #ffffff !important;
    border-color: var(--gold) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}

/* ── Tabs ─────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--bg-offwhite);
    border-bottom: 1px solid var(--border-light);
    gap: 0; padding: 0;
}
[data-testid="stTabs"] [role="tab"] {
    color: #000000 !important;
    font-family: var(--font-body) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.7rem 1.2rem !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: var(--navy) !important;
    background: rgba(0,0,0,0.02) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #000000 !important;
    border-bottom-color: var(--gold) !important;
    background: var(--bg-white) !important;
}

/* ── DataFrames ───────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-light) !important;
    border-radius: 6px !important;
    background: var(--bg-white) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-offwhite) !important;
    color: #000000 !important;
    border-bottom: 1px solid var(--border-light) !important;
}
[data-testid="stDataFrame"] td {
    color: #000000 !important;
}

/* ── Expanders ────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border-light) !important;
    border-radius: 4px !important;
    background: var(--bg-white) !important;
}
[data-testid="stExpander"] summary {
    color: #000000 !important;
    font-weight: 700 !important;
}

/* ── Alerts ───────────────────────────────────── */
[data-testid="stAlert"] { color: #000000 !important; }
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
        icon_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 54px; height: 54px; border-radius: 8px; object-fit: contain; box-shadow: 0 4px 20px rgba(0,0,0,0.5); flex-shrink: 0; background: white;">'
    else:
        icon_html = '<div style="width: 54px; height: 54px; background: linear-gradient(135deg, #9c7a32, #c9a84c); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 4px 20px rgba(0,0,0,0.3); flex-shrink: 0;">🔬</div>'

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0b1120 0%, #0f1a2e 100%);
        padding: 1.5rem 2rem;
        border-radius: 8px;
        border: 1px solid rgba(201,168,76,0.3);
        margin-bottom: 1.5rem;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    ">
        {icon_html}
        <div>
            <div style="
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 1.75rem;
                font-weight: 700;
                color: #f0f4fb;
                letter-spacing: 0.01em;
                line-height: 1.1;
            ">Tensile Pro Suite <span style="color:#c9a84c;">2.1</span></div>
            <div style="
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.72rem;
                color: #a8b4c8;
                letter-spacing: 0.2em;
                text-transform: uppercase;
                margin-top: 2px;
            ">Mechanical Properties & Modulus Alignment &nbsp;·&nbsp; Solomon Scientific &nbsp;·&nbsp; © 2026</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, unit=""):
    return f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        border-top: 3px solid #c9a84c;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    ">
        <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.68rem;color:#000000;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;font-weight:700;">{label}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1.35rem;color:#000000;font-weight:700;">{value}<span style="font-size:0.7rem;color:#000000;margin-left:4px;">{unit}</span></div>
    </div>
    """

def section_title(text, icon=""):
    st.markdown(f"""
    <div style="
        display:flex; align-items:center; gap:0.6rem;
        background: linear-gradient(90deg, #0b1120 0%, #1a2540 100%);
        padding: 0.6rem 1.25rem;
        border-radius: 6px;
        border-left: 4px solid #c9a84c;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    ">
        <span style="font-size:1.1rem; color:#f0f4fb;">{icon}</span>
        <span style="
            font-family:'IBM Plex Sans',sans-serif;
            font-size:0.8rem;
            font-weight:600;
            color:#f0f4fb;
            letter-spacing:0.15em;
            text-transform:uppercase;
        ">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_brand():
    logo_path = "LOGO.png"
    if os.path.exists(logo_path):
        img_b64 = get_base64_of_bin_file(logo_path)
        icon_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 52px; height: 52px; margin: 0 auto 0.75rem auto; border-radius: 10px; display: block; box-shadow: 0 4px 12px rgba(0,0,0,0.1); object-fit: contain; background: white;">'
    else:
        icon_html = '<div style="width:52px; height:52px; margin:0 auto 0.75rem auto; background:linear-gradient(135deg,#9c7a32,#c9a84c); border-radius:10px; display:flex;align-items:center;justify-content:center; font-size:1.5rem; box-shadow:0 4px 12px rgba(0,0,0,0.1);">🔬</div>'

    st.markdown(f"""
    <div style="padding: 1.25rem 0 0.5rem 0; text-align:center;">
        {icon_html}
        <div style="
            font-family:'IBM Plex Sans',sans-serif;
            font-size:0.65rem;
            color:#9c7a32;
            letter-spacing:0.2em;
            text-transform:uppercase;
            margin-bottom:4px;
        ">Solomon Scientific</div>
        <div style="
            font-family:'Playfair Display',Georgia,serif;
            font-size:1.1rem;
            font-weight:700;
            color:#000000;
        ">Tensile Pro Suite <span style="color:#c9a84c;">2.1</span></div>
        <div style="
            margin-top:0.75rem;
            padding-top:0.75rem;
            border-top:1px solid #e2e8f0;
            font-family:'IBM Plex Sans',sans-serif;
            font-size:0.68rem;
            color:#000000;
            font-weight:500;
        ">Batch Master Platform<br>
        <a href='mailto:your.solomon.duf@gmail.com'
           style='color:#9c7a32;text-decoration:none;'>
            ✉ Contact Developer
        </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# PLOTLY THEME (STRICT JOURNAL QUALITY)
# ==========================================
PLOT_BG    = "#ffffff"
PAPER_BG   = "#ffffff"
BLACK      = "#000000"
GOLD       = "#c9a84c"
WHITE      = "#ffffff"

TENSILE_STYLE = dict(
    mirror=True, 
    ticks='inside', 
    showline=True,
    linecolor=BLACK, 
    linewidth=2,
    showgrid=False,   # Strict NO GRIDLINES
    zeroline=False,
    rangemode='tozero',
    title_font=dict(family="Arial", size=18, color=BLACK),
    tickfont=dict(family="Arial", size=14, color=BLACK),
    tickwidth=2, 
    ticklen=6, 
    tickcolor=BLACK,
)

JOURNAL_CONFIG = {
    'toImageButtonOptions': {'format': 'png', 'filename': 'Tensile_Journal_Plot', 'scale': 5},
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
}

PALETTE = [
    "#000000", "#d62728", "#1f77b4", "#2ca02c", 
    "#ff7f0e", "#9467bd", "#8c564b", "#e377c2"
]

def clean_filename(filename):
    return os.path.splitext(filename)[0]

# ==========================================
# SESSION STATE
# ==========================================
if 'master_tensile_df' not in st.session_state:
    st.session_state['master_tensile_df'] = pd.DataFrame()
if 'curve_storage' not in st.session_state:
    st.session_state['curve_storage'] = {}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    render_sidebar_brand()

    st.markdown("### 1 · Specimen Geometry")
    width = st.number_input("Width (mm)", value=4.0)
    thickness = st.number_input("Thickness (mm)", value=4.0)
    l0 = st.number_input("Gauge Length (mm)", value=25.0)
    area = width * thickness
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 2 · Plot Customization")
    line_w = st.slider("Curve Thickness", 1.0, 5.0, 2.5)
    leg_x = st.slider("Legend Horizontal (X)", 0.0, 1.0, 0.05)
    leg_y = st.slider("Legend Vertical (Y)", 0.0, 1.0, 0.95)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 3 · Data Input")
    with st.form("upload_form", clear_on_submit=True):
        batch_id = st.text_input("Batch ID", "Sample A")
        files = st.file_uploader("Upload Replicates (.csv, .xlsx, .txt)", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)
        submit = st.form_submit_button("⚙️ Process Batch Data", use_container_width=True)

    if not st.session_state['master_tensile_df'].empty:
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🔄 Reset Entire Workspace", type="primary", use_container_width=True):
            st.session_state['master_tensile_df'] = pd.DataFrame()
            st.session_state['curve_storage'] = {}
            st.rerun()

    st.markdown("""
    <div style="padding:1rem 0 0.5rem;text-align:center;font-family:'IBM Plex Sans',sans-serif;
                font-size:0.65rem;color:#000000;letter-spacing:0.1em;font-weight:500;">
        For Research & Academic Use Only<br>Version 2.1 Pro
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ROBUST PROCESSING ENGINE
# ==========================================
def robust_load(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        elif file.name.endswith('.txt'):
            content = file.getvalue().decode('utf-8', errors='ignore')
            sep = '\t' if '\t' in content else (',' if ',' in content else r'\s+')
            df = pd.read_csv(io.StringIO(content), sep=sep, engine='python')
        else:
            df = pd.read_csv(file)
        
        df.columns = [str(c).strip() for c in df.columns]
        df = df.apply(pd.to_numeric, errors='coerce').dropna(how='all').reset_index(drop=True)
        cols = df.columns.tolist()
        
        load_col = next((c for c in cols if any(k in c.lower() for k in ['load', 'carico', 'force', 'n'])), None)
        ext_col = next((c for c in cols if any(k in c.lower() for k in ['ext', 'defor', 'mm', 'disp'])), None)
        
        if load_col and ext_col:
            df_std = pd.DataFrame({'Load_N': df[load_col], 'Ext_mm': df[ext_col]})
        else:
            df_std = pd.DataFrame({'Load_N': df.iloc[:, 0], 'Ext_mm': df.iloc[:, 1]})
        
        return df_std.dropna().reset_index(drop=True)
    except Exception as e:
        st.error(f"Error loading {file.name}: {e}")
        return None

if submit and files:
    batch_results = []
    with st.spinner("Processing specimens..."):
        for f in files:
            df_std = robust_load(f)
            if df_std is not None and not df_std.empty:
                df_std['Strain_pct'] = (df_std['Ext_mm'] / l0) * 100
                df_std['Stress_MPa'] = df_std['Load_N'] / area
                
                # --- AUTOMATIC MODULUS DETECTION ---
                search_limit = int(len(df_std) * 0.2)
                window_size = max(5, int(len(df_std) * 0.02))
                max_slope = 0
                best_intercept = 0
                
                for i in range(0, search_limit - window_size):
                    window = df_std.iloc[i : i + window_size]
                    slope, intercept = np.polyfit(window['Strain_pct'], window['Stress_MPa'], 1)
                    if slope > max_slope:
                        max_slope = slope
                        best_intercept = intercept
                
                # --- TOE COMPENSATION ---
                toe_offset = -best_intercept / max_slope if max_slope > 0 else 0
                df_std['Strain_pct'] = df_std['Strain_pct'] - toe_offset
                
                # Origin Alignment & Truncation at Peak
                df_std = df_std[df_std['Strain_pct'] >= 0].reset_index(drop=True)
                origin = pd.DataFrame({'Load_N':[0.0], 'Ext_mm':[0.0], 'Strain_pct':[0.0], 'Stress_MPa':[0.0]})
                df_std = pd.concat([origin, df_std], ignore_index=True)
                
                peak_idx = df_std['Stress_MPa'].idxmax()
                df_std = df_std.iloc[:peak_idx + 1].copy()
                
                display_name = clean_filename(f.name)
                batch_results.append({
                    "Sample": batch_id, "File": display_name,
                    "UTS [MPa]": df_std['Stress_MPa'].max(), 
                    "Elongation [%]": df_std['Strain_pct'].max(),
                    "Modulus [MPa]": max_slope * 100 
                })
                st.session_state['curve_storage'][display_name] = df_std
                
        if batch_results:
            new_data = pd.DataFrame(batch_results)
            st.session_state['master_tensile_df'] = pd.concat([st.session_state['master_tensile_df'], new_data], ignore_index=True)
            st.success("✓ Batch processing complete.")

# ==========================================
# MAIN DASHBOARD VIEW
# ==========================================
df_m = st.session_state['master_tensile_df']
curves = st.session_state['curve_storage']

render_header()

if not df_m.empty:
    n_files = len(df_m)
    n_groups = df_m['Sample'].nunique()
    
    k1, k2, k3 = st.columns(3)
    k1.markdown(metric_card("Specimens Tested", f"{n_files}"), unsafe_allow_html=True)
    k2.markdown(metric_card("Batches", f"{n_groups}"), unsafe_allow_html=True)
    k3.markdown(metric_card("Cross-Section Area", f"{area:.2f}", "mm²"), unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    tabs = st.tabs([
        "📋 Dataset Overview", 
        "🎨 Batch Replicates", 
        "🏛️ Representative Comparison", 
        "💾 Export Data"
    ])
    
    # Clean Journal Legend
    legend_config = dict(
        x=leg_x, y=leg_y, xanchor='left', yanchor='top',
        bgcolor="rgba(255, 255, 255, 0.9)", 
        bordercolor=BLACK, borderwidth=0, # No border around legend text                
        font=dict(family="Arial", size=14, color=BLACK)
    )

    with tabs[0]:
        section_title("Summary Table & Statistics", "📋")
        st.dataframe(df_m, use_container_width=True, height=250)
        
        st.markdown("<br><h4 style='color:#000000;font-family:Arial;'>Aggregated Batch Statistics</h4>", unsafe_allow_html=True)
        agg_df = df_m.groupby("Sample")[["UTS [MPa]", "Elongation [%]", "Modulus [MPa]"]].agg(['mean', 'std'])
        st.dataframe(agg_df, use_container_width=True)

    with tabs[1]:
        section_title("Batch Overlay (Auto-Compensated)", "🎨")
        sel_batch = st.selectbox("Select Batch to Inspect:", sorted(df_m['Sample'].unique()))
        batch_files = df_m[df_m['Sample'] == sel_batch]['File'].tolist()
        
        fig_batch = go.Figure()
        for i, f in enumerate(batch_files):
            if f in curves:
                c_df = curves[f]
                color = PALETTE[i % len(PALETTE)]
                fig_batch.add_trace(go.Scatter(
                    x=c_df['Strain_pct'], y=c_df['Stress_MPa'], 
                    mode='lines', line=dict(width=line_w, color=color), name=f
                ))
                
        fig_batch.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, height=600,
            xaxis=dict(title="<b>Strain (%)</b>", range=[0, None], **TENSILE_STYLE), 
            yaxis=dict(title="<b>Stress (MPa)</b>", range=[0, None], **TENSILE_STYLE), 
            showlegend=True, legend=legend_config,
            margin=dict(l=60, r=40, t=40, b=60)
        )
        st.plotly_chart(fig_batch, use_container_width=True, config=JOURNAL_CONFIG)

    with tabs[2]:
        section_title("Representative Comparison (Journal Ready)", "🏛️")
        st.markdown("<p style='color:#000000;'>Automatically selects the replicate with the UTS closest to the batch mean.</p>", unsafe_allow_html=True)
        
        fig_rep = go.Figure()
        unique_samples = sorted(df_m['Sample'].unique())
        
        for i, s_name in enumerate(unique_samples):
            sub = df_m[df_m['Sample'] == s_name]
            rep_f = sub.iloc[(sub['UTS [MPa]'] - sub['UTS [MPa]'].mean()).abs().argsort()[:1]]['File'].values[0]
            
            if rep_f in curves:
                c_df = curves[rep_f]
                color = PALETTE[i % len(PALETTE)]
                fig_rep.add_trace(go.Scatter(
                    x=c_df['Strain_pct'], y=c_df['Stress_MPa'], 
                    mode='lines', line=dict(width=line_w, color=color), name=f"{s_name}"
                ))
                
        fig_rep.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, height=700,
            xaxis=dict(title="<b>Strain (%)</b>", range=[0, None], **TENSILE_STYLE), 
            yaxis=dict(title="<b>Stress (MPa)</b>", range=[0, None], **TENSILE_STYLE), 
            showlegend=True, legend=legend_config, 
            margin=dict(l=60, r=40, t=40, b=60)
        )
        st.plotly_chart(fig_rep, use_container_width=True, config=JOURNAL_CONFIG)

    with tabs[3]:
        section_title("Data Export", "💾")
        csv_data = df_m.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Batch Statistics (CSV)", csv_data, "Tensile_Summary.csv")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color:#000000;'>To download the high-resolution journal plots, click the <b>camera icon</b> located in the top-right corner of the charts.</p>", unsafe_allow_html=True)

else:
    # --- Empty State UI ---
    st.markdown("""
    <div style="
        margin-top:3rem; padding:3rem 2rem; background:#ffffff;
        border:1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border-radius:8px; text-align:center;
    ">
        <div style="font-size:3rem;margin-bottom:1rem;">📉</div>
        <div style="
            font-family:'Playfair Display',Georgia,serif;
            font-size:1.5rem;color:#1e293b; margin-bottom:0.5rem; font-weight:700;
        ">Ready for Mechanical Analysis</div>
        <div style="
            font-family:'IBM Plex Sans',sans-serif;
            font-size:0.85rem;color:#000000;
            max-width:480px;margin:0 auto;line-height:1.7;
        ">
            Upload your raw Tensile data files via the <b style="color:#c9a84c;">Data Input</b> panel
            in the sidebar. The framework will automatically detect Modulus, compensate for machine toe, 
            align origins, and generate publication-ready representative overlays.
        </div>
    </div>
    """, unsafe_allow_html=True)
