import streamlit as st
import numpy as np
import pandas as pd

# APP STYLING 
st.set_page_config(page_title="SweatSensor - BME Research", layout="wide")

st.title("SweatSense: Heat-Stress Monitoring")
st.markdown("### Low-Cost Enzymatic Patch with Kinetic Correction & Physiological Modeling")
st.write("---")

# SIDEBAR: USER PROFILE (Chapter 13 Inputs) 
st.sidebar.header("👤 User Profile")
body_mass = st.sidebar.number_input("Initial Body Mass (kg)", value=80, help="Required for Chapter 13 Fluid Balance Integral")
work_duration = st.sidebar.slider("Work Duration (minutes)", 0, 180, 45)

# MAIN UI: SENSOR INPUTS (Chapter 8 Inputs) 
col1, col2 = st.columns(2)

with col1:
    st.header("📸 Patch Data")
    intensity = st.slider("Color Intensity (0-100)", 0, 100, 65, help="Raw optical signal from phone camera")
    temp_c = st.slider("Skin/Ambient Temp (°C)", 20, 45, 35, help="Required for Arrhenius Temperature Correction")

# THE ENGINEERING "BRAIN" 
def calculate_risk(intensity, temp_c, time_min, mass):
    # 1. CHAPTER 8: Kinetic Correction (Michaelis-Menten)
    V_max = 100 
    K_m = 15     
    # Arrhenius-style temperature factor (reactions speed up in heat)
    temp_factor = np.exp(0.05 * (temp_c - 25)) 
    corrected_v = intensity / temp_factor
    
    # Preventing division by zero/negative
    if corrected_v >= V_max: corrected_v = V_max - 0.5
    lactate_mm = (K_m * corrected_v) / (V_max - corrected_v)
    
    # 2. CHAPTER 13: Physiological Modeling (Dehydration Integral)
    # Average sweat rate proxy (L/min)
    sweat_rate = 0.015 # Approx 0.9L per hour
    total_fluid_loss = sweat_rate * time_min
    dehydration_pct = (total_fluid_loss / mass) * 100
    
    return lactate_mm, dehydration_pct

lac, dehy = calculate_risk(intensity, temp_c, work_duration, body_mass)

# THE OUTPUTS 
with col2:
    st.header("📊 Real-Time Risk Analysis")
    
    # Metric Boxes
    m1, m2 = st.columns(2)
    m1.metric("Corrected Lactate", f"{lac:.1f} mM")
    m2.metric("Est. Dehydration", f"{dehy:.1f} %")

    # Risk Logic
    if dehy > 2.0 or lac > 20:
        st.error("🚨 HIGH RISK: Immediate intervention required.")
    elif dehy > 1.0 or lac > 12:
        st.warning("⚠️ MODERATE RISK: Increase hydration and monitor.")
    else:
        st.success("✅ LOW RISK: Physiological strain is within safe limits.")

# EDUCATIONAL SECTION
with st.expander("View Engineering Math"):
    st.latex(r"Lactate\ [S] = \frac{K_m \cdot V_{corr}}{V_{max} - V_{corr}}")
    st.latex(r"Dehydration\ \% = \frac{\int_{0}^{t} \dot{V}_{sweat} \, dt}{Mass} \times 100")
