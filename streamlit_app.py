import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# --- 1. Page Configuration & Session State ---
st.set_page_config(page_title="Solomon Tensile Suite 2.1", layout="wide")

if 'master_tensile_df' not in st.session_state:
    st.session_state['master_tensile_df'] = pd.DataFrame()
if 'curve_storage' not in st.session_state:
    st.session_state['curve_storage'] = {}

AXIS_STYLE = dict(
    mirror=True, ticks='outside', showline=True, 
    linecolor='black', linewidth=2.5,
    title_font=dict(family="Times New Roman", size=22, color="black"),
    tickfont=dict(family="Times New Roman", size=18, color="black")
)

# --- 2. Header ---
st.title("🔬 Solomon Tensile Suite 2.1")
st.markdown("**Scientific Batch Framework for Mechanical Testing**")

# --- 3. Sidebar ---
with st.sidebar:
    st.header("📏 Specimen Geometry")
    width = st.number_input("Width (mm)", value=4.0)
    thickness = st.number_input("Thickness (mm)", value=4.0)
    l0 = st.number_input("Gauge Length (mm)", value=25.0)
    area = width * thickness
    
    st.header("📂 Data Input")
    with st.form("upload_form", clear_on_submit=True):
        batch_id = st.text_input("Batch/Sample Name", "Sample Batch 1")
        files = st.file_uploader("Upload Replicates", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)
        submit = st.form_submit_button("Process Batch")

    if st.button("Reset All Data", type="primary"):
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
        # Remove non-numeric rows
        df = df.apply(pd.to_numeric, errors='coerce').dropna(how='all').reset_index(drop=True)
        
        cols = df.columns.tolist()
        # Find Load column (N)
        load_col = next((c for c in cols if any(k in c.lower() for k in ['load', 'carico', 'force', 'sforzo (n)', 'n'])), None)
        # Find Extension column (mm)
        ext_col = next((c for c in cols if any(k in c.lower() for k in ['ext', 'defor', 'strain', 'mm', 'disp'])), None)
        
        if load_col and ext_col:
            df_std = pd.DataFrame({'Load_N': df[load_col], 'Ext_mm': df[ext_col]})
        else:
            # Fallback: Use first two columns if keywords fail
            df_std = pd.DataFrame({'Load_N': df.iloc[:, 0], 'Ext_mm': df.iloc[:, 1]})
        
        return df_std.dropna()
    except Exception as e:
        st.error(f"Error loading {file.name}: {e}")
        return None

if submit and files:
    batch_results = []
    for f in files:
        df_std = robust_load(f)
        
        # --- SAFETY CHECK: Prevent idxmax() crash ---
        if df_std is not None and not df_std.empty:
            df_std['Strain_pct'] = (df_std['Ext_mm'] / l0) * 100
            df_std['Stress_MPa'] = df_std['Load_N'] / area
            
            # Now safe to calculate idxmax
            peak_idx = df_std['Stress_MPa'].idxmax()
            df_std = df_std.iloc[:peak_idx + 1].copy()
            
            # Toe Compensation
            linear_region = df_std[(df_std['Strain_pct'] > 0.1) & (df_std['Strain_pct'] < 0.5)]
            if len(linear_region) > 2:
                E_slope, intercept = np.polyfit(linear_region['Strain_pct'], linear_region['Stress_MPa'], 1)
                shift = -intercept / E_slope
                df_std['Strain_pct'] = df_std['Strain_pct'] - shift
                df_std = df_std[df_std['Strain_pct'] >= 0].reset_index(drop=True)
                # Add (0,0) point
                origin = pd.DataFrame({'Load_N':[0], 'Ext_mm':[0], 'Strain_pct':[0], 'Stress_MPa':[0]})
                df_std = pd.concat([origin, df_std], ignore_index=True)
            
            uts = df_std['Stress_MPa'].max()
            elong = df_std['Strain_pct'].max()
            
            batch_results.append({
                "Sample": batch_id, "File": f.name,
                "UTS [MPa]": uts, "Elongation [%]": elong,
                "Modulus [MPa]": E_slope * 100 if 'E_slope' in locals() else 0
            })
            st.session_state['curve_storage'][f.name] = df_std
        else:
            st.warning(f"Skipping {f.name}: No numeric data found in Load/Extension columns.")
            
    if batch_results:
        new_data = pd.DataFrame(batch_results)
        st.session_state['master_tensile_df'] = pd.concat([st.session_state['master_tensile_df'], new_data], ignore_index=True)

# --- 5. Tabs ---
df_m = st.session_state['master_tensile_df']
curves = st.session_state['curve_storage']

if not df_m.empty:
    tabs = st.tabs(["📊 Dataset", "📉 Trends", "🎨 Batch Stack", "🏛️ Representative Stack", "💾 Export"])

    with tabs[0]:
        st.subheader("Results")
        st.dataframe(df_m)
        st.table(df_m.groupby("Sample")[["UTS [MPa]", "Elongation [%]"]].agg(['mean', 'std']))

    with tabs[3]:
        st.subheader("Representative Stress-Strain Stack")
        h_off = st.slider("Strain Offset (%)", 0, 50, 0)
        fig_rep = go.Figure()
        unique_samples = sorted(df_m['Sample'].unique())
        
        for i, s_name in enumerate(unique_samples):
            sub = df_m[df_m['Sample'] == s_name]
            m_uts = sub['UTS [MPa]'].mean()
            rep_f = sub.iloc[(sub['UTS [MPa]'] - m_uts).abs().argsort()[:1]]['File'].values[0]
            
            if rep_f in curves:
                c_df = curves[rep_f]
                x_s = i * h_off
                fig_rep.add_trace(go.Scatter(x=c_df['Strain_pct'] + x_s, y=c_df['Stress_MPa'], mode='lines', line=dict(width=2.5), showlegend=False))
                
                label = f"<b>{s_name}: UTS = {m_uts:.2f} MPa</b>"
                fig_rep.add_annotation(x=x_s, y=c_df['Stress_MPa'].max(), text=label, showarrow=False, align="left", xanchor="left", yanchor="bottom", yshift=15, font=dict(family="Times New Roman", size=16))

        fig_rep.update_layout(template="simple_white", xaxis_title="<b>Strain (%)</b>", yaxis_title="<b>Stress (MPa)</b>", xaxis=dict(range=[0, None], **AXIS_STYLE), yaxis=dict(range=[0, None], **AXIS_STYLE))
        st.plotly_chart(fig_rep, use_container_width=True)

    with tabs[4]:
        st.download_button("📥 Download Stats", df_m.to_csv(index=False).encode('utf-8'), "summary.csv")
else:
    st.info("👋 Upload specimen files to begin.")
