# 🛰️ Rocha SAR-7: Multi-Sensor Hydro-Climatic Falsification System

**NASA Space Apps Challenge 2026 — Challenge: Dancing with the SARs**

## Overview
**Rocha SAR-7** is an open-source hydro-climatic monitoring tool designed to eliminate false positives in Synthetic Aperture Radar (SAR) surface change detection. Applied to the strategic coastal-wetland transect of **Rocha, Uruguay** (*India Muerta Wetlands*, *Ruta 9 Corridor*, and *El Palenque Coastal Outcrop*), the system implements a **7-Layer Popperian Falsification Protocol** calibrated via an orbital ground-truth bedrock anchor.

## Scientific Methodology
1. **Structure (Sentinel-1 / NISAR):** C-Band SAR VV/VH backscatter ($\sigma^0$ in dB) for surface roughness and water detection.
2. **Thermal Inertia (Landsat 8/9):** Surface temperature differentiation between solid bedrock and saturated sediments.
3. **Hydrological Drainage (NDWI):** Surface water accumulation and soil impermeability verification.
4. **Spectral Chemistry (Sentinel-2):** Clay and iron-oxide alteration indices under drought/flood cycles.
5. **Atmospheric Gas (Sentinel-5P):** Biogenic methane ($CH_4$) flux monitoring over inundated wetlands.
6. **Multi-Regime Dynamics:** Comparative baseline analysis across extreme drought and inundation regimes.
7. **Millimetric Precision (InSAR Phase):** Vertical soil swelling and subsidence tracking.

## Verified Orbital Telemetry
- **Primary Product:** `S1D_IW_SLC__1SDV_20260513T085750_20260513T085817_002763_004AB5_25B9`
- **Ground-Truth Calibration Anchor:** El Palenque Granite Outcrop (`-10.74 dB` verified baseline)
## Real-World Impact
By eliminating SAR false alarms over dynamic ecosystems like the **India Muerta Ramsar Wetlands** and the **Ruta 9 infrastructure corridor**, **Rocha SAR-7** provides environmental agencies, agricultural producers, and civil protection teams with reliable early warnings for extreme floods, droughts, and wetland methane emissions without requiring expensive ground-sensor networks.

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## License
Licensed under the **Apache License 2.0** in compliance with NASA Space Apps Challenge open-source guidelines.
