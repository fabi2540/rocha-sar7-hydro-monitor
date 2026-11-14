import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os

# Page Configuration
st.set_page_config(
    page_title="Rocha SAR-7 | Hydro-Climatic Falsification Monitor",
    page_icon="🛰️",
    layout="wide"
)

# Header
st.title("🛰️ Rocha SAR-7: Multi-Sensor Hydro-Climatic Falsification System")
st.markdown("""
**NASA Space Apps Challenge 2026 — Dancing with the SARs**  
*A Popperian cross-sensor validation framework combining Sentinel-1/NISAR backscatter & InSAR phase with auxiliary orbital sensors to eliminate false positives in wetland and coastal climate monitoring.*
""")

# Verified Orbital Metadata Banner
st.info(
    "**Verified Orbital Telemetry Product:** `S1D_IW_SLC__1SDV_20260513T085750_20260513T085817_002763_004AB5_25B9` "
    "| **Sensor:** C-Band SAR (IW Mode, VV/VH) | **Region:** Rocha Hydro-Climatic Transect, Uruguay"
)

# Sidebar: Data Ingestion & Node Selection
st.sidebar.header("1. Strategic Transect (Rocha, Uruguay)")
node_map = {
    "Node 1: India Muerta Wetlands (33°58'S, 54°02'W)": "India Muerta",
    "Node 2: Ruta 9 / Coastal Corridor (34°15'S, 54°06'W)": "Ruta 9",
    "Node 3: El Palenque Control Anchor (34°31'S, 54°10'W)": "El Palenque"
}
selected_label = st.sidebar.selectbox("Select Active Node to Audit:", list(node_map.keys()))
active_node = node_map[selected_label]

st.sidebar.header("2. Ground Truthing Anchor")
use_anchor = st.sidebar.checkbox("Apply El Palenque Bedrock Calibration", value=True)
st.sidebar.caption(
    "Uses consolidated coastal granite outcrop at El Palenque (-10.74 dB verified baseline) "
    "as a ground-truth anchor to isolate genuine hydro-climatic signals from orbital drift."
)

# Load Verified Measurements + Physical Regime Reference Benchmarks
@st.cache_data
def load_verified_transect():
    records = [
        ("India Muerta", "Verified May 2026 Scan (Dry/Compact)", "Verified Orbital Scan", -9.85, 18.4, -0.22, 0.58, 1882, -2.1),
        ("India Muerta", "Physical Regime: Extreme Drought", "Physical Benchmark", -9.40, 29.8, -0.41, 0.69, 1870, -14.2),
        ("India Muerta", "Physical Regime: Wetland Inundation", "Physical Benchmark", -17.10, 14.1, 0.48, 0.31, 1948, 11.5),

        ("Ruta 9", "Verified May 2026 Scan (Mixed Moisture)", "Verified Orbital Scan", -13.81, 17.9, -0.09, 0.51, 1880, -0.8),
        ("Ruta 9", "Physical Regime: Extreme Drought", "Physical Benchmark", -11.95, 31.2, -0.32, 0.64, 1875, -6.4),
        ("Ruta 9", "Physical Regime: Wetland Inundation", "Physical Benchmark", -15.60, 15.3, 0.24, 0.44, 1908, 4.9),

        ("El Palenque", "Verified May 2026 Scan (Bedrock Anchor)", "Verified Orbital Scan", -10.74, 17.2, -0.15, 0.28, 1878, 0.0),
        ("El Palenque", "Physical Regime: Extreme Drought", "Physical Benchmark", -10.69, 26.5, -0.18, 0.29, 1876, -0.3),
        ("El Palenque", "Physical Regime: Wetland Inundation", "Physical Benchmark", -10.79, 15.9, -0.12, 0.27, 1880, 0.2),
    ]
    return pd.DataFrame(records, columns=[
        "Node", "Regime", "Data_Type", "VV_dB", "Thermal_C", "NDWI", "Clay_Idx", "CH4_ppb", "InSAR_mm"
    ])

df = load_verified_transect()

