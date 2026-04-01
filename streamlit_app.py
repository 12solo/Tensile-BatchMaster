import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import re
import os

# --- 1. Page Configuration & Session State ---
st.set_page_config(page_title="Solomon Tensile Suite 2.1", layout="wide")

if 'master_tensile_df' not in st.session_state:
    st.session_state['master_tensile_df'] = pd.DataFrame()
if 'curve_storage' not in st.session_state:
    st.session_state['curve_storage'] = {}

# Journal Style Global Config
AXIS_STYLE = dict(
    showline=True, mirror=True, ticks='outside', 
    linecolor='black', linewidth=2.5,
    title_font=dict(family="Times New Roman", size=22, color="black"),
    tickfont=dict(family="Times New Roman", size=18, color="black"),
    showgrid=False, zeroline=False, rangemode='tozero'
)

def clean_filename(filename):
    return os.path.splitext(filename)[0]

# --- 2. Header ---
st.title("🔬 Solomon Tensile Suite 2.1")
st.markdown("**Smart Framework: Automatic Modulus Detection & Zero-Intercept Alignment**")

# --- 3. Sidebar ---
with st.sidebar:
    st.header("📏 Specimen Geometry")
    width = st.number_input("Width (mm)", value=4.0)
    thickness = st.number_input("Thickness (mm)", value=4.0)
    l0 = st.number_input("Gauge Length (mm)", value=25.0)
    area = width * thickness
    
    st.header("🎨 Plot Customization")
    line_w = st.slider("Curve Thickness", 1.0, 5.0, 2.5)
    leg_x = st.slider("Legend Horizontal (X)", 0.0, 1.0, 0.05)
    leg_y = st.slider("Legend Vertical (Y)", 0.0, 1.0, 0.95)
    
    st.header("📂 Data Input")
    with st.form("upload_form", clear_on_submit=True):
        batch_id = st.text_input("Batch ID", "Sample A")
        files = st.file_uploader("Upload Replicates", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)
        submit = st.form_submit_button("Process Batch")

    if st.button("Reset Entire Study", type="primary"):
        st.session_state['master_tensile_df'] = pd.DataFrame()
        st.session_state['curve_storage'] = {}
        st.rerun()

# --- 4. Robust Processing Engine ---
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
        st.error(f"Error loading: {e}")
        return None

if submit and files:
    batch_results = []
    for f in files:
        df_std = robust_load(f)
        if df_std is not None and not df_std.empty:
            df_std['Strain_pct'] = (df_std['Ext_mm'] / l0) * 100
            df_std['Stress_MPa'] = df_std['Load_N'] / area
            
            # --- AUTOMATIC MODULUS DETECTION ---
            # We use a sliding window to find the max slope in the first 20% of the test
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
                "Modulus [MPa]": max_slope * 100 # GPa if /10, but keep MPa for consistency
            })
            st.session_state['curve_storage'][display_name] = df_std
            
    if batch_results:
        new_data = pd.DataFrame(batch_results)
        st.session_state['master_tensile_df'] = pd.concat([st.session_state['master_tensile_df'], new_data], ignore_index=True)

# --- 5. Dashboard View ---
df_m = st.session_state['master_tensile_df']
curves = st.session_state['curve_storage']

if not df_m.empty:
    tabs = st.tabs(["📊 Dataset", "📉 Trends", "🎨 Batch Replicates", "🏛️ Representative Comparison", "💾 Export"])
    
    legend_config = dict(
        x=leg_x, y=leg_y, xanchor='left', yanchor='top',
        bgcolor="rgba(255, 255, 255, 0.6)", borderwidth=0,                      
        font=dict(family="Times New Roman", size=18, color="black")
    )

    with tabs[0]:
        st.subheader("Summary Table")
        st.dataframe(df_m, use_container_width=True)
        st.table(df_m.groupby("Sample")[["UTS [MPa]", "Elongation [%]", "Modulus [MPa]"]].agg(['mean', 'std']))

    with tabs[2]:
        st.subheader("Batch Overlay (Auto-Compensated)")
        sel_batch = st.selectbox("Select Batch:", sorted(df_m['Sample'].unique()))
        batch_files = df_m[df_m['Sample'] == sel_batch]['File'].tolist()
        fig_batch = go.Figure()
        for f in batch_files:
            if f in curves:
                c_df = curves[f]
                fig_batch.add_trace(go.Scatter(x=c_df['Strain_pct'], y=c_df['Stress_MPa'], mode='lines', name=f))
        fig_batch.update_layout(template="simple_white", xaxis=dict(title="<b>Strain (%)</b>", range=[0, None], **AXIS_STYLE), yaxis=dict(title="<b>Stress (MPa)</b>", range=[0, None], **AXIS_STYLE), showlegend=True, legend=legend_config)
        st.plotly_chart(fig_batch, use_container_width=True)

    with tabs[3]:
        st.subheader("Representative Comparison (Journal Ready)")
        fig_rep = go.Figure()
        unique_samples = sorted(df_m['Sample'].unique())
        for s_name in unique_samples:
            sub = df_m[df_m['Sample'] == s_name]
            rep_f = sub.iloc[(sub['UTS [MPa]'] - sub['UTS [MPa]'].mean()).abs().argsort()[:1]]['File'].values[0]
            if rep_f in curves:
                c_df = curves[rep_f]
                fig_rep.add_trace(go.Scatter(x=c_df['Strain_pct'], y=c_df['Stress_MPa'], mode='lines', line=dict(width=line_w), name=f"<b>{s_name}</b>"))
        fig_rep.update_layout(template="simple_white", height=800, xaxis=dict(title="<b>Strain (%)</b>", range=[0, None], **AXIS_STYLE), yaxis=dict(title="<b>Stress (MPa)</b>", range=[0, None], **AXIS_STYLE), showlegend=True, legend=legend_config, margin=dict(l=80, r=40, t=40, b=80))
        st.plotly_chart(fig_rep, use_container_width=True)

    with tabs[4]:
        st.download_button("📥 Download Stats", df_m.to_csv(index=False).encode('utf-8'), "summary.csv")
else:
    st.info("👋 Upload specimen files in the sidebar and click 'Process Batch'.")
