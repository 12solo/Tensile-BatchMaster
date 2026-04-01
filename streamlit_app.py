import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# --- 1. Page Configuration & Session State ---
st.set_page_config(page_title="Solomon Tensile Suite 2.1", layout="wide")

# Ensure all data storage is initialized
if 'master_tensile_df' not in st.session_state:
    st.session_state['master_tensile_df'] = pd.DataFrame()
if 'curve_storage' not in st.session_state:
    st.session_state['curve_storage'] = {}

# Journal Style Global Config: Integrated Axis and Border
AXIS_STYLE = dict(
    showline=True,
    mirror=True,           # This creates the "Border" by mirroring the axis
    ticks='outside', 
    linecolor='black', 
    linewidth=2.5,         # The thickness of the border/axis line
    title_font=dict(family="Times New Roman", size=22, color="black"),
    tickfont=dict(family="Times New Roman", size=18, color="black"),
    showgrid=False,        
    zeroline=False,        
    rangemode='tozero'
)

# --- 2. Header ---
st.title("🔬 Solomon Tensile Suite 2.1")
st.markdown("**Complete Scientific Analysis: Replicates, Trends & Zero-Aligned Stacking**")

# --- 3. Sidebar ---
with st.sidebar:
    st.header("📏 Specimen Geometry")
    width = st.number_input("Width (mm)", value=4.0)
    thickness = st.number_input("Thickness (mm)", value=4.0)
    l0 = st.number_input("Gauge Length (mm)", value=25.0)
    area = width * thickness
    
    st.header("🎨 Plot Styling")
    line_w = st.slider("Curve Thickness", 1.0, 5.0, 2.5)
    
    st.header("📂 Data Input")
    with st.form("upload_form", clear_on_submit=True):
        batch_id = st.text_input("Batch/Sample Name", "Sample Batch 1")
        files = st.file_uploader("Upload Replicates (.csv, .xlsx, .txt)", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)
        submit = st.form_submit_button("Process Batch")

    if st.button("Reset Entire Study", type="primary"):
        st.session_state['master_tensile_df'] = pd.DataFrame()
        st.session_state['curve_storage'] = {}
        st.rerun()

# --- 4. Processing Engine ---
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
        ext_col = next((c for c in cols if any(k in c.lower() for k in ['ext', 'defor', 'strain', 'mm', 'disp'])), None)
        
        if load_col and ext_col:
            df_std = pd.DataFrame({'Load_N': df[load_col], 'Ext_mm': df[ext_col]})
        else:
            df_std = pd.DataFrame({'Load_N': df.iloc[:, 0], 'Ext_mm': df.iloc[:, 1]})
        
        return df_std.dropna()
    except Exception as e:
        st.error(f"Error loading {file.name}: {e}")
        return None

if submit and files:
    batch_results = []
    for f in files:
        df_std = robust_load(f)
        if df_std is not None and not df_std.empty:
            df_std['Strain_pct'] = (df_std['Ext_mm'] / l0) * 100
            df_std['Stress_MPa'] = df_std['Load_N'] / area
            
            # Truncate at Maximum Stress (Fracture)
            peak_idx = df_std['Stress_MPa'].idxmax()
            df_std = df_std.iloc[:peak_idx + 1].copy()
            
            # Toe Compensation (X-shift to 0,0)
            linear_region = df_std[(df_std['Strain_pct'] > 0.1) & (df_std['Strain_pct'] < 0.5)]
            if len(linear_region) > 2:
                E_slope, intercept = np.polyfit(linear_region['Strain_pct'], linear_region['Stress_MPa'], 1)
                shift = -intercept / E_slope
                df_std['Strain_pct'] = df_std['Strain_pct'] - shift
                df_std = df_std[df_std['Strain_pct'] >= 0].reset_index(drop=True)
                
                # Origin Injection: Ensure it physically starts at 0,0
                origin = pd.DataFrame({'Load_N':[0], 'Ext_mm':[0], 'Strain_pct':[0], 'Stress_MPa':[0]})
                df_std = pd.concat([origin, df_std], ignore_index=True)
            
            batch_results.append({
                "Sample": batch_id, "File": f.name,
                "UTS [MPa]": df_std['Stress_MPa'].max(), 
                "Elongation [%]": df_std['Strain_pct'].max(),
                "Modulus [MPa]": E_slope * 100 if 'E_slope' in locals() else 0
            })
            st.session_state['curve_storage'][f.name] = df_std
            
    if batch_results:
        new_data = pd.DataFrame(batch_results)
        st.session_state['master_tensile_df'] = pd.concat([st.session_state['master_tensile_df'], new_data], ignore_index=True)

# --- 5. Dashboard View ---
df_m = st.session_state['master_tensile_df']
curves = st.session_state['curve_storage']

