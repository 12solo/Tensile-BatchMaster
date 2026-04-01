import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import re
import os
from PIL import Image

# --- 1. Page Configuration & Session State ---
st.set_page_config(page_title="Solomon Tensile Suite 2.0", layout="wide")

if 'master_tensile_df' not in st.session_state:
    st.session_state['master_tensile_df'] = pd.DataFrame()
if 'curve_storage' not in st.session_state:
    st.session_state['curve_storage'] = {}
if 'legend_map' not in st.session_state:
    st.session_state['legend_map'] = {}

# Journal Style Global Config
AXIS_STYLE = dict(
    mirror=True, ticks='outside', showline=True, 
    linecolor='black', linewidth=2.5,
    title_font=dict(family="Times New Roman", size=22, color="black"),
    tickfont=dict(family="Times New Roman", size=18, color="black")
)

# --- 2. Header & Logo ---
logo_url = "https://raw.githubusercontent.com/12solo/Tensile-test-extrapolator/main/logo%20s.png"
col_l, col_h = st.columns([1, 5])
with col_l:
    try: st.image(logo_url, width=120)
    except: st.header("🔬")
with col_h:
    st.title("Solomon Tensile Suite 2.0")
    st.markdown("---")

# --- 3. Sidebar Configuration ---
with st.sidebar:
    st.header("📝 Specimen Geometry")
    width = st.number_input("Width (mm)", value=4.0)
    thickness = st.number_input("Thickness (mm)", value=4.0)
    l0 = st.number_input("Gauge Length (mm)", value=25.0)
    area = width * thickness
    
    st.header("🎨 Plot Styling")
    line_w = st.slider("Line Thickness", 1.0, 5.0, 2.5)
    
    st.header("📂 Data Input")
    with st.form("upload_form", clear_on_submit=True):
        batch_id = st.text_input("Batch/Sample Name", "Biocomposite-A")
        files = st.file_uploader("Upload Replicates (.csv, .xlsx)", accept_multiple_files=True)
        submit = st.form_submit_button("Process Batch")

    if st.button("Reset All Data", type="primary"):
        st.session_state['master_tensile_df'] = pd.DataFrame()
        st.session_state['curve_storage'] = {}
        st.rerun()

# --- 4. Processing Logic ---
if submit and files:
    batch_results = []
    for f in files:
        try:
            df = pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f)
            # Assume Col 0: Extension, Col 1: Load
            df.columns = ['Ext_mm', 'Load_N']
            df = df.apply(pd.to_numeric, errors='coerce').dropna().reset_index(drop=True)
            
            # Engineering Stress/Strain
            df['Strain_pct'] = (df['Ext_mm'] / l0) * 100
            df['Stress_MPa'] = df['Load_N'] / area
            
            # Toe Compensation (Shift to 0,0)
            linear_region = df[(df['Strain_pct'] > 0.1) & (df['Strain_pct'] < 0.5)]
            if len(linear_region) > 2:
                E_slope, intercept = np.polyfit(linear_region['Strain_pct'], linear_region['Stress_MPa'], 1)
                shift = -intercept / E_slope
                df['Strain_pct'] = df['Strain_pct'] - shift
                df = df[df['Strain_pct'] >= 0].reset_index(drop=True)
            
            uts = df['Stress_MPa'].max()
            elong = df['Strain_pct'].max()
            
            batch_results.append({
                "Sample": batch_id, "File": f.name,
                "UTS [MPa]": uts, "Elongation [%]": elong,
                "Modulus [MPa]": E_slope * 100 if 'E_slope' in locals() else 0
            })
            st.session_state['curve_storage'][f.name] = df
        except Exception as e:
            st.error(f"Error processing {f.name}: {e}")
            
    new_df = pd.DataFrame(batch_results)
    st.session_state['master_tensile_df'] = pd.concat([st.session_state['master_tensile_df'], new_df], ignore_index=True)

# --- 5. Dashboard Tabs ---
df_m = st.session_state['master_tensile_df']
curves = st.session_state['curve_storage']

