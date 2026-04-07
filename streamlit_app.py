import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import os
import base64

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Tensile Pro Suite | Solomon Scientific",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# GLOBAL CSS — Clean Scientific Light Theme
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink:         #111827;
    --ink-mid:     #374151;
    --ink-muted:   #6B7280;
    --gold:        #B45309;
    --gold-light:  #D97706;
    --gold-pale:   #FEF3C7;
    --bg:          #FFFFFF;
    --bg-off:      #F9FAFB;
    --bg-subtle:   #F3F4F6;
    --border:      #E5E7EB;
    --border-dark: #D1D5DB;
    --blue:        #1D4ED8;
    --red:         #B91C1C;
    --green:       #065F46;
    --font-serif:  'Lora', Georgia, serif;
    --font-sans:   'DM Sans', system-ui, sans-serif;
    --font-mono:   'JetBrains Mono', 'Courier New', monospace;
    --radius:      6px;
    --shadow-sm:   0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:   0 4px 12px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
}

/* ── Reset & Base ─────────────────────────────── */
html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    color: var(--ink) !important;
}
.stApp {
    background: var(--bg) !important;
}

/* ── Sidebar ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-off) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--ink) !important;
    font-family: var(--font-sans) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: var(--font-sans) !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--ink-muted) !important;
    margin-top: 0.25rem !important;
}
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1rem 0 !important;
}

/* Sidebar inputs */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    background: var(--bg) !important;
    border: 1px solid var(--border-dark) !important;
    border-radius: var(--radius) !important;
    color: var(--ink) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}
[data-testid="stFileUploadDropzone"] {
    background: var(--bg) !important;
    border: 1.5px dashed var(--border-dark) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--gold) !important;
}

/* ── Main inputs ──────────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--bg) !important;
    border: 1px solid var(--border-dark) !important;
    border-radius: var(--radius) !important;
    color: var(--ink) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}

/* ── Buttons ──────────────────────────────────── */
.stButton > button {
    background: var(--ink) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-sans) !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.5rem 1.1rem !important;
    transition: background 0.15s ease, transform 0.1s ease !important;
}
.stButton > button:hover {
    background: var(--ink-mid) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: var(--red) !important;
}
[data-testid="stDownloadButton"] > button {
    background: var(--bg-subtle) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border-dark) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: var(--border) !important;
}

/* ── Tabs ─────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
    color: var(--ink-muted) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    padding: 0.65rem 1.25rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom-color: var(--gold) !important;
    font-weight: 600 !important;
}

/* ── DataFrames ───────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-off) !important;
    color: var(--ink) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td {
    color: var(--ink-mid) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
}

/* ── Expanders ────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stExpander"] summary {
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* ── Text areas ───────────────────────────────── */
textarea {
    font-family: var(--font-sans) !important;
    font-size: 0.83rem !important;
    color: var(--ink) !important;
    border: 1px solid var(--border-dark) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-off) !important;
}

/* ── Alerts / Success ─────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.82rem !important;
}

/* ── Slider ───────────────────────────────────── */
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
}