if not df_m.empty:
    tabs = st.tabs(["📊 Dataset", "📉 Trends", "🎨 Batch Replicates", "🏛️ Representative Comparison", "💾 Export"])

    with tabs[0]:
        st.subheader("Individual Specimen Results")
        st.dataframe(df_m, use_container_width=True)
        st.subheader("Batch Summary (Mean ± SD)")
        st.table(df_m.groupby("Sample")[["UTS [MPa]", "Elongation [%]", "Modulus [MPa]"]].agg(['mean', 'std']))

    with tabs[1]:
        st.subheader("Inter-Sample Comparison")
        target = st.selectbox("Property to Compare", ["UTS [MPa]", "Elongation [%]", "Modulus [MPa]"])
        trend_df = df_m.groupby("Sample")[target].agg(['mean', 'std', 'count']).reset_index()
        fig_trend = px.line(trend_df, x="Sample", y="mean", error_y=trend_df['std'], markers=True, template="simple_white")
        fig_trend.update_layout(xaxis_title="<b>Sample ID</b>", yaxis_title=f"<b>{target}</b>", xaxis=AXIS_STYLE, yaxis=AXIS_STYLE)
        st.plotly_chart(fig_trend, use_container_width=True)

    with tabs[2]:
        st.subheader("Batch Replicate Overlay (0,0 Alignment)")
        sel_batch = st.selectbox("Select Batch to Inspect:", sorted(df_m['Sample'].unique()))
        batch_files = df_m[df_m['Sample'] == sel_batch]['File'].tolist()
        
        fig_batch = go.Figure()
        for f in batch_files:
            if f in curves:
                c_df = curves[f]
                fig_batch.add_trace(go.Scatter(x=c_df['Strain_pct'], y=c_df['Stress_MPa'], 
                                               mode='lines', name=f, line=dict(width=line_w)))
        
        fig_batch.update_layout(
            template="simple_white", height=700,
            xaxis=dict(title="<b>Strain (%)</b>", range=[0, None], **AXIS_STYLE),
            yaxis=dict(title="<b>Stress (MPa)</b>", range=[0, None], **AXIS_STYLE),
            margin=dict(l=80, r=40, t=40, b=80) 
        )
        st.plotly_chart(fig_batch, use_container_width=True)

    with tabs[3]:
        st.subheader("Representative Comparison (Perfect Corner Alignment)")
        fig_rep = go.Figure()
        unique_samples = sorted(df_m['Sample'].unique())
        
        for i, s_name in enumerate(unique_samples):
            sub = df_m[df_m['Sample'] == s_name]
            m_uts = sub['UTS [MPa]'].mean()
            # Select curve closest to the mean UTS for the batch
            rep_f = sub.iloc[(sub['UTS [MPa]'] - m_uts).abs().argsort()[:1]]['File'].values[0]
            
            if rep_f in curves:
                c_df = curves[rep_f]
                fig_rep.add_trace(go.Scatter(x=c_df['Strain_pct'], y=c_df['Stress_MPa'], 
                                             mode='lines', line=dict(width=line_w), name=s_name))
                
                fig_rep.add_annotation(x=c_df['Strain_pct'].max(), y=c_df['Stress_MPa'].max(),
                                       text=f"<b>{s_name}</b>", showarrow=True, arrowhead=1,
                                       ax=20, ay=-30, font=dict(family="Times New Roman", size=16))

        fig_rep.update_layout(
            template="simple_white", height=800,
            xaxis=dict(title="<b>Engineering Strain (%)</b>", range=[0, None], **AXIS_STYLE),
            yaxis=dict(title="<b>Engineering Stress (MPa)</b>", range=[0, None], **AXIS_STYLE),
            legend=dict(font=dict(family="Times New Roman", size=16)),
            margin=dict(l=80, r=40, t=40, b=80) 
        )
        st.plotly_chart(fig_rep, use_container_width=True)

    with tabs[4]:
        st.subheader("Export Results")
        csv_sum = df_m.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Stats Summary", csv_sum, "tensile_summary.csv", "text/csv")
        
        # Build XY Data for all representative curves
        rep_xy = []
        for s_name in unique_samples:
            sub = df_m[df_m['Sample'] == s_name]
            m_uts = sub['UTS [MPa]'].mean()
            rep_f = sub.iloc[(sub['UTS [MPa]'] - m_uts).abs().argsort()[:1]]['File'].values[0]
            temp = curves[rep_f][['Strain_pct', 'Stress_MPa']].copy()
            temp.columns = [f"{s_name}_Strain", f"{s_name}_Stress"]
            rep_xy.append(temp)
        
        if rep_xy:
            final_xy = pd.concat(rep_xy, axis=1).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download XY Data", final_xy, "representative_curves.csv", "text/csv")
else:
    st.info("👋 Use the sidebar to upload specimen files and begin analysis.")