if not df_m.empty:
    tabs = st.tabs(["📊 Dataset", "📉 Trends", "🎨 Batch Stack", "🏛️ Representative Stack", "💾 Export"])

    with tabs[0]:
        st.subheader("Individual Specimen Results")
        st.dataframe(df_m, use_container_width=True)
        
        st.subheader("Batch Statistics (Mean ± SD)")
        stats = df_m.groupby("Sample")[["UTS [MPa]", "Elongation [%]", "Modulus [MPa]"]].agg(['mean', 'std']).T
        st.table(stats)

    with tabs[1]:
        st.subheader("Inter-Sample Comparison")
        target = st.selectbox("Select Property", ["UTS [MPa]", "Elongation [%]", "Modulus [MPa]"])
        trend_df = df_m.groupby("Sample")[target].agg(['mean', 'std', 'count']).reset_index()
        
        fig_trend = px.line(trend_df, x="Sample", y="mean", 
                            error_y=trend_df['std'], markers=True, template="simple_white")
        fig_trend.update_layout(xaxis_title="<b>Sample ID</b>", yaxis_title=f"<b>{target}</b>", 
                                xaxis=AXIS_STYLE, yaxis=AXIS_STYLE)
        st.plotly_chart(fig_trend, use_container_width=True)

    with tabs[2]:
        st.subheader("Batch Replicate Inspection")
        sel_batch = st.selectbox("Select Batch:", sorted(df_m['Sample'].unique()))
        batch_files = df_m[df_m['Sample'] == sel_batch]['File'].tolist()
        h_offset = st.slider("Strain Offset (%)", 0, 20, 2)
        
        fig_batch = go.Figure()
        for i, f in enumerate(batch_files):
            c_df = curves[f]
            x_shift = i * h_offset
            fig_batch.add_trace(go.Scatter(x=c_df['Strain_pct'] + x_shift, y=c_df['Stress_MPa'], 
                                           mode='lines', name=f"Specimen {i+1}", showlegend=False))
            # Annotation
            fig_batch.add_annotation(x=(c_df['Strain_pct']+x_shift).mean(), y=c_df['Stress_MPa'].max(),
                                     text=f"<b>Spec {i+1}</b>", showarrow=False, yshift=15,
                                     font=dict(family="Times New Roman", size=14))
        
        fig_batch.update_layout(template="simple_white", height=700, xaxis_title="<b>Strain (%)</b>", 
                                yaxis_title="<b>Stress (MPa)</b>", xaxis=AXIS_STYLE, yaxis=AXIS_STYLE)
        st.plotly_chart(fig_batch, use_container_width=True)

    with tabs[3]:
        st.subheader("Representative Stress-Strain Stack")
        h_off_global = st.slider("Global Strain Offset (%)", 0, 50, 5)
        fig_rep = go.Figure()
        
        unique_samples = sorted(df_m['Sample'].unique())
        for i, s_name in enumerate(unique_samples):
            sub = df_m[df_m['Sample'] == s_name]
            m_uts = sub['UTS [MPa]'].mean()
            s_uts = sub['UTS [MPa]'].std()
            # Find file closest to mean UTS
            rep_f = sub.iloc[(sub['UTS [MPa]'] - m_uts).abs().argsort()[:1]]['File'].values[0]
            
            c_df = curves[rep_f]
            x_shift = i * h_off_global
            
            fig_rep.add_trace(go.Scatter(x=c_df['Strain_pct'] + x_shift, y=c_df['Stress_MPa'], 
                                         mode='lines', line=dict(width=line_w), showlegend=False))
            
            # Scientific Inline Legend: Name and UTS in one row
            label = f"<b>{s_name}: UTS = {m_uts:.2f} ± {s_uts:.2f} MPa</b>"
            fig_rep.add_annotation(x=x_shift, y=c_df['Stress_MPa'].max(),
                                   text=label, showarrow=False, align="left", xanchor="left", yanchor="bottom",
                                   yshift=10, font=dict(family="Times New Roman", size=16))

        fig_rep.update_layout(template="simple_white", height=800, xaxis_title="<b>Engineering Strain (%)</b>", 
                              yaxis_title="<b>Engineering Stress (MPa)</b>", xaxis=AXIS_STYLE, yaxis=AXIS_STYLE)
        st.plotly_chart(fig_rep, use_container_width=True)

    with tabs[4]:
        st.subheader("Data Export")
        csv_sum = df_m.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results Summary", csv_sum, "tensile_results.csv", "text/csv")
        
        # Build Representative XY Export
        rep_list = []
        for s_name in unique_samples:
            sub = df_m[df_m['Sample'] == s_name]
            rep_f = sub.iloc[(sub['UTS [MPa]'] - sub['UTS [MPa]'].mean()).abs().argsort()[:1]]['File'].values[0]
            temp = curves[rep_f][['Strain_pct', 'Stress_MPa']].copy()
            temp.columns = [f"{s_name}_Strain_%", f"{s_name}_Stress_MPa"]
            rep_list.append(temp)
        
        if rep_list:
            rep_csv = pd.concat(rep_list, axis=1).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Representative Curves (XY Data)", rep_csv, "rep_curves.csv", "text/csv")
else:
    st.info("👋 Upload specimen batches to begin analysis.")