/* ── Spinner ──────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--gold) !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPERS
# ==========================================
def get_base64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def clean_filename(filename):
    return os.path.splitext(filename)[0]

def render_header():
    logo_path = "LOGO.png"
    if os.path.exists(logo_path):
        img_b64 = get_base64(logo_path)
        logo_html = f'<img src="data:image/png;base64,{img_b64}" style="height:44px;width:44px;object-fit:contain;border-radius:8px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.12);">'
    else:
        logo_html = '<span style="font-size:1.6rem;">🔬</span>'

    st.markdown(f"""
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        padding: 1.25rem 1.75rem;
        background: #111827;
        border-radius: 8px;
        margin-bottom: 1.75rem;
        margin-top: 0.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.10);
    ">
        <div style="display:flex;align-items:center;gap:1rem;">
            {logo_html}
            <div>
                <div style="
                    font-family:'Lora',Georgia,serif;
                    font-size:1.45rem;
                    font-weight:700;
                    color:#F9FAFB;
                    line-height:1.15;
                    letter-spacing:-0.01em;
                ">Tensile Pro Suite <span style="color:#D97706;">2.1</span></div>
                <div style="
                    font-family:'DM Sans',sans-serif;
                    font-size:0.68rem;
                    color:#9CA3AF;
                    letter-spacing:0.18em;
                    text-transform:uppercase;
                    margin-top:2px;
                ">Mechanical Properties Analysis &nbsp;·&nbsp; Solomon Scientific</div>
            </div>
        </div>
        <div style="
            font-family:'DM Sans',sans-serif;
            font-size:0.65rem;
            color:#6B7280;
            letter-spacing:0.12em;
            text-transform:uppercase;
            text-align:right;
            line-height:1.8;
        ">
            © 2026<br>Research Use
        </div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, unit="", color_bar="#B45309"):
    return f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E5E7EB;
        border-radius:6px;
        padding:1rem 1.25rem;
        border-left:3px solid {color_bar};
        box-shadow:0 1px 3px rgba(0,0,0,0.05);
        height:100%;
    ">
        <div style="
            font-family:'DM Sans',sans-serif;
            font-size:0.63rem;
            color:#6B7280;
            letter-spacing:0.14em;
            text-transform:uppercase;
            font-weight:600;
            margin-bottom:6px;
        ">{label}</div>
        <div style="
            font-family:'JetBrains Mono','Courier New',monospace;
            font-size:1.4rem;
            color:#111827;
            font-weight:500;
            line-height:1;
        ">{value}<span style="font-size:0.72rem;color:#6B7280;margin-left:5px;font-weight:400;">{unit}</span></div>
    </div>
    """

def section_header(text, sub=""):
    sub_html = f'<div style="font-family:\'DM Sans\',sans-serif;font-size:0.78rem;color:#6B7280;margin-top:2px;">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div style="margin: 1.75rem 0 1rem 0; padding-bottom:0.6rem; border-bottom:1px solid #E5E7EB;">
        <div style="
            font-family:'Lora',Georgia,serif;
            font-size:1.05rem;
            font-weight:600;
            color:#111827;
            letter-spacing:-0.01em;
        ">{text}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_brand():
    logo_path = "LOGO.png"
    if os.path.exists(logo_path):
        img_b64 = get_base64(logo_path)
        icon = f'<img src="data:image/png;base64,{img_b64}" style="width:42px;height:42px;object-fit:contain;border-radius:8px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.1);">'
    else:
        icon = '<div style="font-size:1.6rem;">🔬</div>'

    st.markdown(f"""
    <div style="padding:1rem 0 0.75rem 0;">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.65rem;">
            {icon}
            <div>
                <div style="font-family:'Lora',Georgia,serif;font-size:1rem;font-weight:700;color:#111827;line-height:1.2;">
                    Tensile Pro <span style="color:#D97706;">2.1</span>
                </div>
                <div style="font-family:'DM Sans',sans-serif;font-size:0.62rem;color:#6B7280;letter-spacing:0.1em;text-transform:uppercase;">
                    Solomon Scientific
                </div>
            </div>
        </div>
        <div style="
            padding:0.5rem 0.75rem;
            background:#F3F4F6;
            border-radius:5px;
            font-family:'DM Sans',sans-serif;
            font-size:0.7rem;
            color:#374151;
            line-height:1.5;
        ">
            Batch Master Platform &nbsp;·&nbsp;
            <a href='mailto:your.solomon.duf@gmail.com' style='color:#B45309;text-decoration:none;font-weight:500;'>
                Contact Developer
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# EXPORT UTILITY
# ==========================================
def export_to_excel_with_logo(df, sheet_title):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_title)
        worksheet = writer.sheets[sheet_title]
        for i in range(df.shape[1]):
            col_len = len(str(df.columns[i]))
            data_len = int(df.iloc[:, i].fillna("").astype(str).str.len().max()) if len(df) > 0 else 0
            worksheet.set_column(i, i, max(col_len, data_len) + 2)
        logo_path = "LOGO.png"
        if os.path.exists(logo_path):
            worksheet.insert_image(1, len(df.columns) + 1, logo_path, {'x_scale': 0.55, 'y_scale': 0.55})
    return output.getvalue()

# ==========================================
# JOURNAL PLOT THEME
# ==========================================
BLACK  = "#000000"
WHITE  = "#FFFFFF"
PLOT_BG = "#FFFFFF"

AXIS_STYLE = dict(
    mirror=True,
    ticks='inside',
    showline=True,
    linecolor=BLACK,
    linewidth=1.5,
    showgrid=False,
    zeroline=False,
    rangemode='tozero',
    title_font=dict(family="Arial", size=16, color=BLACK),
    tickfont=dict(family="Arial", size=13, color=BLACK),
    tickwidth=1.5,
    ticklen=5,
    tickcolor=BLACK,
)

JOURNAL_CONFIG = {
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'Tensile_Plot',
        'scale': 5,
        'width': 900,
        'height': 650,
    },
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
}

PALETTE = [
    "#111827", "#B91C1C", "#1D4ED8", "#065F46",
    "#92400E", "#5B21B6", "#0E7490", "#BE185D",
]

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
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### Specimen Geometry")
    width = st.number_input("Width (mm)", value=4.0, format="%.2f")
    thickness = st.number_input("Thickness (mm)", value=4.0, format="%.2f")
    l0 = st.number_input("Gauge Length (mm)", value=25.0, format="%.2f")
    area = width * thickness
    st.markdown(
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
        f'color:#374151;background:#F3F4F6;border-radius:5px;padding:0.4rem 0.65rem;margin-top:0.25rem;">'
        f'A₀ = <b>{area:.3f} mm²</b></div>',
        unsafe_allow_html=True
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Plot Style")
    line_w = st.slider("Line Weight", 1.0, 4.0, 2.0, 0.25)
    leg_x  = st.slider("Legend X", 0.0, 1.0, 0.04)
    leg_y  = st.slider("Legend Y", 0.0, 1.0, 0.96)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Data Input")

    with st.form("upload_form", clear_on_submit=True):
        batch_id = st.text_input("Batch / Group ID", "Sample A")
        files = st.file_uploader(
            "Upload Replicates (.csv, .xlsx, .txt)",
            type=['csv', 'xlsx', 'txt'],
            accept_multiple_files=True
        )
        submit = st.form_submit_button("⚙ Process Batch", use_container_width=True)

    if not st.session_state['master_tensile_df'].empty:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### Manage Data")

        with st.expander("Delete / Replace"):
            samples = sorted(st.session_state['master_tensile_df']['Sample'].unique())
            batch_to_del = st.selectbox("Delete Entire Batch", ["— select —"] + samples)
            if st.button("Delete Batch", use_container_width=True):
                if batch_to_del != "— select —":
                    files_rm = st.session_state['master_tensile_df'][
                        st.session_state['master_tensile_df']['Sample'] == batch_to_del
                    ]['File'].tolist()
                    st.session_state['master_tensile_df'] = st.session_state['master_tensile_df'][
                        st.session_state['master_tensile_df']['Sample'] != batch_to_del
                    ]
                    for fr in files_rm:
                        st.session_state['curve_storage'].pop(fr, None)
                    st.rerun()

            all_files = sorted(st.session_state['master_tensile_df']['File'].tolist())
            file_to_del = st.selectbox("Delete Single Replicate", ["— select —"] + all_files)
            if st.button("Delete Replicate", use_container_width=True):
                if file_to_del != "— select —":
                    st.session_state['master_tensile_df'] = st.session_state['master_tensile_df'][
                        st.session_state['master_tensile_df']['File'] != file_to_del
                    ]
                    st.session_state['curve_storage'].pop(file_to_del, None)
                    st.rerun()

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
        if st.button("↺  Reset Workspace", type="primary", use_container_width=True):
            st.session_state['master_tensile_df'] = pd.DataFrame()
            st.session_state['curve_storage'] = {}
            st.rerun()

    st.markdown("""
    <div style="padding:1rem 0 0;font-family:'DM Sans',sans-serif;font-size:0.63rem;
                color:#9CA3AF;text-align:center;letter-spacing:0.08em;line-height:1.8;">
        RESEARCH & ACADEMIC USE ONLY<br>VERSION 2.1 PRO
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# PROCESSING ENGINE
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
        ext_col  = next((c for c in cols if any(k in c.lower() for k in ['ext', 'defor', 'mm', 'disp'])), None)

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
    with st.spinner("Processing specimens…"):
        for f in files:
            df_std = robust_load(f)
            if df_std is not None and not df_std.empty:
                df_std['Strain_pct'] = (df_std['Ext_mm'] / l0) * 100
                df_std['Stress_MPa'] = df_std['Load_N'] / area

                # ── Automatic Modulus (steepest window) ──────
                search_limit = int(len(df_std) * 0.20)
                window_size  = max(5, int(len(df_std) * 0.02))
                max_slope, best_intercept = 0, 0

                for i in range(0, search_limit - window_size):
                    w = df_std.iloc[i: i + window_size]
                    slope, intercept = np.polyfit(w['Strain_pct'], w['Stress_MPa'], 1)
                    if slope > max_slope:
                        max_slope, best_intercept = slope, intercept

                # ── Toe Compensation ─────────────────────────
                toe_offset = -best_intercept / max_slope if max_slope > 0 else 0
                df_std['Strain_pct'] -= toe_offset
                df_std = df_std[df_std['Strain_pct'] >= 0].reset_index(drop=True)

                origin = pd.DataFrame({'Load_N': [0.0], 'Ext_mm': [0.0],
                                       'Strain_pct': [0.0], 'Stress_MPa': [0.0]})
                df_std = pd.concat([origin, df_std], ignore_index=True)

                # ── Break Detection (trim post-fracture data) ─
                peak_idx = df_std['Stress_MPa'].idxmax()
                uts      = df_std['Stress_MPa'][peak_idx]

                post_peak = df_std.iloc[peak_idx:]
                break_candidates = post_peak[post_peak['Stress_MPa'] < 0.10 * uts]

                if not break_candidates.empty:
                    # Trim at fracture point — remove everything after break
                    break_idx = break_candidates.index[0]
                    df_std = df_std.iloc[:break_idx].copy()   # excludes post-fracture data
                    # Recompute peak after trim
                    peak_idx = df_std['Stress_MPa'].idxmax()
                    uts      = df_std['Stress_MPa'][peak_idx]

                # ── 0.2 % Offset Yield ───────────────────────
                offset_stress = max_slope * (df_std['Strain_pct'] - 0.2)
                diff = np.abs(df_std['Stress_MPa'] - offset_stress)
                valid_mask = df_std['Strain_pct'] >= 0.2

                if valid_mask.any():
                    yield_idx    = diff[valid_mask].idxmin()
                    yield_stress = df_std['Stress_MPa'].iloc[yield_idx]
                    yield_strain = df_std['Strain_pct'].iloc[yield_idx]
                else:
                    yield_stress = yield_strain = np.nan

                # ── Energy Integrals ─────────────────────────
                work_done = np.trapezoid(df_std['Load_N'], df_std['Ext_mm'] / 1000)
                toughness = np.trapezoid(df_std['Stress_MPa'], df_std['Strain_pct'] / 100)

                # ── Break values (last point of trimmed curve) ─
                elong_break  = df_std['Strain_pct'].iloc[-1]
                stress_break = df_std['Stress_MPa'].iloc[-1]
                modulus_mpa  = max_slope * 100   # convert %⁻¹ → unitless ε

                display_name = clean_filename(f.name)
                batch_results.append({
                    "Sample":               batch_id,
                    "File":                 display_name,
                    "Modulus [MPa]":        round(modulus_mpa, 2),
                    "Yield Stress [MPa]":   round(yield_stress, 2),
                    "Yield Strain [%]":     round(yield_strain, 2),
                    "UTS [MPa]":            round(uts, 2),
                    "Stress at Break [MPa]":round(stress_break, 2),
                    "Elong. at Break [%]":  round(elong_break, 2),
                    "Work Done [J]":        round(work_done, 4),
                    "Toughness [MJ/m³]":    round(toughness, 4),
                })
                st.session_state['curve_storage'][display_name] = df_std

    if batch_results:
        new_data = pd.DataFrame(batch_results)
        st.session_state['master_tensile_df'] = pd.concat(
            [st.session_state['master_tensile_df'], new_data], ignore_index=True
        )
        st.success(f"✓ {len(batch_results)} specimen(s) processed for batch "{batch_id}".")

# ==========================================
# DASHBOARD
# ==========================================
df_m   = st.session_state['master_tensile_df']
curves = st.session_state['curve_storage']

render_header()

if not df_m.empty:
    # ── KPI row ───────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(metric_card("Specimens", f"{len(df_m)}", color_bar="#111827"), unsafe_allow_html=True)
    k2.markdown(metric_card("Batches", f"{df_m['Sample'].nunique()}", color_bar="#B45309"), unsafe_allow_html=True)
    k3.markdown(metric_card("Cross-Section", f"{area:.3f}", "mm²", color_bar="#1D4ED8"), unsafe_allow_html=True)
    mean_uts = df_m['UTS [MPa]'].mean()
    k4.markdown(metric_card("Mean UTS", f"{mean_uts:.1f}", "MPa", color_bar="#065F46"), unsafe_allow_html=True)
    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    legend_cfg = dict(
        x=leg_x, y=leg_y, xanchor='left', yanchor='top',
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#E5E7EB",
        borderwidth=1,
        font=dict(family="Arial", size=13, color=BLACK),
    )

    tabs = st.tabs([
        "Dataset Overview",
        "Batch Replicates",
        "Representative Comparison",
        "Export",
        "Methods",
    ])

    # ── Tab 0: Overview ───────────────────────────
    with tabs[0]:
        section_header("Results Table", "All computed mechanical properties per specimen.")
        st.dataframe(df_m, use_container_width=True, height=260)

        section_header("Batch Statistics", "Mean ± SD per group.")
        num_cols = [c for c in df_m.columns if c not in ["Sample", "File"]]
        agg = df_m.groupby("Sample")[num_cols].agg(['mean', 'std']).round(3)
        st.dataframe(agg, use_container_width=True)

    # ── Tab 1: Batch Replicates ───────────────────
    with tabs[1]:
        section_header("Batch Overlay", "All replicates plotted with automatic toe compensation. Post-fracture data removed.")
        sel_batch   = st.selectbox("Batch:", sorted(df_m['Sample'].unique()), key="batch_sel")
        batch_files = df_m[df_m['Sample'] == sel_batch]['File'].tolist()

        fig = go.Figure()
        for i, fname in enumerate(batch_files):
            if fname in curves:
                c = curves[fname]
                fig.add_trace(go.Scatter(
                    x=c['Strain_pct'], y=c['Stress_MPa'],
                    mode='lines',
                    line=dict(width=line_w, color=PALETTE[i % len(PALETTE)]),
                    name=fname,
                ))

        fig.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=580,
            xaxis=dict(title="<b>Strain (%)</b>", **AXIS_STYLE),
            yaxis=dict(title="<b>Stress (MPa)</b>", **AXIS_STYLE),
            legend=legend_cfg,
            margin=dict(l=70, r=40, t=30, b=60),
            font=dict(family="Arial"),
        )
        st.plotly_chart(fig, use_container_width=True, config=JOURNAL_CONFIG)

    # ── Tab 2: Representative Comparison ──────────
    with tabs[2]:
        section_header("Representative Comparison", "Replicate closest to batch mean UTS selected per group.")

        col_opt, _ = st.columns([2, 3])
        with col_opt:
            show_sd_band = st.checkbox("Show ±1 SD band (requires ≥2 replicates per batch)", value=False)

        fig2 = go.Figure()
        unique_samples = sorted(df_m['Sample'].unique())

        for i, s_name in enumerate(unique_samples):
            sub   = df_m[df_m['Sample'] == s_name]
            rep_f = sub.iloc[
                (sub['UTS [MPa]'] - sub['UTS [MPa]'].mean()).abs().argsort()[:1]
            ]['File'].values[0]

            color = PALETTE[i % len(PALETTE)]

            if show_sd_band:
                # Interpolate all replicates to common strain grid and build SD band
                rep_files = sub['File'].tolist()
                all_curves = [curves[f] for f in rep_files if f in curves]
                if len(all_curves) >= 2:
                    max_strain = min(c['Strain_pct'].max() for c in all_curves)
                    strain_grid = np.linspace(0, max_strain, 400)
                    interp_stresses = []
                    for ac in all_curves:
                        interp_stresses.append(np.interp(strain_grid, ac['Strain_pct'], ac['Stress_MPa']))
                    mean_stress = np.mean(interp_stresses, axis=0)
                    sd_stress   = np.std(interp_stresses, axis=0)

                    fig2.add_trace(go.Scatter(
                        x=np.concatenate([strain_grid, strain_grid[::-1]]),
                        y=np.concatenate([mean_stress + sd_stress, (mean_stress - sd_stress)[::-1]]),
                        fill='toself',
                        fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)',
                        line=dict(color='rgba(0,0,0,0)'),
                        showlegend=False,
                        hoverinfo='skip',
                    ))

            if rep_f in curves:
                c_df = curves[rep_f]
                fig2.add_trace(go.Scatter(
                    x=c_df['Strain_pct'], y=c_df['Stress_MPa'],
                    mode='lines',
                    line=dict(width=line_w, color=color),
                    name=f"<b>{s_name}</b>",
                ))

        fig2.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=620,
            xaxis=dict(title="<b>Strain (%)</b>", **AXIS_STYLE),
            yaxis=dict(title="<b>Stress (MPa)</b>", **AXIS_STYLE),
            legend=legend_cfg,
            margin=dict(l=70, r=40, t=30, b=60),
            font=dict(family="Arial"),
        )
        st.plotly_chart(fig2, use_container_width=True, config=JOURNAL_CONFIG)

        st.markdown(
            '<p style="font-family:\'DM Sans\',sans-serif;font-size:0.75rem;color:#6B7280;">'
            '💡 To save a high-resolution image (300–500 DPI equivalent), click the <b>camera icon</b> '
            'in the top-right corner of the chart. Export scale is set to 5×.</p>',
            unsafe_allow_html=True
        )

    # ── Tab 3: Export ─────────────────────────────
    with tabs[3]:
        section_header("Data Export")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("""
            <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:6px;
                        padding:1rem 1.25rem;margin-bottom:0.75rem;">
                <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;font-weight:600;
                            color:#111827;margin-bottom:4px;">Batch Statistics</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:0.75rem;color:#6B7280;">
                    Full summary of all computed mechanical properties.
                </div>
            </div>
            """, unsafe_allow_html=True)
            excel_stats = export_to_excel_with_logo(df_m, "Tensile_Summary")
            st.download_button(
                "↓  Download Summary (Excel)",
                excel_stats,
                "Tensile_Summary.xlsx",
                use_container_width=True,
            )

        with c2:
            st.markdown("""
            <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:6px;
                        padding:1rem 1.25rem;margin-bottom:0.75rem;">
                <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;font-weight:600;
                            color:#111827;margin-bottom:4px;">All Curves — Wide Format</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:0.75rem;color:#6B7280;">
                    Strain/stress columns per replicate. Representative specimen tagged [REP].
                </div>
            </div>
            """, unsafe_allow_html=True)

            export_list = []
            for s_name in sorted(df_m['Sample'].unique()):
                sub   = df_m[df_m['Sample'] == s_name]
                rep_f = sub.iloc[
                    (sub['UTS [MPa]'] - sub['UTS [MPa]'].mean()).abs().argsort()[:1]
                ]['File'].values[0]
                for fname in sub['File'].tolist():
                    if fname in curves:
                        tag  = " [REP]" if fname == rep_f else ""
                        temp = curves[fname][['Strain_pct', 'Stress_MPa']].copy().reset_index(drop=True)
                        temp.columns = [
                            f"{s_name} | {fname}{tag} _ Strain (%)",
                            f"{s_name} | {fname}{tag} _ Stress (MPa)",
                        ]
                        export_list.append(temp)

            if export_list:
                wide_df     = pd.concat(export_list, axis=1)
                excel_curves = export_to_excel_with_logo(wide_df, "All_Curves")
                st.download_button(
                    "↓  Download All Curves (Excel)",
                    excel_curves,
                    "Tensile_All_Curves.xlsx",
                    use_container_width=True,
                )

    # ── Tab 4: Methods ────────────────────────────
    with tabs[4]:
        section_header("Computational Methods", "Automated data reduction pipeline.")

        with st.expander("Toe Compensation & Pre-Processing", expanded=True):
            st.markdown(r"""
**Toe compensation** removes initial artifactual compliance from machine slack or specimen seating.

The algorithm scans the first 20 % of the stress–strain trace with a sliding window, identifying the maximum linear gradient (Young's modulus). The fitted line is extrapolated to zero stress; its strain-intercept defines the **toe offset** $\delta$:

$$\delta = \frac{-b_{\max}}{m_{\max}}$$

The entire trace is shifted by $-\delta$ so the elastic region passes exactly through the origin $(0,\,0)$.

**Post-fracture trimming**: data are removed once load falls below 10 % of UTS, preventing machine rebound from distorting the fracture point.
            """)

        with st.expander("Modulus & Yield Parameters", expanded=False):
            st.markdown(r"""
**Young's Modulus** ($E$) is estimated from the steepest contiguous window in the elastic region:

$$E = \frac{\Delta\sigma}{\Delta\varepsilon} \quad (\text{MPa})$$

**0.2 % Offset Yield Stress** ($\sigma_y$): a line of slope $E$ is translated +0.2 % along the strain axis; its intersection with the empirical curve defines $\sigma_y$.

$$\sigma_{\text{offset}} = E\,(\varepsilon - 0.002)$$
            """)

        with st.expander("Break Detection & Ultimate Limits", expanded=False):
            st.markdown(r"""
**Ultimate Tensile Strength**:

$$\text{UTS} = \sigma_{\max} = \frac{F_{\max}}{A_0}$$

**Fracture point**: the first post-peak index where $\sigma < 0.10 \times \text{UTS}$. All data beyond this index are discarded before plotting and property extraction.
            """)

        with st.expander("Energy Integrals", expanded=False):
            st.markdown(r"""
**Work done** (trapezoidal integration over the load–extension curve):

$$W = \int_0^{x_f} F\,\mathrm{d}x \quad (\text{J})$$

**Volumetric toughness** (area under engineering stress–strain):

$$U_T = \int_0^{\varepsilon_f} \sigma\,\mathrm{d}\varepsilon \quad (\text{MJ\,m}^{-3})$$
            """)

        section_header("Auto-Generated Methods Text", "Copy directly into your manuscript.")
        methods_text = (
            "Mechanical properties were determined by uniaxial tensile testing. "
            "Raw data were processed using the Tensile Pro Suite v2.1 (Solomon Scientific). "
            "Toe compensation was applied by extrapolating the maximum elastic gradient to the strain axis, "
            "correcting for machine compliance and specimen seating artefacts. "
            "Young's modulus was identified via a steepest-window linear regression over the first 20 % of the trace. "
            "The 0.2 % strain offset method was used to define yield strength. "
            "Fracture was defined as the point at which load dropped below 10 % of the ultimate tensile load; "
            "post-fracture data were excluded from all analyses. "
            "Volumetric toughness (MJ m⁻³) and total work done (J) were computed by trapezoidal numerical integration "
            "of the engineering stress–strain and load–extension curves, respectively."
        )
        st.text_area("", methods_text, height=140)

else:
    # ── Empty State ───────────────────────────────
    st.markdown("""
    <div style="
        margin-top: 3rem;
        padding: 3.5rem 2.5rem;
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        text-align: center;
        max-width: 560px;
        margin-left: auto;
        margin-right: auto;
    ">
        <div style="font-size:2.5rem;margin-bottom:1rem;opacity:0.5;">📈</div>
        <div style="
            font-family:'Lora',Georgia,serif;
            font-size:1.35rem;
            font-weight:600;
            color:#111827;
            margin-bottom:0.5rem;
        ">Ready for Analysis</div>
        <div style="
            font-family:'DM Sans',sans-serif;
            font-size:0.85rem;
            color:#6B7280;
            line-height:1.75;
            max-width:400px;
            margin:0 auto;
        ">
            Set your specimen geometry in the sidebar, assign a <b style="color:#B45309;">Batch ID</b>,
            then upload your raw tensile data files (.csv, .xlsx, or .txt).<br><br>
            The pipeline will automatically detect modulus, yield stress, UTS, break characteristics,
            toughness, and work done.
        </div>
    </div>
    """, unsafe_allow_html=True)