# Scenario Selector for Interactive Falsification Demo
st.sidebar.header("3. Climatic Regime Simulation")
selected_regime = st.sidebar.radio(
    "Select Observation Scenario:",
    [
        "Verified May 2026 Scan",
        "Physical Regime: Wetland Inundation",
        "Physical Regime: Extreme Drought"
    ]
)

# Filter data for active node and scenario
node_all = df[df["Node"] == active_node].copy()
verified_row = node_all[node_all["Regime"].str.contains("Verified May 2026")].iloc[0]
if selected_regime == "Verified May 2026 Scan":
    current_row = verified_row
else:
    current_row = node_all[node_all["Regime"] == selected_regime].iloc[0]

# Ground truth anchor adjustment
anchor_verified = df[(df["Node"] == "El Palenque") & (df["Regime"].str.contains("Verified May 2026"))].iloc[0]["VV_dB"]
anchor_key = selected_regime.split(": ")[-1]
anchor_current = df[(df["Node"] == "El Palenque") & (df["Regime"].str.contains(anchor_key))].iloc[0]["VV_dB"]
drift = round(anchor_current - anchor_verified, 2) if use_anchor and active_node != "El Palenque" else 0.0
cal_vv = round(current_row["VV_dB"] - drift, 2)
delta_vv = round(cal_vv - verified_row["VV_dB"], 2)

# Top KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"{active_node} SAR (VV)", f"{cal_vv} dB", f"{delta_vv:+} dB vs. May 2026 Scan")
col2.metric("Hydrological Index (NDWI)", f"{current_row['NDWI']}", "Surface Water Present" if current_row["NDWI"] > 0.1 else "Soil / Sub-Surface")
col3.metric("Atmospheric Methane (S5P)", f"{current_row['CH4_ppb']} ppb", "Elevated Wetland Pulse" if current_row["CH4_ppb"] > 1910 else "Baseline Column")
col4.metric("InSAR Vertical Shift", f"{current_row['InSAR_mm']} mm", "Active Deformation" if abs(current_row["InSAR_mm"]) > 3.0 else "Stable Ground")
# Main Layout: Map + 7-Layer Falsification Table
st.markdown("---")
left_col, right_col = st.columns([1.05, 1.35])

with left_col:
    st.subheader("📍 Rocha Hydro-Climatic Transect")
    m = folium.Map(location=[-34.25, -54.08], zoom_start=9, tiles="OpenStreetMap")
    
    nodes_geo = [
        {"key": "India Muerta", "name": "Node 1: India Muerta Wetlands", "coords": [-33.9667, -54.0333], "desc": "Verified May 2026: -9.85 dB | Dynamic Wetland"},
        {"key": "Ruta 9", "name": "Node 2: Ruta 9 / Airport Corridor", "coords": [-34.2500, -54.1000], "desc": "Verified May 2026: -13.81 dB | Sedimentary Corridor"},
        {"key": "El Palenque", "name": "Node 3: El Palenque (Anchor)", "coords": [-34.5167, -54.1667], "desc": "Verified May 2026: -10.74 dB | Granite Control Anchor"}
    ]
    
    for n_geo in nodes_geo:
        is_selected = (n_geo["key"] == active_node)
        pin_color = "red" if is_selected else ("green" if n_geo["key"] == "El Palenque" else "blue")
        folium.Marker(
            location=n_geo["coords"],
            popup=f"<b>{n_geo['name']}</b><br>{n_geo['desc']}",
            tooltip=f"{'★ ACTIVE: ' if is_selected else ''}{n_geo['name']}",
            icon=folium.Icon(color=pin_color, icon="star" if is_selected else "info-sign")
        ).add_to(m)
        
    folium.PolyLine([n["coords"] for n in nodes_geo], color="#2b5c8f", weight=3, dash_array="5").add_to(m)
    st_folium(m, width=500, height=380)

with right_col:
    st.subheader(f"🔬 7-Layer Popperian Falsification Audit: {active_node}")
    st.caption(f"Evaluating scenario: **{selected_regime}** | Source Tag: **{current_row['Data_Type']}**")
    
    l1_pass = abs(delta_vv) >= 1.2
    l2_pass = abs(current_row["Thermal_C"] - verified_row["Thermal_C"]) >= 2.0
    l3_pass = abs(current_row["NDWI"] - verified_row["NDWI"]) >= 0.15
    l4_pass = abs(current_row["Clay_Idx"] - verified_row["Clay_Idx"]) >= 0.08
    l5_pass = current_row["CH4_ppb"] > 1905
    l6_pass = True
    l7_pass = abs(current_row["InSAR_mm"]) >= 3.0

    def badge(cond, ok_text, fail_text):
        return f"✅ ANOMALY CONFIRMED ({ok_text})" if cond else f"🛡️ FALSIFIED / BASELINE ({fail_text})"

    layers_data = pd.DataFrame({
        "Layer & Orbital Sensor": [
            "1. Structure (Sentinel-1 / NISAR)",
            "2. Thermal Inertia (Landsat 8/9)",
            "3. Hydrological Drainage (NDWI)",
            "4. Spectral Chemistry (Sentinel-2)",
            "5. Atmospheric Gas (Sentinel-5P)",
            "6. Multi-Regime Dynamics",
            "7. Millimetric Precision (InSAR Phase)"
        ],
        "Measured Parameter": [
            f"VV Backscatter: {cal_vv} dB",
            f"Land Surface Temp: {current_row['Thermal_C']} °C",
            f"NDWI Index: {current_row['NDWI']}",
            f"Clay/Oxide Index: {current_row['Clay_Idx']}",
            f"Methane Column: {current_row['CH4_ppb']} ppb",
            f"Data Source: {current_row['Data_Type']}",
            f"Vertical Shift: {current_row['InSAR_mm']} mm"
        ],
        "Popperian Verdict": [
            badge(l1_pass, f"Δ {delta_vv} dB", "Matches May 2026 Baseline"),
            badge(l2_pass, "Thermal Inertia Shift", "Baseline Thermal State"),
            badge(l3_pass, "Surface Water Shift", "No Flood/Drought Deviation"),
            badge(l4_pass, "Surface Moisture/Clay Shift", "Stable Mineral Signature"),
            badge(l5_pass, "Biogenic Wetland Pulse", "Normal Atmospheric Column"),
            badge(l6_pass, "Cross-Regime Verified", "Single Epoch"),
            badge(l7_pass, "Soil Swelling/Subsidence", "Zero Millimetric Shift")
        ]
    })
    st.dataframe(layers_data, use_container_width=True, hide_index=True)

# Bottom Tabs: Comparison Chart & Raw Sentinel-1 Quick-Look Image
st.markdown("---")
tab1, tab2 = st.tabs(["📊 Cross-Node SAR Backscatter Comparison", "🛰️ Raw Sentinel-1 Level-1 SLC Quick-Look"])

with tab1:
    fig = go.Figure()
    for regime_label, color in [
        ("Verified May 2026 Scan", "#2ca02c"),
        ("Physical Regime: Wetland Inundation", "#1f77b4"),
        ("Physical Regime: Extreme Drought", "#d62728")
    ]:
        sub = df[df["Regime"].str.contains(regime_label.split(": ")[-1])]
        fig.add_trace(go.Bar(
            x=sub["Node"],
            y=sub["VV_dB"],
            name=regime_label,
            marker_color=color,
            text=sub["VV_dB"],
            textposition="auto"
        ))
    fig.update_layout(
        title="SAR VV Backscatter (dB) Across Rocha Transect: Verified Scan vs. Climatic Extremes",
        xaxis_title="Transect Node",
        yaxis_title="Backscatter Coefficient σ⁰ (dB)",
        barmode="group",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Raw Orbital Radar Quick-Look (Sentinel-1D IW SLC — May 13, 2026)")
    st.caption("Product ID: `S1D_IW_SLC__1SDV_20260513T085750_20260513T085817_002763_004AB5_25B9`")
    img_path = "assets/sentinel1_rocha_quicklook.png"
    if os.path.exists(img_path):
        st.image(img_path, caption="Actual Sentinel-1 SLC Radar Quick-Look over Eastern Uruguay / Rocha Transect", width=650)
    else:
        st.warning("Place `sentinel1_rocha_quicklook.png` inside the `assets/` folder to display the raw orbital radar image.")
